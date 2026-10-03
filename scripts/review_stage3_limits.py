"""Check headline direction under disclosure rounding; no forecast or causal fit."""
from __future__ import annotations

import csv
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from analysis.stage3_analysis import validate_inputs


def log_growth_bounds(current, baseline):
    ch = current["precision_million"] / 2
    bh = baseline["precision_million"] / 2
    assert min(current["value"] - ch, baseline["value"] - bh) > 0
    center = 100 * math.log(current["value"] / baseline["value"])
    low = 100 * math.log((current["value"] - ch) / (baseline["value"] + bh))
    high = 100 * math.log((current["value"] + ch) / (baseline["value"] - bh))
    assert low <= center <= high
    return center, low, high


def frequency_bounds(lookup, quarter):
    dc, dl, dh = log_growth_bounds(lookup[(2026, quarter, "M001")],
                                  lookup[(2025, quarter, "M001")])
    mc, ml, mh = log_growth_bounds(lookup[(2026, quarter, "M002")],
                                  lookup[(2025, quarter, "M002")])
    return dc - mc, dl - mh, dh - ml


def main():
    inputs = validate_inputs(ROOT)
    lookup = inputs["lookup"]
    records = []
    for name, metric in (("DAU YoY log growth", "M001"), ("MAU YoY log term", "M002"),
                         ("Frequency-proxy YoY log term", "M008")):
        if metric == "M008":
            first, last = frequency_bounds(lookup, 1), frequency_bounds(lookup, 2)
        else:
            first = log_growth_bounds(lookup[(2026, 1, metric)], lookup[(2025, 1, metric)])
            last = log_growth_bounds(lookup[(2026, 2, metric)], lookup[(2025, 2, metric)])
        change, low, high = last[0] - first[0], last[1] - first[2], last[2] - first[1]
        expected = "increase" if change > 0 else "decrease" if change < 0 else "unchanged"
        robust = (low > 0 if change > 0 else high < 0 if change < 0 else False)
        records.append({
            "check_id": f"RB{len(records)+1:02d}", "quantity": name,
            "comparison": "2026Q2 YoY term minus 2026Q1 YoY term",
            "point_change": change, "rounding_low_change": low, "rounding_high_change": high,
            "unit": "100 natural-log growth points", "point_direction": expected,
            "direction_survives_disclosure_rounding": robust,
            "source_ids": "|".join(sorted({sid for year, quarter in ((2025,1),(2025,2),(2026,1),(2026,2))
                                           for m in (("M001","M002") if metric=="M008" else (metric,))
                                           for sid in lookup[(year,quarter,m)]["source_id"].split("|")})),
            "bound_type": "conservative disclosed rounding bounds; not a statistical CI",
            "interpretation": "Arithmetic direction only; excludes measurement error, mix, seasonality and causal attribution",
        })
    # Evaluate all 256 corners of the eight disclosed DAU/MAU rounding ranges.
    # This verifies the analytic bounds, not a distribution over plausible effects.
    keys = [(year, quarter, metric) for year, quarter in ((2025,1),(2025,2),(2026,1),(2026,2))
            for metric in ("M001", "M002")]
    corners = [[] for _ in records]
    for signs in itertools.product((-1, 1), repeat=len(keys)):
        values = {key: lookup[key]["value"] + sign * lookup[key]["precision_million"] / 2
                  for key, sign in zip(keys, signs)}
        da = 100 * (math.log(values[(2026,2,"M001")] / values[(2025,2,"M001")]) -
                    math.log(values[(2026,1,"M001")] / values[(2025,1,"M001")]))
        ma = 100 * (math.log(values[(2026,2,"M002")] / values[(2025,2,"M002")]) -
                    math.log(values[(2026,1,"M002")] / values[(2025,1,"M002")]))
        for collection, value in zip(corners, (da, ma, da-ma)):
            collection.append(value)
    for record, values in zip(records, corners):
        assert record["rounding_low_change"] <= record["point_change"] <= record["rounding_high_change"]
        assert math.isclose(min(values), record["rounding_low_change"], abs_tol=1e-10)
        assert math.isclose(max(values), record["rounding_high_change"], abs_tol=1e-10)
        record["verified_disclosure_corners"] = len(values)
    path = ROOT / "data/public/stage3_robustness_checks.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps({"check": "headline_rounding_direction", "rows": records,
                      "boundary": "This does not estimate treatment effects or forecast future users."},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
