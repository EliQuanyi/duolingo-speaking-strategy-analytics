"""Stage 4 v2: direct dual-arm accounting, with no economic default values.

Pure arithmetic helpers accept numbers for unit testing. Publication requires
the matching accounting contract and provenance declarations in build_outputs.
Neither software assertions nor a source string constitute source verification.
"""

import csv
import io
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEANS = ("mean_contribution_t", "mean_contribution_c", "mean_serving_cost_t", "mean_serving_cost_c")
CONTRACT = (
    "all_originally_assigned_including_zero_users",
    "comparable_population_and_period",
    "net_contribution_excludes_ai_and_includes_refunds_non_ai_fees",
    "serving_cost_includes_control_failures_and_paid_follow_on",
    "assignment_identification_verified",
)


def number(value, field, nonnegative=False, positive=False, integer=False):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field}: boolean is not a measurement")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{field}: invalid numeric value") from exc
    if not result.is_finite() or (nonnegative and result < 0) or (positive and result <= 0):
        raise ValueError(f"{field}: invalid domain")
    if integer and result != result.to_integral_value():
        raise ValueError(f"{field}: account count must be integral")
    return result


def contrast(m_t, m_c, c_t, c_c):
    """Per originally assigned account; no shared path means are assumed."""
    mt, mc = number(m_t, "m_t"), number(m_c, "m_c")
    ct, cc = number(c_t, "c_t", nonnegative=True), number(c_c, "c_c", nonnegative=True)
    dm = None if mt is None or mc is None else mt - mc
    dc = None if ct is None or cc is None else ct - cc
    return {"delta_contribution": dm, "delta_serving_cost": dc,
            "delta_variable_value": None if dm is None or dc is None else dm - dc}


def per_account_threshold(delta_cost, fixed_cost, deployment_n):
    """Single-population conditional threshold; deployment N is never a scale label."""
    dc = number(delta_cost, "delta_cost")
    f = number(fixed_cost, "fixed_cost", nonnegative=True)
    n = number(deployment_n, "deployment_n", positive=True, integer=True)
    return None if dc is None or f is None or n is None else dc + f / n


def context_missing(config):
    missing = [f"contract.{key}" for key in CONTRACT if config.get("contract", {}).get(key) is not True]
    for key in ("period_start", "period_end", "currency"):
        if not config.get(key):
            missing.append(key)
    return missing


def validate(config):
    if config.get("version") != "stage4-v2.0" or set(config.get("policies", {})) != {"P1", "P2"}:
        raise ValueError("Only the evidence-constrained P1/P2 comparison is accepted")
    if not config.get("population_id"):
        raise ValueError("Population definition is required")
    for key in CONTRACT:
        flag = config.get("contract", {}).get(key)
        if flag is not None and type(flag) is not bool:
            raise ValueError(f"{key}: must be a boolean or null")
    for key in ("period_start", "period_end"):
        if config.get(key) is not None:
            date.fromisoformat(config[key])
    if config.get("period_start") and config.get("period_end") and config["period_end"] < config["period_start"]:
        raise ValueError("End precedes start")
    if config.get("currency") is not None and (not isinstance(config["currency"], str) or len(config["currency"]) != 3 or not config["currency"].isalpha()):
        raise ValueError("Currency must be a three-letter accounting currency")
    for policy_id, policy in config["policies"].items():
        if policy.get("increment_verified") is not None and type(policy["increment_verified"]) is not bool:
            raise ValueError("increment_verified must be a boolean or null")
        scope_flag = policy.get("deployment_effect_scope_matched")
        if scope_flag is not None and type(scope_flag) is not bool:
            raise ValueError("deployment_effect_scope_matched must be a boolean or null")
        f = number(policy.get("fixed_incremental_cost_total"), "fixed cost", nonnegative=True)
        if f is not None and not policy.get("fixed_cost_source_ref"):
            raise ValueError("Fixed cost requires provenance, including an observed zero")
        groups = policy["groups"]
        if sorted(g["original_tier"] for g in groups) != ["Free", "Max", "Super"]:
            raise ValueError("Each policy must preserve all three original tiers exactly once")
        for group in groups:
            for key in ("assignment_n_t", "assignment_n_c", "deployment_n"):
                number(group.get(key), key, positive=True, integer=True)
            for key in MEANS:
                number(group.get(key), key, nonnegative="cost" in key)
            if group.get("deployment_n") is not None and not group.get("deployment_source_ref"):
                raise ValueError("Deployment size requires a verified population source")
            if any(group.get(key) is not None for key in MEANS):
                if group.get("measurement_basis") != "invoice_contribution_and_metered_serving_cost":
                    raise ValueError("Quoted plan prices or aggregate company metrics cannot substitute for arm means")
                if context_missing(config):
                    raise ValueError("Numeric arm means cannot be published under an incomplete accounting contract")
                if not group.get("economic_source_refs") or not isinstance(group["economic_source_refs"], list):
                    raise ValueError("Arm means require governed source references, not quoted plan prices")
                if any(group.get(key) is None for key in ("assignment_n_t", "assignment_n_c")):
                    raise ValueError("Arm means require all-assigned denominators")
    return True


def symbolic_sensitivity():
    return [
        {"parameter": "m_T", "expression": "d(v_variable)/d(m_T)=+1", "meaning": "Treatment contribution increases variable net value one-for-one", "condition": "Same population, accounting period and definitions; hold other terms fixed", "empirical_status": "accounting_identity_not_measured_response"},
        {"parameter": "m_C", "expression": "d(v_variable)/d(m_C)=-1", "meaning": "A higher control contribution reduces incremental value", "condition": "Do not assume a zero-income control", "empirical_status": "accounting_identity_not_measured_response"},
        {"parameter": "c_T", "expression": "d(v_variable)/d(c_T)=-1", "meaning": "Treatment serving cost reduces incremental value", "condition": "Include failures, retries and paid follow-on without double counting", "empirical_status": "accounting_identity_not_measured_response"},
        {"parameter": "c_C", "expression": "d(v_variable)/d(c_C)=+1", "meaning": "Baseline serving cost belongs in the contrast", "condition": "Absolute arm costs nonnegative; incremental cost may have either sign", "empirical_status": "accounting_identity_not_measured_response"},
        {"parameter": "fixed_cost", "expression": "V=sum_s(N_s*delta_v_s)-F; dV/dF=-1", "meaning": "Only decision-incremental fixed expense reduces policy value", "condition": "No allocation to normalized example populations; no sunk costs", "empirical_status": "accounting_identity_not_measured_response"},
        {"parameter": "break_even", "expression": "delta_m >= delta_c + F/N", "meaning": "Minimum contribution condition for one explicitly scoped deployment population", "condition": "Real N>0, matched H, contribution excludes AI; no arbitrary numeric threshold", "empirical_status": "symbolic_boundary_not_empirical_threshold"},
        {"parameter": "quota", "expression": "offer_workload <= attempt_cap*enforced_workload_cap", "meaning": "An enforceable quota bounds only the offer workload", "condition": "Caps and billable mapping must be real; excludes paid follow-on, other cost and F", "empirical_status": "design_constraint_not_learning_or_total_cost_bound"},
        {"parameter": "learning_budget", "expression": "delta_cost_total <= approved_incremental_learning_budget", "meaning": "Teaching investment may use a real budget plus separate learning guardrails", "condition": "Budget is a management choice; do not monetize test-score points or impose a zero-profit goal automatically", "empirical_status": "decision_rule_requires_actual_budget_and_learning_evidence"},
    ]


def build_outputs(config):
    validate(config)
    rows, policies = [], []
    for policy_id, policy in config["policies"].items():
        policy_rows = []
        for group in policy["groups"]:
            values = contrast(*(group.get(key) for key in MEANS))
            missing = context_missing(config) + [key for key in MEANS + ("assignment_n_t", "assignment_n_c") if group.get(key) is None]
            if policy.get("increment_verified") is not True:
                missing.append("actual_policy_increment")
            if not group.get("economic_source_refs"):
                missing.append("economic_source_refs")
            status = "unknown" if values["delta_variable_value"] is None else "accounting_contrast_only_requires_source_and_identification_review"
            row = {"policy_id": policy_id, "original_tier": group["original_tier"], "effect_scope": group["effect_scope"],
                   "population_id": config["population_id"], "period_start": config.get("period_start"), "period_end": config.get("period_end"), "currency": config.get("currency"),
                   **values, "deployment_n": group.get("deployment_n"), "economic_status": status,
                   "missing_inputs": " | ".join(missing), "evidence_status": "unknown_not_zero" if missing else "declared_sources_require_manual_audit",
                   "decision_boundary": "No total ROI, actual threshold, ranking or Scale from missing arm evidence"}
            rows.append(row)
            policy_rows.append(row)
        f = number(policy.get("fixed_incremental_cost_total"), "fixed cost", nonnegative=True)
        total_ready = f is not None and policy.get("increment_verified") is True and policy.get("deployment_effect_scope_matched") is True and all(not row["missing_inputs"] and row["deployment_n"] is not None for row in policy_rows)
        total = sum(number(row["deployment_n"], "N", positive=True, integer=True) * row["delta_variable_value"] for row in policy_rows) - f if total_ready else None
        policies.append({"policy_id": policy_id, "actual_increment_status": "verified_declaration_requires_audit" if policy.get("increment_verified") is True else "not_verified",
                         "total_incremental_value": total, "currency": config.get("currency"), "overall_economic_status": "accounting_total_not_automatic_scale" if total is not None else "not_identified",
                         "deployment_effect_scope_matched": policy.get("deployment_effect_scope_matched"),
                         "condition": "V=sum_s(N_s*delta_v_s)-F; include original-Max and other-tier indirect effects",
                         "next_action": "Verify actual policy increment first; do not select a winner from missing data"})
    return rows, policies, symbolic_sensitivity()


def csv_text(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def generated_texts(config):
    groups, policies, sensitivities = build_outputs(config)
    return {
        "data/public/stage4_economic_readiness.csv": csv_text(groups),
        "data/public/stage4_policy_readiness.csv": csv_text(policies),
        "data/public/stage4_symbolic_sensitivity.csv": csv_text(sensitivities),
    }


def learning_coverage(observations):
    """Coverage of the already published study analysis, not adoption or ITT."""
    fields = {"randomized_Video_Call_n", "randomized_Control_n", "analysed_Video_Call_n", "analysed_Control_n"}
    selected = [row for row in observations if row["field"] in fields]
    by_field = {row["field"]: row for row in selected}
    if len(selected) != 4 or len(by_field) != 4:
        raise ValueError("Study coverage needs the four observed counts")
    if any(row["unit"] != "persons" for row in selected) or len({row["source_url"] for row in selected}) != 1 or len({row["coverage_period"] for row in selected}) != 1:
        raise ValueError("Study counts must have one common source, window and person unit")
    rows = []
    for arm, label in (("video_call", "Video_Call"), ("control", "Control")):
        assigned = by_field[f"randomized_{label}_n"]
        analysed = by_field[f"analysed_{label}_n"]
        n = number(assigned["value"], "assigned study n", positive=True, integer=True)
        a = number(analysed["value"], "analysed study n", nonnegative=True, integer=True)
        if a > n or assigned["source_url"] != analysed["source_url"]:
            raise ValueError("Study counts mismatch")
        rows.append({"study_id": "DRR-25-06", "arm": arm, "assigned_n": n, "analysed_n": a,
                     "not_in_analysis_n": n - a, "not_in_analysis_percent": (100 * (n - a) / n).quantize(Decimal("0.1")),
                     "input_observation_ids": assigned["observation_id"] + "|" + analysed["observation_id"],
                     "source_url": assigned["source_url"], "published_on": assigned["source_publication_date"],
                     "accessed_on": assigned["access_date"], "window": assigned["coverage_period"],
                     "population": "Japanese L1 adult B1.1 English-course learners; residence and device unverified",
                     "interpretation": "Analysis exclusion is not all attrition; no natural adoption rate, full ITT, or commercial uplift"})
    return rows


def load_config():
    return json.loads((ROOT / "quant/evidence_inputs.json").read_text(encoding="utf-8"))
