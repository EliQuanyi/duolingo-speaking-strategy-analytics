"""Check/rebuild only factual derivatives and current v2 outputs in a clean package.

The bridge uses the already audited period identity directly. No retired
selection-sensitivity or D economics is imported or generated.
"""
import argparse
import csv
import io
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'quant'))
from analysis.stage3_analysis import validate_inputs, compute_diagnostics
from evidence_model import generated_texts, load_config, csv_text, learning_coverage


def csv_bytes(data):
    buf = io.StringIO(newline='')
    w = csv.DictWriter(buf, fieldnames=list(data[0]))
    w.writeheader()
    w.writerows(data)
    return buf.getvalue().encode('utf-8')


def read(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rebuild', action='store_true', help='default is read-only check')
    args = ap.parse_args()
    inputs = validate_inputs(ROOT)
    tables = compute_diagnostics(inputs)
    outputs = {f'data/public/{name}.csv':csv_bytes(value) for name,value in tables.items()}
    for relative, text in generated_texts(load_config()).items():
        outputs[relative] = text.encode('utf-8')
    outputs['data/public/stage4_learning_coverage.csv'] = csv_text(learning_coverage(read('data/public/stage4_public_observations.csv'))).encode('utf-8')
    for relative, expected in outputs.items():
        p = ROOT / relative
        if args.rebuild:
            p.write_bytes(expected)
        elif p.read_bytes() != expected:
            raise ValueError(f'Derived table differs: {relative}')
    main = {(r['period_end'],r['metric_id']):r for r in read('data/public/company_quarterly_metrics.csv')}
    bridge = read('data/public/stage3_base_period_bridge.csv')
    for r in bridge:
        values=[float(main[(p,r['metric_id'])]['value']) for p in ('2026-03-31','2026-06-30','2025-03-31','2025-06-30')]
        q1,q2,p1,p2=values
        current=100*math.log(q2/q1)
        base=-100*math.log(p2/p1)
        for key,value in [('current_qoq_log_points',current),('base_period_contribution_log_points',base),('yoy_log_change',current+base)]:
            if not math.isclose(float(r[key]),value,abs_tol=1e-10):
                raise ValueError(f'Bridge differs: {r["metric_id"]} {key}')
    # Validate the data behind the final figures independently of the plotting code.
    coverage={(r['study_id'],r['arm']):r for r in read('data/public/stage4_learning_coverage.csv')}
    bridge_by={r['metric_id']:r for r in bridge}
    lineage=read('reports/figure_lineage.csv')
    for r in lineage:
        key=r['key'].split('|')
        if r['figure_id'] in ('F01','F02'):
            source=main[tuple(key)]
            actual=source['value']
            if source['source_id'] != r['source_id'] or source['source_url'] != r['source_url']:
                raise ValueError('Figure source mismatch')
        elif r['figure_id']=='F03':
            actual=bridge_by[key[0]][key[1]]
        else:
            actual=coverage[tuple(key[:2])][key[2]]
        if actual != r['raw_value']:
            raise ValueError(f'Figure value mismatch: {r}')
    print(json.dumps({'status':'passed','mode':'rebuild' if args.rebuild else 'check_only','company_input_qa':inputs['report']['status'],'derived_tables':len(outputs),'bridge_rows_recomputed':len(bridge),'figure_points_checked':len(lineage),'legacy_D_reads_or_exports':0}))


if __name__=='__main__':
    main()
