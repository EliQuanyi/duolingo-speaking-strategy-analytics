"""Stage 3 base-period bridge and excluded-participant assumption sensitivity.

Reuses public inputs. No fitted causal effect, imputed individual records, or ROI.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from analysis.stage3_analysis import validate_inputs

STUDY_PATH = ROOT / "data/public/stage3_learning_study_inputs.csv"
BRIDGE_PATH = ROOT / "data/public/stage3_base_period_bridge.csv"
SENSITIVITY_PATH = ROOT / "data/public/stage3_learning_selection_sensitivity.csv"
VALIDATION_PATH = ROOT / "analysis/stage3_closeout_validation.json"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def study_inputs(sources):
    records = read_csv(STUDY_PATH)
    assert len(records) == 2 and {row["arm"] for row in records} == {"video_call", "control"}
    arms = {}
    for row in records:
        assert row["study_id"] == "DRR-25-06"
        assert row["unit"] == "Versant speaking points"
        assert date.fromisoformat(row["accessed_on"]) <= date(2026, 10, 2)
        for prefix in ("count", "mean"):
            sid = row[f"{prefix}_source_id"]
            assert sid in sources and sources[sid]["url"] == row[f"{prefix}_source_url"]
            assert row[f"{prefix}_locator"]
        assigned, analyzed = int(row["assigned_n"]), int(row["analyzed_n"])
        assert 0 < analyzed < assigned
        pre, post = Decimal(row["pre_mean"]), Decimal(row["post_mean"])
        assert pre.is_finite() and post.is_finite() and min(pre, post) >= 0
        arms[row["arm"]] = {"assigned": assigned, "analyzed": analyzed,
                            "excluded": assigned - analyzed, "pre": pre, "post": post}
    return arms


def base_period_bridge(lookup):
    rows = []
    for metric, label in (("M001", "DAU"), ("M002", "MAU"), ("M008", "DAU/MAU proxy")):
        periods = ((2026, 1), (2026, 2), (2025, 1), (2025, 2))
        values = [lookup[(*period, metric)]["value"] for period in periods]
        current_q1, current_q2, prior_q1, prior_q2 = values
        current_log = 100 * math.log(current_q2 / current_q1)
        prior_log = 100 * math.log(prior_q2 / prior_q1)
        yoy_difference = 100 * (math.log(current_q2 / prior_q2) - math.log(current_q1 / prior_q1))
        assert math.isclose(yoy_difference, current_log - prior_log, abs_tol=1e-10)
        source_metrics = ("M001", "M002") if metric == "M008" else (metric,)
        source_ids = sorted({sid for period in periods for m in source_metrics
                             for sid in lookup[(*period, m)]["source_id"].split("|")})
        source_urls = sorted({url for period in periods for m in source_metrics
                              for url in lookup[(*period, m)]["source_url"].split("|")})
        rows.append({
            "metric_id": metric, "quantity": label,
            "current_window": "2026Q1 to 2026Q2", "prior_window": "2025Q1 to 2025Q2",
            "current_q1_value": current_q1, "current_q2_value": current_q2,
            "prior_q1_value": prior_q1, "prior_q2_value": prior_q2,
            "input_unit": "ratio" if metric == "M008" else "million users",
            "current_qoq_pct": 100 * (current_q2 / current_q1 - 1),
            "prior_qoq_pct": 100 * (prior_q2 / prior_q1 - 1),
            "current_qoq_log_points": current_log,
            "prior_qoq_log_points": prior_log,
            "base_period_contribution_log_points": -prior_log,
            "yoy_log_change": yoy_difference,
            "identity_residual_log_points": yoy_difference - (current_log - prior_log),
            "decomposition_unit": "100 natural-log growth points",
            "source_ids": "|".join(source_ids), "source_urls": "|".join(source_urls),
            "evidence_label": "derived_observed_official",
            "boundary": "Arithmetic period bridge; not seasonally adjusted or a causal contribution",
        })
    old = read_csv(ROOT / "data/public/stage3_robustness_checks.csv")
    assert len(old) == 3
    for row, previous in zip(rows, old):
        assert math.isclose(row["yoy_log_change"], float(previous["point_change"]), abs_tol=1e-10)
    assert math.isclose(rows[0]["yoy_log_change"] - rows[1]["yoy_log_change"],
                        rows[2]["yoy_log_change"], abs_tol=1e-10)
    return rows


def selection_sensitivity(arms):
    treatment, control = arms["video_call"], arms["control"]
    wt = Decimal(treatment["excluded"]) / treatment["assigned"]
    wc = Decimal(control["excluded"]) / control["assigned"]
    observed_difference = treatment["post"] - control["post"]
    tipping_shift = -observed_difference / wt
    # Shifts are illustrative D assumptions, not observed excluded scores or plausible bounds.
    scenarios = (("LS01", Decimal(0), Decimal(0), "Excluded means equal own-arm analyzed means"),
                 ("LS02", Decimal(-3), Decimal(0), "Treatment excluded mean three points lower"),
                 ("LS03", Decimal(-5), Decimal(0), "Treatment excluded mean five points lower"),
                 ("LS04", Decimal(-5), Decimal(-5), "Both excluded means five points lower"),
                 ("LS05", Decimal(-5), Decimal(5), "Treatment lower and control higher"),
                 ("LS06", tipping_shift, Decimal(0), "Equality threshold with zero control shift"))
    rows = []
    for sid, dt, dc, description in scenarios:
        mt, mc = treatment["post"] + dt, control["post"] + dc
        assert min(mt, mc) >= 0
        reconstructed_t = (treatment["analyzed"] * treatment["post"] + treatment["excluded"] * mt) / treatment["assigned"]
        reconstructed_c = (control["analyzed"] * control["post"] + control["excluded"] * mc) / control["assigned"]
        difference = reconstructed_t - reconstructed_c
        assert abs(difference - (observed_difference + wt * dt - wc * dc)) < Decimal("1e-20")
        rows.append({
            "scenario_id": sid, "study_id": "DRR-25-06", "scenario": description,
            "treatment_excluded_n": treatment["excluded"], "control_excluded_n": control["excluded"],
            "treatment_shift_assumption": float(dt), "control_shift_assumption": float(dc),
            "treatment_excluded_mean_assumption": float(mt), "control_excluded_mean_assumption": float(mc),
            "hypothetical_assigned_post_mean_t": float(reconstructed_t),
            "hypothetical_assigned_post_mean_c": float(reconstructed_c),
            "hypothetical_post_mean_difference": float(difference),
            "direction": "equal" if abs(difference) < Decimal("1e-20") else "positive" if difference > 0 else "negative",
            "unit": "Versant speaking points", "evidence_label": "D_assumption_sensitivity",
            "input_sources": "S011|S015", "computed_on": "2026-10-02",
            "boundary": "No actual ITT, gain difference, adjusted coefficient, CI, p-value or commercial uplift estimated",
        })
    return rows


def csv_bytes(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Recompute and compare files without writing")
    args = parser.parse_args()
    inputs = validate_inputs(ROOT)
    arms = study_inputs(inputs["sources"])
    bridge = base_period_bridge(inputs["lookup"])
    sensitivity = selection_sensitivity(arms)
    outputs = {BRIDGE_PATH: csv_bytes(bridge), SENSITIVITY_PATH: csv_bytes(sensitivity)}
    expected_checks = {
        "company_input_qa": "passed",
        "study_arm_counts_units_source_links": "passed",
        "base_bridge_matches_three_existing_headline_changes": "passed",
        "dau_mau_frequency_bridge_reconciles": "passed",
        "weighted_excluded_mean_identity_six_scenarios": "passed",
        "no_shift_recovers_observed_post_mean_difference": "passed",
        "equality_threshold_has_zero_difference": "passed",
        "same_shift_and_different_arm_counts_handled": "passed",
    }
    assert math.isclose(sensitivity[0]["hypothetical_post_mean_difference"], 0.94, abs_tol=1e-12)
    assert sensitivity[2]["direction"] == "negative"
    assert sensitivity[3]["direction"] == "positive"
    assert sensitivity[5]["direction"] == "equal"
    for path, payload in outputs.items():
        if args.check_only:
            assert path.read_bytes() == payload, f"Stale or altered derived output: {path.name}"
        else:
            path.write_bytes(payload)
    hashed_paths = [ROOT / "data/public/company_quarterly_metrics.csv", STUDY_PATH, *outputs]
    report = {
        "version": "Stage 3 v1.2", "reviewed_on": "2026-10-02", "status": "passed",
        "checks": expected_checks, "rows": {path.name: len(rows) for path, rows in
                                              ((BRIDGE_PATH, bridge), (SENSITIVITY_PATH, sensitivity))},
        "sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in hashed_paths},
        "inference_boundary": "Base bridge is descriptive; selection sensitivity is hypothetical, not recovered ITT or ROI",
    }
    report_payload = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if args.check_only:
        assert VALIDATION_PATH.read_bytes() == report_payload, "Validation record is stale"
    else:
        VALIDATION_PATH.write_bytes(report_payload)
    print(json.dumps({**report, "mode": "check_only" if args.check_only else "generated",
                      "base_bridge": [{"metric": r["quantity"], "current": r["current_qoq_log_points"],
                                       "base": r["base_period_contribution_log_points"], "net": r["yoy_log_change"]}
                                      for r in bridge],
                      "tipping_excluded_treatment_mean": sensitivity[-1]["treatment_excluded_mean_assumption"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
