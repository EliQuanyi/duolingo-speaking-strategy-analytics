"""Company-level Stage 3 diagnostics, with no feature-effect estimation."""
from __future__ import annotations

import calendar
import csv
import hashlib
import html
import json
import math
import platform
import textwrap
from collections import Counter
from datetime import date
from pathlib import Path

NUMERIC_METRICS = ("M001", "M002", "M004", "M005", "M006", "M007", "M009")
ALL_METRICS = NUMERIC_METRICS + ("M008",)
MAIN_QUARTERS = ((2024, 3), (2024, 4), (2025, 1), (2025, 2),
                 (2025, 3), (2025, 4), (2026, 1), (2026, 2))
BASE_QUARTERS = ((2023, 3), (2023, 4), (2024, 1), (2024, 2))
METRIC_COLUMNS = (
    "period_start", "period_end", "fiscal_year", "fiscal_quarter", "metric_id",
    "value", "unit", "aggregation_type", "scope", "source_id", "source_locator",
    "accessed_on", "transformation_note", "original_value", "original_unit",
    "published_on", "source_url", "evidence_label", "precision_million",
    "reported_yoy_pct",
)
TIMELINE_COLUMNS = (
    "event_id", "event_date", "event_date_precision", "reported_on", "feature",
    "tier", "platform", "language_or_market", "rollout_scope_text",
    "claim_type", "source_id",
)
INPUT_NAMES = {
    "quarterly": "data/public/company_quarterly_metrics.csv",
    "baselines": "data/public/company_comparison_baselines.csv",
    "timeline": "data/public/product_timeline.csv",
    "dictionary": "data/metric_dictionary.csv",
    "sources": "data/source_register.csv",
}
PALETTE = {"blue": "#245B84", "gold": "#A16E12", "ink": "#303942"}
FIGURE_NAMES = (
    "01_active_scale_and_frequency.png",
    "02_dau_yoy_log_decomposition.png",
    "03_subscribers_and_subscription_bookings.png",
    "04_bookings_and_revenue_timing.png",
    "05_subscription_commercial_share.png",
)


class InputValidationError(ValueError):
    def __init__(self, report):
        self.report = report
        failed = [name for name, item in report["checks"].items()
                  if item["status"] == "failed"]
        super().__init__("Stage 3 input validation failed: " + ", ".join(failed))


class Checks:
    def __init__(self):
        self.items = {}

    def add(self, name, passed, detail=""):
        item = self.items.setdefault(
            name, {"status": "passed", "evaluations": 0, "failures": []})
        item["evaluations"] += 1
        if not passed:
            item["status"] = "failed"
            item["failures"].append(str(detail))

    @property
    def passed(self):
        return all(item["status"] == "passed" for item in self.items.values())


def _read_csv(path, required):
    if not path.is_file():
        raise FileNotFoundError(
            f"Required Stage 3 input is missing: {path}. "
            "Prepare the sourced CSV before running; no values will be fabricated.")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(required) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values())
               for row in rows):
            raise ValueError(f"{path.name}: row/header column count mismatch")
        return rows


def _source_ids(row):
    return [part.strip() for part in row["source_id"].split("|") if part.strip()]


def _quarter_dates(year, quarter):
    month = 3 * quarter
    return (date(year, month - 2, 1).isoformat(),
            date(year, month, calendar.monthrange(year, month)[1]).isoformat())


def _previous_quarter(year, quarter):
    return (year - 1, 4) if quarter == 1 else (year, quarter - 1)


def _original_factor(unit):
    factors = {
        "million users": 1, "million accounts": 1, "usd million": 1,
        "million": 1, "millions": 1, "ratio": 1,
        "thousand users": 0.001, "thousand accounts": 0.001,
        "usd thousand": 0.001, "usd thousands": 0.001, "thousands": 0.001,
        "users": 0.000001, "accounts": 0.000001, "usd": 0.000001,
    }
    normalized = unit.lower().strip().replace("_", " ")
    if normalized not in factors:
        raise ValueError(f"Unsupported original unit: {unit!r}")
    return factors[normalized]


def _parse_original(value):
    return float(str(value).replace("$", "").replace(",", "").strip())


def _source_precision(value, unit):
    """Infer the displayed last digit and convert its step to millions."""
    text = str(value).replace("$", "").replace(",", "").strip()
    if "e" in text.lower():
        raise ValueError("Original value must preserve displayed decimal precision")
    decimals = len(text.split(".", 1)[1]) if "." in text else 0
    return 10 ** (-decimals) * _original_factor(unit)


def _growth_interval(current, baseline):
    """Propagate disclosed rounding steps, without interpreting them as CIs."""
    current_half = current.get("effective_rounding_step_million", current["precision_million"]) / 2
    base_half = baseline.get("effective_rounding_step_million", baseline["precision_million"]) / 2
    if baseline["value"] - base_half <= 0:
        raise ValueError("Rounded baseline includes a nonpositive value")
    return (
        100 * ((current["value"] - current_half) /
               (baseline["value"] + base_half) - 1),
        100 * ((current["value"] + current_half) /
               (baseline["value"] - base_half) - 1),
    )


def _ratio_row(dau, mau):
    return {
        **dau, "metric_id": "M008", "value": dau["value"] / mau["value"],
        "unit": "ratio", "aggregation_type": "derived_ratio",
        "precision_million": 0.0, "reported_yoy_pct": "",
        "source_id": "|".join(sorted(set(_source_ids(dau) + _source_ids(mau)))),
    }


def validate_inputs(root):
    """Read and validate the sourced tables. Never create or change files."""
    root = Path(root).resolve()
    raw_tables = {
        "quarterly": _read_csv(root / INPUT_NAMES["quarterly"], METRIC_COLUMNS),
        "baselines": _read_csv(root / INPUT_NAMES["baselines"], METRIC_COLUMNS),
        "timeline": _read_csv(root / INPUT_NAMES["timeline"], TIMELINE_COLUMNS),
        "dictionary": _read_csv(root / INPUT_NAMES["dictionary"],
                                ("metric_id", "unit", "aggregation_type")),
        "sources": _read_csv(root / INPUT_NAMES["sources"],
                             ("source_id", "url", "published_on")),
    }
    checks = Checks()
    sources = {row["source_id"]: row for row in raw_tables["sources"]}
    dictionary = {row["metric_id"]: row for row in raw_tables["dictionary"]}
    checks.add("source_register_unique_id", len(sources) == len(raw_tables["sources"]))
    checks.add("metric_dictionary_unique_id", len(dictionary) == len(raw_tables["dictionary"]))
    checks.add("dictionary_metric_coverage", set(ALL_METRICS).issubset(dictionary))
    typed = {}
    for name, expected_quarters, expected_metrics in (
        ("quarterly", MAIN_QUARTERS, ALL_METRICS),
        ("baselines", BASE_QUARTERS, NUMERIC_METRICS),
    ):
        rows = []
        for raw in raw_tables[name]:
            row = dict(raw)
            key = f'{name}:{raw["period_end"]}:{raw["metric_id"]}'
            nonempty = ("period_start", "period_end", "fiscal_year", "fiscal_quarter",
                        "metric_id", "value", "unit", "aggregation_type", "scope",
                        "source_id", "source_locator", "accessed_on", "published_on",
                        "source_url", "evidence_label", "precision_million")
            checks.add("required_values", all(raw[field].strip() for field in nonempty), key)
            try:
                row["value"] = float(raw["value"])
                row["precision_million"] = float(raw["precision_million"])
                row["fiscal_year"] = int(raw["fiscal_year"])
                row["fiscal_quarter"] = int(raw["fiscal_quarter"])
                if raw["reported_yoy_pct"].strip():
                    row["reported_yoy_pct"] = float(raw["reported_yoy_pct"])
                expected_dates = _quarter_dates(row["fiscal_year"], row["fiscal_quarter"])
                published_dates = [date.fromisoformat(item.strip())
                                   for item in raw["published_on"].split("|")]
                published = max(published_dates)
                accessed = date.fromisoformat(raw["accessed_on"])
                checks.add("numeric_and_date_parse", True)
            except (ValueError, OverflowError) as error:
                checks.add("numeric_and_date_parse", False, f"{key}: {error}")
                continue
            checks.add("quarter_boundaries",
                       (row["period_start"], row["period_end"]) == expected_dates, key)
            checks.add("disclosure_access_dates",
                       date.fromisoformat(expected_dates[1]) <= published <= accessed, key)
            checks.add("finite_positive_values",
                       math.isfinite(row["value"]) and row["value"] > 0 and
                       math.isfinite(row["precision_million"]) and
                       row["precision_million"] >= 0, key)
            metric = dictionary.get(row["metric_id"])
            checks.add("metric_fk", metric is not None, key)
            if metric:
                checks.add("unit_and_aggregation",
                           row["unit"] == metric["unit"] and
                           row["aggregation_type"] == metric["aggregation_type"], key)
            ids = _source_ids(row)
            checks.add("source_fk", bool(ids) and all(item in sources for item in ids), key)
            checks.add("source_url_matches_register",
                       {url.strip() for url in row["source_url"].split("|")} ==
                       {sources[item]["url"] for item in ids if item in sources}, key)
            if row["metric_id"] == "M008":
                checks.add("derived_ratio_precision", row["precision_million"] == 0, key)
            else:
                try:
                    converted = _parse_original(raw["original_value"]) * _original_factor(raw["original_unit"])
                    checks.add("original_value_conversion",
                               math.isclose(converted, row["value"], abs_tol=1e-9, rel_tol=1e-12), key)
                    if row.get("derivation_type") != "annual_minus_ytd":
                        expected_precision = _source_precision(raw["original_value"], raw["original_unit"])
                        checks.add("source_precision_unit_conversion",
                                   math.isclose(expected_precision, row["precision_million"],
                                                abs_tol=1e-12, rel_tol=1e-12),
                                   f"{key}: expected={expected_precision}, actual={row['precision_million']}")
                except ValueError as error:
                    checks.add("original_value_conversion", False, f"{key}: {error}")
            if row.get("derivation_type") == "annual_minus_ytd":
                try:
                    lineage = json.loads(row.get("input_lineage", ""))
                    legs = {leg["period_type"]: leg for leg in lineage}
                    annual, ytd = legs["annual"], legs["ytd9m"]
                    computed = (float(annual["value"]) * _original_factor(annual["unit"])
                                - float(ytd["value"]) * _original_factor(ytd["unit"]))
                    passed = (
                        row["fiscal_quarter"] == 4 and row["aggregation_type"] == "quarterly_flow" and len(lineage) == 2 and
                        set(ids) == {annual["source_id"], ytd["source_id"]} and
                        all(leg["source_id"] in sources and leg["source_locator"].strip()
                            and leg["source_url"] == sources[leg["source_id"]]["url"]
                            for leg in lineage) and
                        math.isclose(computed, row["value"], abs_tol=1e-9, rel_tol=1e-12))
                    checks.add("annual_minus_ytd_lineage", passed, key)
                    # Subtracting two rounded flows adds their rounding half-widths.
                    # JSON numbers do not preserve source trailing digits: these
                    # legs are integers explicitly reported in USD thousands.
                    leg_steps = []
                    for leg in lineage:
                        leg_value = float(leg["value"])
                        if leg["unit"] == "USD thousand" and leg_value.is_integer():
                            leg_steps.append(0.001)
                        else:
                            leg_steps.append(_source_precision(leg["value"], leg["unit"]))
                    row["effective_rounding_step_million"] = sum(leg_steps)
                    checks.add("derived_input_precision_conversion",
                               math.isclose(row["precision_million"], sum(leg_steps),
                                            abs_tol=1e-12, rel_tol=1e-12),
                               f"{key}: propagated={sum(leg_steps)}, actual={row['precision_million']}")
                except (ValueError, KeyError, TypeError) as error:
                    checks.add("annual_minus_ytd_lineage", False, f"{key}: {error}")
            rows.append(row)
        typed[name] = rows
        counts = Counter((row["period_end"], row["metric_id"], row["scope"]) for row in rows)
        checks.add(f"{name}_primary_key", all(count == 1 for count in counts.values()),
                   [key for key, count in counts.items() if count != 1])
        actual = {(row["fiscal_year"], row["fiscal_quarter"], row["metric_id"]) for row in rows}
        expected = {(year, quarter, metric) for year, quarter in expected_quarters
                    for metric in expected_metrics}
        checks.add(f"{name}_coverage", actual == expected and len(rows) == len(expected),
                   f"missing={sorted(expected - actual)}; extra={sorted(actual - expected)}")
    all_rows = typed["baselines"] + typed["quarterly"]
    scopes = {row["scope"] for row in all_rows}
    checks.add("consistent_global_scope", scopes == {"global_company"}, sorted(scopes))
    lookup = {(row["fiscal_year"], row["fiscal_quarter"], row["metric_id"]): row for row in all_rows}
    for year, quarter in MAIN_QUARTERS + BASE_QUARTERS:
        dau, mau = lookup.get((year, quarter, "M001")), lookup.get((year, quarter, "M002"))
        if dau and mau and mau["value"] > 0 and math.isfinite(mau["value"]):
            checks.add("dau_not_above_mau", dau["value"] <= mau["value"], f"{year} Q{quarter}")
            ratio = lookup.get((year, quarter, "M008"))
            if ratio:
                checks.add("dau_mau_ratio_identity",
                           math.isclose(ratio["value"], dau["value"] / mau["value"],
                                        abs_tol=1e-12, rel_tol=1e-12), f"{year} Q{quarter}")
            else:
                lookup[(year, quarter, "M008")] = _ratio_row(dau, mau)
        for component, total in (("M005", "M006"), ("M009", "M007")):
            part, whole = lookup.get((year, quarter, component)), lookup.get((year, quarter, total))
            if part and whole:
                checks.add("subscription_component_not_above_total",
                           part["value"] <= whole["value"], f"{year} Q{quarter}:{component}/{total}")
    reconciliations = []
    for row in typed["quarterly"]:
        year, quarter, metric = row["fiscal_year"], row["fiscal_quarter"], row["metric_id"]
        for cadence, base_period in (("yoy", (year - 1, quarter)), ("qoq", _previous_quarter(year, quarter))):
            checks.add("comparison_baseline_coverage", (*base_period, metric) in lookup,
                       f"{year} Q{quarter}:{metric}:{cadence}")
        base = lookup.get((year - 1, quarter, metric))
        if base and row["reported_yoy_pct"] != "":
            try:
                low, high = _growth_interval(row, base)
                reported = row["reported_yoy_pct"]
                reported_step = float(row.get("reported_yoy_precision_pp") or 1)
                tolerance = reported_step / 2
                checks.add("official_yoy_provenance",
                           bool(row.get("reported_yoy_locator", "").strip()) and
                           bool(row.get("reported_yoy_source_id", "").strip()) and
                           all(sid in sources for sid in _source_ids(
                               {"source_id": row.get("reported_yoy_source_id", "")})) and
                           math.isfinite(reported_step) and reported_step > 0,
                           f"{year} Q{quarter}:{metric}")
                passed = (math.isfinite(reported) and low <= reported + tolerance + 1e-9
                          and high >= reported - tolerance - 1e-9)
                checks.add("official_yoy_rounding_reconciliation", passed,
                           f"{year} Q{quarter}:{metric}: interval=[{low:.6f},{high:.6f}], reported={reported}")
                reconciliations.append({
                    "period_end": row["period_end"], "metric_id": metric,
                    "reported_yoy_pct": reported,
                    "calculated_yoy_pct": 100 * (row["value"] / base["value"] - 1),
                    "rounding_low_pct": low, "rounding_high_pct": high,
                    "official_rounding_tolerance_percentage_points": tolerance, "passed": passed,
                })
            except ValueError as error:
                checks.add("official_yoy_rounding_reconciliation", False, str(error))
    events = raw_tables["timeline"]
    event_ids = [row["event_id"] for row in events]
    checks.add("timeline_unique_event_id", bool(events) and len(event_ids) == len(set(event_ids)))
    for event in events:
        ids = _source_ids(event)
        checks.add("timeline_source_fk", bool(ids) and all(item in sources for item in ids), event["event_id"])
        checks.add("timeline_required_values",
                   all(event[field].strip() for field in ("event_id", "event_date_precision",
                       "reported_on", "feature", "rollout_scope_text", "claim_type")), event["event_id"])
        try:
            date.fromisoformat(event["reported_on"])
            event_date, precision = event["event_date"], event["event_date_precision"]
            passed = precision in ("day", "month", "quarter", "quarter_end", "year",
                                   "unknown", "unspecified", "reported_snapshot")
            if precision in ("day", "quarter_end"):
                date.fromisoformat(event_date)
                if precision == "quarter_end":
                    day = date.fromisoformat(event_date)
                    passed = passed and day.month in (3, 6, 9, 12) and day.day == calendar.monthrange(day.year, day.month)[1]
            elif precision == "month":
                date.fromisoformat(event_date + "-01")
            elif precision == "year":
                date.fromisoformat(event_date + "-01-01")
            elif precision == "quarter":
                if event_date:
                    year_text, quarter_text = event_date.replace(" ", "").split("Q")
                    passed = passed and 1 <= int(quarter_text) <= 4
                    int(year_text)
                else:
                    start = date.fromisoformat(event.get("event_window_start", ""))
                    end = date.fromisoformat(event.get("event_window_end", ""))
                    quarter = (start.month - 1) // 3 + 1
                    passed = passed and (start.isoformat(), end.isoformat()) == _quarter_dates(start.year, quarter)
            else:
                passed = passed and not event_date
            checks.add("timeline_date_precision", passed, event["event_id"])
        except (ValueError, TypeError):
            checks.add("timeline_date_precision", False, event["event_id"])
    report = {
        "status": "passed" if checks.passed else "failed",
        "validation_scope": "local input consistency and arithmetic, not Notebook execution or visual acceptance",
        "analysis_window": "2024 Q3–2026 Q2",
        "baseline_window": "2023 Q3–2024 Q2 (comparison inputs only)",
        "scope": sorted(scopes), "checks": checks.items,
        "inputs": {name: {"path": relative, "rows": len(raw_tables[name]),
                         "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest()}
                   for name, relative in INPUT_NAMES.items()},
        "official_yoy_reconciliations": reconciliations,
        "limitations": [
            "Local consistency checks do not independently verify original source authenticity.",
            "Company metrics cannot identify Video Call treatment effects.",
            "DAU/MAU is a ratio of quarterly averages, not cohort retention.",
            "Paid subscriptions are quarter-end paying accounts, not conversion.",
            "Bookings and revenue are different quarterly flows; their gap is not deferred revenue.",
            "Eight main quarters do not support robust causal or seasonal modeling.",
            "Input rounding intervals are not statistical confidence intervals.",
            "Q4 annual-minus-YTD rounding bounds propagate both source legs, "
            "separately from the derived displayed value's last digit.",
        ],
    }
    if not checks.passed:
        raise InputValidationError(report)
    return {"root": root, "quarterly": sorted(typed["quarterly"],
                key=lambda row: (row["period_end"], row["metric_id"])),
            "baselines": typed["baselines"], "timeline": events,
            "lookup": lookup, "sources": sources, "report": report}


def compute_diagnostics(inputs):
    lookup = inputs["lookup"]
    diagnostics, decomposition, commercial = [], [], []
    for row in inputs["quarterly"]:
        year, quarter, metric = row["fiscal_year"], row["fiscal_quarter"], row["metric_id"]
        result = {key: row[key] for key in ("period_start", "period_end", "fiscal_year",
                  "fiscal_quarter", "metric_id", "value", "unit", "aggregation_type", "scope", "source_id")}
        result["calculation_label"] = "analyst_derived_from_disclosed_values"
        for cadence, base_period in (("yoy", (year - 1, quarter)), ("qoq", _previous_quarter(year, quarter))):
            base = lookup[(*base_period, metric)]
            result.update({
                f"{cadence}_baseline_period_end": base["period_end"],
                f"{cadence}_baseline_value": base["value"],
                f"{cadence}_baseline_source_id": base["source_id"],
                f"{cadence}_pct": 100 * (row["value"] / base["value"] - 1),
            })
            low, high = _growth_interval(row, base) if metric != "M008" else ("", "")
            result[f"{cadence}_rounding_low_pct"] = low
            result[f"{cadence}_rounding_high_pct"] = high
        result["reported_yoy_pct"] = row["reported_yoy_pct"]
        result["reported_yoy_source_id"] = row.get("reported_yoy_source_id", "")
        result["reported_yoy_locator"] = row.get("reported_yoy_locator", "")
        result["reported_yoy_precision_pp"] = row.get("reported_yoy_precision_pp", "")
        diagnostics.append(result)
    for year, quarter in MAIN_QUARTERS:
        dau, mau, ratio = (lookup[(year, quarter, metric)] for metric in ("M001", "M002", "M008"))
        for cadence, base_period in (("yoy", (year - 1, quarter)), ("qoq", _previous_quarter(year, quarter))):
            base_dau, base_mau, base_ratio = (lookup[(*base_period, metric)] for metric in ("M001", "M002", "M008"))
            dau_log = 100 * math.log(dau["value"] / base_dau["value"])
            mau_log = 100 * math.log(mau["value"] / base_mau["value"])
            ratio_log = 100 * math.log(ratio["value"] / base_ratio["value"])
            decomposition.append({
                "period_end": dau["period_end"], "fiscal_year": year, "fiscal_quarter": quarter,
                "comparison": cadence, "baseline_period_end": base_dau["period_end"],
                "dau_log_growth_points": dau_log, "mau_log_component_points": mau_log,
                "ratio_log_component_points": ratio_log,
                "identity_residual_points": dau_log - mau_log - ratio_log,
                "unit": "100 log growth points", "scope": dau["scope"],
                "source_id": "|".join(sorted(set(_source_ids(dau) + _source_ids(mau)))),
                "baseline_source_id": "|".join(sorted(set(_source_ids(base_dau) + _source_ids(base_mau)))),
                "interpretation": "Arithmetic identity; not causal contribution or percent share",
            })
        sub_book, total_book, total_rev, sub_rev = (lookup[(year, quarter, metric)]
                                                  for metric in ("M005", "M006", "M007", "M009"))
        commercial.append({
            "period_end": dau["period_end"], "fiscal_year": year, "fiscal_quarter": quarter,
            "scope": dau["scope"], "subscription_bookings_usd_million": sub_book["value"],
            "total_bookings_usd_million": total_book["value"],
            "subscription_revenue_usd_million": sub_rev["value"],
            "total_revenue_usd_million": total_rev["value"],
            "subscription_share_of_total_bookings_pct": 100 * sub_book["value"] / total_book["value"],
            "subscription_share_of_total_revenue_pct": 100 * sub_rev["value"] / total_rev["value"],
            "subscription_bookings_to_subscription_revenue_ratio": sub_book["value"] / sub_rev["value"],
            "subscription_bookings_minus_subscription_revenue_usd_million": sub_book["value"] - sub_rev["value"],
            "source_id": "|".join(sorted({sid for item in (sub_book, total_book, total_rev, sub_rev)
                                         for sid in _source_ids(item)})),
            "calculation_label": "analyst_derived_from_disclosed_values",
            "interpretation": "Same-quarter flow comparison; not conversion, profit, cash flow, or change in deferred revenue",
        })
    return {"business_diagnostics": diagnostics, "engagement_decomposition": decomposition,
            "commercial_structure": commercial}


def _write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to create empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def create_figures(inputs, tables):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#8B9196", "text.color": PALETTE["ink"],
        "axes.labelcolor": PALETTE["ink"], "grid.color": "#DFE3E6",
        "grid.linewidth": 0.65, "axes.grid": False, "savefig.dpi": 170,
        "figure.facecolor": "white",
    })
    folder = inputs["root"] / "analysis/figures"
    folder.mkdir(parents=True, exist_ok=True)
    labels = [f"{year}\nQ{quarter}" for year, quarter in MAIN_QUARTERS]
    x, lookup, paths = list(range(len(labels))), inputs["lookup"], []
    source_ids = sorted({sid for row in inputs["quarterly"] for sid in _source_ids(row)})
    baseline_ids = sorted({sid for row in inputs["baselines"] for sid in _source_ids(row)})

    def finish(figure, filename, note, baselines=False):
        source_note = "Sources: " + ", ".join(source_ids)
        if baselines:
            source_note += "; comparison bases: " + ", ".join(baseline_ids)
        lines = []
        for line in ("Global Duolingo company | 2024 Q3–2026 Q2 | growth recomputed from disclosed rounded values",
                     source_note, note):
            lines.extend(textwrap.wrap(line, width=135))
        figure.text(0.065, 0.03, "\n".join(lines), fontsize=8.3,
                    va="bottom", ha="left", linespacing=1.45)
        figure.subplots_adjust(left=0.085, right=0.97, top=0.90,
                               bottom=0.18 + 0.017 * max(0, len(lines) - 3),
                               hspace=0.50, wspace=0.25)
        path = folder / filename
        figure.savefig(path, metadata={"Software": "Duolingo Stage 3 Matplotlib"})
        plt.close(figure)
        paths.append(str(path))

    def axis_style(axis, ylabel, zero=True):
        axis.set_xticks(x, labels)
        axis.set_ylabel(ylabel)
        axis.grid(axis="y")
        if zero:
            axis.set_ylim(bottom=0)

    def series(metric):
        return [lookup[(year, quarter, metric)]["value"] for year, quarter in MAIN_QUARTERS]

    figure, axes = plt.subplots(2, 1, figsize=(12, 8))
    figure.suptitle("Active reach and engagement frequency", fontsize=16, x=0.065, ha="left")
    axes[0].plot(x, series("M002"), color=PALETTE["gold"], marker="s", linestyle="--",
                 label="MAU: quarterly mean of monthly users")
    axes[0].plot(x, series("M001"), color=PALETTE["blue"], marker="o",
                 label="DAU: quarterly mean of daily users")
    axis_style(axes[0], "Million users")
    axes[0].legend(loc="upper left", fontsize=9)
    axes[1].plot(x, [100 * value for value in series("M008")], color=PALETTE["blue"], marker="o")
    axis_style(axes[1], "DAU / MAU (%)")
    axes[1].set_ylim(0, max(50, max(series("M008")) * 115))
    finish(figure, FIGURE_NAMES[0],
           "Ratio of quarterly averages; not mean monthly ratios, cohort retention, or Video Call adoption.")

    figure, axis = plt.subplots(figsize=(12, 6.5))
    figure.suptitle("DAU year-over-year growth: an arithmetic log decomposition",
                   fontsize=15, x=0.065, ha="left")
    yoy = [row for row in tables["engagement_decomposition"] if row["comparison"] == "yoy"]
    mau_log = [row["mau_log_component_points"] for row in yoy]
    ratio_log = [row["ratio_log_component_points"] for row in yoy]
    axis.bar(x, mau_log, color=PALETTE["blue"], width=0.62, label="MAU log component")
    ratio_bottom = [max(0, value) if delta >= 0 else min(0, value)
                    for value, delta in zip(mau_log, ratio_log)]
    axis.bar(x, ratio_log, bottom=ratio_bottom, color=PALETTE["gold"], width=0.62,
             hatch="//", label="DAU/MAU log component")
    axis.plot(x, [row["dau_log_growth_points"] for row in yoy],
              color=PALETTE["ink"], marker="D", linestyle="--", label="DAU total log growth")
    axis_style(axis, "100 log growth points", zero=False)
    axis.axhline(0, color=PALETTE["ink"], linewidth=0.8)
    axis.legend(loc="upper right", fontsize=9)
    finish(figure, FIGURE_NAMES[1],
           "100 ln(DAU_t/DAU_base) = MAU component + ratio component; "
           "not percentage-point growth contributions or causal effects.", True)

    figure, axes = plt.subplots(2, 1, figsize=(12, 8))
    figure.suptitle("Paid-account stock and subscription purchase growth",
                   fontsize=15, x=0.065, ha="left")
    axes[0].plot(x, series("M004"), color=PALETTE["blue"], marker="o")
    axis_style(axes[0], "Million paying accounts\n(quarter end)")
    diagnostic_lookup = {(row["fiscal_year"], row["fiscal_quarter"], row["metric_id"]): row
                         for row in tables["business_diagnostics"]}
    for metric, color, marker, linestyle, label in (
        ("M004", PALETTE["blue"], "o", "-", "Paid-account stock YoY"),
        ("M005", PALETTE["gold"], "s", "--", "Subscription bookings YoY"),
    ):
        axes[1].plot(x, [diagnostic_lookup[(year, quarter, metric)]["yoy_pct"]
                        for year, quarter in MAIN_QUARTERS],
                     color=color, marker=marker, linestyle=linestyle, label=label)
    axis_style(axes[1], "Year-over-year change (%)", zero=False)
    axes[1].axhline(0, color=PALETTE["ink"], linewidth=0.8)
    axes[1].legend(fontsize=9, loc="best")
    finish(figure, FIGURE_NAMES[2],
           "YoY recomputed from disclosed rounded values. Stock and purchase flows have different time bases. "
           "No conversion, renewals, ARPPU, or Video Call monetization is estimated.", True)

    figure, axes = plt.subplots(2, 1, figsize=(12, 8))
    figure.suptitle("Quarterly purchase and revenue-recognition timing", fontsize=15, x=0.065, ha="left")
    for axis, book_metric, rev_metric, title in (
        (axes[0], "M006", "M007", "Total company"),
        (axes[1], "M005", "M009", "Subscriptions"),
    ):
        axis.plot(x, series(book_metric), color=PALETTE["gold"], marker="s", linestyle="--", label="Bookings")
        axis.plot(x, series(rev_metric), color=PALETTE["blue"], marker="o", label="GAAP revenue")
        axis_style(axis, "USD million\n(quarterly flow)")
        axis.set_title(title, loc="left", fontsize=11)
        axis.legend(loc="upper left", fontsize=9)
    finish(figure, FIGURE_NAMES[3],
           "Same-quarter flows; the gap is not profit, operating cash flow, "
           "or a reconciled change in deferred revenue.")

    figure, axis = plt.subplots(figsize=(12, 6.5))
    figure.suptitle("Subscriptions' share of company commercial flows", fontsize=15, x=0.065, ha="left")
    commercial = tables["commercial_structure"]
    axis.plot(x, [row["subscription_share_of_total_bookings_pct"] for row in commercial],
              color=PALETTE["gold"], marker="s", linestyle="--", label="Subscription bookings / total bookings")
    axis.plot(x, [row["subscription_share_of_total_revenue_pct"] for row in commercial],
              color=PALETTE["blue"], marker="o", label="Subscription revenue / total revenue")
    axis_style(axis, "Share of respective total (%)")
    axis.set_ylim(0, 100)
    axis.legend(loc="lower left", fontsize=9)
    finish(figure, FIGURE_NAMES[4],
           "Two separate denominators; no product, tier, geography, margin, or learning-effect attribution.")
    return paths


def run_analysis(root):
    """Validate first, then generate only the declared derivative outputs."""
    inputs = validate_inputs(root)
    tables = compute_diagnostics(inputs)
    residuals = [abs(row["identity_residual_points"]) for row in tables["engagement_decomposition"]]
    passed = max(residuals, default=0) < 1e-9
    inputs["report"]["checks"]["log_decomposition_identity"] = {
        "status": "passed" if passed else "failed", "evaluations": len(residuals),
        "max_absolute_residual_log_growth_points": max(residuals, default=0),
        "failures": [] if passed else ["Residual exceeds 1e-9"],
    }
    if not passed:
        inputs["report"]["status"] = "failed"
        raise InputValidationError(inputs["report"])
    for name, rows in tables.items():
        _write_csv(inputs["root"] / f"data/public/{name}.csv", rows)
    figures = create_figures(inputs, tables)
    import matplotlib
    inputs["report"]["runtime"] = {"python": platform.python_version(), "matplotlib": matplotlib.__version__}
    inputs["report"]["notebook_execution"] = {
        "status": "not_verified_by_module",
        "note": "run_analysis does not establish fresh-kernel Notebook execution; the runner records that separately.",
    }
    inputs["report"]["outputs"] = {
        "tables": {name: {"path": f"data/public/{name}.csv", "rows": len(rows)} for name, rows in tables.items()},
        "figures": [str(Path(path).relative_to(inputs["root"])).replace("\\", "/") for path in figures],
    }
    validation = inputs["root"] / "analysis/stage3_validation.json"
    validation.write_text(json.dumps(inputs["report"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
    return {"inputs": inputs, "tables": tables, "figures": figures, "validation_path": str(validation)}


def html_table(rows, columns, caption):
    headings = "".join(f"<th>{html.escape(label)}</th>" for _, label in columns)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(key, '')))}</td>"
                                    for key, _ in columns) + "</tr>" for row in rows)
    return (f"<p><strong>{html.escape(caption)}</strong></p>"
            '<table style="border-collapse:collapse;font-size:13px">'
            f"<thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table>")


def summary_markdown(result):
    lookup = result["inputs"]["lookup"]
    diagnostics = {(row["fiscal_year"], row["fiscal_quarter"], row["metric_id"]): row
                   for row in result["tables"]["business_diagnostics"]}
    year, quarter = MAIN_QUARTERS[-1]
    dau, mau, paid = (lookup[(year, quarter, metric)]["value"] for metric in ("M001", "M002", "M004"))
    ratio, bookings = 100 * lookup[(year, quarter, "M008")]["value"], lookup[(year, quarter, "M005")]["value"]
    return (
        f"**Latest disclosed quarter: {year} Q{quarter}.** DAU {dau:.1f}m "
        f"(YoY {diagnostics[(year, quarter, 'M001')]['yoy_pct']:+.2f}%), MAU {mau:.1f}m; "
        f"their quarterly-average ratio is {ratio:.2f}%. "
        f"Paid subscriptions are {paid:.1f}m paying accounts **at quarter end**. "
        f"Subscription bookings are USD {bookings:.3f}m **for the quarter**.\n\n"
        "These are global company observations. Log identities and commercial ratios "
        "describe arithmetic; they do not establish Video Call effects, cohort retention, "
        "conversion, learning gains, or unit economics."
    )
