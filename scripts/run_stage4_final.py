"""Build/check only Stage4 v2 evidence outputs; never read the v1 D configuration."""
import argparse
import contextlib
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "quant"))
from evidence_model import generated_texts, load_config, learning_coverage, csv_text


def execute_notebook(path):
    import nbformat
    if not path.exists():
        nb = nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell("# Stage4 v2｜证据约束的量化交接\n\n经济参数全部未知；本 Notebook 展示实际缺口和符号敏感度，不生成模拟收益。direct执行不是标准Jupyter kernel验收。"),
            nbformat.v4.new_code_cell("import sys, json\nfrom pathlib import Path\nroot = Path.cwd()\nif not (root / 'quant/evidence_inputs.json').exists():\n    root = root.parent\nsys.path.insert(0, str(root / 'quant'))\nfrom evidence_model import load_config, build_outputs\nconfig = load_config()\ngroups, policies, sensitivities = build_outputs(config)\nprint('version:', config['version'])\nprint('period:', config['period_start'], config['period_end'], 'currency:', config['currency'])\nprint('No authored economic estimates are loaded.')"),
            nbformat.v4.new_code_cell("for row in groups:\n    print(row['policy_id'], row['original_tier'], 'delta_value=', row['delta_variable_value'], 'status=', row['economic_status'])\n    print('missing:', row['missing_inputs'])"),
            nbformat.v4.new_code_cell("for row in policies:\n    print(row['policy_id'], 'total=', row['total_incremental_value'], row['overall_economic_status'])\n    print(row['condition'])\nfor row in sensitivities:\n    print(row['parameter'], row['expression'], '|', row['empirical_status'])"),
        ], metadata={"execution_method": "fresh_python_process_direct_compile_exec_not_jupyter_kernel", "stage4_version": "v2.0", "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
    else:
        nb = nbformat.read(path, as_version=4)
    namespace = {"__name__": "__main__"}
    count = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        count += 1
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            exec(compile(cell.source, f"{path.name}:cell{count}", "exec"), namespace)
        cell.execution_count = count
        cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text=captured.getvalue())]
    nbformat.validate(nb)
    nbformat.write(nb, path)
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute-direct", action="store_true")
    args = parser.parse_args()
    if args.check_only and args.execute_direct:
        parser.error("check-only cannot execute or write")
    outputs = generated_texts(load_config())
    with (ROOT / "data/public/stage4_public_observations.csv").open(encoding="utf-8-sig", newline="") as handle:
        outputs["data/public/stage4_learning_coverage.csv"] = csv_text(learning_coverage(list(csv.DictReader(handle))))
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check_only:
            if not path.exists() or path.read_bytes() != content.encode("utf-8"):
                raise ValueError(f"Generated output differs: {relative}")
        else:
            path.write_bytes(content.encode("utf-8"))
    count = execute_notebook(ROOT / "quant/evidence_model.ipynb") if args.execute_direct else None
    print(json.dumps({"version": "stage4-v2.0", "mode": "check_only_no_writes" if args.check_only else "build",
                      "generated_files": list(outputs), "direct_code_cells_executed": count,
                      "economic_status": "not_identified", "numeric_scenarios_generated": False,
                      "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in outputs}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
