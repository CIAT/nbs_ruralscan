"""Publish a review batch, its images and its index from selected local inputs."""

from collections.abc import Callable, Iterable
import json
import os
from pathlib import Path

from nbs_ruralscan.ingest.integrity import validate_source_id
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import staged_publish
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def batch_directory(
    root: Path, output: Path | None, corpus: Path | None = None
) -> Path:
    result = _absolute(output if output is not None else root / "docs/review")
    compiler = Path(__file__).resolve().parents[3]
    path = result.resolve()
    for p in (
        root / "schema",
        root / "pipeline",
        compiler / "schema",
        compiler / "pipeline",
        compiler / ".cache/corpus",
        root / ".cache/corpus",
        corpus,
    ):
        if p is not None and path.is_relative_to(p.resolve()):
            raise ValueError(f"Review output overlaps protected inputs: {p}")
    return result


def publish_batch(
    directory: Path,
    batch_id: str,
    render: Callable[[Path], dict],
    *,
    inputs: ReviewInputs,
    crop_ids: Iterable[str] = (),
    dry_run: bool = False,
) -> Path:
    """Render to private files and install images, batch, then updated index."""
    validate_source_id(batch_id)
    if batch_id.casefold() in {"index", "decisions"}:
        raise ValueError(f"Reserved review batch ID: {batch_id}")
    directory = _absolute(directory)
    images = []
    for eid in crop_ids:
        validate_source_id(eid)
        images.append(directory / "img" / f"{eid}.png")
    batch, index = directory / f"{batch_id}.json", directory / "index.json"
    outputs = [*images, batch, index]
    inputs.check_outputs(outputs)
    context = SchemaBuildPaths(directory / "schema")

    def stage(paths):
        inputs.verify()
        assert paths.output_root is not None
        target = paths.output_root
        prior = target / batch.name
        if prior.exists():
            existing = json.loads(prior.read_text(encoding="utf-8"))
            if (
                not isinstance(existing, dict)
                or existing.get("batch", {}).get("id") != batch_id
            ):
                raise ValueError(
                    f"Existing output is not this review batch: {batch.name}"
                )
        idx = target / "index.json"
        listing = (
            json.loads(idx.read_text(encoding="utf-8"))
            if idx.exists()
            else {"batches": []}
        )
        if any(
            b["id"] != batch_id and b["id"].casefold() == batch_id.casefold()
            for b in listing["batches"]
        ):
            raise ValueError(
                f"Review batch ID collides with an existing ID: {batch_id}"
            )
        payload = render(target)
        info = payload["batch"]
        if info["id"] != batch_id:
            raise ValueError("Rendered review batch does not match requested batch ID")
        (target / batch.name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        entry = {key: info[key] for key in ("id", "title", "date", "n")}
        entry["file"] = f"review/{batch.name}"
        if info.get("kind"):
            entry["kind"] = info["kind"]
        listing["batches"] = [b for b in listing["batches"] if b["id"] != batch_id] + [
            entry
        ]
        idx.write_text(
            json.dumps(listing, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        return []

    def check_png(path):
        from PIL import Image

        with Image.open(path) as img:
            if img.format != "PNG":
                raise ValueError(f"Invalid review crop: {path.name}")
            img.verify()

    staged_publish(
        context,
        outputs,
        stage,
        optional_destinations=tuple(images),
        artifact_validators={
            **{path: check_png for path in images},
            index: lambda _: inputs.verify(),
        },
        dry_run=dry_run,
    )
    return batch
