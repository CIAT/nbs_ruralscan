"""Render source pages used by the T4 feedback view; original PDFs stay untouched."""

import importlib.util
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "t4_feedback", ROOT / "scripts/report-t4-bounded-review.py"
)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def main():
    data = REPORT.build_data()
    pages = {
        (r["source"], p["page"])
        for g in data["groups"]
        for r in g["records"]
        for p in r["source_pages"]
    }
    destination = ROOT / "docs/review/source-pages"
    destination.mkdir(parents=True, exist_ok=True)
    for source, number in sorted(pages):
        with fitz.open(ROOT / ".cache/corpus" / f"{source}.pdf") as pdf:
            if number < 1 or number > len(pdf):
                raise ValueError(f"{source}: invalid PDF page {number}")
            pdf[number - 1].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(
                destination / f"{source}-p{number}.png"
            )
    print(f"Rendered {len(pages)} original source pages")


if __name__ == "__main__":
    main()
