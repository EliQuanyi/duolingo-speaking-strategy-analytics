"""Read-only independent checks of Stage 4 v2 evidence-constrained outputs.

All artificial economic numbers below are software-test fixtures only. They
never enter business CSVs, the Notebook, or empirical/economic conclusions.
This command neither rebuilds artifacts nor executes Notebook cells.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import csv
import hashlib
import importlib.util
import io
import json
import runpy
import sys
from decimal import Decimal, localcontext
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
D = Decimal
MEANS = ("mean_contribution_t", "mean_contribution_c", "mean_serving_cost_t", "mean_serving_cost_c")
CONTRACT = ("all_originally_assigned_including_zero_users", "comparable_population_and_period",
            "net_contribution_excludes_ai_and_includes_refunds_non_ai_fees",
            "serving_cost_includes_control_failures_and_paid_follow_on", "assignment_identification_verified")
OUTPUTS = ("data/public/stage4_economic_readiness.csv", "data/public/stage4_policy_readiness.csv",
           "data/public/stage4_symbolic_sensitivity.csv", "data/public/stage4_learning_coverage.csv")
LEGACY_NAMES = {"scenario_inputs.json", "opportunity_model.py", "opportunity_model.ipynb",
                "scenario_results.csv", "stage4_billing_paths.csv", "stage4_break_even.csv",
                "stage4_sensitivity.csv", "run_stage4.py"}
SYMBOLS = {
    "m_T": "d(v_variable)/d(m_T)=+1",
    "m_C": "d(v_variable)/d(m_C)=-1",
    "c_T": "d(v_variable)/d(c_T)=-1",
    "c_C": "d(v_variable)/d(c_C)=+1",
    "fixed_cost": "V=sum_s(N_s*delta_v_s)-F; dV/dF=-1",
    "break_even": "delta_m >= delta_c + F/N",
    "quota": "offer_workload <= attempt_cap*enforced_workload_cap",
    "learning_budget": "delta_cost_total <= approved_incremental_learning_budget",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_model():
    spec = importlib.util.spec_from_file_location("stage4_evidence_under_test", ROOT / "quant/evidence_model.py")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def verify_unknown_artifacts(config):
    require(config["version"] == "stage4-v2.0", "Wrong final evidence version")
    for name in ("period_start", "period_end", "currency"):
        require(config[name] is None, f"Unverified {name} was silently fixed")
    require(set(config["contract"]) == set(CONTRACT)
            and all(value is None for value in config["contract"].values()), "Unknown accounting contract filled")
    groups = {}
    for p, policy in config["policies"].items():
        require(p in ("P1", "P2"), "Unexpected policy")
        require(policy["increment_verified"] is None and policy["fixed_incremental_cost_total"] is None,
                "Unknown rights/fixed cost converted into a decision input")
        require(policy["deployment_effect_scope_matched"] is None,
                "Policy exposure/deployment extrapolation falsely verified")
        for group in policy["groups"]:
            require(all(group[name] is None for name in MEANS + ("assignment_n_t", "assignment_n_c", "deployment_n")),
                    "Real economic parameter is no longer unknown; manual evidence review required")
            require(group.get("measurement_basis") is None and not group["economic_source_refs"],
                    "Unknown measurement falsely declared")
            groups[p, group["original_tier"]] = group
    require(set(groups) == {(p, s) for p in ("P1", "P2") for s in ("Free", "Super", "Max")},
            "Six original-policy/tier groups required")
    exported = rows(OUTPUTS[0])
    require(len(exported) == 6 and len({(r["policy_id"], r["original_tier"]) for r in exported}) == 6,
            "Economic readiness key/row count mismatch")
    needed = {f"contract.{name}" for name in CONTRACT}
    needed.update(MEANS + ("assignment_n_t", "assignment_n_c", "period_start", "period_end", "currency",
                           "actual_policy_increment", "economic_source_refs"))
    for row in exported:
        group = groups[row["policy_id"], row["original_tier"]]
        require(row["effect_scope"] == group["effect_scope"] and row["population_id"] == config["population_id"],
                "Effect/population scope differs from input")
        for field in ("delta_contribution", "delta_serving_cost", "delta_variable_value", "deployment_n",
                      "period_start", "period_end", "currency"):
            require(row[field] == "", f"Unknown {field} published as a number/value")
        require(row["economic_status"] == "unknown" and row["evidence_status"] == "unknown_not_zero",
                "Unknown economic effects labeled as observed zeros")
        require(needed <= set(row["missing_inputs"].split(" | ")), "Consequential missing fields omitted")
        if row["original_tier"] == "Max":
            require("separate_identification" in row["effect_scope"], "Max spillover treated as measured direct effect")
    policies = rows(OUTPUTS[1])
    require(len(policies) == 2 and {r["policy_id"] for r in policies} == {"P1", "P2"}, "Policy readiness keys differ")
    for row in policies:
        require(row["total_incremental_value"] == "" and row["currency"] == "", "Missing evidence produced total value")
        require(row["deployment_effect_scope_matched"] == "", "Unknown exposure/deployment match published as verified")
        require(row["overall_economic_status"] == "not_identified" and row["actual_increment_status"] == "not_verified",
                "Unverified policy assigned a economic/Scale result")
    return {"economic_groups": 6, "policy_rows": 2, "all_economic_outputs": "unknown_not_zero",
            "source_audit_boundary": "Declarations and software checks are not independent source authentication"}


def verify_symbolic_artifacts():
    symbolic = rows(OUTPUTS[2])
    require(len(symbolic) == 8 and len({r["parameter"] for r in symbolic}) == 8, "Eight unique symbolic relations required")
    for row in symbolic:
        require(row["parameter"] in SYMBOLS and row["expression"] == SYMBOLS[row["parameter"]], "Symbolic formula changed")
        require(row["condition"] and row["empirical_status"], "Symbolic relation missing applicability boundary")
        require(row["empirical_status"] not in ("measured", "A_official", "empirical_result"), "Identity passed as measured response")
    quota = next(row for row in symbolic if row["parameter"] == "quota")
    require("excludes paid follow-on" in quota["condition"], "Offer quota presented as total serving-cost bound")
    budget = next(row for row in symbolic if row["parameter"] == "learning_budget")
    require("do not monetize test-score points" in budget["condition"], "Learning scores monetized without identification")
    return {"symbolic_relations": 8, "numeric_economic_thresholds_or_domains": "none"}


def verify_learning_coverage():
    observed = rows("data/public/stage4_public_observations.csv")
    ids = {row["observation_id"] for row in observed}
    require(len(ids) == len(observed), "Duplicate observation ID")
    required_fields = {"randomized_Video_Call_n", "randomized_Control_n", "analysed_Video_Call_n", "analysed_Control_n"}
    relevant = [row for row in observed if row["field"] in required_fields]
    require(len(relevant) == 4 and {row["field"] for row in relevant} == required_fields,
            "Study count fields are duplicated or missing")
    require({row["unit"] for row in relevant} == {"persons"}
            and len({row["source_url"] for row in relevant}) == 1
            and len({row["coverage_period"] for row in relevant}) == 1,
            "All four study count observations must share source, window and person unit")
    lookup = {row["field"]: row for row in relevant}
    derived = rows(OUTPUTS[3])
    require(len(derived) == 2 and {row["arm"] for row in derived} == {"video_call", "control"}, "Study coverage arms differ")
    for row in derived:
        label = "Video_Call" if row["arm"] == "video_call" else "Control"
        assigned, analysed = lookup[f"randomized_{label}_n"], lookup[f"analysed_{label}_n"]
        n, a = D(assigned["value"]), D(analysed["value"])
        require(n == 329 and D(0) <= a <= n and a == a.to_integral_value(), "Original randomization denominator invalid")
        require(assigned["unit"] == analysed["unit"] == "persons", "Count units are not persons")
        require(assigned["source_url"] == analysed["source_url"]
                and assigned["coverage_period"] == analysed["coverage_period"], "Study count source/window mismatch")
        excluded = n - a
        percent = (excluded * D(100) / n).quantize(D(".1"))
        for field, expected in (("assigned_n", n), ("analysed_n", a), ("not_in_analysis_n", excluded),
                                ("not_in_analysis_percent", percent)):
            require(D(row[field]) == expected, f"Independent study coverage calculation differs: {row['arm']}/{field}")
        require(row["input_observation_ids"] == assigned["observation_id"] + "|" + analysed["observation_id"],
                "Study count lineage mismatch")
        for field, expected in (("source_url", assigned["source_url"]),
                                ("published_on", assigned["source_publication_date"]),
                                ("accessed_on", assigned["access_date"]), ("window", assigned["coverage_period"])):
            require(row[field] == expected, "Study source metadata missing/mismatched")
        require("not all attrition" in row["interpretation"] and "no natural adoption rate" in row["interpretation"]
                and "full ITT" in row["interpretation"] and "commercial uplift" in row["interpretation"], "Selection boundary omitted")
    for row in observed:
        if row["observation_id"].startswith("P"):
            require(row["comparability_status"] != "comparable", "Unresolved price rows declared comparable")
    return {"independently_recomputed_rows": 2, "assigned_denominator_each_arm": 329,
            "computed_quantity": "not included in analysis; not natural adoption, full ITT or economic uplift",
            "limitation": "Recomputes registered source inputs; does not re-open or certify original webpages"}


def fixture_config(config):
    """Artificial software fixture only, never a permissible business input."""
    test = copy.deepcopy(config)
    test.update(population_id="FIXTURE_ONLY_NOT_ECONOMIC_EVIDENCE", period_start="2099-01-01",
                period_end="2099-03-31", currency="USD")
    test["contract"] = {name: True for name in CONTRACT}
    samples = {"Free": (11, 7, 3, 2, 10), "Super": (4, 5, 1, 3, 20), "Max": (6, 8, 4, 2, 30)}
    for p, policy in test["policies"].items():
        policy.update(increment_verified=True, deployment_effect_scope_matched=True,
                      fixed_incremental_cost_total=13 if p == "P1" else 17,
                      fixed_cost_source_ref="FIXTURE_ONLY_NOT_ECONOMIC_EVIDENCE")
        for group in policy["groups"]:
            mt, mc, ct, cc, n = samples[group["original_tier"]]
            group.update(dict(zip(MEANS, (mt, mc, ct, cc))))
            group.update(assignment_n_t=3, assignment_n_c=4, deployment_n=n,
                         measurement_basis="invoice_contribution_and_metered_serving_cost",
                         economic_source_refs=["FIXTURE_ONLY_NOT_ECONOMIC_EVIDENCE"],
                         deployment_source_ref="FIXTURE_ONLY_NOT_ECONOMIC_EVIDENCE")
    return test


def verify_arithmetic(model, config):
    cases = [
        ("unequal arm means", ("10.75", "7.25", "2.20", "1.10")),
        ("cost savings and negative contribution", ("-2", "-3", "1", "4")),
        ("observed zero", (0, 0, 0, 0)),
        ("all unknown", (None, None, None, None)),
        ("missing treatment contribution", (None, 4, 2, 1)),
        ("missing control contribution", (4, None, 2, 1)),
        ("missing treatment cost", (4, 3, None, 1)),
        ("missing control cost", (4, 3, 1, None)),
    ]
    for label, values in cases:
        mt, mc, ct, cc = [None if v is None else D(str(v)) for v in values]
        dm = None if mt is None or mc is None else mt - mc
        dc = None if ct is None or cc is None else ct - cc
        expected = {"delta_contribution": dm, "delta_serving_cost": dc,
                    "delta_variable_value": None if dm is None or dc is None else dm - dc}
        require(model.contrast(*values) == expected, f"Independent dual-arm arithmetic differs: {label}")
    for dc, f, n in (("-2", "6", "3"), ("2.5", "5", "4"), (0, 0, 1),
                     (None, 0, 1), (0, None, 1), (0, 0, None)):
        expected = None if any(v is None for v in (dc, f, n)) else D(str(dc)) + D(str(f)) / D(str(n))
        require(model.per_account_threshold(dc, f, n) == expected, "Independent fixed-cost/deployment threshold differs")
    artificial = fixture_config(config)
    group_rows, policy_rows, _ = model.build_outputs(artificial)
    for row in group_rows:
        group = next(g for g in artificial["policies"][row["policy_id"]]["groups"] if g["original_tier"] == row["original_tier"])
        expected = (D(group[MEANS[0]]) - D(group[MEANS[1]])) - (D(group[MEANS[2]]) - D(group[MEANS[3]]))
        require(row["delta_variable_value"] == expected, "Full-assignment mean contrast altered by counts/adoption")
    for row in policy_rows:
        policy = artificial["policies"][row["policy_id"]]
        expected = sum((D(g["deployment_n"]) * ((D(g[MEANS[0]]) - D(g[MEANS[1]]))
                                               - (D(g[MEANS[2]]) - D(g[MEANS[3]]))) for g in policy["groups"]), D(0))
        expected -= D(policy["fixed_incremental_cost_total"])
        require(row["total_incremental_value"] == expected, "Policy total must include all original tiers and deduct F once")
        require(row["overall_economic_status"] == "accounting_total_not_automatic_scale", "Arithmetic total automatically approved Scale")
    for field in MEANS + ("deployment_n",):
        partial = copy.deepcopy(artificial)
        partial["policies"]["P1"]["groups"][2][field] = None
        _, policies, _ = model.build_outputs(partial)
        require(next(r for r in policies if r["policy_id"] == "P1")["total_incremental_value"] is None,
                f"Missing original Max {field} silently treated as zero")
    unverified = copy.deepcopy(artificial)
    unverified["policies"]["P1"]["increment_verified"] = False
    require(model.build_outputs(unverified)[1][0]["total_incremental_value"] is None, "No real policy increment but total published")
    for scope_flag in (None, False):
        unmatched = copy.deepcopy(artificial)
        unmatched["policies"]["P1"]["deployment_effect_scope_matched"] = scope_flag
        require(model.build_outputs(unmatched)[1][0]["total_incremental_value"] is None,
                "Unverified or unmatched deployment exposure allowed a policy total")
    zeros = copy.deepcopy(artificial)
    for policy in zeros["policies"].values():
        policy["fixed_incremental_cost_total"] = 0
        for group in policy["groups"]:
            group.update({field: 0 for field in MEANS})
    zero_rows, zero_policies, _ = model.build_outputs(zeros)
    require(all(row["delta_variable_value"] == 0 for row in zero_rows)
            and all(row["total_incremental_value"] == 0 for row in zero_policies), "Provenanced observed zero rejected or replaced by unknown")
    return {"independent_contrast_cases": len(cases), "independent_threshold_cases": 6,
            "whole_policy_weighted_sum_and_single_F_deduction": "passed", "missing_Max_terms_block_total": "passed",
            "unknown_or_unmatched_deployment_scope_blocks_total": "passed",
            "observed_zero_vs_unknown": "passed", "fixture_status": "source-code-only artificial tests; no economic evidence or exported scenarios"}


def verify_bad_inputs(model, config):
    cases = []
    def rejected(label, operation):
        try:
            operation()
        except (ValueError, TypeError):
            cases.append(label)
            return
        raise AssertionError(f"Bad input accepted: {label}")
    def mutated(label, mutation):
        test = fixture_config(config)
        mutation(test)
        rejected(label, lambda: model.validate(test))
    for field in ("assignment_n_t", "assignment_n_c", "deployment_n"):
        for bad in (0, -1, .5, True):
            mutated(f"{field} invalid domain {bad!r}", lambda c, field=field, bad=bad: c["policies"]["P1"]["groups"][0].__setitem__(field, bad))
    for bad in (0, -1, .5, True):
        rejected(f"threshold deployment domain {bad!r}", lambda bad=bad: model.per_account_threshold(None, None, bad))
    for bad in (-1, True, "NaN", "Infinity"):
        rejected(f"absolute arm cost domain {bad!r}", lambda bad=bad: model.contrast(1, 1, bad, 0))
    for bad in (True, "NaN", "Infinity"):
        rejected(f"contribution domain {bad!r}", lambda bad=bad: model.contrast(bad, 1, 0, 0))
    for bad in (-1, True, "NaN"):
        rejected(f"fixed expense domain {bad!r}", lambda bad=bad: model.per_account_threshold(0, bad, 1))
    for bad in (0, 1, "true"):
        mutated(f"numeric/string contract boolean {bad!r}", lambda c, bad=bad: c["contract"].__setitem__(CONTRACT[0], bad))
        mutated(f"numeric/string increment boolean {bad!r}", lambda c, bad=bad: c["policies"]["P1"].__setitem__("increment_verified", bad))
        mutated(f"numeric/string deployment scope boolean {bad!r}", lambda c, bad=bad: c["policies"]["P1"].__setitem__("deployment_effect_scope_matched", bad))
    for name in CONTRACT:
        mutated(f"numeric output without contract {name}", lambda c, name=name: c["contract"].__setitem__(name, None))
    for basis in (None, "quoted_plan_price", "company_aggregate", "selected_completer_score"):
        mutated(f"invalid economic measurement basis {basis!r}", lambda c, basis=basis: c["policies"]["P1"]["groups"][0].__setitem__("measurement_basis", basis))
    mutated("missing economic source declaration", lambda c: c["policies"]["P1"]["groups"][0].__setitem__("economic_source_refs", []))
    mutated("missing fixed expense provenance including zero", lambda c: c["policies"]["P1"].update(fixed_incremental_cost_total=0, fixed_cost_source_ref=None))
    mutated("deployment without source declaration", lambda c: c["policies"]["P1"]["groups"][0].__setitem__("deployment_source_ref", None))
    mutated("wrong currency shape", lambda c: c.__setitem__("currency", "JPY/month"))
    mutated("missing common currency with numeric means", lambda c: c.__setitem__("currency", None))
    mutated("period reversed", lambda c: c.__setitem__("period_end", "2098-01-01"))
    mutated("invalid calendar date", lambda c: c.__setitem__("period_start", "2099-02-30"))
    mutated("duplicate original tier", lambda c: c["policies"]["P1"]["groups"][0].__setitem__("original_tier", "Max"))
    observed = rows("data/public/stage4_public_observations.csv")
    for bad in (0, -1, .5, True):
        altered = copy.deepcopy(observed)
        next(row for row in altered if row["field"] == "randomized_Video_Call_n")["value"] = bad
        rejected(f"study assigned denominator invalid {bad!r}", lambda altered=altered: model.learning_coverage(altered))
    altered = copy.deepcopy(observed)
    next(row for row in altered if row["field"] == "analysed_Video_Call_n")["value"] = 330
    rejected("study analysed count exceeds assigned denominator", lambda: model.learning_coverage(altered))
    duplicate = copy.deepcopy(observed)
    duplicate.append(copy.deepcopy(next(row for row in duplicate if row["field"] == "randomized_Video_Call_n")))
    rejected("duplicate study count field cannot be silently overwritten", lambda: model.learning_coverage(duplicate))
    for field, bad, label in (("unit", "accounts", "wrong study count unit"),
                              ("coverage_period", "DIFFERENT_TEST_WINDOW", "mismatched study window"),
                              ("source_url", "https://fixture.invalid/other-study", "mismatched study source")):
        altered = copy.deepcopy(observed)
        next(row for row in altered if row["field"] == "analysed_Video_Call_n")[field] = bad
        rejected(label, lambda altered=altered: model.learning_coverage(altered))
    return {"invalid_cases_rejected": len(cases), "cases": cases,
            "source_verification_limit": "Rejects invalid declarations/bases; source authenticity and causality still require manual review"}


def verify_generation_isolation(model):
    reads = set()
    original_text, original_bytes, original_open = Path.read_text, Path.read_bytes, Path.open
    def allow_read(path):
        absolute = Path(path).resolve()
        require(absolute.name not in LEGACY_NAMES and "figures/stage4" not in absolute.as_posix(),
                f"Final generation attempted to read a legacy D artifact: {absolute.name}")
        reads.add(str(absolute))
    def guarded_text(path, *args, **kwargs):
        allow_read(path)
        return original_text(path, *args, **kwargs)
    def guarded_bytes(path, *args, **kwargs):
        allow_read(path)
        return original_bytes(path, *args, **kwargs)
    def guarded_open(path, mode="r", *args, **kwargs):
        require(not any(token in mode for token in ("w", "a", "x", "+")), "Read-only generator tried to write via Path.open")
        allow_read(path)
        return original_open(path, mode, *args, **kwargs)
    def forbidden_write(*args, **kwargs):
        raise AssertionError("Read-only generation attempted to write an artifact")
    original_builtin_open = builtins.open
    def guarded_builtin_open(path, mode="r", *args, **kwargs):
        require(not any(token in mode for token in ("w", "a", "x", "+")), "Read-only generator tried to write via open")
        if isinstance(path, (str, Path)):
            allow_read(path)
        return original_builtin_open(path, mode, *args, **kwargs)
    for name in ("quant/evidence_model.py", "scripts/run_stage4_final.py"):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            require(not any("opportunity_model" in module or module.endswith("run_stage4") for module in modules),
                    f"Legacy D code imported by {name}")
    captured = io.StringIO()
    with patch.object(Path, "read_text", guarded_text), patch.object(Path, "read_bytes", guarded_bytes), \
            patch.object(Path, "open", guarded_open), patch.object(Path, "write_text", forbidden_write), \
            patch.object(Path, "write_bytes", forbidden_write), patch("builtins.open", guarded_builtin_open), \
            patch.dict(sys.modules, {"evidence_model": model}), \
            patch.object(sys, "argv", ["run_stage4_final.py", "--check-only"]), contextlib.redirect_stdout(captured):
        model.generated_texts(model.load_config())
        runpy.run_path(str(ROOT / "scripts/run_stage4_final.py"), run_name="__main__")
    result = json.loads(captured.getvalue())
    require(result["mode"] == "check_only_no_writes" and result["numeric_scenarios_generated"] is False,
            "Final runner entered a numeric generation/write mode")
    require(set(result["generated_files"]) == set(OUTPUTS), "Unexpected final derivative output set")
    for relative, expected_hash in result["sha256"].items():
        require(sha(ROOT / relative) == expected_hash, "Runner hash does not match actual artifact")
    relevant_reads = sorted(Path(path).relative_to(ROOT).as_posix() for path in reads if Path(path).is_relative_to(ROOT))
    return {"check_only_runner": "executed under legacy-read and write guards", "read_paths": relevant_reads,
            "legacy_D_reads": 0, "writes": 0, "limitation": "Guards actual Path/builtin reads and statically checks imports on current generation path"}


def verify_notebook(config):
    notebook = json.loads((ROOT / "quant/evidence_model.ipynb").read_text(encoding="utf-8"))
    require(notebook["metadata"].get("execution_method") == "fresh_python_process_direct_compile_exec_not_jupyter_kernel",
            "Final Notebook direct-method metadata missing")
    cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    require(len(cells) == 3 and [cell["execution_count"] for cell in cells] == [1, 2, 3], "Three actual executed code cells required")
    outputs = []
    for cell in cells:
        require(cell["outputs"] and all(output["output_type"] == "stream" and output["name"] == "stdout" for output in cell["outputs"]),
                "Actual stdout absent or Notebook has error outputs")
        for legacy in LEGACY_NAMES:
            source = cell["source"]
            require(legacy not in ("".join(source) if isinstance(source, list) else source), "Final Notebook loads legacy D code/data")
        text = ""
        for output in cell["outputs"]:
            value = output["text"]
            text += "".join(value) if isinstance(value, list) else value
        outputs.append(text)
    expected_first = f"version: {config['version']}\nperiod: None None currency: None\nNo authored economic estimates are loaded.\n"
    require(outputs[0] == expected_first, "Notebook context output stale or missing-data filled")
    expected_second = ""
    for row in rows(OUTPUTS[0]):
        expected_second += f"{row['policy_id']} {row['original_tier']} delta_value= None status= unknown\nmissing: {row['missing_inputs']}\n"
    require(outputs[1] == expected_second, "Notebook group readiness differs from current CSV")
    expected_third = ""
    for row in rows(OUTPUTS[1]):
        expected_third += f"{row['policy_id']} total= None {row['overall_economic_status']}\n{row['condition']}\n"
    for row in rows(OUTPUTS[2]):
        expected_third += f"{row['parameter']} {row['expression']} | {row['empirical_status']}\n"
    require(outputs[2] == expected_third, "Notebook policy/symbolic readiness differs from current CSV")
    return {"actual_saved_code_outputs": 3, "stdout_matches_current_artifacts": True,
            "standard_jupyter_kernel": "not validated",
            "limitation": "Matches saved actual outputs and method declarations; does not independently re-execute Notebook or authenticate process freshness from metadata alone"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Read-only validation; also the default.")
    parser.parse_args()
    paths = [ROOT / name for name in OUTPUTS + ("quant/evidence_inputs.json", "quant/evidence_model.py",
                                              "quant/evidence_model.ipynb", "data/public/stage4_public_observations.csv",
                                              "scripts/run_stage4_final.py")]
    before = {str(path): sha(path) for path in paths if path.is_file()}
    checks = {}
    def check(name, operation):
        try:
            checks[name] = {"status": "passed", **operation()}
        except Exception as error:
            checks[name] = {"status": "failed", "error": f"{type(error).__name__}: {error}"}
    try:
        config = json.loads((ROOT / "quant/evidence_inputs.json").read_text(encoding="utf-8"))
        model = load_model()
    except Exception as error:
        print(json.dumps({"status": "failed", "writes": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    with localcontext() as context:
        context.prec = 50
        check("unknown_economic_parameters_and_outputs", lambda: verify_unknown_artifacts(config))
        check("independent_symbolic_relations", verify_symbolic_artifacts)
        check("independent_registered_learning_counts", verify_learning_coverage)
        check("independent_arithmetic_fixtures", lambda: verify_arithmetic(model, config))
        check("invalid_inputs_and_basis_gates", lambda: verify_bad_inputs(model, config))
        check("final_generation_isolated_from_D", lambda: verify_generation_isolation(model))
        check("saved_actual_direct_Notebook_outputs", lambda: verify_notebook(config))
    after = {str(path): sha(path) for path in paths if path.is_file()}
    check("read_only_artifact_hashes", lambda: (require(before == after, "Existing artifacts changed during read-only verification")
                                               or {"unchanged_artifacts": len(before)}))
    passed = all(result["status"] == "passed" for result in checks.values())
    print(json.dumps({"status": "passed" if passed else "failed", "writes": False,
                      "checks": checks, "fixture_evidence": "software tests only; no artificial economics exported",
                      "not_validated": ["original webpage authenticity", "real account entitlements", "causal business or natural-use effects",
                                        "actual unit costs", "policy winner or scale readiness", "standard Jupyter kernel"]},
                     ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
