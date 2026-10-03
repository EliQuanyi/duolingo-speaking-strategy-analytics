"""Read-only Stage 4 verification, with independent Decimal economic arithmetic.

Default and --check-only read existing artifacts. They never rebuild outputs,
execute Notebook cells, access the network, or write a verification file.
Public model helpers are used only for the separate interface/boundary suite.
"""
from __future__ import annotations

import argparse
import base64
import copy
import csv
import hashlib
import importlib.util
import itertools
import json
import sys
from decimal import Decimal, localcontext
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
D = Decimal
ZERO, ONE = D(0), D(1)
TOL = D("1e-10")
POLICIES = ("P0", "P1", "P2")
TIERS = ("Free", "Super", "Max")
CASES = ("low", "base", "high")
FILES = {
    "results": "data/public/scenario_results.csv",
    "paths": "data/public/stage4_billing_paths.csv",
    "thresholds": "data/public/stage4_break_even.csv",
    "sensitivity": "data/public/stage4_sensitivity.csv",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def number(value):
    require(not isinstance(value, bool), "Boolean used as an economic number")
    result = value if isinstance(value, D) else D(str(value))
    require(result.is_finite(), f"Non-finite number: {value}")
    return result


def close(actual, expected, label):
    if expected is None:
        require(actual in (None, ""), f"{label}: expected an undefined threshold, got {actual}")
        return
    a, b = number(actual), number(expected)
    require(abs(a - b) <= TOL * max(ONE, abs(a), abs(b)),
            f"{label}: stored={a}, independently expected={b}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(name):
    path = ROOT / FILES[name]
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def key(row):
    return row["policy_id"], row["scenario_id"], row["original_tier"]


def unique(rows, key_function, expected_keys, label):
    indexed = {key_function(row): row for row in rows}
    require(len(indexed) == len(rows), f"{label}: duplicate primary key")
    require(set(indexed) == set(expected_keys), f"{label}: missing or unexpected keys")
    return indexed


def probability_path(tier, gain, loss):
    """Independent marginal construction; no model helper or clipping."""
    q0 = [number(x) for x in tier["control_probabilities"]]
    qt = q0.copy()
    outgoing = [ZERO, ZERO, ZERO]
    require(len(q0) == 3 and sum(q0) == ONE, "Control path mass must equal one")
    for amount, donor, receiver in (
        (gain, tier["gain_from"], tier["gain_to"]),
        (loss, tier["loss_from"], tier["loss_to"]),
    ):
        require(ZERO <= amount <= ONE, "Path-shift rate is outside [0, 1]")
        outgoing[donor] += amount
        qt[donor] -= amount
        qt[receiver] += amount
    require(all(outgoing[i] <= q0[i] for i in range(3)), "Original donor mass overspent")
    require(all(ZERO <= x <= ONE for x in qt), "Impossible path probability")
    require(sum(qt) == ONE and sum(t - c for t, c in zip(qt, q0)) == ZERO,
            "Marginal path mass not conserved")
    return q0, qt


def independent(config, p, s, case, gain=None, loss=None, price=None):
    """Expand billing paths and attempted-workload costs using Decimal only."""
    tier, scenario = config["tiers"][s], config["scenarios"][case]
    params = scenario.get(p, {})
    g = number(params.get(f"{s}_gain_rate", 0)) if gain is None else number(gain)
    loss_rate = number(params.get(f"{s}_loss_rate", 0)) if loss is None else number(loss)
    k = number(config["unit_cost_demo_usd_per_service_minute"]) if price is None else number(price)
    target = config["policies"][p]["target_tier"] == s
    q0, qt = probability_path(tier, g, loss_rate)
    m = [number(x) for x in tier["contribution_usd_per_path"]]
    u = [number(x) for x in tier["non_offer_service_minutes_per_path"]]
    e, a, r = (number(scenario[x]) for x in
               ("exposure_probability", "adoption_given_exposure", "success_probability"))
    attempts = number(params.get("offer_attempts_per_adopter", 0)) if target else ZERO
    assigned_attempts = e * a * attempts
    successful_units = assigned_attempts * r * number(scenario["successful_service_minutes"])
    failed_units = assigned_attempts * (ONE - r) * number(scenario["failed_service_minutes"])
    offer_units = successful_units + failed_units
    effective = assigned_attempts * r * number(scenario["effective_minutes_per_success"])
    m0 = sum((q * value for q, value in zip(q0, m)), ZERO)
    mt = sum((q * value for q, value in zip(qt, m)), ZERO)
    u0 = sum((q * value for q, value in zip(q0, u)), ZERO)
    ut = sum((q * value for q, value in zip(qt, u)), ZERO) + offer_units
    dm, du = mt - m0, ut - u0
    f = number(config["fixed_cost_per_account_demo_usd"]) if target else ZERO
    other = number(config["other_incremental_cost_demo_usd_per_account"]) if target else ZERO
    dc = k * du + other
    variable, net = dm - dc, dm - dc - f
    expected = {
        "gain_rate_demo": g, "loss_rate_demo": loss_rate,
        "control_path_contribution_usd": m0, "treatment_path_contribution_usd": mt,
        "delta_non_ai_contribution_usd": dm,
        "control_service_minutes": u0, "treatment_service_minutes": ut,
        "offer_service_minutes": offer_units, "delta_service_minutes": du,
        "control_ai_cost_usd": k * u0, "treatment_ai_cost_usd": k * ut,
        "unit_cost_demo_usd_per_service_minute": k,
        "other_incremental_cost_usd": other, "delta_ai_and_service_cost_usd": dc,
        "effective_offer_minutes": effective, "assigned_offer_attempts": assigned_attempts,
        "fixed_cost_per_target_account_demo_usd": f,
        "variable_contribution_usd_per_account": variable,
        "variable_contribution_usd_per_1000_normalized_accounts": number(config["normalization_accounts"]) * variable,
        "net_contribution_usd_per_account_demo": net,
    }
    sign = "positive" if net > TOL else "negative" if net < -TOL else "zero"
    return expected, q0, qt, sign, failed_units


def verify_contract(config):
    require(config["evidence_label"] == "D_assumption_sensitivity", "Economic inputs lost D label")
    require(config["horizon_days"] == 90 and config["currency"] == "USD", "Horizon/currency mismatch")
    require(config["policy_status"] == "conditional_unverified_account_entitlements", "Policy verification overstated")
    for field in ("deployment_accounts", "tier_weights", "fixed_cost_total_usd"):
        require(config[field] is None, f"Unknown {field} was filled")
    require(number(config["normalization_accounts"]) == 1000, "Declared 1000-account output unit changed")
    require(set(config["tiers"]) == set(TIERS), "Original-tier strata changed")
    require({p: config["policies"][p]["target_tier"] for p in POLICIES}
            == {"P0": "none", "P1": "Super", "P2": "Free"}, "Policy target mapping changed")
    free, max_tier = config["tiers"]["Free"], config["tiers"]["Max"]
    require(free["path_ids"][free["loss_from"]] == "first_max_path"
            and free["path_ids"][free["loss_to"]] == "first_super_path",
            "Original Free loss must be potential purchase diversion, not Max downgrade")
    require(max_tier["path_ids"][max_tier["loss_from"]] == "maintain_or_renew_max_path"
            and max_tier["path_ids"][max_tier["loss_to"]] == "downgrade_super_path",
            "Actual Max downgrade belongs in original Max stratum")
    require("complete" in config["path_basis"] and "across arms" in config["path_basis"],
            "Whole-H path and equal-within-path arm assumptions missing")
    require("disjoint" in config["cost_basis"] and "retries" in config["cost_basis"],
            "Offer/paid-workload overlap or retry accounting not declared")
    return {"original_tiers": 3, "common_horizon_days": 90,
            "economic_parameter_evidence": "D only", "deployment_N_F_and_weights": "unknown"}


def verify_scenarios(config, rows):
    expected_keys = list(itertools.product(POLICIES, CASES, TIERS))
    indexed = unique(rows, key, expected_keys, "27 scenarios")
    require(len(rows) == 27, "Expected 27 scenario rows")
    numeric_checks = 0
    for (p, case, s), row in indexed.items():
        values, _, _, sign, failure_units = independent(config, p, s, case)
        for field, value in values.items():
            close(row[field], value, f"{p}/{case}/{s}/{field}")
            numeric_checks += 1
        require(row["net_sign_in_demo"] == sign, "Net sign differs from Decimal result")
        require(row["horizon_days"] == "90" and row["currency"] == "USD", "Output unit mismatch")
        require(row["evidence_label"] == "D_assumption_sensitivity", "Output economic label lost")
        require(row["real_economic_status"] == "not_identified_no_overall_winner", "Actual ranking claimed")
        require(row["policy_status"] == config["policy_status"], "Account-policy status mismatch")
        require("including_zero_users" in row["denominator"], "Zero-users removed from denominator")
        if p == "P0":
            close(row["net_contribution_usd_per_account_demo"], ZERO, "P0 delta")
            close(row["delta_service_minutes"], ZERO, "P0 incremental cost")
        if config["policies"][p]["target_tier"] == s:
            require(failure_units > ZERO, "Failed attempts not represented in current D scenarios")
            require(values["treatment_service_minutes"] >= values["offer_service_minutes"], "Paid workload omitted")
            if p == "P2":
                require(values["treatment_service_minutes"] > values["offer_service_minutes"],
                        "Post-purchase paid-entitlement workload missing")
        else:
            close(row["offer_service_minutes"], ZERO, "Non-target direct offer workload")
    return {"rows": len(rows), "independent_numeric_comparisons": numeric_checks,
            "method": "Decimal path sums and separately expanded successful/failed workload"}


def verify_paths(config, rows):
    expected_keys = [(p, case, s, path_id) for p, case, s in itertools.product(POLICIES, CASES, TIERS)
                     for path_id in config["tiers"][s]["path_ids"]]
    indexed = unique(rows, lambda r: key(r) + (r["path_id"],), expected_keys, "81 billing paths")
    require(len(rows) == 81, "Expected 81 path rows")
    for p, case, s in itertools.product(POLICIES, CASES, TIERS):
        _, q0, qt, _, _ = independent(config, p, s, case)
        tier = config["tiers"][s]
        for j, path_id in enumerate(tier["path_ids"]):
            row = indexed[p, case, s, path_id]
            for field, value in {
                "control_probability_demo": q0[j], "treatment_probability_demo": qt[j],
                "delta_probability_demo": qt[j] - q0[j],
                "whole_path_contribution_demo_usd": tier["contribution_usd_per_path"][j],
                "non_offer_workload_demo_service_minutes": tier["non_offer_service_minutes_per_path"][j],
            }.items():
                close(row[field], value, f"{p}/{case}/{s}/{path_id}/{field}")
            require(row["evidence_label"] == "D_marginal_billing_path", "Path label mismatch")
            require(row["horizon_days"] == "90", "Path billing window mismatch")
    return {"rows": 81, "conserved_marginal_distributions": 27,
            "free_purchase_diversion_and_original_Max_downgrade": "separate paths"}


def verify_sensitivity(config, rows):
    expected_keys = []
    for p in ("P1", "P2"):
        s = config["policies"][p]["target_tier"]
        expected_keys.extend((p, s, number(g), number(loss), number(k))
                             for g, loss, k in itertools.product(
                                 config["sensitivity"][f"{p}_gain_rates"],
                                 config["sensitivity"][f"{p}_loss_rates"],
                                 config["sensitivity"]["unit_costs_usd_per_service_minute"]))
    def scan_key(row):
        return (row["policy_id"], row["original_tier"], number(row["gain_rate_demo"]),
                number(row["loss_rate_demo"]), number(row["unit_cost_demo_usd_per_service_minute"]))
    indexed = unique(rows, scan_key, expected_keys, "joint sensitivity")
    require(len(rows) == 360, "Expected 360 joint-sensitivity rows")
    comparisons = 0
    for (p, s, g, loss, k), row in indexed.items():
        values, _, _, sign, _ = independent(config, p, s, "base", g, loss, k)
        for field in row:
            if field in values:
                close(row[field], values[field], f"scan/{p}/{s}/{g}/{loss}/{k}/{field}")
                comparisons += 1
        require(row["net_sign_in_demo"] == sign, "Sensitivity net sign differs")
        require(row["evidence_label"] == "D_assumption_sensitivity" and row["horizon_days"] == "90",
                "Sensitivity evidence/window mismatch")
    return {"rows": len(rows), "independent_numeric_comparisons": comparisons,
            "method": "independent Decimal; fixed offer dose and moving paid-path workload"}


def verify_thresholds(config, rows):
    expected_keys = list(itertools.product(("P1", "P2"), CASES, TIERS))
    indexed = unique(rows, key, expected_keys, "18 break-even rows")
    require(len(rows) == 18, "Expected 18 threshold rows")
    substitutions = 0
    for (p, case, s), row in indexed.items():
        result, _, _, _, _ = independent(config, p, s, case)
        t = config["tiers"][s]
        m = [number(x) for x in t["contribution_usd_per_path"]]
        u = [number(x) for x in t["non_offer_service_minutes_per_path"]]
        gf, gt, lf, lt = (t[x] for x in ("gain_from", "gain_to", "loss_from", "loss_to"))
        k = result["unit_cost_demo_usd_per_service_minute"]
        gm, lm = m[gt] - m[gf], m[lf] - m[lt]
        gu, lu = u[gt] - u[gf], u[lf] - u[lt]
        gn, ln = gm - k * gu, lm - k * lu
        offer = k * result["offer_service_minutes"]
        f, other = result["fixed_cost_per_target_account_demo_usd"], result["other_incremental_cost_usd"]
        g, loss = result["gain_rate_demo"], result["loss_rate_demo"]
        gain_numerator = loss * ln + offer + other + f
        required_gain = gain_numerator / gn if abs(gn) > TOL else None
        required_loss = (g * gn - offer - other - f) / ln if abs(ln) > TOL else None
        du = result["delta_service_minutes"]
        required_k = (result["delta_non_ai_contribution_usd"] - other - f) / du if abs(du) > TOL else None
        cap = number(t["control_probabilities"][gf]) - (loss if gf == lf else ZERO)
        values = {
            "gain_margin_net_of_paid_workload_usd": gn,
            "loss_margin_net_of_paid_workload_usd": ln,
            "gain_rate_break_even": required_gain,
            "gain_available_donor_probability_cap": cap,
            "loss_rate_break_even": required_loss,
            "unit_cost_break_even_usd_per_service_minute": required_k,
            "max_incremental_service_cost_usd_per_account": result["delta_non_ai_contribution_usd"] - f,
            "minimum_delta_non_ai_contribution_usd_per_account": result["delta_ai_and_service_cost_usd"] + f,
        }
        for field, expected in values.items():
            close(row[field], expected, f"threshold/{p}/{case}/{s}/{field}")
        expected_constraints = {
            "gain_constraint": "lower_bound" if gn > TOL else "upper_bound" if gn < -TOL else "independent_of_gain",
            "loss_constraint": "upper_bound" if ln > TOL else "lower_bound" if ln < -TOL else "independent_of_loss",
            "unit_cost_constraint": "upper_bound" if du > TOL else "lower_bound" if du < -TOL else "independent_of_unit_cost",
        }
        for field, expected in expected_constraints.items():
            require(row[field] == expected, f"{p}/{case}/{s}: wrong {field} direction")
        if required_gain is not None:
            close(required_gain * gn - loss * ln - offer - other - f, ZERO, "Gain-threshold substitution")
            substitutions += 1
        if required_loss is not None:
            close(g * gn - required_loss * ln - offer - other - f, ZERO, "Loss-threshold substitution")
            substitutions += 1
        if required_k is not None:
            close(result["delta_non_ai_contribution_usd"] - required_k * du - other - f,
                  ZERO, "Price-threshold substitution")
            substitutions += 1
        if gn > TOL:
            economic_gain_exists = max(ZERO, required_gain) <= cap + TOL
        elif gn < -TOL:
            economic_gain_exists = min(cap, required_gain) >= -TOL
        else:
            economic_gain_exists = gain_numerator <= TOL
        require(row["economically_feasible_gain_exists_in_D_generator"] == str(economic_gain_exists),
                "Wrong feasible-gain domain result")
        point_feasible = None if required_gain is None else -TOL <= required_gain <= cap + TOL
        require(row["gain_threshold_point_feasible_in_D_generator"] == ("" if point_feasible is None else str(point_feasible)),
                "Threshold-point feasibility confused with existence of a profitable feasible rate")
        require(row["evidence_label"] == "D_conditional_threshold", "Threshold mislabeled as effect estimate")
        require(row["symbolic_condition"] == "delta_m >= delta_c + F/N_deployment", "Unknown deployment F/N lost")
    return {"rows": len(rows), "thresholds_substituted_independently": substitutions,
            "negative_unit_workload": "inequality reversal checked", "undefined_thresholds": "not divided by zero"}


def load_model():
    spec = importlib.util.spec_from_file_location("stage4_model_interface_under_test", ROOT / "quant/opportunity_model.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_interfaces(config_float):
    """These helpers test interfaces; none are counted as independent arithmetic."""
    model = load_model()
    cases = []
    def reject(label, operation):
        try:
            operation()
        except (ValueError, TypeError):
            cases.append({"case": label, "status": "rejected_as_expected"})
            return
        raise AssertionError(f"Malformed input accepted: {label}")
    def mutated(label, mutation):
        config = copy.deepcopy(config_float)
        mutation(config)
        reject(label, lambda: model.validate_config(config))
    mutated("nonconserved path probability", lambda c: c["tiers"]["Free"]["control_probabilities"].__setitem__(0, .9))
    mutated("negative path probability", lambda c: c["tiers"]["Free"]["control_probabilities"].__setitem__(0, -.1))
    mutated("duplicate path ID", lambda c: c["tiers"]["Free"]["path_ids"].__setitem__(0, "first_super_path"))
    mutated("negative unit cost", lambda c: c.__setitem__("unit_cost_demo_usd_per_service_minute", -.1))
    mutated("nonfinite cost", lambda c: c.__setitem__("unit_cost_demo_usd_per_service_minute", float("nan")))
    mutated("boolean cost", lambda c: c.__setitem__("unit_cost_demo_usd_per_service_minute", True))
    mutated("deployment N silently filled", lambda c: c.__setitem__("deployment_accounts", 1000))
    mutated("tier weights silently filled", lambda c: c.__setitem__("tier_weights", [.5, .4, .1]))
    mutated("fixed total silently filled", lambda c: c.__setitem__("fixed_cost_total_usd", 50))
    mutated("wrong common currency", lambda c: c.__setitem__("currency", "JPY"))
    mutated("wrong common horizon", lambda c: c.__setitem__("horizon_days", 30))
    mutated("economic inputs called facts", lambda c: c.__setitem__("evidence_label", "A_official"))
    mutated("unverified rights called verified", lambda c: c.__setitem__("policy_status", "verified"))
    mutated("offer attempts exceed cap", lambda c: c["scenarios"]["base"]["P2"].__setitem__("offer_attempts_per_adopter", 5))
    mutated("effective time exceeds billable successful time", lambda c: c["scenarios"]["base"].__setitem__("effective_minutes_per_success", 5))
    mutated("workload exceeds offer limit", lambda c: c["scenarios"]["base"].__setitem__("successful_service_minutes", 5))
    mutated("adoption above one", lambda c: c["scenarios"]["base"].__setitem__("adoption_given_exposure", 1.1))
    reject("original donor overspend", lambda: model.shifted_probabilities(config_float["tiers"]["Super"], .16, 0))
    shared = copy.deepcopy(config_float["tiers"]["Super"])
    shared["loss_from"], shared["loss_to"] = shared["gain_from"], 2
    reject("two shifts overspend shared donor", lambda: model.shifted_probabilities(shared, .14, .02))
    reject("P0 given a path uplift", lambda: model.evaluate(config_float, "P0", "Super", "base", gain=.01))
    original = model.evaluate(config_float, "P1", "Super", "base")
    scaled = copy.deepcopy(config_float)
    scaled["normalization_accounts"] = 2000
    rescaled = model.evaluate(scaled, "P1", "Super", "base")
    for field in ("fixed_cost_per_target_account_demo_usd", "net_contribution_usd_per_account_demo",
                  "variable_contribution_usd_per_account"):
        close(rescaled[field], original[field], "Normalization must not alter fixed allocation or per-account values")
    close(rescaled["variable_contribution_usd_per_1000_normalized_accounts"],
          2 * original["variable_contribution_usd_per_1000_normalized_accounts"], "Variable-only normalization scaling")
    zero_dose = copy.deepcopy(config_float)
    for scenario in zero_dose["scenarios"].values():
        for field in ("successful_service_minutes", "failed_service_minutes", "effective_minutes_per_success"):
            scenario[field] = 0
    for tier in zero_dose["tiers"].values():
        tier["non_offer_service_minutes_per_path"] = [0, 0, 0]
    zero_row = model.evaluate(zero_dose, "P1", "Super", "base")
    zero_threshold = model.break_even(zero_dose, zero_row)
    require(zero_threshold["unit_cost_break_even_usd_per_service_minute"] is None
            and zero_threshold["unit_cost_constraint"] == "independent_of_unit_cost", "Zero price denominator not handled")
    negative_row = model.evaluate(config_float, "P1", "Max", "base")
    negative_threshold = model.break_even(config_float, negative_row)
    require(negative_row["delta_service_minutes"] < 0
            and negative_threshold["unit_cost_constraint"] == "lower_bound", "Negative price denominator inequality not reversed")
    positive_threshold = model.break_even(config_float, original)
    require(original["delta_service_minutes"] > 0
            and positive_threshold["unit_cost_constraint"] == "upper_bound", "Positive price denominator direction wrong")
    shared_config = copy.deepcopy(config_float)
    shared_config["tiers"]["Super"] = shared
    shared_row = model.evaluate(shared_config, "P1", "Super", "base", gain=.10, loss=.02)
    shared_threshold = model.break_even(shared_config, shared_row)
    close(shared_threshold["gain_available_donor_probability_cap"], D(".13"),
          "Loss must consume a shared original donor before feasible gain cap is computed")
    zero_gain = copy.deepcopy(zero_dose)
    zero_gain["tiers"]["Super"]["contribution_usd_per_path"][1] = 3
    zero_gain_row = model.evaluate(zero_gain, "P1", "Super", "base")
    zero_gain_threshold = model.break_even(zero_gain, zero_gain_row)
    require(zero_gain_threshold["gain_rate_break_even"] is None
            and zero_gain_threshold["gain_constraint"] == "independent_of_gain"
            and zero_gain_threshold["economically_feasible_gain_exists_in_D_generator"] is False
            and zero_gain_threshold["gain_threshold_point_feasible_in_D_generator"] is None,
            "Zero gain slope with positive remaining costs incorrectly passes economics")
    zero_gain["fixed_cost_per_account_demo_usd"] = 0
    zero_gain["scenarios"]["base"]["P1"]["Super_loss_rate"] = 0
    zero_gain_pass = model.break_even(zero_gain, model.evaluate(zero_gain, "P1", "Super", "base"))
    require(zero_gain_pass["economically_feasible_gain_exists_in_D_generator"] is True,
            "Zero gain slope and zero other net burden must allow the zero-net boundary")
    negative_gain = copy.deepcopy(zero_dose)
    negative_gain["tiers"]["Super"]["contribution_usd_per_path"] = [3, 2, 1]
    negative_gain["fixed_cost_per_account_demo_usd"] = 0
    negative_gain_threshold = model.break_even(negative_gain, model.evaluate(negative_gain, "P1", "Super", "base"))
    close(negative_gain_threshold["gain_rate_break_even"], D(".01"), "Negative gain-slope boundary")
    require(negative_gain_threshold["gain_constraint"] == "upper_bound"
            and negative_gain_threshold["economically_feasible_gain_exists_in_D_generator"] is True,
            "Negative gain slope must reverse direction while retaining feasible lower gain rates")
    zero_loss = copy.deepcopy(zero_dose)
    zero_loss["tiers"]["Super"]["contribution_usd_per_path"][2] = 12
    zero_loss_threshold = model.break_even(zero_loss, model.evaluate(zero_loss, "P1", "Super", "base"))
    require(zero_loss_threshold["loss_rate_break_even"] is None
            and zero_loss_threshold["loss_constraint"] == "independent_of_loss", "Zero loss denominator not handled")
    return {"independent_arithmetic_evidence": False, "rejected_inputs": cases,
            "normalization_invariance": "passed", "unit_price_denominator_signs": ["positive", "zero", "negative"],
            "shared_donor_threshold_cap": "passed", "gain_slope_signs": ["positive", "zero", "negative"],
            "zero_gain_slope_feasible_and_infeasible_burdens": "passed", "zero_loss_slope": "passed"}


class RichTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag == "td":
            self.cell = ""

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag == "td":
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = None


def displayed_rows(rows, fields, numeric_fields):
    def display(row, field):
        if row[field] == "":
            return "unknown / n.a."
        return f"{float(row[field]):.6g}" if field in numeric_fields else row[field]
    return [[display(row, field) for field in fields] for row in rows]


def verify_notebook():
    notebook_path = ROOT / "quant/opportunity_model.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    meta = notebook["metadata"]
    require(meta.get("execution_method") == "fresh_python_process_direct_cells"
            and meta.get("execution_status") == "passed", "Fresh direct Notebook execution metadata absent")
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    require(len(code_cells) == 6 and [cell["execution_count"] for cell in code_cells] == list(range(1, len(code_cells) + 1)),
            "Code cells were not all sequentially executed")
    outputs = [output for cell in code_cells for output in cell["outputs"]]
    require(outputs and not any(output["output_type"] == "error" for output in outputs), "Notebook has missing/error outputs")
    html_outputs, image_hashes = [], []
    for output in outputs:
        data = output.get("data", {})
        if "text/html" in data:
            content = data["text/html"]
            html_outputs.append("".join(content) if isinstance(content, list) else content)
        if "image/png" in data:
            encoded = data["image/png"]
            encoded = "".join(encoded) if isinstance(encoded, list) else encoded
            image_hashes.append(hashlib.sha256(base64.b64decode(encoded, validate=True)).hexdigest())
    require(html_outputs and any("<table" in content for content in html_outputs), "Actual rich table outputs absent")
    tables = []
    for content in html_outputs:
        parser = RichTableParser()
        parser.feed(content)
        tables.append(parser.rows)
    results = read_rows("results")
    threshold_rows = read_rows("thresholds")
    primary = [r for r in results if (r["policy_id"], r["original_tier"])
               in (("P0", "Super"), ("P1", "Super"), ("P2", "Free"))]
    target_thresholds = [r for r in threshold_rows if (r["policy_id"], r["original_tier"])
                         in (("P1", "Super"), ("P2", "Free"))]
    spillovers = [r for r in results if r["scope"] == "hypothetical_spillover_D"]
    primary_fields = ["policy_id", "scenario_id", "original_tier", "delta_non_ai_contribution_usd",
                      "delta_ai_and_service_cost_usd", "fixed_cost_per_target_account_demo_usd",
                      "net_contribution_usd_per_account_demo"]
    threshold_fields = ["policy_id", "scenario_id", "original_tier", "gain_rate_break_even",
                        "gain_constraint", "economically_feasible_gain_exists_in_D_generator",
                        "unit_cost_break_even_usd_per_service_minute", "unit_cost_constraint"]
    spillover_fields = ["policy_id", "scenario_id", "original_tier", "gain_rate_demo", "loss_rate_demo",
                       "delta_non_ai_contribution_usd", "delta_ai_and_service_cost_usd",
                       "net_contribution_usd_per_account_demo"]
    require(displayed_rows(primary, primary_fields, set(primary_fields[3:])) in tables,
            "Saved primary-account table does not match current CSV values at its declared display precision")
    require(displayed_rows(target_thresholds, threshold_fields,
                           {"gain_rate_break_even", "unit_cost_break_even_usd_per_service_minute"}) in tables,
            "Saved threshold table does not match current CSV values")
    require(displayed_rows(spillovers, spillover_fields, set(spillover_fields[3:])) in tables,
            "Saved spillover table does not match current CSV values")
    figure_paths = ("analysis/figures/stage4/01_response_intensity.png", "analysis/figures/stage4/02_cost_diversion_boundary.png")
    require(len(image_hashes) >= 2, "Two actual PNG Notebook outputs required")
    for name in figure_paths:
        require(sha(ROOT / name) in image_hashes, f"Notebook PNG stale versus {name}")
    return {"code_cells_with_actual_execution_counts": len(code_cells), "actual_outputs": len(outputs),
            "html_outputs": len(html_outputs), "png_outputs_matched_to_current_files": 2,
            "rendered_tables_matched_to_current_CSV": 3, "standard_jupyter_kernel": "not validated",
            "limitation": "Inspects saved direct execution metadata and actual outputs; does not independently re-execute cells or certify a process from metadata alone"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Read current artifacts only (also the default).")
    parser.parse_args()
    checks = {}
    def run_check(name, operation):
        try:
            details = operation()
            checks[name] = {"status": "passed", **details}
        except Exception as error:
            checks[name] = {"status": "failed", "error": f"{type(error).__name__}: {error}"}
    config_path = ROOT / "quant/scenario_inputs.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"), parse_float=D)
        config_float = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as error:
        print(json.dumps({"status": "failed", "writes": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    guarded_paths = [ROOT / FILES[name] for name in FILES]
    guarded_paths += [config_path, ROOT / "quant/opportunity_model.py", ROOT / "quant/opportunity_model.ipynb",
                      ROOT / "quant/stage4_validation.json"]
    before = {str(path): sha(path) for path in guarded_paths if path.is_file()}
    with localcontext() as context:
        context.prec = 50
        run_check("comparison_contract_and_units", lambda: verify_contract(config))
        run_check("independent_27_scenarios", lambda: verify_scenarios(config, read_rows("results")))
        run_check("independent_81_billing_paths", lambda: verify_paths(config, read_rows("paths")))
        run_check("independent_360_joint_sensitivity", lambda: verify_sensitivity(config, read_rows("sensitivity")))
        run_check("independent_18_thresholds", lambda: verify_thresholds(config, read_rows("thresholds")))
        run_check("public_interface_and_boundary_checks", lambda: verify_interfaces(config_float))
        run_check("saved_fresh_direct_Notebook_outputs", verify_notebook)
    after = {str(path): sha(path) for path in guarded_paths if path.is_file()}
    run_check("read_only_artifact_hashes", lambda: (require(before == after, "Artifacts changed during read-only verification")
                                                    or {"unchanged_artifacts": len(before)}))
    passed = all(item["status"] == "passed" for item in checks.values())
    result = {"status": "passed" if passed else "failed", "writes": False, "checks": checks,
              "scope": "Local arithmetic, contract, interfaces and saved direct Notebook provenance only",
              "not_validated": ["real entitlements", "real costs or business uplift", "global-policy spillover causality",
                                "full-population learning effect", "standard Jupyter kernel", "real strategy winner"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
