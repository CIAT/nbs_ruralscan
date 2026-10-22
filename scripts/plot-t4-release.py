#!/usr/bin/env python3
"""Draw retained source bands without interpolation or inferred tail limits.

Run: uv run --no-project --with matplotlib python scripts/plot-t4-release.py
"""

import csv
import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "t4-source-bands"
import matplotlib.pyplot as plt  # noqa: E402 — select noninteractive backend first

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff/agroforestry-t4/v0.1.3/plots"


def plot(row, out):
    profiles = json.loads(row["relationship_params"]).get("profiles", [])
    if not profiles:
        return
    fig, axes = plt.subplots(
        len(profiles),
        1,
        figsize=(8, 2.5 * len(profiles)),
        squeeze=False,
        layout="constrained",
    )
    for ax, profile in zip(axes[:, 0], profiles):
        bands = profile["intervals"]
        edges = [
            b[k]
            for source in profiles
            if source["unit"] == profile["unit"]
            for b in source["intervals"]
            for k in ("lower", "upper")
            if b[k] is not None
        ]
        if not edges:
            ax.text(0.1, 0.5, "No finite boundaries reported", transform=ax.transAxes)
            continue
        low, high = min(edges), max(edges)
        pad = max(high - low, abs(high) * 0.1, 0.1) * 0.15
        left, right = low - pad, high + pad
        ax.set_facecolor("#f0f0f0")
        for b in bands:
            if b["score"] is None:
                continue
            x1 = left if b["lower"] is None else b["lower"]
            x2 = right if b["upper"] is None else b["upper"]
            ax.plot([x1, x2], [b["score"]] * 2, color="#157359", linewidth=3)
            for key, x in (("lower", x1), ("upper", x2)):
                if b[key] is not None:
                    ax.plot(
                        x,
                        b["score"],
                        "o",
                        color="#157359",
                        markerfacecolor="#157359" if b[key + "_inclusive"] else "white",
                        markersize=6,
                    )
                else:
                    ax.plot(
                        x, b["score"], "<" if key == "lower" else ">", color="#157359"
                    )
        ax.set(
            xlim=(left, right),
            ylim=(-0.05, 1.05),
            xlabel=profile["unit"],
            ylabel="Suitability score",
            title=profile["source_id"].replace("_", " "),
        )
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle(
        row["variable"].replace("_", " ").capitalize()
        + " — source responses, not pooled",
        fontsize=13,
    )
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / (row["mapping_id"] + ".svg"), metadata={"Date": None})
    fig.savefig(out / (row["mapping_id"] + ".png"), dpi=130)
    plt.close(fig)
    return fig


if __name__ == "__main__":
    with (ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            plot(row, OUT)
