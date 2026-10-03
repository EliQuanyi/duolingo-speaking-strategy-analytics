"""Run Stage 4 with existing dependencies; direct cells do not validate a Jupyter kernel."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from quant.opportunity_model import validate_config


def build_notebook():
    import nbformat
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    cells = [
        md("# Stage 4 — Conditional opportunity and entitlement economics\n\n"
           "**All economic numbers are D assumptions, not forecasts, real ROI or experimental effects.** "
           "H1: existing individual iOS accounts, Japanese L1 English learners in Japan around course B1.1. "
           "Actual speaking level and account entitlement require separate screening. "
           "H=90 days is a design choice. The three original tiers are reported separately; weights and deployment size are unknown.\n\n"
           "Read [business review](stage4_business_review.md), [assumptions](assumptions.md) and "
           "[policy evidence](policy_evidence.md) before using these results. P0 account rights are unverified. "
           "No published learning score, company growth or VOC proportion calibrates economic inputs."),
        md("## Rebuild and inspect the input contract\n\n"
           "Run from repository root using the existing Stage 3 dependencies. No network, secrets or new packages. "
           "Four derivative CSVs and two plots are generated; scenario_inputs.json is the authoritative D input."),
        code("from pathlib import Path\nimport sys\nfrom IPython.display import display, HTML, Image\n"
             "ROOT = Path.cwd().resolve()\n"
             "if not (ROOT / 'quant/scenario_inputs.json').is_file():\n"
             "    raise RuntimeError('Execute with cwd at repository root')\n"
             "if str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))\n"
             "from quant.opportunity_model import run, table_html\n"
             "result = run(ROOT)\n"
             "print('D conditional model generated:', {k:len(v) for k,v in result['tables'].items()})\n"
             "print('Actual economics: NOT IDENTIFIED. No cross-tier ranking or total forecast.')"),
        md("## Accounting model\n\n"
           "For each originally assigned tier s and policy p: v = delta_m - delta_c - F/N_deployment. "
           "Zero users stay in the denominator. m is H-period net contribution before AI cost, with whole billing paths "
           "and necessary non-AI fees/refunds; c includes offer attempts plus non-offer paid workload. "
           "P0's *relative* effect is zero, while its absolute serving cost may be nonzero.\n\n"
           "Marginal probabilities q0 and qp each sum to one. D gain/loss shifts are a scenario construction, "
           "not observable joint counterfactual transitions. Common path contributions/workloads across arms are explicit D assumptions. "
           "Upgrades and renewals are not added twice; no extra adoption multiplier is applied to full-assignment billing outcomes.\n\n"
           "An illustrative common service-minute rate combines an unknown provider stack; it is not learner speaking time "
           "or actual Duolingo cost. Failed attempts consume workload and no effective minutes. Retries are already attempts. "
           "The normalized 1000 accounts do not determine deployment size, fixed-cost allocation or original-tier weights."),
        code("primary = [r for r in result['tables']['results'] if (r['policy_id'], r['original_tier']) in [('P0','Super'), ('P1','Super'), ('P2','Free')]]\n"
             "display(HTML(table_html(primary, ['policy_id','scenario_id','original_tier','delta_non_ai_contribution_usd',"
             "'delta_ai_and_service_cost_usd','fixed_cost_per_target_account_demo_usd','net_contribution_usd_per_account_demo'])))"),
        md("## D scenarios: response intensity is not economic optimism\n\n"
           "Shared low/reference/high intensity assumptions increase use as well as costs. "
           "Any positive or negative number describes only authored inputs. Different tiers are not ranked."),
        code("display(Image(filename=result['figures'][0]))"),
        md("## Exact conditional thresholds\n\n"
           "If donor-to-gain net marginal contribution G = delta_path_m - k*delta_path_u is positive, "
           "g_min = (loss_rate*L + k*offer_workload + other_delta_cost + f) / G. "
           "L includes serving-cost savings on a lost expensive paid path. Probabilities must remain feasible. "
           "This holds offer workload fixed but recomputes paid workload as the billing gain/loss rate changes. "
           "No effect is estimated. G<=0 changes or removes the inequality direction.\n\n"
           "For common price k and delta_u>0, k_max=(delta_m-other_delta_cost-f)/delta_u. "
           "If delta_u<0 it is a lower-bound condition; if zero there is no price threshold. "
           "All fixed-cost values below are D allocations, not F divided by 1000."),
        code("thresholds = [r for r in result['tables']['thresholds'] if (r['policy_id'],r['original_tier']) in [('P1','Super'),('P2','Free')]]\n"
             "display(HTML(table_html(thresholds, ['policy_id','scenario_id','original_tier','gain_rate_break_even',"
             "'gain_constraint','economically_feasible_gain_exists_in_D_generator','unit_cost_break_even_usd_per_service_minute','unit_cost_constraint'])))"),
        md("## Joint cost / diversion sensitivity\n\n"
           "The black line is the algebraic zero-net boundary in an uncalibrated D domain. "
           "The displayed loss is foregone Max purchase/upgrade in Free/Super, not original-Max downgrade. "
           "360 discrete scans are exported in stage4_sensitivity.csv. The smooth chart grid is presentation-only "
           "and reconstructible from this code, not extra observations, probability mass or confidence intervals."),
        code("display(Image(filename=result['figures'][1]))"),
        md("## Spillovers and omitted total ranking\n\n"
           "Original Max downgrade is modeled separately as a D information/entitlement spillover. "
           "A trial restricted to original Super accounts cannot identify this original Max effect. "
           "No real spillover is currently measured; separate exposure evidence is required. "
           "Other unaffected layers have zero by a D assumption, not an observed null result."),
        code("spillovers = [r for r in result['tables']['results'] if r['policy_id']!='P0' and r['original_tier']!='none' and r['scope']=='hypothetical_spillover_D']\n"
             "display(HTML(table_html(spillovers,['policy_id','scenario_id','original_tier','gain_rate_demo','loss_rate_demo',"
             "'delta_non_ai_contribution_usd','delta_ai_and_service_cost_usd','net_contribution_usd_per_account_demo'])))"),
        md("## Decision handoff\n\n"
           "Market evidence supports H1 as the priority learning task; public business data makes substitution/cost material, "
           "not identified. The model defines break-even conditions and required data. **No unconditional P1/P2 winner.** "
           "Stage 5 should first qualify a genuine incremental offer and measure natural effective practice, all-assigned "
           "billing contribution and serving workload, while tracking independent unpracticed learning tasks and course "
           "displacement. A per-Super test leaves Max spillover and total policy value unresolved. "
           "No sample-size claim is made without a matching baseline/variance.\n\n"
           "Fresh-process execution: `python -B scripts/run_stage4.py --execute-direct`. "
           "Independent numerical verification: `python -B scripts/verify_stage4.py`. "
           "Direct sequential code execution with captured real outputs is not standard Jupyter kernel validation."),
    ]
    for i, cell in enumerate(cells):
        cell.id = f"stage4-{i:02d}"
    notebook = nbformat.v4.new_notebook(cells=cells)
    notebook.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                         "language_info": {"name": "python", "file_extension": ".py"}}
    nbformat.validate(notebook)
    return notebook


def execute_worker():
    import nbformat
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    path = ROOT / "quant/opportunity_model.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    InteractiveShell.instance()
    os.chdir(ROOT)
    namespace = {"__name__": "__main__"}
    execution_count = 0
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        execution_count += 1
        cell.execution_count, cell.outputs = execution_count, []
        error = None
        with capture_output(stdout=True, stderr=True, display=True) as output:
            try:
                exec(compile(cell.source, f"{path.name}:cell{execution_count}", "exec"), namespace)
            except Exception as caught:
                error = caught
                trace = traceback.format_exc()
        for name in ("stdout", "stderr"):
            value = getattr(output, name)
            if value:
                cell.outputs.append(nbformat.v4.new_output("stream", name=name, text=value))
        for rich in output.outputs:
            cell.outputs.append(nbformat.v4.new_output("display_data", data=rich.data, metadata=rich.metadata))
        if error:
            cell.outputs.append(nbformat.v4.new_output("error", ename=type(error).__name__, evalue=str(error), traceback=trace.splitlines()))
            notebook.metadata["execution_status"] = "failed"
            nbformat.write(notebook, path)
            raise RuntimeError(f"Notebook code cell {execution_count}: {error}")
    notebook.metadata.update({"execution_method": "fresh_python_process_direct_cells", "execution_status": "passed",
                              "execution_note": "Real sequential code outputs; no standard Jupyter/ZeroMQ validation"})
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    print(json.dumps({"status": "passed", "fresh_python_process": True, "code_cells": execution_count,
                      "executor": "direct_cells", "standard_kernel": "not_validated", "economic_effect": "not_identified"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check-only", action="store_true")
    modes.add_argument("--execute-direct", action="store_true")
    modes.add_argument("--direct-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.check_only and (ROOT / "quant/evidence_inputs.json").exists():
        raise RuntimeError("Stage4 v1 D build is retired and would overwrite the current strategy comparison. Use scripts/run_stage4_final.py --execute-direct for v2; preserved v1 files are historical audit only.")
    config = json.loads((ROOT / "quant/scenario_inputs.json").read_text(encoding="utf-8"))
    validate_config(config)
    if args.check_only:
        print(json.dumps({"status": "passed", "scope": "D input contract only; no files written"}))
    elif args.direct_worker:
        execute_worker()
    else:
        import nbformat
        path = ROOT / "quant/opportunity_model.ipynb"
        if not path.exists():
            nbformat.write(build_notebook(), path)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        worker = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--direct-worker"], cwd=ROOT, env=environment)
        return worker.returncode
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        print(f"Stage 4 stopped: {error}", file=sys.stderr)
        raise SystemExit(1)
