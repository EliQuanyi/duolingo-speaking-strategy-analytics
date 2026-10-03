"""Execute Stage 3 locally; --check-only performs no file writes."""
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

from analysis.stage3_analysis import InputValidationError, validate_inputs


def build_notebook():
    """Scaffold with nbformat; values and summaries are generated only at execution."""
    import nbformat
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    cells = [
        md("# Duolingo Stage 3: company operating diagnostics\n\n"
           "Global public disclosures, **2024 Q3–2026 Q2**. "
           "Comparison bases: **2023 Q3–2024 Q2**, for YoY and the first main-quarter QoQ. "
           "External company context; no Video Call experiment or causal-effect estimate."),
        md("### Run the validated local analysis\n\n"
           "Execute from the repository root. All sourced inputs must exist. "
           "No network requests. This cell regenerates three derivative CSVs, "
           "five PNGs and a validation JSON. Dependencies: analysis/requirements.txt."),
        code("from pathlib import Path\nimport sys\n"
             "from IPython.display import display, Markdown, HTML, Image\n\n"
             "ROOT = Path.cwd().resolve()\n"
             "if not (ROOT / 'docs/kpi_tree.md').is_file():\n"
             "    raise RuntimeError('Execute with cwd set to the repository root.')\n"
             "if str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))\n"
             "from analysis.stage3_analysis import run_analysis, html_table, summary_markdown, MAIN_QUARTERS\n"
             "result = run_analysis(ROOT)\n"
             "print('Input QA:', result['inputs']['report']['status'], "
             "'| main quarters:', len(MAIN_QUARTERS), '| figures:', len(result['figures']))"),
        md("## tl;dr\n\nThis summary is computed only after input validation."),
        code("display(Markdown(summary_markdown(result)))"),
        md("## Context & Methods\n\n"
           "- DAU is quarterly mean daily users; MAU is quarterly mean monthly users. "
           "Their ratio is an analyst-derived participation-frequency proxy, not retention.\n"
           "- Paid subscriptions are quarter-end paying accounts. Bookings and GAAP "
           "revenue are distinct quarterly flows.\n"
           "- YoY/QoQ use sourced comparable bases. Whole-percent official YoY is "
           "reconciled with current/baseline rounding intervals and half the source's "
           "reported percentage step (0.5 percentage points for whole-percent disclosure); "
           "these bounds are not confidence intervals.\n"
           "- The identity is 100 ln(DAU_t/DAU_base) = 100 ln(MAU_t/MAU_base) "
           "+ 100 ln(ratio_t/ratio_base). Unit: **100 log growth points**, "
           "not percentage-point contributions, causal effects, or growth shares.\n\n"
           "### Key Assumptions\n\n"
           "Definitions and scope must remain comparable. Local checks establish "
           "input consistency, not original-source authenticity. Eight main quarters "
           "cannot identify seasonality or product effects. No regression or "
           "significance tests. Q4 annual-minus-YTD lineage is checked where used. "
           "For M008 no rounding interval is invented: its value is derived from DAU and MAU."),
        md("## Data\n\n"
           "Inputs: company_quarterly_metrics.csv, company_comparison_baselines.csv, "
           "product_timeline.csv, metric_dictionary.csv and source_register.csv. "
           "Hashes and actual checks: analysis/stage3_validation.json. "
           "The table below includes only the eight main quarters."),
        code("lookup = result['inputs']['lookup']\n"
             "company_rows = []\n"
             "for year, quarter in MAIN_QUARTERS:\n"
             "    row = {'quarter': f'{year} Q{quarter}'}\n"
             "    for metric in ('M001', 'M002', 'M004', 'M005', 'M006', 'M007', 'M009'):\n"
             "        row[metric] = f\"{lookup[(year, quarter, metric)]['value']:.3f}\"\n"
             "    row['M008'] = f\"{100 * lookup[(year, quarter, 'M008')]['value']:.2f}\"\n"
             "    company_rows.append(row)\n"
             "display(HTML(html_table(company_rows, [\n"
             "    ('quarter', 'Quarter'), ('M001', 'DAU (m avg)'), ('M002', 'MAU (m avg)'),\n"
             "    ('M004', 'Paid (m end)'), ('M005', 'Sub bookings (USD m)'),\n"
             "    ('M006', 'Total bookings (USD m)'), ('M007', 'Total revenue (USD m)'),\n"
             "    ('M009', 'Sub revenue (USD m)'), ('M008', 'DAU/MAU (%)')],\n"
             "    'Global company values; display digits do not imply extra measurement precision')))\n"),
        md("## Results\n\n### 1. Active scale and frequency\n\n"
           "The quarterly-average ratio is not cohort retention or feature adoption."),
        code("display(Image(filename=result['figures'][0]))"),
        md("### 2. DAU growth decomposition\n\n"
           "MAU and ratio components sum in log-growth units. This identity does not "
           "identify the causes of either component."),
        code("decomposition_rows = [\n"
             "    {key: (f'{value:.3f}' if isinstance(value, float) else value)\n"
             "     for key, value in row.items()}\n"
             "    for row in result['tables']['engagement_decomposition'] if row['comparison'] == 'yoy']\n"
             "display(HTML(html_table(decomposition_rows, [\n"
             "    ('period_end', 'Quarter end'), ('baseline_period_end', 'YoY base'),\n"
             "    ('dau_log_growth_points', 'DAU total'), ('mau_log_component_points', 'MAU component'),\n"
             "    ('ratio_log_component_points', 'Ratio component')],\n"
             "    'Unit: 100 log growth points; not percent growth or causal contributions')))\n"
             "display(Image(filename=result['figures'][1]))"),
        md("### 3. Paid stock and subscription demand\n\n"
           "Stock and flows have different time bases. Conversion, renewal and price/mix "
           "effects are not identified."),
        code("display(Image(filename=result['figures'][2]))"),
        md("### 4. Purchase versus recognition timing\n\n"
           "The descriptive flow gap does not reconcile deferred revenue, profit or cash flow."),
        code("display(Image(filename=result['figures'][3]))"),
        md("### 5. Subscription commercial structure\n\n"
           "Each share uses its respective total-flow denominator."),
        code("commercial_rows = [\n"
             "    {key: (f'{value:.3f}' if isinstance(value, float) else value)\n"
             "     for key, value in row.items()}\n"
             "    for row in result['tables']['commercial_structure']]\n"
             "display(HTML(html_table(commercial_rows, [\n"
             "    ('period_end', 'Quarter end'),\n"
             "    ('subscription_share_of_total_bookings_pct', 'Sub/total bookings (%)'),\n"
             "    ('subscription_share_of_total_revenue_pct', 'Sub/total revenue (%)'),\n"
             "    ('subscription_bookings_to_subscription_revenue_ratio', 'Sub bookings/revenue')],\n"
             "    'Commercial composition; not feature conversion or profit')))\n"
             "display(Image(filename=result['figures'][4]))"),
        md("### Product disclosures, sources and QA\n\n"
           "Events retain actual-date precision, reported dates and management claim "
           "labels. Concurrent business movement is not causality. CURR stays a dated "
           "limited disclosure; it is never filled into an eight-quarter series."),
        code("display(HTML(html_table(result['inputs']['timeline'], [\n"
             "    ('event_id', 'Event'), ('event_date', 'Date'), ('event_date_precision', 'Precision'),\n"
             "    ('event_window_start', 'Window start'), ('event_window_end', 'Window end'),\n"
             "    ('reported_on', 'Reported'), ('feature', 'Feature'), ('tier', 'Tier'),\n"
             "    ('rollout_scope_text', 'Disclosure'), ('claim_type', 'Claim type'),\n"
             "    ('source_id', 'Sources')], 'Sourced disclosures; missing exact dates stay missing')))\n"
             "used_ids = {source_id for row in result['inputs']['quarterly'] + "
             "result['inputs']['baselines'] + result['inputs']['timeline']\n"
             "    for source_id in row['source_id'].split('|')}\n"
             "source_rows = [{'source_id': source_id, 'title': source['title'], 'url': source['url']}\n"
             "    for source_id, source in result['inputs']['sources'].items() if source_id in used_ids]\n"
             "display(HTML(html_table(source_rows, [('source_id', 'ID'), ('title', 'Original source'), "
             "('url', 'URL')], 'Source register links')))\n"
             "qa_rows = [{'check': name, 'status': check['status'], 'evaluations': check['evaluations']}\n"
             "    for name, check in result['inputs']['report']['checks'].items()]\n"
             "display(HTML(html_table(qa_rows, [('check', 'Check'), ('status', 'Status'), "
             "('evaluations', 'Evaluations')], 'Actual local input and identity checks')))\n"),
        md("## Takeaways\n\n"
           "The derivative tables establish company operating context. The companion "
           "business review owns at most three evidence-labelled Driver hypotheses "
           "and alternative explanations. Stage 2 H1/H2 mechanisms and VOC "
           "counterexamples guide future tests and guardrails; self-selected theme "
           "counts do not explain company movements. Stage 4 must label adoption, "
           "incremental retention/conversion, cannibalization and AI cost as unknown "
           "scenario parameters. Stage 5 needs real randomized events.\n\n"
           "**Jupyter rebuild:** python scripts/run_stage3.py --execute\n\n"
           "**Fresh Python process rebuild (no Jupyter kernel):** "
           "python scripts/run_stage3.py --execute-direct\n\n"
           "**Read-only input QA:** python scripts/run_stage3.py --check-only"),
    ]
    for index, cell in enumerate(cells):
        cell.id = f"stage3-{index:02d}"
    notebook = nbformat.v4.new_notebook(cells=cells)
    notebook.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "file_extension": ".py"},
    }
    nbformat.validate(notebook)
    return notebook


def _record_execution(method, status, error=""):
    validation_path = ROOT / "analysis/stage3_validation.json"
    if validation_path.is_file():
        report = json.loads(validation_path.read_text(encoding="utf-8"))
        report["notebook_execution"] = {
            "status": status, "executor": method,
            "python_executable": sys.executable.replace(str(Path.home()), "%USERPROFILE%"),
            "jupyter_kernel": method == "nbclient",
            "fresh_python_process": True,
            "note": ("Real code cells executed in a fresh Python process; "
                     "this is not Jupyter kernel validation." if method != "nbclient"
                     else "Real code cells executed in a fresh Jupyter kernel."),
        }
        if error:
            report["notebook_execution"]["error"] = error
        validation_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")


def _execute_direct_worker():
    """Actually execute normal Python cells, capturing their real rich outputs."""
    import nbformat
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output

    notebook_path = ROOT / "analysis/business_review.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)
    nbformat.validate(notebook)
    InteractiveShell.instance()
    namespace = {"__name__": "__main__", "__file__": str(notebook_path)}
    os.chdir(ROOT)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
            cell.metadata.pop("execution", None)
    method = "fresh_python_process_direct_cells"
    notebook.metadata["execution_method"] = method
    notebook.metadata["execution_note"] = (
        "Real outputs from sequential compile/exec in a fresh Python process. "
        "No Jupyter kernel or ZeroMQ transport was used.")
    execution_count = 0
    for cell_index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        execution_count += 1
        cell.execution_count = execution_count
        error = None
        error_traceback = []
        with capture_output(stdout=True, stderr=True, display=True) as captured:
            try:
                exec(compile(cell.source, f"{notebook_path.name}:cell-{cell_index + 1}", "exec"),
                     namespace)
            except Exception as caught:
                error = caught
                error_traceback = traceback.format_exception(type(caught), caught, caught.__traceback__)
        if captured.stdout:
            cell.outputs.append(nbformat.v4.new_output("stream", name="stdout", text=captured.stdout))
        if captured.stderr:
            cell.outputs.append(nbformat.v4.new_output("stream", name="stderr", text=captured.stderr))
        for rich in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output(
                "display_data", data=rich.data, metadata=rich.metadata))
        if error is not None:
            cell.outputs.append(nbformat.v4.new_output(
                "error", ename=type(error).__name__, evalue=str(error), traceback=error_traceback))
            notebook.metadata["execution_status"] = "failed"
            nbformat.validate(notebook)
            nbformat.write(notebook, notebook_path)
            _record_execution(method, "failed", f"{type(error).__name__}: {error}")
            print(f"Direct execution stopped at code cell {execution_count}: {error}", file=sys.stderr)
            return 1
    notebook.metadata["execution_status"] = "passed"
    nbformat.validate(notebook)
    nbformat.write(notebook, notebook_path)
    _record_execution(method, "passed")
    print(f"Notebook: {execution_count} real code cells executed in a fresh Python process.")
    print("Method: fresh_python_process_direct_cells; no Jupyter kernel validation.")
    print("Outputs: 3 derivative CSVs; 5 PNGs; actual rich Notebook outputs; validation JSON.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-only", action="store_true", help="Validate inputs; write no files.")
    mode.add_argument("--execute", action="store_true", help="Execute fresh kernel and save all derivatives.")
    mode.add_argument("--execute-direct", action="store_true",
                      help="Execute real cells in a fresh Python process; no Jupyter kernel.")
    mode.add_argument("--direct-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        inputs = validate_inputs(ROOT)
        if args.check_only:
            print(json.dumps(inputs["report"], ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.execute_direct:
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            worker = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).resolve()), "--direct-worker"],
                cwd=ROOT, env=environment)
            return worker.returncode
        if args.direct_worker:
            return _execute_direct_worker()
        import nbformat
        preflight = subprocess.run(
            [sys.executable, "-B", "-c",
             "import zmq; c=zmq.Context(); s=c.socket(zmq.PAIR); "
             "s.bind('tcp://127.0.0.1:*'); s.close(); c.term()"],
            capture_output=True, text=True, timeout=20)
        if preflight.returncode:
            details = (preflight.stderr or preflight.stdout).strip()
            raise RuntimeError(
                "The current Python/ZeroMQ runtime cannot create a local kernel "
                f"communication socket (exit {preflight.returncode}). "
                f"No fresh-kernel Notebook execution occurred. {details}")
        # pyzmq's Windows sockets require a selector event loop.
        if sys.platform == "win32":
            import asyncio
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        from nbclient import NotebookClient
        from jupyter_client import KernelManager
        from jupyter_client.kernelspec import KernelSpec, KernelSpecManager

        class CurrentPythonKernelSpecManager(KernelSpecManager):
            def get_kernel_spec(self, kernel_name):
                if kernel_name == "python3":
                    return KernelSpec(
                        argv=[sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                        display_name="Python 3 (current interpreter)", language="python")
                return super().get_kernel_spec(kernel_name)

        notebook_path = ROOT / "analysis/business_review.ipynb"
        if not notebook_path.is_file():
            raise FileNotFoundError(f"Required Notebook is missing: {notebook_path}")
        notebook = nbformat.read(notebook_path, as_version=4)
        nbformat.validate(notebook)
        kernel = KernelManager(kernel_name="python3",
                               kernel_spec_manager=CurrentPythonKernelSpecManager())
        old_pythonpath, old_bytecode = os.environ.get("PYTHONPATH"), os.environ.get("PYTHONDONTWRITEBYTECODE")
        try:
            os.environ["PYTHONPATH"] = str(ROOT) + (os.pathsep + old_pythonpath if old_pythonpath else "")
            os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
            client = NotebookClient(notebook, km=kernel, timeout=180, kernel_name="python3",
                                    resources={"metadata": {"path": str(ROOT)}}, record_timing=False)
            client.execute(cwd=str(ROOT))
        finally:
            if kernel.has_kernel:
                kernel.shutdown_kernel(now=True)
            for key, prior in (("PYTHONPATH", old_pythonpath), ("PYTHONDONTWRITEBYTECODE", old_bytecode)):
                if prior is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = prior
        for cell in notebook.cells:
            cell.metadata.pop("execution", None)
        notebook.metadata["execution_method"] = "nbclient_fresh_jupyter_kernel"
        notebook.metadata["execution_status"] = "passed"
        notebook.metadata["execution_note"] = "Real outputs from fresh-kernel nbclient execution."
        nbformat.validate(notebook)
        nbformat.write(notebook, notebook_path)
        _record_execution("nbclient", "passed")
        print("Stage 3 fresh-kernel Notebook executed and saved.")
        print("Outputs: 3 derivative CSVs; 5 PNGs; analysis/stage3_validation.json")
        return 0
    except InputValidationError as error:
        print(json.dumps(error.report, ensure_ascii=False, indent=2, sort_keys=True))
        return 1
    except (FileNotFoundError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Stage 3 stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
