"""Stage 4 conditional economics. Economic inputs are D examples, never estimates."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from pathlib import Path

POLICIES = ("P0", "P1", "P2")
TIERS = ("Free", "Super", "Max")
SCENARIOS = ("low", "base", "high")
EPS = 1e-10


def finite(value, name, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: finite numeric value required")
    if low is not None and value < low or high is not None and value > high:
        raise ValueError(f"{name}: outside [{low}, {high}]")
    return float(value)


def probabilities(values, name):
    if len(values) != 3:
        raise ValueError(f"{name}: three complete billing-path bins required")
    for value in values:
        finite(value, name, 0, 1)
    if not math.isclose(sum(values), 1, abs_tol=EPS):
        raise ValueError(f"{name}: probabilities must sum to one")


def shifted_probabilities(tier, gain, loss):
    """D marginal-probability construction; not observed joint potential outcomes."""
    finite(gain, "gain", 0, 1)
    finite(loss, "loss", 0, 1)
    q0 = tier["control_probabilities"]
    q = list(q0)
    outgoing = [0.0] * 3
    for amount, source, destination in (
        (gain, tier["gain_from"], tier["gain_to"]),
        (loss, tier["loss_from"], tier["loss_to"]),
    ):
        outgoing[source] += amount
        q[source] -= amount
        q[destination] += amount
    # A single original donor cannot be allocated twice by this D generator.
    if any(outgoing[i] > q0[i] + EPS for i in range(3)):
        raise ValueError("D path shift exceeds original donor probability")
    if any(x < -EPS or x > 1 + EPS for x in q):
        raise ValueError("D path shift generates impossible probability")
    q = [min(1.0, max(0.0, x)) for x in q]
    probabilities(q, "treatment path probabilities")
    return q


def offer_workload(scenario, attempts):
    """All attempts include retries once; failure costs never count as effective practice."""
    e = scenario["exposure_probability"]
    a = scenario["adoption_given_exposure"]
    r = scenario["success_probability"]
    assigned_attempts = e * a * attempts
    billable = assigned_attempts * (
        r * scenario["successful_service_minutes"]
        + (1 - r) * scenario["failed_service_minutes"])
    effective = assigned_attempts * r * scenario["effective_minutes_per_success"]
    return billable, effective, assigned_attempts


def validate_config(config):
    if config.get("evidence_label") != "D_assumption_sensitivity":
        raise ValueError("Economic config must explicitly remain D assumption sensitivity")
    if config.get("currency") != "USD" or config.get("horizon_days") != 90:
        raise ValueError("Current contract is common USD / 90-day horizon")
    if config.get("policy_status") != "conditional_unverified_account_entitlements":
        raise ValueError("Actual account entitlements have not been established")
    if any(config.get(x) is not None for x in ("deployment_accounts", "tier_weights", "fixed_cost_total_usd")):
        raise ValueError("Deployment, weights and total fixed cost remain unknown; no total ranking")
    if any(v is not None for v in config.get("real_parameters", {}).values()):
        raise ValueError("Actual parameters require a separately reviewed input version; current model is D only")
    if config["normalization_accounts"] != 1000:
        raise ValueError("Current output contract explicitly normalizes 1000 accounts; not deployment N")
    finite(config["fixed_cost_per_account_demo_usd"], "fixed cost demo", 0)
    finite(config["unit_cost_demo_usd_per_service_minute"], "unit cost demo", 0)
    finite(config["other_incremental_cost_demo_usd_per_account"], "other cost difference")
    if set(config["tiers"]) != set(TIERS) or set(config["policies"]) != set(POLICIES) or set(config["scenarios"]) != set(SCENARIOS):
        raise ValueError("Three declared policies, original tiers and scenarios required")
    for name, tier in config["tiers"].items():
        probabilities(tier["control_probabilities"], name)
        if len(set(tier["path_ids"])) != 3:
            raise ValueError("Unique billing path IDs required")
        for field in ("contribution_usd_per_path", "non_offer_service_minutes_per_path"):
            if len(tier[field]) != 3:
                raise ValueError("Three path values required")
            for value in tier[field]:
                finite(value, field, 0 if "minutes" in field else None)
        for field in ("gain_from", "gain_to", "loss_from", "loss_to"):
            if type(tier[field]) is not int or tier[field] not in range(3):
                raise ValueError("Path index must be 0, 1 or 2")
        if tier["gain_from"] == tier["gain_to"] or tier["loss_from"] == tier["loss_to"]:
            raise ValueError("A gain/loss shift must change its path")
    for p, policy in config["policies"].items():
        if policy["target_tier"] != {"P0": "none", "P1": "Super", "P2": "Free"}[p]:
            raise ValueError("Policy target conflicts with comparison contract")
        finite(policy["offer_attempt_cap"], "offer cap", 0)
        finite(policy["max_service_minutes_per_attempt"], "attempt workload cap", 0)
    for name, scenario in config["scenarios"].items():
        for field in ("exposure_probability", "adoption_given_exposure", "success_probability"):
            finite(scenario[field], field, 0, 1)
        for field in ("successful_service_minutes", "failed_service_minutes", "effective_minutes_per_success"):
            finite(scenario[field], field, 0)
        if scenario["effective_minutes_per_success"] > scenario["successful_service_minutes"]:
            raise ValueError("In this D workload definition effective time cannot exceed successful service time")
        for p in ("P1", "P2"):
            finite(scenario[p]["offer_attempts_per_adopter"], "attempts", 0, config["policies"][p]["offer_attempt_cap"])
            cap = config["policies"][p]["max_service_minutes_per_attempt"]
            if max(scenario["successful_service_minutes"], scenario["failed_service_minutes"]) > cap:
                raise ValueError("Attempt workload exceeds the D quota definition")
            for s in TIERS:
                shifted_probabilities(config["tiers"][s], scenario[p].get(f"{s}_gain_rate", 0), scenario[p].get(f"{s}_loss_rate", 0))
    for p in ("P1", "P2"):
        s = config["policies"][p]["target_tier"]
        for g in config["sensitivity"][f"{p}_gain_rates"]:
            for loss in config["sensitivity"][f"{p}_loss_rates"]:
                shifted_probabilities(config["tiers"][s], g, loss)
    for value in config["sensitivity"]["unit_costs_usd_per_service_minute"]:
        finite(value, "scan unit cost", 0)
    return {"status": "passed", "scope": "D config, units, marginal path mass, quotas; not empirical parameter validation"}


def evaluate(config, policy_id, tier_id, scenario_id, gain=None, loss=None, unit_cost=None):
    tier = config["tiers"][tier_id]
    scenario = config["scenarios"][scenario_id]
    target = config["policies"][policy_id]["target_tier"] == tier_id
    params = scenario.get(policy_id, {})
    gain = params.get(f"{tier_id}_gain_rate", 0.0) if gain is None else gain
    loss = params.get(f"{tier_id}_loss_rate", 0.0) if loss is None else loss
    if policy_id == "P0" and (gain != 0 or loss != 0):
        raise ValueError("P0 relative to itself cannot have a path effect")
    k = config["unit_cost_demo_usd_per_service_minute"] if unit_cost is None else unit_cost
    finite(k, "unit cost", 0)
    q0 = tier["control_probabilities"]
    qt = shifted_probabilities(tier, gain, loss)
    m = tier["contribution_usd_per_path"]
    u = tier["non_offer_service_minutes_per_path"]
    attempts = params.get("offer_attempts_per_adopter", 0) if target else 0
    offer_u, effective, assigned_attempts = offer_workload(scenario, attempts)
    m0 = sum(q * v for q, v in zip(q0, m))
    mt = sum(q * v for q, v in zip(qt, m))
    u0 = sum(q * v for q, v in zip(q0, u))
    ut = sum(q * v for q, v in zip(qt, u)) + offer_u
    # Fixed-cost allocation is a D per-target-account value, NOT F/normalization.
    f = config["fixed_cost_per_account_demo_usd"] if target else 0.0
    other = config["other_incremental_cost_demo_usd_per_account"] if target else 0.0
    delta_m, delta_u = mt - m0, ut - u0
    delta_c = k * delta_u + other
    variable = delta_m - delta_c
    return {
        "policy_id": policy_id, "scenario_id": scenario_id, "original_tier": tier_id,
        "horizon_days": config["horizon_days"], "currency": config["currency"],
        "evidence_label": config["evidence_label"], "policy_status": config["policy_status"],
        "population_id": "H1_JP_English_existing_individual_iOS",
        "denominator": "all_originally_assigned_accounts_in_this_tier_including_zero_users",
        "scope": "direct_target_D" if target else ("hypothetical_spillover_D" if gain or loss else "unchanged_by_D_assumption"),
        "gain_rate_demo": gain, "loss_rate_demo": loss,
        "control_path_contribution_usd": m0, "treatment_path_contribution_usd": mt,
        "delta_non_ai_contribution_usd": delta_m,
        "control_service_minutes": u0, "treatment_service_minutes": ut,
        "offer_service_minutes": offer_u, "delta_service_minutes": delta_u,
        "control_ai_cost_usd": k * u0, "treatment_ai_cost_usd": k * ut,
        "unit_cost_demo_usd_per_service_minute": k,
        "other_incremental_cost_usd": other, "delta_ai_and_service_cost_usd": delta_c,
        "effective_offer_minutes": effective, "assigned_offer_attempts": assigned_attempts,
        "fixed_cost_per_target_account_demo_usd": f,
        "variable_contribution_usd_per_account": variable,
        "variable_contribution_usd_per_1000_normalized_accounts": config["normalization_accounts"] * variable,
        "net_contribution_usd_per_account_demo": variable - f,
        "net_sign_in_demo": "positive" if variable - f > EPS else "negative" if variable - f < -EPS else "zero",
        "real_economic_status": "not_identified_no_overall_winner",
        "input_ref": "quant/scenario_inputs.json",
        "boundary": "D examples only; no empirical ROI, population total, tier weights or actual F/N",
        "q0": q0, "qt": qt,
    }


def break_even(config, result):
    """Exact conditional thresholds, accounting for paid-workload changes with path rates."""
    t = config["tiers"][result["original_tier"]]
    m, u = t["contribution_usd_per_path"], t["non_offer_service_minutes_per_path"]
    gm = m[t["gain_to"]] - m[t["gain_from"]]
    gu = u[t["gain_to"]] - u[t["gain_from"]]
    lm = m[t["loss_from"]] - m[t["loss_to"]]
    lu = u[t["loss_from"]] - u[t["loss_to"]]
    k = result["unit_cost_demo_usd_per_service_minute"]
    gn, ln = gm - k * gu, lm - k * lu
    offer_cost = k * result["offer_service_minutes"]
    f, other = result["fixed_cost_per_target_account_demo_usd"], result["other_incremental_cost_usd"]
    numerator = result["loss_rate_demo"] * ln + offer_cost + other + f
    required_gain = numerator / gn if abs(gn) > EPS else None
    gain_kind = "lower_bound" if gn > EPS else "upper_bound" if gn < -EPS else "independent_of_gain"
    cap = t["control_probabilities"][t["gain_from"]] - (
        result["loss_rate_demo"] if t["loss_from"] == t["gain_from"] else 0.0)
    feasible = (required_gain <= cap + EPS if gn > EPS else
                required_gain >= -EPS if gn < -EPS else numerator <= EPS)
    point_feasible = None if required_gain is None else -EPS <= required_gain <= cap + EPS
    du = result["delta_service_minutes"]
    price_numerator = result["delta_non_ai_contribution_usd"] - other - f
    price_threshold = price_numerator / du if abs(du) > EPS else None
    loss_threshold = (result["gain_rate_demo"] * gn - offer_cost - other - f) / ln if abs(ln) > EPS else None
    return {
        "policy_id": result["policy_id"], "scenario_id": result["scenario_id"], "original_tier": result["original_tier"],
        "evidence_label": "D_conditional_threshold", "horizon_days": config["horizon_days"],
        "gain_margin_net_of_paid_workload_usd": gn, "loss_margin_net_of_paid_workload_usd": ln,
        "gain_rate_break_even": required_gain, "gain_constraint": gain_kind,
        "gain_available_donor_probability_cap": cap,
        "economically_feasible_gain_exists_in_D_generator": feasible,
        "gain_threshold_point_feasible_in_D_generator": point_feasible,
        "loss_rate_break_even": loss_threshold,
        "loss_constraint": "upper_bound" if ln > EPS else "lower_bound" if ln < -EPS else "independent_of_loss",
        "unit_cost_break_even_usd_per_service_minute": price_threshold,
        "unit_cost_constraint": "upper_bound" if du > EPS else "lower_bound" if du < -EPS else "independent_of_unit_cost",
        "max_incremental_service_cost_usd_per_account": result["delta_non_ai_contribution_usd"] - f,
        "minimum_delta_non_ai_contribution_usd_per_account": result["delta_ai_and_service_cost_usd"] + f,
        "symbolic_condition": "delta_m >= delta_c + F/N_deployment",
        "boundary": "Hold offer workload and other assumptions fixed; path workload changes with gain/loss. Thresholds are D functions, not estimated effects or feasible observed prices. Negative upper bounds can imply no feasible nonnegative price/rate.",
    }


def csv_text(rows):
    import io
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def parameter_register(config):
    """Every scalar economic/design number retains its JSON pointer and D/U classification."""
    rows = []
    def visit(value, parts):
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, parts + [key])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, parts + [str(index)])
        elif isinstance(value, (int, float)) or value is None:
            pointer = "/" + "/".join(parts)
            text = "/".join(parts)
            if "real_parameters" in text:
                unit = "unavailable governed measure; requires arm/population/horizon/schema definition"
            elif "given_exposure" in text:
                unit = "fraction of exposed accounts"
            elif "success_probability" in text:
                unit = "fraction of offer attempts"
            elif "probabilit" in text or "_rate" in text:
                unit = "fraction of all originally assigned accounts in this tier"
            elif "unit_cost" in text:
                unit = "USD per illustrative service minute"
            elif "minutes" in text:
                unit = "illustrative service minutes" if "effective" not in text else "D effective practice minutes"
            elif "contribution_usd_per_path" in text:
                unit = "USD per complete 90-day billing path before AI cost"
            elif "fixed_cost_per_account" in text or "cost_demo_usd_per_account" in text:
                unit = "USD per originally assigned target account / 90 days"
            elif "usd" in text:
                unit = "USD; total deployment amount unknown" if value is None else "USD"
            elif "attempt" in text:
                unit = "offer attempts including retries; per adopter unless quota cap"
            elif "days" in text:
                unit = "days from assignment; D design window"
            elif "accounts" in text:
                unit = "accounts; normalization is not deployment size"
            elif "gain_from" in text or "gain_to" in text or "loss_from" in text or "loss_to" in text:
                unit = "billing path index; D construction"
            else:
                unit = "unknown original-tier population weights" if "tier_weights" in text else "D dimensionless"
            rows.append({"parameter_id": pointer, "value": value, "unit": unit,
                         "evidence_label": "U_not_observed" if value is None else "D_authored_not_estimated",
                         "source_url": "", "input_ref": f"quant/scenario_inputs.json#{pointer}",
                         "period": "90-day design horizon, not historical observations", "as_of": config["as_of"],
                         "population": config["population"], "role": "unknown" if value is None else "design_or_sensitivity",
                         "range_basis": "not available" if value is None else "authored example; logical bounds checked; no empirically defensible domain established",
                         "limitation": "Not actual prices, ARPU, costs, measured adoption, retention or commercial effects; do not use D scans for real-world robust ranking"})
    visit(config, [])
    return rows


def table_html(rows, fields):
    def fmt(v):
        return "unknown / n.a." if v is None else f"{v:.6g}" if isinstance(v, float) else str(v)
    head = "".join(f"<th>{html.escape(f)}</th>" for f in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(fmt(r[f]))}</td>" for f in fields) + "</tr>" for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def strategy_comparison():
    common = {
        "population": "H1 Japanese L1 English course around B1.1; existing individual iOS accounts; speaking level separate",
        "horizon": "90-day D design; original-tier assignment includes zero users",
        "evidence_strength": "A policy statements / restricted learning evidence / C exploratory needs; economic numbers D only",
        "real_economic_status": "not_identified; no overall ROI ranking",
        "learning_guardrails": "blinded delayed unpracticed expression; course displacement; error/interruption quality; all-assigned follow-up",
        "cost_guardrail": "actual incremental serving invoice plus F/N_deployment must fit measured contribution or explicit learning budget",
        "model_result_ref": "data/public/scenario_results.csv",
        "threshold_ref": "data/public/stage4_break_even.csv",
        "sensitivity_ref": "data/public/stage4_sensitivity.csv",
    }
    return [dict(common, **row) for row in (
        {"policy_id": "P0", "name": "Maintain audited current entitlements and Max value boundary",
         "incremental_policy": "Zero relative delta; absolute serving cost not zero; account rights unverified",
         "target_original_tier": "Free / Super / Max reported separately",
         "benefit_mechanism": "Preserve existing access and differentiation; baseline reference only",
         "commercial_outcomes": "baseline whole-path net contribution, not published subscriber stock ARPU",
         "costs": "existing serving cost; no incremental fixed investment",
         "risks": "opportunity delay; cannot conclude optimal status quo from missing evidence",
         "kpi": "baseline effective practice and whole-path contribution; no ROI ratio with zero investment",
         "priority": "common control; not a ranked economic winner",
         "entry_gate": "audit dated account-level eligibility, remaining quota, course/device/role",
         "stop_rule": "do not replace rights with assumed Max-only baseline"},
        {"policy_id": "P1", "name": "Incremental limited Lily access for uncovered original Super",
         "incremental_policy": "D 24 attempts over 90 days, <=4 service minutes each; failures/retries count once",
         "target_original_tier": "Super genuinely not Lily-eligible under P0; Max spillover separate",
         "benefit_mechanism": "lower natural speaking friction near learned course content; keep or renew contribution",
         "commercial_outcomes": "Super path gain less foregone Max upgrades; original Max downgrade separately",
         "costs": "extra offer workload plus changed paid follow-on workload plus incremental fixed allocation",
         "risks": "no real eligibility increment; ineffective practice; displacement; Max substitution",
         "kpi": "candidate weekly effective autonomous expression minutes per originally assigned account; Stage5 to predefine primary",
         "priority": "first verification branch conditional on eligibility; not selected by D ROI",
         "entry_gate": "eligible uncovered subgroup exists; lawful internal trial access and matching baseline later required",
         "stop_rule": "no real increment => stop branch; no natural useful practice or cost exceeds evidence-supported threshold => iterate/stop; missing Max spillover forbids total-policy claim"},
        {"policy_id": "P2", "name": "Limited Lily trial for original Free without existing trial rights",
         "incremental_policy": "D first14days 4 attempts, <=4 service minutes each; expire closed, no auto-charge",
         "target_original_tier": "Free without trial under P0; original Super/Max spillovers separate",
         "benefit_mechanism": "reduce entry barrier; additional effective practice and first paid contribution hypothesis",
         "commercial_outcomes": "first Super path gain less foregone first Max purchase; not original Max downgrade",
         "costs": "trial failures/workload plus post-purchase paid workload, refund/fee contribution and fixed allocation",
         "risks": "too small dose; free substitutes; abuse; paid diversion; immature annual renewal outcome",
         "kpi": "all-assigned net contribution over H with effective practice/learning guardrails; no conversion-only success",
         "priority": "retain conditional thresholds; await task/workload baseline before quota trial; no immediate scale",
         "entry_gate": "verify current free trial exclusion and expiry; useful practice and cost baseline available",
         "stop_rule": "gain cannot meet feasible contribution threshold or learning/cost guardrails fail => stop/iterate; no population weights => no total ranking"},
    )]


def calculate(config):
    validate_config(config)
    results, paths, thresholds, sensitivity = [], [], [], []
    for p in POLICIES:
        for case in SCENARIOS:
            for s in TIERS:
                row = evaluate(config, p, s, case)
                for j, path_id in enumerate(config["tiers"][s]["path_ids"]):
                    paths.append({
                        "policy_id": p, "scenario_id": case, "original_tier": s, "path_id": path_id,
                        "horizon_days": config["horizon_days"], "control_probability_demo": row["q0"][j],
                        "treatment_probability_demo": row["qt"][j], "delta_probability_demo": row["qt"][j] - row["q0"][j],
                        "whole_path_contribution_demo_usd": config["tiers"][s]["contribution_usd_per_path"][j],
                        "non_offer_workload_demo_service_minutes": config["tiers"][s]["non_offer_service_minutes_per_path"][j],
                        "evidence_label": "D_marginal_billing_path", "input_ref": "quant/scenario_inputs.json",
                        "boundary": "Marginal path bins, not identifiable joint counterfactual transitions or observed endpoint ARPU",
                    })
                if p != "P0":
                    thresholds.append(break_even(config, row))
                row.pop("q0")
                row.pop("qt")
                results.append(row)
    for p in ("P1", "P2"):
        s = config["policies"][p]["target_tier"]
        for g in config["sensitivity"][f"{p}_gain_rates"]:
            for loss in config["sensitivity"][f"{p}_loss_rates"]:
                for k in config["sensitivity"]["unit_costs_usd_per_service_minute"]:
                    row = evaluate(config, p, s, "base", gain=g, loss=loss, unit_cost=k)
                    sensitivity.append({key: row[key] for key in (
                        "policy_id", "original_tier", "horizon_days", "gain_rate_demo", "loss_rate_demo",
                        "unit_cost_demo_usd_per_service_minute", "delta_non_ai_contribution_usd",
                        "delta_service_minutes", "delta_ai_and_service_cost_usd", "fixed_cost_per_target_account_demo_usd",
                        "net_contribution_usd_per_account_demo", "net_sign_in_demo", "evidence_label", "input_ref", "boundary")})
    return {"results": results, "paths": paths, "thresholds": thresholds, "sensitivity": sensitivity}


def make_figures(root, config, tables):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    directory = root / "analysis/figures/stage4"
    directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "figure.dpi": 150})
    figures = []
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8), constrained_layout=True)
    for ax, p in zip(axes, ("P1", "P2")):
        tier = config["policies"][p]["target_tier"]
        rows = [r for r in tables["results"] if r["policy_id"] == p and r["original_tier"] == tier]
        x = range(3)
        ax.plot(x, [r["delta_non_ai_contribution_usd"] for r in rows], marker="o", label="Non-AI contribution delta")
        ax.plot(x, [r["delta_ai_and_service_cost_usd"] + r["fixed_cost_per_target_account_demo_usd"] for r in rows], marker="s", label="Service delta + D fixed allocation")
        ax.plot(x, [r["net_contribution_usd_per_account_demo"] for r in rows], marker="^", label="Net delta (D)")
        ax.axhline(0, color="#333", lw=.8)
        ax.set_xticks(list(x), SCENARIOS)
        ax.set_title(f"{p} / original {tier}: D examples only")
        ax.set_xlabel("Response intensity; not scenario probabilities")
        ax.set_ylabel("USD per assigned account / 90 days (D)")
        ax.legend(fontsize=8)
    fig.suptitle("Higher use need not improve net value; tiers are NOT ranked", fontsize=12)
    path = directory / "01_response_intensity.png"
    fig.savefig(path)
    plt.close(fig)
    figures.append(str(path))
    grids = {}
    for p in ("P1", "P2"):
        tier = config["policies"][p]["target_tier"]
        t = config["tiers"][tier]
        g = config["scenarios"]["base"][p][f"{tier}_gain_rate"]
        cap = t["control_probabilities"][t["loss_from"]]
        x = [cap * j / 40 for j in range(41)]
        k = [0.1 * j / 40 for j in range(41)]
        z = [[evaluate(config, p, tier, "base", gain=g, loss=l, unit_cost=price)["net_contribution_usd_per_account_demo"] for l in x] for price in k]
        grids[p] = (tier, g, x, k, z)
    scale = math.ceil(max(abs(v) for _, _, _, _, z in grids.values() for row in z for v in row) * 10) / 10 or .1
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8), constrained_layout=True)
    for ax, p in zip(axes, ("P1", "P2")):
        tier, g, x, k, z = grids[p]
        image = ax.pcolormesh([v * 100 for v in x], k, z, shading="nearest", cmap="RdBu", vmin=-scale, vmax=scale)
        ax.set_xlim(0, x[-1] * 100)
        ax.set_ylim(0, k[-1])
        if min(min(row) for row in z) <= 0 <= max(max(row) for row in z):
            line = ax.contour([v * 100 for v in x], k, z, levels=[0], colors="#202020", linewidths=1.2)
            ax.clabel(line, fmt={0: "break-even"}, fontsize=8)
        ax.set_title(f"{p} / {tier}; gain = {100 * g:.1f} pp (D)")
        ax.set_xlabel("D potential Max-path diversion (percentage points)")
        ax.set_ylabel("D USD / service minute; common arm price")
        fig.colorbar(image, ax=ax, label="Net USD / assigned account / 90 days (D)")
    fig.suptitle("Joint cost / diversion sensitivity: uncalibrated D domain", fontsize=12)
    path = directory / "02_cost_diversion_boundary.png"
    fig.savefig(path)
    plt.close(fig)
    figures.append(str(path))
    return figures


def run(root):
    config_path = root / "quant/scenario_inputs.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    tables = calculate(config)
    mapping = {"results": "scenario_results.csv", "paths": "stage4_billing_paths.csv", "thresholds": "stage4_break_even.csv", "sensitivity": "stage4_sensitivity.csv"}
    hashes = {}
    for key, name in mapping.items():
        path = root / "data/public" / name
        path.write_text(csv_text(tables[key]), encoding="utf-8", newline="")
        hashes[f"data/public/{name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    parameter_path = root / "quant/parameter_register.csv"
    parameter_path.write_text(csv_text(parameter_register(config)), encoding="utf-8", newline="")
    hashes["quant/parameter_register.csv"] = hashlib.sha256(parameter_path.read_bytes()).hexdigest()
    strategy_path = root / "quant/strategy_comparison.csv"
    strategy_path.write_text(csv_text(strategy_comparison()), encoding="utf-8", newline="")
    hashes["quant/strategy_comparison.csv"] = hashlib.sha256(strategy_path.read_bytes()).hexdigest()
    figures = make_figures(root, config, tables)
    return {"config": config, "tables": tables, "figures": figures, "sha256": hashes}
