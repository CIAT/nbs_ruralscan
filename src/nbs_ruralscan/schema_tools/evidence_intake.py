"""Gated evidence intake with explicit inputs and recoverable register writes."""

from __future__ import annotations

import csv
import json
import hashlib
import os
from contextlib import ExitStack
from dataclasses import dataclass, fields, replace
from datetime import date
from pathlib import Path

import fitz


from nbs_ruralscan.ingest.integrity import (
    identity_error,
    pdf_title_error,
    source_identity_differs,
    validate_source_id,
)
from nbs_ruralscan.recipe.evidence import EvidenceUnit, validate
from nbs_ruralscan.recipe.cell_synthesis import load_bands
from nbs_ruralscan.schema_tools import check_bands, check_context, check_direction
from nbs_ruralscan.schema_tools.check_numbers import (
    _floats,
    _nums,
    _rel_nums,
    observed_range_mismatches,
)
from nbs_ruralscan.schema_tools.check_scope import m2b_policy
from nbs_ruralscan.schema_tools.validate_sources import _native_part
from nbs_ruralscan.schema_tools.migrate_effects import (
    append_to_register,
    resync_vars_extracted,
    stamp_extracted,
)

from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import staged_publish

#: accepted extraction rulesets (methodology/RULESET_VERSIONS.md; v1.6.3–v1.6.6 are search /
#: tagging / note-rule patches — the extraction contract is unchanged since v1.6.2, apart from
#: v1.6.9's `context.practice_as_described`, which `check_context` polices)
_RULESETS = {
    "v1.6.0",
    "v1.6.1",
    "v1.6.2",
    "v1.6.3",
    "v1.6.4",
    "v1.6.5",
    "v1.6.6",
    "v1.6.7",
    "v1.6.8",
    "v1.6.9",
    "v1.6.10",
    "v1.6.11",
    "v1.6.12",
    "v1.6.13",
    "v1.6.14",
    "v1.6.15",
    "v1.6.16",
    "v1.7.0",
    "v1.8.0",
    # Historical stamps remain valid; --allow-structural controls T4 scope.
    "v1.6.17",
    # v1.6.18: catalogue #39, no mechanism no unit
    "v1.6.18",
    # v1.9.0: catalogue #50, operational-risk evidence (Pete review 2026-10-22/23)
    "v1.9.0",
    # v1.9.1: catalogue #51, significance at the 5% convention
    "v1.9.1",
    # v1.9.2: catalogue #52, capture structure required; no synthetic mulch
    "v1.9.2",
    # v1.9.3: catalogue #53, reviewer-readable units (acronyms, baseline, absolute amounts)
    "v1.9.3",
    # v1.9.4: catalogue #54, preserve T4 relationships separately from executable mappings
    "v1.9.4",
    # v1.9.5: page-linked T4 spatial-targeting / implementation-purpose gate
    "v1.9.5",
    # v1.9.6: scientific plausibility before T4 numeric calibration
    "v1.9.6",
    # v1.9.7: catalogue #56, hazard severity + stated event magnitude logged on hazard units
    "v1.9.7",
    # v1.9.8: retain quantitative regional profiles for compatible-source synthesis
    "v1.9.8",
    # v1.9.9: catalogue #57, ranges by weaker end, single-plot cap, p = .05 case by case
    "v1.9.9",
    # v1.10.0: reported practice ranges and reviewed calibration are distinct
    "v1.10.0",
    # v1.10.1: catalogue #59-#62, inferred limits, design geometry, one dataset one unit
    "v1.10.1",
}


@dataclass(frozen=True)
class EvidenceIntakePaths:
    """All data used by the gated staging-to-register entrypoint.

    Evidence and sources are the only write targets. Other files and the corpus
    are read-only. Individual paths support layouts independent of the compiler.
    """

    evidence: Path
    sources: Path
    queue: Path
    families: Path
    variables: Path
    bands: Path
    contexts: Path
    direction_sense: Path
    operational_policy: Path
    corpus: Path

    def __post_init__(self):
        # Keep leaf/parent symlinks visible to publication preflight.
        for field in fields(self):
            object.__setattr__(
                self, field.name, Path(os.path.abspath(getattr(self, field.name)))
            )

    @classmethod
    def from_root(
        cls, root: Path, *, corpus: Path | None = None
    ) -> EvidenceIntakePaths:
        root = Path(root).resolve()
        reg = root / "schema/registers"
        look = root / "schema/lookups"
        return cls(
            evidence=reg / "EV_evidence_register.csv",
            sources=reg / "SRC_source_register.csv",
            queue=root / "pipeline/acquisition_queue.csv",
            families=reg / "FAM_family_registry.csv",
            variables=reg / "VONT_variable_ontology.csv",
            bands=reg / "BANDS_magnitude_bands.csv",
            contexts=root / "schema/T7_geographic_context.csv",
            direction_sense=look / "variable_direction_sense.csv",
            operational_policy=look / "m2b_variable_policy.csv",
            corpus=corpus if corpus is not None else root / ".cache/corpus",
        )

    def require_inputs(self) -> None:
        for field in fields(self):
            path = getattr(self, field.name)
            if field.name == "corpus":
                if not path.is_dir():
                    raise FileNotFoundError(f"Missing intake corpus directory: {path}")
            elif not path.is_file():
                raise FileNotFoundError(f"Missing intake input {field.name}: {path}")

    def preflight_writes(self) -> None:
        destinations = [self.evidence, self.sources]
        SchemaBuildPaths(self.evidence.parent / "schema").preflight(destinations)
        if self.evidence.resolve() == self.sources.resolve():
            raise ValueError("Intake evidence and source destinations must be distinct")
        readonly = {
            getattr(self, field.name).resolve()
            for field in fields(self)
            if field.name not in {"evidence", "sources", "corpus"}
        }
        for path in destinations:
            if path.resolve() in readonly or path.resolve().is_relative_to(
                self.corpus.resolve()
            ):
                raise ValueError(f"Intake destination overlaps read-only input: {path}")


def _col(path: Path, col: str) -> set[str]:
    with path.open(newline="", encoding="utf-8") as f:
        return {r[col] for r in csv.DictReader(f) if r.get(col)}


def _indexed_csv(path: Path, key: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            value = row.get(key) or ""
            if not value or value in rows:
                raise ValueError(f"{path.name}: blank/duplicate {key}: {value!r}")
            rows[value] = row
    return rows


def _validate_payload_shape(u: dict) -> None:
    """Reject JSON/type tricks before permissive dataclass construction or checks."""
    # json.loads accepts NaN/Infinity by default. Neither is evidence or portable JSON.
    json.dumps(u, allow_nan=False)
    objects = {"relationship", "context"}
    pages = {"page", "justification_page", "selection_justification_page"}
    for key, value in u.items():
        if key in objects:
            if value is not None and not isinstance(value, dict):
                raise ValueError(f"{key} must be an object or null")
        elif key in pages:
            if value is not None and not (key == "page" and value == ""):
                if type(value) is not int or value < 1:
                    raise ValueError(f"{key} requires an integer page >= 1")
        elif key == "reviewer_ok":
            if value is not None and type(value) is not bool:
                raise ValueError("reviewer_ok must be a boolean or null")
        elif value is not None and not isinstance(value, str):
            raise ValueError(f"{key} must be a string or null")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def gate(
    units: list[dict],
    allowed_roles: set[str] | None = None,
    *,
    paths: EvidenceIntakePaths,
) -> list[str]:
    paths.require_inputs()
    if allowed_roles is None:
        allowed_roles = {"nbs_effect", "asset_vulnerability"}
    errs: list[str] = []
    bands = load_bands(paths.bands)
    vont = _col(paths.variables, "canonical_variable_id")
    fams = _col(paths.families, "suitability_family_id")
    aez, fs = check_context._t7(paths.contexts)
    try:
        sources = _indexed_csv(paths.sources, "source_id")
        identities = _indexed_csv(paths.queue, "source_id")
    except ValueError as exc:
        return [f"source identity register invalid: {exc}"]
    with (paths.families).open(newline="", encoding="utf-8") as f:
        family_nbs = {
            (r["suitability_family_id"], r["nbs_id"]) for r in csv.DictReader(f)
        }
    unit_fields = {f.name for f in fields(EvidenceUnit)}
    with (paths.evidence).open(newline="", encoding="utf-8") as f:
        ev_fields = set(csv.DictReader(f).fieldnames or [])
    operational_policy = m2b_policy(paths.operational_policy)
    direction_sense = check_direction.load_sense(paths.direction_sense)
    # reviewed cue exceptions (direction confirmed against the full quote) pass here too,
    # exactly as in the register-wide check
    cue_exceptions = check_direction._exceptions(
        exceptions_path=paths.direction_sense.parent / "direction_cue_exceptions.csv"
    )
    docs: dict[str, fitz.Document | None] = {}
    seen: set[str] = set()
    with ExitStack() as stack:
        for u in units:
            eid = (
                u.get("evidence_id", "<missing>")
                if isinstance(u, dict)
                else "<invalid>"
            )
            try:
                if not isinstance(u, dict):
                    raise ValueError("staged unit must be an object")
                unknown = set(u) - ev_fields
                if unknown:
                    raise ValueError(f"unknown evidence fields: {sorted(unknown)}")
                _validate_payload_shape(u)
                unit = EvidenceUnit(**{k: v for k, v in u.items() if k in unit_fields})
                problems = validate(unit)
                if (
                    len("".join(c for c in _native_part(unit.quote) if c.isalnum()))
                    < 12
                ):
                    problems.append(
                        "native quote must contain at least 12 alphanumeric characters"
                    )
                validate_source_id(unit.source_id)
                if u.get("reviewer_ok") not in (None, False):
                    problems.append("new extraction cannot grant reviewer approval")
                if u.get("review_state"):
                    problems.append(
                        "new extraction cannot set review_state; use review workflow"
                    )
                if unit.taxon and unit.claim_scope == "practice_technology":
                    problems.append(
                        "practice_technology must not carry a taxon; retain species/crop scope"
                    )
                if unit.relationship is not None and not isinstance(
                    unit.relationship, dict
                ):
                    problems.append("relationship must be an object or null")
                # an effect claim IS its relationship: a null or empty one would skip every
                # relationship gate (numbers, bands, direction) and enter synthesis with no
                # claim (caught 2026-11-02: a lane builder that never returned its
                # relationship dict). Direction itself stays conditional: cost and
                # beneficiary rows legitimately carry none (schema/spec.md T6 economics).
                if u.get("use_role") in ("nbs_effect", "asset_vulnerability") and not (
                    isinstance(unit.relationship, dict) and unit.relationship
                ):
                    problems.append("effect unit needs a non-empty relationship")
                if unit.context is not None and not isinstance(unit.context, dict):
                    problems.append("context must be an object or null")
                if problems:
                    raise ValueError("; ".join(problems))
            except (TypeError, ValueError, AttributeError) as exc:
                errs.append(f"{eid}: invalid evidence unit: {exc}")
                continue
            sid = u["source_id"]
            if eid in seen:
                errs.append(f"{eid}: duplicate evidence_id in staging")
            seen.add(eid)
            source = sources.get(sid)
            identity = identities.get(sid)
            if source is None:
                errs.append(f"{eid}: source {sid} is not registered in SRC")
            identity_problem = identity_error(identity)
            if identity_problem:
                errs.append(f"{eid}: {identity_problem}")
            elif source and identity and source_identity_differs(source, identity):
                errs.append(
                    f"{eid}: SRC identity differs from verified acquisition queue; reconcile first"
                )
            if (u["suitability_family_id"], u["nbs_id"]) not in family_nbs:
                errs.append(f"{eid}: family does not belong to nbs_id {u['nbs_id']}")
            if unit.locator_type not in {"page", "section"}:
                errs.append(
                    f"{eid}: locator {unit.locator_type} needs its dedicated adapter; not supported by this gate"
                )
                continue
            if unit.locator_type == "page" and sid not in docs:
                pdf = paths.corpus / f"{sid}.pdf"
                try:
                    if pdf.exists() and source:
                        problem = pdf_title_error(pdf, source.get("citation") or "")
                        if problem:
                            errs.append(
                                f"{eid}: source document identity hold: {problem}"
                            )
                    docs[sid] = (
                        stack.enter_context(fitz.open(pdf)) if pdf.exists() else None
                    )
                except Exception as exc:
                    errs.append(f"{eid}: unreadable cached PDF ({exc})")
                    docs[sid] = None
            d = docs.get(sid)
            if (u.get("locator_type") or "page") == "section":
                # section locator → the rendered snapshot (.md/.txt/.html) is the artefact,
                # exactly as validate_sources resolves it (WOCAT adapter, 2026-10-06)
                snap = next(
                    (
                        paths.corpus / f"{sid}{ext}"
                        for ext in (".md", ".txt", ".html")
                        if (paths.corpus / f"{sid}{ext}").exists()
                    ),
                    None,
                )
                if snap is None:
                    errs.append(
                        f"{eid}: no cached snapshot for section locator ({sid})"
                    )
                else:
                    text = " ".join(
                        snap.read_text(encoding="utf-8", errors="replace").split()
                    )
                    if " ".join(_native_part(u["quote"]).split()) not in text:
                        errs.append(
                            f"{eid}: quote not verbatim in snapshot {snap.name}"
                        )
                    if not (u.get("locator") or "").strip():
                        errs.append(f"{eid}: section locator missing")
            elif d is None:
                errs.append(f"{eid}: no cached PDF for {sid}")
            else:
                try:
                    if source and source.get("artifact_sha1"):
                        digest = hashlib.sha1(
                            (paths.corpus / f"{sid}.pdf").read_bytes()
                        ).hexdigest()
                        expected = source["artifact_sha1"]
                        if (
                            len(expected) not in (16, 40)
                            or digest[: len(expected)] != expected
                        ):
                            errs.append(
                                f"{eid}: cached PDF hash differs from SRC; reverify source identity"
                            )
                    text = " ".join(d[u["page"] - 1].get_text().split())
                    # a non-English quote is stored "<native> (English: <translation>)" per
                    # the AGENTS.md lock; only the native part is in the PDF, so verify that
                    # - the central guardrail (validate_sources) already does exactly this
                    if " ".join(_native_part(u["quote"]).split()) not in text:
                        errs.append(f"{eid}: quote not verbatim on page {u['page']}")
                except Exception as e:  # noqa: BLE001
                    errs.append(f"{eid}: page {u.get('page')} unreadable ({e})")
            for quote_key, page_key in (
                ("justification_quote", "justification_page"),
                ("selection_justification", "selection_justification_page"),
            ):
                supplementary = u.get(quote_key)
                supplementary_page = u.get(page_key)
                if not supplementary and supplementary_page is None:
                    continue
                if not supplementary or supplementary_page is None:
                    errs.append(
                        f"{eid}: {quote_key} and {page_key} must be supplied together"
                    )
                    continue
                native = " ".join(_native_part(supplementary).split())
                if len("".join(c for c in native if c.isalnum())) < 12:
                    errs.append(f"{eid}: {quote_key} lacks a substantive native quote")
                    continue
                if d is None:
                    errs.append(
                        f"{eid}: {quote_key} needs cached PDF for its page locator"
                    )
                    continue
                try:
                    supplementary_text = " ".join(
                        d[supplementary_page - 1].get_text().split()
                    )
                    if native not in supplementary_text:
                        errs.append(
                            f"{eid}: {quote_key} not verbatim on page {supplementary_page}"
                        )
                except (IndexError, ValueError) as exc:
                    errs.append(f"{eid}: {page_key} unreadable ({exc})")
            rel = u.get("relationship") or {}
            for mismatch in observed_range_mismatches(rel):
                detail = mismatch.get("problem") or (
                    "is incompatible with selected observed-class intervals; "
                    "outer class endpoint "
                    f"{mismatch['class_envelope']}"
                )
                errs.append(
                    f"{eid}: {mismatch['field']}={mismatch['stored']} {detail} "
                    "— preserve source classes and correct the summary before intake; "
                    "these are observations, not suitability limits"
                )
            # the WHOLE relationship, exactly the surface `check_numbers.check` walks — not
            # only the numeric fields. The 2026-10-13 retrospective found the gate passing
            # lanes that the next build then flagged at 23%: every miss was a study descriptor
            # (buffer width, exceedance probability, project geometry) written into
            # `outcome_raw`, where a mis-stitched value would hide just as well. Descriptors
            # belong in `context.note`, which is not a claim surface (catalogue #22).
            rn = _rel_nums(json.dumps(rel, ensure_ascii=False))
            # compare as FLOATS, like check_numbers.check: otherwise an integral float
            # magnitude (41.0) never matches a quote that prints "41"
            q = _nums(_native_part(u["quote"]))
            missing = sorted(
                n for n in rn if n not in q and not (_floats({n}) & _floats(q))
            )
            if missing:
                errs.append(
                    f"{eid}: numbers not in quote {missing} — if these are study descriptors, "
                    "move them to context.note; relationship carries claims only"
                )
            row = {
                "evidence_id": eid,
                "use_role": u["use_role"],
                "variable": u["variable"],
                # the QUOTE has to travel with the row: check_context verifies a `severity_cue`
                # verbatim against quote / note / outcome_raw, and without it a cue that lives
                # only in the quote (the normal case) failed here while passing the central
                # guardrail — so lanes were pushing cues into `note` to satisfy a false flag
                "quote": u.get("quote") or "",
                "ruleset_version": u.get("ruleset_version") or "",
                "context": u.get("context") or {},
                "relationship": rel,
            }
            errs += [
                f"{eid}: context {f['signal']} {f['detail']}"
                for f in check_context.check_unit(row, aez, fs)
            ]
            errs += [
                f"{eid}: bands {f['signal']} {f['detail']}"
                for f in check_bands.check_unit(row, bands)
            ]
            errs += [
                f"{eid}: direction {f['signal']} {f['detail']}"
                for f in check_direction.check_unit(
                    {
                        **row,
                        "variable": u.get("variable", ""),
                        "use_role": u.get("use_role", ""),
                        "source_id": sid,
                        "relationship": json.dumps(rel),
                    },
                    senses=direction_sense,
                )
                if not (f["signal"] == "cue_word_conflict" and eid in cue_exceptions)
            ]
            if u["variable"] not in vont:
                errs.append(f"{eid}: variable '{u['variable']}' has no VONT id")
            if u.get("suitability_family_id") not in fams:
                errs.append(
                    f"{eid}: family '{u.get('suitability_family_id')}' not in FAM"
                )
            if u.get("use_role") not in allowed_roles:
                errs.append(
                    f"{eid}: use_role '{u.get('use_role')}' is not allowed here "
                    f"(allowed: {sorted(allowed_roles)})"
                )
            pol = operational_policy.get(u.get("variable") or "")
            if u.get("use_role") == "operational_risk" and pol:
                if pol["decision"] == "exclude":
                    errs.append(
                        f"{eid}: '{u['variable']}' may not be an operational_risk unit "
                        f"(catalogue #50): {pol['reason']}"
                    )
            if u.get("ruleset_version") not in _RULESETS:
                errs.append(
                    f"{eid}: ruleset_version '{u.get('ruleset_version')}' not in {sorted(_RULESETS)}"
                )
    return errs


@dataclass(frozen=True)
class IntakeResult:
    appended: int
    variables_changed: dict[str, str]
    stamped: list[str]


class IntakeGateError(ValueError):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("; ".join(problems))


def ingest(
    units: list[dict],
    *,
    paths: EvidenceIntakePaths,
    allowed_roles: set[str] | None = None,
    run_id: str = "",
    extractor: str = "claude (gated pipeline)",
    day: str | None = None,
    dry_run: bool = False,
) -> IntakeResult:
    """Gate a batch and prepare EV plus SRC together before installing either.

    Stable inputs and one writer are required. Caught installation failures roll
    back; incomplete rollback retains recovery copies. This is not crash-safe or
    atomically visible to readers. Ledger stamps and generated artifacts remain
    separate orchestrator operations. A dry run performs no writes.
    """
    if not dry_run and not run_id.strip():
        raise ValueError(
            "run_id is required to write (it marks the touched sources swept)"
        )
    paths.require_inputs()
    paths.preflight_writes()
    results: list[IntakeResult] = []

    def prepare(selected: EvidenceIntakePaths) -> IntakeResult:
        problems = gate(units, allowed_roles, paths=selected)
        if problems:
            raise IntakeGateError(problems)
        n = append_to_register(units, selected.evidence, dry_run=dry_run)
        if dry_run:
            return IntakeResult(n, {}, [])
        touched = {u["source_id"] for u in units}
        changed = resync_vars_extracted(touched, selected.sources, selected.evidence)
        stamped = stamp_extracted(
            touched,
            run_id,
            extractor,
            day if day is not None else date.today().isoformat(),
            selected.sources,
        )
        return IntakeResult(n, changed, stamped)

    if dry_run:
        return prepare(paths)
    root = Path(os.path.commonpath([paths.evidence.parent, paths.sources.parent]))

    def render(staged: SchemaBuildPaths) -> list[Path]:
        assert staged.output_root is not None
        selected = replace(
            paths,
            evidence=staged.output_root / paths.evidence.relative_to(root),
            sources=staged.output_root / paths.sources.relative_to(root),
        )
        results.append(prepare(selected))
        return []

    staged_publish(
        SchemaBuildPaths(root / "schema"), [paths.evidence, paths.sources], render
    )
    return results[0]
