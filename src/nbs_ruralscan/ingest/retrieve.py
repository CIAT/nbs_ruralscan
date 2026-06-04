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
    r"\d+(?:\.\d+)?\s*(?:°|deg|degree|%|percent|mm|m\b|km|ppm|<|>|–|-|to)\b", re.I
)


def _terms_re(terms: list[str]) -> re.Pattern[str]:
    alt = "|".join(re.escape(t) for t in terms if t)
    return re.compile(rf"\b(?:{alt})\b", re.I)


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
            preview = flat[:400]
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
        for m in rx.finditer(flat):
            a = max(0, m.start() - window // 2)
            b = min(len(flat), m.end() + window // 2)
            snippet = flat[a:b].strip()
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
