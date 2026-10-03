"""Bounded independent Stage 3 checks; optional actual rebuild, no source edits."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from analysis import stage3_analysis as analysis


def rows(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def hashes(paths):
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}


def check_bad_input(label, table_name, mutate, expected_failure):
    original_reader = analysis._read_csv
    target = (ROOT / analysis.INPUT_NAMES[table_name]).resolve()

    def altered_reader(path, required):
        actual = original_reader(path, required)
        if path.resolve() == target:
            actual = copy.deepcopy(actual)
            mutate(actual)
        return actual

    with patch.object(analysis, "_read_csv", side_effect=altered_reader):
        try:
            analysis.validate_inputs(ROOT)
        except analysis.InputValidationError as error:
            failed = [name for name, item in error.report["checks"].items()
                      if item["status"] == "failed"]
            assert expected_failure in failed, (label, failed)
            return {"case": label, "status": "rejected_as_expected", "failed_checks": failed}
    raise AssertionError(f"Bad input was silently accepted: {label}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true",
                        help="Actually rerun direct Notebook cells and compare output hashes.")
    args = parser.parse_args()
    analysis.validate_inputs(ROOT)
    primary = {(r["period_end"], r["metric_id"]): r
               for r in rows("data/public/company_quarterly_metrics.csv")}
    cross = rows("data/public/source_cross_checks.csv")
    assert len(cross) == 32
    for record in cross:
        main_row = primary[(record["period_end"], record["metric_id"])]
        difference = abs(float(record["primary_value"]) - float(record["comparison_value"]))
        tolerance = (float(record["primary_precision_million"]) +
                     float(record["comparison_precision_million"])) / 2
        assert math.isclose(float(main_row["value"]), float(record["primary_value"]), abs_tol=1e-12)
        assert main_row["source_id"] == record["primary_source_id"]
        assert math.isclose(float(main_row["precision_million"]),
                            float(record["primary_precision_million"]), abs_tol=1e-12)
        assert math.isclose(difference, float(record["absolute_difference_million"]), abs_tol=1e-12)
        assert math.isclose(tolerance, float(record["tolerance_million"]), abs_tol=1e-12)
        assert difference <= tolerance + 1e-9
        assert record["consistent_with_rounding"] == "True"
    q4 = primary[("2025-12-31", "M009")]
    legs = json.loads(q4["input_lineage"])
    assert math.isclose(float(q4["value"]), (873442 - 631156) / 1000, abs_tol=1e-12)
    assert math.isclose(float(q4["precision_million"]),
                        sum(float(leg["precision_million"]) for leg in legs), abs_tol=1e-12)
    assert math.isclose(float(q4["precision_million"]), 0.002, abs_tol=1e-12)
    # Independent formula implementation, without the module's growth/decomposition helpers.
    latest = {metric: float(primary[("2026-06-30", metric)]["value"])
              for metric in analysis.ALL_METRICS}
    baseline = {metric: float(primary[("2025-06-30", metric)]["value"])
                for metric in analysis.ALL_METRICS}
    diagnostics = {r["metric_id"]: r for r in rows("data/public/business_diagnostics.csv")
                   if r["period_end"] == "2026-06-30"}
    for metric in analysis.ALL_METRICS:
        expected = (latest[metric] / baseline[metric] - 1) * 100
        assert math.isclose(expected, float(diagnostics[metric]["yoy_pct"]), abs_tol=1e-12)
    decomposition = next(r for r in rows("data/public/engagement_decomposition.csv")
                         if r["period_end"] == "2026-06-30" and r["comparison"] == "yoy")
    independent = {
        "dau_log_growth_points": 100 * math.log(latest["M001"] / baseline["M001"]),
        "mau_log_component_points": 100 * math.log(latest["M002"] / baseline["M002"]),
        "ratio_log_component_points": 100 * math.log(
            (latest["M001"] / latest["M002"]) / (baseline["M001"] / baseline["M002"])),
    }
    for key, expected in independent.items():
        assert math.isclose(expected, float(decomposition[key]), abs_tol=1e-12)

    def wrong_precision(table):
        next(r for r in table if r["period_end"] == "2024-09-30" and
             r["metric_id"] == "M007")["precision_million"] = "1"

    def wrong_ratio(table):
        next(r for r in table if r["metric_id"] == "M008")["value"] = "0.9"

    negative = [
        check_bad_input("duplicate quarter/metric", "quarterly", lambda t: t.append(copy.deepcopy(t[0])),
                        "quarterly_primary_key"),
        check_bad_input("thousand/million rounding step error", "quarterly", wrong_precision,
                        "source_precision_unit_conversion"),
        check_bad_input("wrong DAU/MAU identity", "quarterly", wrong_ratio, "dau_mau_ratio_identity"),
        check_bad_input("missing comparison baseline", "baselines", lambda t: t.pop(0),
                        "baselines_coverage"),
    ]
    artifacts = ["data/public/" + name + ".csv" for name in
                 ("business_diagnostics", "engagement_decomposition", "commercial_structure")]
    artifacts += ["analysis/figures/" + name for name in analysis.FIGURE_NAMES]
    before = hashes(artifacts)
    rebuild = "not_requested"
    if args.rebuild:
        result = subprocess.run([sys.executable, "-B", "scripts/run_stage3.py", "--execute-direct"],
                                cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert before == hashes(artifacts), "Identical inputs did not regenerate identical CSVs/PNGs"
        rebuild = "8_output_hashes_identical_after_real_fresh_process_rebuild"
    import nbformat
    notebook = nbformat.read(ROOT / "analysis/business_review.ipynb", as_version=4)
    nbformat.validate(notebook)
    code_cells = [c for c in notebook.cells if c.cell_type == "code"]
    assert [c.execution_count for c in code_cells] == list(range(1, len(code_cells) + 1))
    outputs = [output for cell in code_cells for output in cell.outputs]
    assert not any(output.output_type == "error" for output in outputs)
    png_count = sum("image/png" in output.get("data", {}) for output in outputs)
    html_count = sum("text/html" in output.get("data", {}) for output in outputs)
    assert png_count == 5 and html_count == 6
    assert notebook.metadata.execution_status == "passed"
    assert notebook.metadata.execution_method == "fresh_python_process_direct_cells"
    summary = {
        "status": "passed", "cross_source_rounding_pairs": len(cross),
        "independent_latest_yoy_metrics": 8, "independent_log_components": independent,
        "q4_value_and_two_leg_precision": "passed", "negative_cases": negative,
        "artifact_rebuild": rebuild, "artifact_sha256": before,
        "notebook": {"code_cells": len(code_cells), "errors": 0, "png_outputs": png_count,
                     "html_outputs": html_count, "method": notebook.metadata.execution_method,
                     "jupyter_kernel_verified": False},
        "boundary": "This verifies local tables and calculations, not all original source values.",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
