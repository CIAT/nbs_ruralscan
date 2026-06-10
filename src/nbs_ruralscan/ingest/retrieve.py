"""Vectorless retrieval over a `DocIndex`.

Keyword + structure navigation (no embeddings): scan page-tagged body text, table
contents, captions and section headings for the target terms; return page-stamped
passages ranked so that threshold-bearing hits (a number + unit near the term) and
structured sources (tables, captions) surface first. Deterministic and auditable —
"retrieved Table 3, p.7" — which is the point (method §5.1).
"""

from __future__ import annotations

import re

from .models import DocIndex, Passage

# a number with a unit/operator nearby — marks a likely threshold
_NUMERIC = re.compile(
    r"\d+(?:\.\d+)?\s*(?:(?:°|%|<|>|–|-)|(?:deg|degree|percent|mm|m\b|km|ppm|to)\b)",
    re.I,
)


def _terms_re(terms: list[str]) -> re.Pattern[str]:
    alt = "|".join(re.escape(t) for t in terms if t)
    return re.compile(rf"\b(?:{alt})\b", re.I)


def _filter_table_text(
    rows: list[list[str]], rx: re.Pattern[str], max_rows: int = 12
) -> str:
    """Filter columns in a table to retain only relevant information, then format.

    Always keeps column 0 (usually categories/labels).
    Keeps any column where the header matches terms or cells contain numeric patterns.
    Caps rows at max_rows to avoid token blowup on massive tables.
    """
    if not rows:
        return ""

    num_cols = max(len(r) for r in rows)
    if num_cols <= 1:
        # Single-column table, nothing to filter
        formatted_rows = [" | ".join(r) for r in rows]
    else:
        # Standardize row lengths to prevent IndexError
        std_rows = []
        for r in rows:
            if len(r) < num_cols:
                std_rows.append(r + [""] * (num_cols - len(r)))
            else:
                std_rows.append(r[:num_cols])

        header = std_rows[0]
        keep_indices = {0}  # always keep first column

        # Analyze other columns
        for col_idx in range(1, num_cols):
            # 1) Does header match the terms pattern?
            header_text = header[col_idx]
            if rx.search(header_text):
                keep_indices.add(col_idx)
                continue

            # 2) Do cells in this column contain numeric info?
            has_numeric = False
            for r in std_rows[1:]:
                cell = r[col_idx]
                if _NUMERIC.search(cell):
                    has_numeric = True
                    break
            if has_numeric:
                keep_indices.add(col_idx)

        # If we filtered out all columns except column 0, keep all columns (no filtering)
        if len(keep_indices) <= 1:
            keep_indices = set(range(num_cols))

        sorted_indices = sorted(list(keep_indices))

        # Format the filtered table rows
        formatted_rows = []
        for r in std_rows:
            formatted_rows.append(" | ".join(r[idx] for idx in sorted_indices))

    # Truncate rows if too long
    if len(formatted_rows) > max_rows:
        return "\n".join(formatted_rows[:max_rows]) + "\n... [table truncated]"
    return "\n".join(formatted_rows)


def retrieve(
    index: DocIndex,
    terms: list[str],
    *,
    window: int = 240,
    max_passages: int = 12,
) -> list[Passage]:
    """Return ranked, page-stamped passages relevant to ``terms``."""
    rx = _terms_re(terms)
    out: list[Passage] = []
    seen: set[tuple[int, str]] = set()

    # 1) structured sources first — tables and captions matching a term
    for t in index.tables:
        flat = " | ".join(" ".join(r) for r in t.rows)
        if rx.search(flat):
            score = 4.0 + (2.0 if _NUMERIC.search(flat) else 0.0)
            preview = _filter_table_text(t.rows, rx)
            key = (t.page, preview[:60])
            if key not in seen:
                seen.add(key)
                out.append(
                    Passage(
                        page=t.page,
                        text=preview,
                        kind="table",
                        label=t.label or "table",
                        score=score,
                    )
                )
    for c in index.captions:
        if rx.search(c.text) or rx.search(c.label):
            out.append(
                Passage(
                    page=c.page, text=c.text, kind="caption", label=c.label, score=3.0
                )
            )
    for s in index.sections:
        if rx.search(s.title):
            out.append(
                Passage(
                    page=s.page,
                    text=s.title,
                    kind="section",
                    label="heading",
                    score=2.0,
                )
            )

    # 2) body windows around each term hit
    for pno, text in enumerate(index.pages, start=1):
        flat = re.sub(r"\s+", " ", text)
        matches = list(rx.finditer(flat))
        if not matches:
            continue

        # Calculate raw window spans for each match
        intervals = []
        for m in matches:
            a = max(0, m.start() - window // 2)
            b = min(len(flat), m.end() + window // 2)
            intervals.append((a, b))

        # Sort and merge overlapping or adjacent intervals
        intervals.sort(key=lambda x: x[0])
        merged = []
        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        # Extract passages from merged intervals
        for start, end in merged:
            snippet = flat[start:end].strip()
            key = (pno, snippet[:60])
            if key in seen:
                continue
            seen.add(key)
            score = 1.0 + (2.0 if _NUMERIC.search(snippet) else 0.0)
            # bonus when multiple distinct terms co-occur
            score += 0.5 * (len({h.lower() for h in rx.findall(snippet)}) - 1)
            out.append(Passage(page=pno, text=snippet, kind="body", score=score))

    out.sort(key=lambda p: p.score, reverse=True)
    return out[:max_passages]
