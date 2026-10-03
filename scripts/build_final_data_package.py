"""Freeze an explicit, reviewed allowlist. No directory glob enters the ZIP."""
import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'duolingo-analysis-v1.1-closeout-stage4-v2-stage5-v1'
DEST = ROOT / 'reports/generated/duolingo_analysis_data_v1.zip'

# grain, key, measurement/period, authoritative field explanation
TABLES = {
    'data/source_register.csv': ('一份来源登记', ['source_id'], '发布/覆盖/访问日期分列；21项不是独立研究数', 'docs/DATA_POLICY.md'),
    'data/metric_dictionary.csv': ('一个公司或未来功能指标定义', ['metric_id'], '单位和期间逐行；定义不是观测', 'docs/kpi_tree.md'),
    'data/data_availability.csv': ('一个指标可得性/缺口判断', ['metric_id'], '公开公司与内部功能粒度分开', 'docs/DATA_POLICY.md'),
    'data/public/company_quarterly_metrics.csv': ('一个公司季度指标', ['period_end','metric_id'], '2024Q3–2026Q2；million users/accounts、USD million或ratio逐行', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'data/public/company_comparison_baselines.csv': ('一个上年比较基期指标', ['period_end','metric_id'], '2023Q3–2024Q2；与主表同单位，仅比较用途', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'data/public/product_timeline.csv': ('一项披露事件或计划', ['event_id'], '发生日期可未知；reported_on为披露日', 'data/PACKAGE_FIELD_REFERENCE.md#时间线与对账'),
    'data/public/source_cross_checks.csv': ('一项双来源舍入对账', ['period_end','metric_id','comparison_source_id'], '32行不是新增测量；容差不是CI', 'data/PACKAGE_FIELD_REFERENCE.md#时间线与对账'),
    'data/public/business_diagnostics.csv': ('一个公司季度描述指标', ['period_end','metric_id'], '公开值及yoy/qoq比较；舍入界非CI', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'data/public/engagement_decomposition.csv': ('一个季度和比较类型的增长恒等式', ['period_end','comparison'], '100自然对数增长点；非因果贡献', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'data/public/commercial_structure.csv': ('一个季度商业结构', ['period_end'], 'USD million、百分比或ratio；非利润/ARPU', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'data/public/stage3_robustness_checks.csv': ('一项舍入方向检查', ['check_id'], '披露舍入范围；不是置信区间或用户样本', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'data/public/stage3_base_period_bridge.csv': ('一个指标的本期/基期增长桥接', ['metric_id'], '2026Q1→Q2与2025Q1→Q2；100自然对数增长点', 'data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生'),
    'analysis/driver_evidence.csv': ('一项诊断主张', ['driver_id'], '算术、管理层解释和机制候选分别标记', 'data/PACKAGE_FIELD_REFERENCE.md#账本与契约'),
    'market/competitor_claims.csv': ('一条提供方/替代品原子主张', ['claim_id'], '访问至2026-09-29；版本资格逐项；非效果排名', 'data/PACKAGE_FIELD_REFERENCE.md#账本与契约'),
    'market/competitor_evidence_v2.csv': ('一条竞品来源定位观察', ['claim_id'], '97观察/48URL/34可区分体验者；多行不增独立样本', 'data/PACKAGE_FIELD_REFERENCE.md#账本与契约'),
    'quant/strategy_comparison.csv': ('一个策略对象', ['policy_id'], 'P0/P1/P2；非H1/H2/H3的ROI排名', 'quant/evidence_assumptions.md'),
    'quant/stage4_claim_ledger.csv': ('一条Stage4主张及禁用外推', ['claim_id'], '16条包括明确撤销项；不当成16个新研究', 'data/PACKAGE_FIELD_REFERENCE.md#账本与契约'),
    'quant/stage4_gap_register.csv': ('一个未知量和最低补证', ['gap_id'], '10缺口；内部、公开未得及尚未产生的效果分开', 'data/PACKAGE_FIELD_REFERENCE.md#账本与契约'),
    'data/public/stage4_public_observations.csv': ('一条官方观察或明确未知/访问结果', ['observation_id'], '28行；JPY报价不可比/研究计数/推出陈述；非28用户', 'quant/evidence_assumptions.md'),
    'data/public/stage4_learning_coverage.csv': ('同研究的一条原分组覆盖', ['study_id','arm'], '人数/百分比；30天；不是全员ITT或全部失访', 'quant/evidence_assumptions.md'),
    'data/public/stage4_economic_readiness.csv': ('一政策×原套餐层', ['policy_id','original_tier'], '经济均值、差及N为空未知；不是0', 'quant/evidence_assumptions.md'),
    'data/public/stage4_policy_readiness.csv': ('一个候选政策的总体就绪', ['policy_id'], 'P1/P2；真实总体值为空未知', 'quant/evidence_assumptions.md'),
    'data/public/stage4_symbolic_sensitivity.csv': ('一条数学或设计关系', ['parameter'], '8关系；±1为常数；无实证参数域', 'quant/evidence_assumptions.md'),
    'experiments/event_spec.csv': ('一个拟采集记录合同', ['record_name'], '20规格行；无实际用户事件', 'experiments/test_plan.md'),
    'reports/figure_lineage.csv': ('一个图中数值的来源', ['figure_id','key'], '58图点；显示变换与原单位分列', 'data/PACKAGE_FIELD_REFERENCE.md#图与运行规格'),
}

OWN_FILES = [
    'docs/DECISION_BRIEF.md','docs/MASTER_PLAN.md','docs/DATA_POLICY.md','docs/kpi_tree.md',
    'docs/DELIVERABLES.md','docs/FINAL_DELIVERY.md','docs/retrospective.md','docs/reusable_sop.md',
    'docs/STAGE_STATUS.md','docs/REPRODUCTION_GUIDE.md','docs/NEXT_PHASE_PLAN.md',
    'data/PACKAGE_FIELD_REFERENCE.md',
    'analysis/stage3_analysis.py','analysis/requirements.txt','analysis/business_review.ipynb',
    'market/competitor_scenario_review.md','market/competitor_evidence_quality_review.md','market/voc_quality_review.md',
    'reports/market_final_review.md','reports/decision_card.md','reports/monitoring_design.md',
    'reports/executive_decision_book.docx','reports/executive_decision_book.pdf',
    'reports/strategy_dashboard.xlsx','reports/strategy_dashboard.pdf',
    'experiments/test_plan.md','experiments/test_plan.docx','experiments/test_plan.pdf','experiments/stage5_final_validation.json',
    'quant/stage4_final_delivery.md','quant/stage4_public_evidence_v2.md','quant/evidence_assumptions.md',
    'quant/evidence_inputs.json','quant/evidence_model.py','quant/evidence_model.ipynb','quant/stage4_final_validation.json',
    'scripts/run_stage3.py','scripts/run_stage4_final.py','scripts/verify_stage4_final.py','scripts/rebuild_package_tables.py',
    'scripts/build_final_documents.py','scripts/export_final_documents.ps1','scripts/render_final_pdfs.py',
    'scripts/build_final_data_package.py','scripts/build_monitoring_dashboard.mjs','scripts/build_monitoring_dashboard.py','scripts/build_monitoring_dashboard.ps1',
    'reports/generated/monitoring_build/monitoring_artifact_qa.json',
    'reports/generated/monitoring_build/monitoring_native_qa.json',
    'reports/generated/monitoring_build/monitoring_reimport_qa.json',
    'reports/generated/monitoring_build/monitoring_packaging_qa.json',
    'reports/generated/monitoring_build/monitoring_pdf_qa.json',
    'reports/generated/monitoring_build/monitoring_pdf_render_qa.json',
]
EXCLUDED = {'scenario_results.csv','stage4_billing_paths.csv','stage4_break_even.csv','stage4_sensitivity.csv','stage3_learning_selection_sensitivity.csv','scenario_inputs.json','parameter_register.csv','opportunity_model.py','opportunity_model.ipynb'}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def content():
    names=list(TABLES)+OWN_FILES
    result={}
    metadata=[]
    for name in names:
        if Path(name).name in EXCLUDED or any(part in ('private','raw','processed','history') for part in Path(name).parts) or Path(name).name.startswith('.env'):
            raise ValueError(f'Forbidden package member {name}')
        p=ROOT/name
        b=p.read_bytes()
        meta={'path':name,'bytes':len(b),'sha256':sha(b),'sharing':'Own analysis/code/specification or minimal extracted factual data and own paraphrase; source material retains rights; no full third-party text license implied'}
        if name in TABLES:
            grain,key,scope,reference=TABLES[name]
            data=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'),newline='')))
            if not data or None in data[0] or any(None in r for r in data):
                raise ValueError(f'Invalid CSV {name}')
            keys=[tuple(r[k] for k in key) for r in data]
            if len(keys)!=len(set(keys)) or any(not all(v.strip() for v in key) for key in keys):
                raise ValueError(f'Duplicate or empty PK {name}')
            meta.update(rows=len(data),columns=list(data[0]),grain=grain,primary_key=key,unit_period_scope=scope,field_definition_ref=reference,empty_value='unknown or unavailable/not applicable per field contract; never implicitly zero')
        metadata.append(meta)
        result[name]=b
    # Repeated public paraphrases are analytical observations, not a copy of
    # comment text. Personal supplied files and raw excerpts are never read.
    manifest={'version':VERSION,'frozen_on':'2026-10-03','product_evidence_cutoff':'2026-10-02','company_quarters':'2024Q3–2026Q2','build_from':'explicit allowlist in scripts/build_final_data_package.py','files':metadata,'exclusions':sorted(EXCLUDED),'reproduction_boundary':'Starts from supplied public CSV; original web collection/manual coding not automatically reproduced; private 298-row intake omitted; its counts remain received aggregate evidence','standard_jupyter':'not validated; direct route only','source_authentication':'Hashes establish bytes, not source authenticity or causality'}
    result['MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    text=[f'# 最终冻结数据包 {VERSION}','', '冻结2026-10-03；产品证据截止2026-10-02。仅收公开最小事实、自行分析与必要方法；第三方保留权利。', '', '## 文件、粒度与边界','', '| 文件 | 行数或类型 | 粒度与时期/单位 | 字段定义 |','|---|---:|---|---|']
    for m in metadata:
        if 'rows' in m:
            text.append(f'| {m["path"]} | {m["rows"]} | {m["grain"]}；{m["unit_period_scope"]} | {m["field_definition_ref"]} |')
    text+=['','各表的完整字段名、主键及SHA-256在根目录MANIFEST.json；运行生成的README_PACKAGE.md给出环境、顺序和验收边界。来源URL在原表/登记中。', '', '## 分享判断','', '不再分发第三方全文、评论原文、私人记录、认证、v1经济D输入/输出/图。竞品CSV是自行概括的逐主张与来源定位，非原文评论集。298条收到的自选记录不入包，只保留已审核的计数和偏差说明；因此包内不能复算其私有原始标签。', '', '不存在整份第三方内容的开放许可承诺；链接原文，保留来源的原权利。代码/自己的分析也不在本次任务中未经用户指定添加新的开源许可。','', '## 复现与冻结','', '执行python -B scripts/rebuild_package_tables.py进行只读数值/图点校验；--rebuild只写公司三个派生和v2四表。桥接三个数值由本脚本独立复算，历史原生成脚本在仓库中。', '执行python -B scripts/run_stage3.py --execute-direct、python -B scripts/run_stage4_final.py --execute-direct可重建普通Notebook输出；不等于标准kernel通过。需要现有依赖并记录实际环境。', 'Word/PDF与Excel监控制作路径见README_PACKAGE.md。原网页和账户资格不自动刷新；输入变化后版本、报告、图与manifest需重新审核。']
    result['data/public/MANIFEST.md']=('\n'.join(text)+'\n').encode('utf-8')
    result['README_PACKAGE.md']=f'''# Duolingo 分析数据移交包

版本 {VERSION}；冻结2026-10-03。解压后在根目录运行。Windows图表使用Microsoft YaHei，当前实际Office为16.0。Notebook使用既有Anaconda Python3.13.5和analysis/requirements.txt版本；正式文稿使用bundled Python3.12.14/python-docx1.2.0/matplotlib3.11.2。bundled Python未提供nbformat/IPython，不能直接运行Notebook。CSV最小复核只需标准库。没有安装新依赖。

## 最小复核

先按[复现指南](docs/REPRODUCTION_GUIDE.md)选择只读核验或编辑重建；业务阅读入口为[最终交付](docs/FINAL_DELIVERY.md)，下一轮选择集中在[后续规划](docs/NEXT_PHASE_PLAN.md)。不必运行Word/Excel或Notebook即可完成以下标准库核验。

1. 核对MANIFEST.json的路径/哈希与CSV主键/粒度。不要把观察行数、URL或检查次数当用户样本。
2. `python -B scripts/rebuild_package_tables.py`只读校验公司输入QA、三张公司派生、四张v2派生、桥接三行及报告58图点。
3. `python -B scripts/run_stage4_final.py --check-only`对账当前v2；`python -B scripts/verify_stage4_final.py --check-only`提供另一条独立方法/边界复核。真实经济量仍为空。无D输入/输出。

## 重建与文稿

`python -B scripts/run_stage3.py --execute-direct`需要nbformat、IPython、matplotlib等现有分析依赖，在新Python进程执行公司Notebook；`python -B scripts/run_stage4_final.py --execute-direct`需要nbformat。交互Jupyter/ZeroMQ未通过。

`python -B scripts/build_final_documents.py`使用bundled python-docx/matplotlib重建Word和四图；`powershell -File scripts/export_final_documents.ps1`用本地隐藏Word COM导出同版PDF；`python -B scripts/render_final_pdfs.py experiments/test_plan.pdf reports/executive_decision_book.pdf`以bundled Poppler渲染验收。Office版本、字体与可用授权会影响导出；没有声称跨系统排版完全一致。

监控由build_monitoring_dashboard.mjs/py/ps1生成，使用bundled artifact-tool；实际保存/导出边界见reports/monitoring_design.md。Excel COM重算与原生图测试通过，但许可到期导致Save/原生PDF导出失败；正式PDF为重新导入最终xlsx的同版sheet渲染快照，不能称Excel打印输出或生产监控。

## 分析边界

经济/政策未知保留null或CSV空白，不是0；不提供真实ROI、MDE/N、学习/经营uplift、总体预测或已执行试验。市场竞争表为同任务供给与风险，不是满意度/效果排名。原文网页到CSV是人工有限核读；用户私有298条记录未打包，其总量及提交标签聚合无法从这个公开包独立重建。当前部署/资格、完整研究PDF与真实成本仍有缺口。

PDF/Word/Excel为本项目自己的产物；原资料只通过必要事实、自行概括及URL提供，未附全文再分发授权。所有列表采用白名单，不打包目录。MANIFEST.json不含自身哈希，验证时对其版本、清单结构与成员集合另查；CRC/哈希不认证来源或因果。

这是最小复现包，并非整个项目仓库：历史文档中提到但未列入MANIFEST的材料只在仓库保留。Stage4原验收记录包含全仓库审核对象，不要求包内复跑该历史closeout；包内采用上述当前模型/独立校验。仓库reports/final_delivery_validation.json记录本ZIP校验，避免循环哈希不收入本ZIP。监控六份实际QA收据已收入包。
'''.encode('utf-8')
    return result,manifest


def validate_authorized_manifest(data, members):
    """Check against this reviewed source allowlist, not only ZIP self-reporting."""
    allowed=set(TABLES)|set(OWN_FILES)
    registered=[m['path'] for m in data['files']]
    extras={'MANIFEST.json','data/public/MANIFEST.md','README_PACKAGE.md'}
    if data.get('version')!=VERSION or data.get('product_evidence_cutoff')!='2026-10-02':
        raise ValueError('Archive version/evidence cutoff differs from reviewed source')
    if len(registered)!=len(set(registered)) or set(registered)!=allowed:
        raise ValueError('Archive manifest differs from reviewed source allowlist')
    if len(members)!=len(set(members)) or set(members)!=allowed|extras:
        raise ValueError('Archive members differ from reviewed source allowlist')
    for m in data['files']:
        if m['path'] in TABLES:
            grain,key,scope,reference=TABLES[m['path']]
            if (m.get('primary_key'),m.get('grain'),m.get('unit_period_scope'),m.get('field_definition_ref'))!=(key,grain,scope,reference):
                raise ValueError(f'Archive table contract differs: {m["path"]}')
    return allowed|extras


def verify_zip():
    with zipfile.ZipFile(DEST) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        data=json.loads(z.read('MANIFEST.json'))
        expected=validate_authorized_manifest(data,z.namelist())
        for m in data['files']:
            if sha(z.read(m['path']))!=m['sha256']:
                raise ValueError(f'Hash mismatch {m["path"]}')
        # Check the actual newly authored reader path inside the archive, not
        # repository-only files that happen to exist on the author's machine.
        reader_links=0
        for name in ('docs/FINAL_DELIVERY.md','docs/REPRODUCTION_GUIDE.md','docs/NEXT_PHASE_PLAN.md','README_PACKAGE.md'):
            document=z.read(name).decode('utf-8')
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',document):
                target=target.strip('<>').split('#',1)[0]
                if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target):
                    continue
                resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),target))
                if resolved not in expected:
                    raise ValueError(f'Package reader link missing: {name} -> {target}')
                reader_links+=1
        if any(Path(n).name in EXCLUDED or n.startswith(('data/private/','data/raw/','data/processed/')) for n in z.namelist()):
            raise ValueError('Forbidden archive member')
        # Extract only this known explicit set into a new isolated directory.
        # No cleanup command or user path is moved/deleted.
        task_temp=Path(tempfile.mkdtemp(prefix='duolingo_final_package_'))
        for name in z.namelist():
            target=(task_temp/name).resolve()
            if not target.is_relative_to(task_temp.resolve()):
                raise ValueError('Unsafe archive path')
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(name))
    check=subprocess.run([sys.executable,'-B','scripts/rebuild_package_tables.py'],cwd=task_temp,capture_output=True,text=True,check=True)
    independent=subprocess.run([sys.executable,'-B','scripts/verify_stage4_final.py','--check-only'],cwd=task_temp,capture_output=True,text=True,check=True)
    independent_result=json.loads(independent.stdout)
    if independent_result['status']!='passed':
        raise ValueError('Isolated Stage4 independent verification failed')
    print(json.dumps({'status':'passed','archive':DEST.relative_to(ROOT).as_posix(),'version':VERSION,'files':len(expected),'csv_tables':len(TABLES),'bytes':DEST.stat().st_size,'source_allowlist_and_contracts':'passed','primary_reader_local_links_checked':reader_links,'isolated_csv_reproduction':json.loads(check.stdout),'isolated_stage4_independent_checks':{k:v['status'] for k,v in independent_result['checks'].items()},'private_or_retired_D_files':0,'sha256':sha(DEST.read_bytes())},ensure_ascii=False))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--check-only',action='store_true')
    args=ap.parse_args()
    if not args.check_only:
        payload,manifest=content()
        DEST.parent.mkdir(parents=True,exist_ok=True)
        # Deterministic member metadata for repeatable archives of unchanged bytes.
        with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,b in payload.items():
                info=zipfile.ZipInfo(name,date_time=(2026,10,3,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,b)
        (ROOT/'data/FINAL_PACKAGE_MANIFEST.md').write_bytes(payload['data/public/MANIFEST.md'])
        (ROOT/'data/final_package_manifest.json').write_bytes(payload['MANIFEST.json'])
    verify_zip()


if __name__=='__main__':
    main()
