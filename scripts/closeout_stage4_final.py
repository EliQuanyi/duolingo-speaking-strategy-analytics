"""Record/recheck the scoped Stage4 v2 handoff; never collect data or build it."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "quant/stage4_final_validation.json"
TABLES = {
    "data/public/stage4_public_observations.csv": (28, "observation_id"),
    "data/public/stage4_learning_coverage.csv": (2, "arm"),
    "data/public/stage4_economic_readiness.csv": (6, None),
    "data/public/stage4_policy_readiness.csv": (2, "policy_id"),
    "data/public/stage4_symbolic_sensitivity.csv": (8, "parameter"),
    "quant/stage4_claim_ledger.csv": (16, "claim_id"),
    "quant/stage4_gap_register.csv": (10, "gap_id"),
    "quant/strategy_comparison.csv": (3, "policy_id"),
}
DOCS = ("quant/stage4_final_delivery.md", "quant/evidence_assumptions.md", "quant/stage4_public_evidence_v2.md", "quant/README.md")


def read_rows(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f"Malformed CSV: {relative}")
        return rows


def run_check(arguments):
    result = subprocess.run([sys.executable, "-B", *arguments], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def review():
    # These scripts check current outputs and arithmetic; no writes or new data.
    generated = run_check(["scripts/run_stage4_final.py", "--check-only"])
    independent = run_check(["scripts/verify_stage4_final.py", "--check-only"])
    table_receipt = {}
    loaded = {}
    for relative, (count, key) in TABLES.items():
        rows = loaded[relative] = read_rows(relative)
        if len(rows) != count or (key and len({row[key] for row in rows}) != count):
            raise ValueError(f"CSV scope/key changed: {relative}")
        table_receipt[relative] = {"rows": count, "columns": len(rows[0]), "status": "metadata_integrity_passed_not_evidence_volume"}
    claims = loaded["quant/stage4_claim_ledger.csv"]
    gaps = loaded["quant/stage4_gap_register.csv"]
    claim_ids = {row["claim_id"] for row in claims}
    gap_ids = {row["gap_id"] for row in gaps}
    sources = {row["source_id"] for row in read_rows("data/source_register.csv")}
    if not all(set(row["linked_gap_ids"].split("|")) <= gap_ids for row in claims):
        raise ValueError("Claim gap reference is unresolved")
    if not all(set(row["claim_ids"].split("|")) <= claim_ids for row in gaps):
        raise ValueError("Gap claim reference is unresolved")
    for row in claims + gaps + loaded["data/public/stage4_public_observations.csv"]:
        for ref in re.findall(r"(?<![A-Za-z0-9])S\d{3}\b", " ".join(row.values())):
            if ref not in sources:
                raise ValueError(f"Unknown canonical source: {ref}")
    prices = [r for r in loaded["data/public/stage4_public_observations.csv"] if r["observation_id"] in {f"P{i:02}" for i in range(1, 9)}]
    if len(prices) != 8 or any(r["comparability_status"] != "noncomparable" or any(r[k] for k in ("billing_period", "sku_id", "individual_or_family")) for r in prices):
        raise ValueError("Unresolved public prices converted into comparable offers")
    local_links = 0
    for relative in DOCS:
        path = ROOT / relative
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            if target != RECEIPT and not target.exists():
                raise ValueError(f"Broken local link: {relative} -> {link}")
            local_links += 1
    expected_version_text = {
        "README.md": "quant/stage4_final_delivery.md",
        "docs/STAGE_STATUS.md": "证据约束核算与交接v2.0",
        "docs/MASTER_PLAN.md": "quant/stage4_final_delivery.md",
        "docs/DELIVERABLES.md": "quant/evidence_model.ipynb",
        "data/PACKAGE_SPEC.md": "不进入正式v2证据包",
    }
    for relative, marker in expected_version_text.items():
        if marker not in (ROOT / relative).read_text(encoding="utf-8"):
            raise ValueError(f"Current entry point not aligned: {relative}")
    legacy = subprocess.run([sys.executable, "-B", "scripts/run_stage4.py", "--execute-direct"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if legacy.returncode != 1 or "v1 D build is retired" not in legacy.stderr:
        raise ValueError("Legacy build was not stopped before overwriting current strategy")
    files = list(TABLES) + list(DOCS) + ["quant/evidence_inputs.json", "quant/evidence_model.py", "quant/evidence_model.ipynb", "scripts/run_stage4_final.py", "scripts/verify_stage4_final.py", "scripts/closeout_stage4_final.py", "data/source_register.csv", "data/data_availability.csv"]
    return {
        "version": "stage4-v2.0", "reviewed_on": "2026-10-02",
        "documentation_refresh": {"reviewed_on": "2026-10-03", "scope": "README Stage5 handoff status corrected for publication; model, economic inputs, outputs and original source review unchanged"},
        "stage_status": "degraded_pass_evidence_constrained_accounting_and_handoff",
        "real_economic_status": "not_identified_not_passed",
        "generated_output_check": generated,
        "independent_validation": independent,
        "table_integrity": table_receipt,
        "claim_gap_source_references": "passed",
        "authored_local_links": {"checked": local_links, "status": "passed"},
        "current_entry_points": "passed",
        "legacy_overwrite_prevention": "expected_stop_exit_1_no_D_rebuild",
        "source_review_scope": {
            "primary_body_crosschecks": "Root re-read SEC rollout paragraph, Japan App Store IAP list, and same-study company method/count release",
            "delegated_primary_review": "Bounded Lily supply/metadata lookup, official PDF direct GET403 and same-URL indexed study excerpt; original PDF not fully recovered",
            "not_authenticated": "Current account entitlement/actual prices, internal bills/costs, all-assigned efficacy, real effect sizes, policy interference, N/F",
            "cursor": "Not dispatched; local authentication file absent at initial existence check; no remote evidence",
            "refresh": "Manual official read-to-CSV, not automated web refresh"
        },
        "runtime": {"actual_authoring_execution": "run_stage4_final.py --execute-direct in a new Python process, 3 code cells with saved stdout", "independent_notebook_check": "saved outputs checked, not independently re-executed", "standard_jupyter_kernel": "not_validated", "new_dependencies_installed": False},
        "scope_exclusions": ["v1 D economic files/figures/parameters", "real ROI/ranking or Scale", "future growth point forecasts", "Stage5 execution"],
        "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    result = review()
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.check_only:
        if not RECEIPT.exists() or RECEIPT.read_text(encoding="utf-8") != content:
            raise ValueError("Final receipt differs; source or artifact changed and needs renewed review")
    else:
        RECEIPT.write_text(content, encoding="utf-8")
    print(json.dumps({"status": "passed", "mode": "check_only_no_writes" if args.check_only else "record_written", "receipt": str(RECEIPT), "real_economic_status": "not_identified_not_passed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
