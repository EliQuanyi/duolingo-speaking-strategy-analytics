"""Final repository artifact acceptance; no source collection or business effects.

Writes only the final receipt. --check-only compares the existing receipt with
actual files and checks without updating it. Requires the inspected pypdf runtime.
"""
import argparse
import csv
import copy
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'reports/final_delivery_validation.json'
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REQUIRED = [
    'reports/executive_decision_book.docx','reports/executive_decision_book.pdf',
    'reports/strategy_dashboard.xlsx','reports/strategy_dashboard.pdf',
    'experiments/test_plan.docx','experiments/test_plan.pdf','experiments/event_spec.csv',
    'reports/decision_card.md','reports/figure_lineage.csv','reports/market_final_review.md',
    'reports/monitoring_design.md','quant/stage4_final_delivery.md',
    'quant/evidence_model.ipynb','quant/stage4_final_validation.json',
    'experiments/stage5_final_validation.json','docs/FINAL_DELIVERY.md',
    'docs/retrospective.md','docs/reusable_sop.md','docs/STAGE_STATUS.md',
    'docs/REPRODUCTION_GUIDE.md','docs/NEXT_PHASE_PLAN.md',
    'docs/PORTFOLIO_CASE_STUDY.md','docs/PUBLICATION.md',
    '.gitattributes','.github/workflows/validate-public-analysis.yml',
    'docs/REQUIREMENTS_MATRIX.md','README.md','data/PACKAGE_FIELD_REFERENCE.md',
    'data/final_package_manifest.json','data/FINAL_PACKAGE_MANIFEST.md',
    'reports/generated/duolingo_analysis_data_v1.zip',
    'scripts/build_final_documents.py','scripts/export_final_documents.ps1',
    'scripts/build_final_data_package.py','scripts/rebuild_package_tables.py',
    'scripts/verify_final_delivery.py',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def normalized(text):
    return re.sub(r'\s+', '', text)


def pdf_page_body(text, page_number):
    """Remove only this page's complete footer line at an extraction boundary.

    Word's actual footer is at the bottom of the page, but pypdf currently
    extracts it as the first line. Never match across lines or into body digits.
    """
    lines = text.splitlines()
    nonempty = [i for i, line in enumerate(lines) if line.strip()]
    boundaries = {nonempty[0], nonempty[-1]} if nonempty else set()
    footer = f'DuolingoSpeaking分析final-v1.0|{page_number}'
    removed = {i for i in boundaries if normalized(lines[i]) == footer}
    return '\n'.join(line for i, line in enumerate(lines) if i not in removed), len(removed)


def pdf_text_boundary_checks():
    # These examples expose the original cross-line digit deletion and ensure
    # that similar text inside the body is retained, rather than hidden by QA.
    footer = 'Duolingo Speaking 分析  final-v1.0  |  3 '
    cases = [
        ('numeric_heading', footer + '\n4. 唯一 primary、测量窗口', 3,
         '4. 唯一 primary、测量窗口', 1),
        ('numeric_list_at_tail', '3. 冻结后随机试验\n' + footer, 3,
         '3. 冻结后随机试验', 1),
        ('wrong_page_number', footer + '\n4. 正文', 4,
         footer + '\n4. 正文', 0),
        ('inline_body_reference', '引用：' + footer + '，不能删除。', 3,
         '引用：' + footer + '，不能删除。', 0),
        ('interior_body_line', '正文开头\n' + footer + '\n正文结束', 3,
         '正文开头\n' + footer + '\n正文结束', 0),
        ('same_line_body_digits', footer + '4. 正文', 3,
         footer + '4. 正文', 0),
    ]
    for name, text, page, expected, count in cases:
        require(pdf_page_body(text, page) == (expected, count),
                f'PDF footer boundary regression: {name}')
    left, _ = pdf_page_body('跨页段落前半\nDuolingo Speaking 分析 final-v1.0 | 1', 1)
    right, _ = pdf_page_body('Duolingo Speaking 分析 final-v1.0 | 2\n2个数字开头的后半', 2)
    require(normalized(left + right) == '跨页段落前半2个数字开头的后半',
            'PDF footer boundary regression: split paragraph')
    return {'status': 'passed', 'cases': len(cases) + 1,
            'body_digits_and_footer_like_body_text_retained': True}


def word_pdf(docx, pdf, pages):
    reader = PdfReader(ROOT/pdf)
    require(len(reader.pages)==pages, f'Unexpected PDF pages {pdf}')
    # A Word paragraph may span pages. Ignore the actual repeated page footer
    # inserted into extract_text, so it does not split that body paragraph.
    bodies = [pdf_page_body(p.extract_text() or '', i)
              for i, p in enumerate(reader.pages, 1)]
    require(all(count == 1 for _, count in bodies), f'Expected one complete page footer: {pdf}')
    pdf_text = normalized(''.join(body for body, _ in bodies))
    with zipfile.ZipFile(ROOT/docx) as z:
        tree=ET.fromstring(z.read('word/document.xml'))
        paragraphs=[''.join(t.text or '' for t in p.findall('.//w:t',NS)) for p in tree.findall('.//w:p',NS)]
        paragraphs=[normalized(p) for p in paragraphs if len(normalized(p))>=8]
        matches=sum(p in pdf_text for p in paragraphs)
        coverage=matches/len(paragraphs)
        require(coverage>=.98, f'Word/PDF paragraph coverage below gate: {pdf} {coverage}')
        illustrations=len(tree.findall('.//w:drawing',NS))
    return {'pages':pages,'word_paragraphs_checked':len(paragraphs),
            'paragraphs_present_in_pdf':matches,'paragraph_text_coverage':coverage,
            'word_illustrations':illustrations,
            'page_footers_ignored':sum(count for _, count in bodies),
            'body_text_rule':'Whitespace ignored; only complete first/last extracted footer line matching each page number removed; body text retained',
            'engine':'Actual Microsoft Word COM 16.0 export',
            'limitation':'Text check plus actual export and visual review; not a pixel-equivalence certificate'}


def receipt_hashes(path):
    data=load(path)
    for name,digest in data['sha256'].items():
        require(sha(name)==digest, f'Receipt hash stale {path}: {name}')
    return {'matched_files':len(data['sha256']), 'not_source_authentication':True}


def monitoring():
    qa='reports/generated/monitoring_build/'
    final=load(qa+'monitoring_pdf_qa.json')
    native=load(qa+'monitoring_native_qa.json')
    require(sha('reports/strategy_dashboard.xlsx')==final['xlsx_sha256'],'Monitoring XLSX stale')
    require(sha('reports/strategy_dashboard.pdf')==final['pdf_sha256'],'Monitoring PDF stale')
    require(len(PdfReader(ROOT/'reports/strategy_dashboard.pdf').pages)==2,'Monitor PDF not two pages')
    cases=native['native_boundary_tests']
    require(len(cases)==25 and all(c['actual']==c['expected'] and c['color']==c['expected_color'] for c in cases),'Native state/color tests failed')
    inputs=('D8','H8','D9','H9','D10','H10','D11','H11','D12','H12','D13','H13','D14','H14','D15','H15')
    with zipfile.ZipFile(ROOT/'reports/strategy_dashboard.xlsx') as z:
        book=ET.fromstring(z.read('xl/workbook.xml'))
        require(len(book.findall('x:sheets/x:sheet',NS))==2,'Workbook sheets')
        first=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        second=ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
        cells={c.attrib['r']:c for c in second.findall('.//x:c',NS)}
        for address in inputs:
            cell=cells.get(address)
            require(cell is None or (not cell.findall('x:f',NS) and not cell.findall('x:v',NS) and not ''.join(cell.itertext()).strip()),f'Planning fixture remains {address}')
        require(cells['B5'].find('x:f',NS) is not None,'Missing readiness formula')
        format_formulas=[f.text for f in second.findall('.//x:conditionalFormatting/x:cfRule/x:formula',NS)]
        require(any('LEFT($B$5,2)' in (f or '') for f in format_formulas),'Native conditional format missing explicit formula')
        types=ET.fromstring(z.read('[Content_Types].xml'))
        charts=[t.attrib['PartName'].lstrip('/') for t in types if t.attrib.get('ContentType')=='application/vnd.openxmlformats-officedocument.drawingml.chart+xml']
        require(len(charts)==1,'Editable chart absent or count differs')
        require(charts[0] in z.namelist(),'Chart content-type points to missing part')
        values={c.attrib['r']:c.find('x:v',NS).text for c in first.findall('.//x:c',NS) if c.find('x:v',NS) is not None}
        with (ROOT/'data/public/company_quarterly_metrics.csv').open(encoding='utf-8-sig',newline='') as f:
            dau=sorted((r for r in csv.DictReader(f) if r['metric_id']=='M001'),key=lambda r:r['period_end'])
        for row,source in enumerate(dau,24):
            require(float(values[f'C{row}'])==float(source['value']),'Monitor DAU differs')
    return {'sheets':2,'pages':2,'editable_charts':1,'blank_planning_inputs_checked':16,
            'source_dau_rows_checked':8,'native_state_and_color_cases':25,
            'native_chart_edit_and_restore':native['chart_edit_restored'],
            'native_save_passed':native['native_save_succeeded'],
            'native_pdf_passed':native['native_pdf_succeeded'],
            'pdf_mode':'raster snapshots re-rendered from final XLSX; not searchable body text',
            'visual_review':'Both current PDF pages inspected by agent and root'}


def run_check(script, *args):
    r=subprocess.run([sys.executable,'-B',script,*args],cwd=ROOT,capture_output=True,text=True,check=True)
    return json.loads(r.stdout)


def package_manifest_boundary_checks():
    import importlib.util
    spec=importlib.util.spec_from_file_location('final_package_builder',ROOT/'scripts/build_final_data_package.py')
    builder=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    data=load('data/final_package_manifest.json')
    members=[m['path'] for m in data['files']]+['MANIFEST.json','data/public/MANIFEST.md','README_PACKAGE.md']
    builder.validate_authorized_manifest(data,members)
    cases=[]
    bad=copy.deepcopy(data)
    bad['files'].append({'path':'unapproved_note.md'})
    cases.append(('self_consistent_added_file',bad,members+['unapproved_note.md']))
    bad=copy.deepcopy(data)
    bad['version']='unreviewed-version'
    cases.append(('wrong_version',bad,members))
    bad=copy.deepcopy(data)
    bad['product_evidence_cutoff']='unreviewed-cutoff'
    cases.append(('wrong_cutoff',bad,members))
    bad=copy.deepcopy(data)
    bad['files'].append(copy.deepcopy(bad['files'][0]))
    cases.append(('duplicate_manifest_path',bad,members))
    cases.append(('duplicate_archive_member',copy.deepcopy(data),members+[members[0]]))
    bad=copy.deepcopy(data)
    removed=bad['files'].pop(0)['path']
    cases.append(('self_consistent_missing_required_file',bad,[m for m in members if m!=removed]))
    bad=copy.deepcopy(data)
    next(m for m in bad['files'] if m['path']=='data/source_register.csv')['primary_key']=['wrong_key']
    cases.append(('wrong_table_contract',bad,members))
    for name,case,case_members in cases:
        try:
            builder.validate_authorized_manifest(case,case_members)
        except ValueError:
            continue
        raise ValueError(f'Archive allowlist regression: {name}')
    return {'status':'passed','invalid_cases_rejected':len(cases),
            'valid_current_manifest_accepted':True,
            'scope':'Software boundary cases only; no artificial business data exported'}


def final_checks():
    for name in REQUIRED:
        require((ROOT/name).is_file() and (ROOT/name).stat().st_size>0, f'Missing final artifact {name}')
    with (ROOT/'experiments/event_spec.csv').open(encoding='utf-8-sig',newline='') as f:
        events=list(csv.DictReader(f))
    require(len(events)==20 and len(events[0])==11,'Event contract shape')
    require(len({r['record_name'] for r in events})==20 and all('not_collected' in r['readiness'] for r in events),'Event specs misrepresented')
    package=run_check('scripts/build_final_data_package.py','--check-only')
    require(package['status']=='passed','Package verification failed')
    with zipfile.ZipFile(ROOT/'reports/generated/duolingo_analysis_data_v1.zip') as z:
        manifest=json.loads(z.read('MANIFEST.json'))
        require(manifest==load('data/final_package_manifest.json'),'Repository/package manifest diverged')
        for meta in manifest['files']:
            require(sha(meta['path'])==meta['sha256'],f'Package frozen file now changed {meta["path"]}')
        require(z.read('data/public/MANIFEST.md')==(ROOT/'data/FINAL_PACKAGE_MANIFEST.md').read_bytes(),'Markdown manifest mirror differs')
    return {
        'version':'closeout-v1.1','reviewed_on':'2026-10-03','product_evidence_cutoff':'2026-10-02',
        'artifact_gate':'passed_with_explicit_technical_and_evidence_limits',
        'business_effect_gate':'not_passed_not_ready_not_executed',
        'actual_checks':{
            'required_artifacts_present':len(REQUIRED),
            'pdf_text_boundary_regressions':pdf_text_boundary_checks(),
            'book':word_pdf('reports/executive_decision_book.docx','reports/executive_decision_book.pdf',11),
            'experiment':word_pdf('experiments/test_plan.docx','experiments/test_plan.pdf',8),
            'current_visual_qa':{'book':11,'experiment':8,'monitor':2,'status':'Book pages 7 and 9 visually reinspected after closeout edits; other 9 page render hashes unchanged from inspected version; experiment and monitor unchanged'},
            'stage4_unchanged_receipt':receipt_hashes('quant/stage4_final_validation.json'),
            'stage5_receipt':receipt_hashes('experiments/stage5_final_validation.json'),
            'event_contracts':{'rows':20,'fields':11,'actual_events':0},
            'monitoring':monitoring(),
            'frozen_package':package,
            'package_allowlist_boundary_regressions':package_manifest_boundary_checks(),
            'independent_review':'Experiment/market/quant/packaging issues corrected; limited human reasoning reviews, not full independent source authentication'},
        'not_passed':[
            'natural-use all-assigned learning/business effects and actual current access',
            'causal company Driver attribution, genuine cost/contribution/Max spillover/N/F',
            'real policy ROI/ranking, numeric forecast, experimental MDE/N and Scale',
            'original full learning PDF and exhaustive original-source audit',
            'standard Jupyter kernel; Excel native Save/PDF export'],
        'new_dependencies_installed':False,
        'sha256':{n:sha(n) for n in REQUIRED},
        'integrity_boundary':'Actual byte/structural/numeric/package checks; does not authenticate external sources or establish product causality'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check-only',action='store_true')
    args=ap.parse_args()
    report=final_checks()
    if args.check_only:
        require(RECEIPT.is_file() and load('reports/final_delivery_validation.json')==report,'Final receipt missing/stale')
    else:
        RECEIPT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','mode':'check_only' if args.check_only else 'receipt_written',
                      'artifact_gate':report['artifact_gate'],'actual_business_effect':'not_identified',
                      'book_pages':11,'experiment_pages':8,'monitor_pages':2,
                      'package_files':report['actual_checks']['frozen_package']['files'],
                      'csv_tables':report['actual_checks']['frozen_package']['csv_tables'],
                      'receipt':str(RECEIPT)},ensure_ascii=False))


if __name__=='__main__':
    main()
