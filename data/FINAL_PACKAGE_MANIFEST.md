# 最终冻结数据包 duolingo-analysis-v1.1-closeout-stage4-v2-stage5-v1

冻结2026-10-03；产品证据截止2026-10-02。仅收公开最小事实、自行分析与必要方法；第三方保留权利。

## 文件、粒度与边界

| 文件 | 行数或类型 | 粒度与时期/单位 | 字段定义 |
|---|---:|---|---|
| data/source_register.csv | 21 | 一份来源登记；发布/覆盖/访问日期分列；21项不是独立研究数 | docs/DATA_POLICY.md |
| data/metric_dictionary.csv | 14 | 一个公司或未来功能指标定义；单位和期间逐行；定义不是观测 | docs/kpi_tree.md |
| data/data_availability.csv | 14 | 一个指标可得性/缺口判断；公开公司与内部功能粒度分开 | docs/DATA_POLICY.md |
| data/public/company_quarterly_metrics.csv | 64 | 一个公司季度指标；2024Q3–2026Q2；million users/accounts、USD million或ratio逐行 | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| data/public/company_comparison_baselines.csv | 28 | 一个上年比较基期指标；2023Q3–2024Q2；与主表同单位，仅比较用途 | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| data/public/product_timeline.csv | 16 | 一项披露事件或计划；发生日期可未知；reported_on为披露日 | data/PACKAGE_FIELD_REFERENCE.md#时间线与对账 |
| data/public/source_cross_checks.csv | 32 | 一项双来源舍入对账；32行不是新增测量；容差不是CI | data/PACKAGE_FIELD_REFERENCE.md#时间线与对账 |
| data/public/business_diagnostics.csv | 64 | 一个公司季度描述指标；公开值及yoy/qoq比较；舍入界非CI | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| data/public/engagement_decomposition.csv | 16 | 一个季度和比较类型的增长恒等式；100自然对数增长点；非因果贡献 | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| data/public/commercial_structure.csv | 8 | 一个季度商业结构；USD million、百分比或ratio；非利润/ARPU | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| data/public/stage3_robustness_checks.csv | 3 | 一项舍入方向检查；披露舍入范围；不是置信区间或用户样本 | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| data/public/stage3_base_period_bridge.csv | 3 | 一个指标的本期/基期增长桥接；2026Q1→Q2与2025Q1→Q2；100自然对数增长点 | data/PACKAGE_FIELD_REFERENCE.md#公司指标与派生 |
| analysis/driver_evidence.csv | 3 | 一项诊断主张；算术、管理层解释和机制候选分别标记 | data/PACKAGE_FIELD_REFERENCE.md#账本与契约 |
| market/competitor_claims.csv | 33 | 一条提供方/替代品原子主张；访问至2026-09-29；版本资格逐项；非效果排名 | data/PACKAGE_FIELD_REFERENCE.md#账本与契约 |
| market/competitor_evidence_v2.csv | 97 | 一条竞品来源定位观察；97观察/48URL/34可区分体验者；多行不增独立样本 | data/PACKAGE_FIELD_REFERENCE.md#账本与契约 |
| quant/strategy_comparison.csv | 3 | 一个策略对象；P0/P1/P2；非H1/H2/H3的ROI排名 | quant/evidence_assumptions.md |
| quant/stage4_claim_ledger.csv | 16 | 一条Stage4主张及禁用外推；16条包括明确撤销项；不当成16个新研究 | data/PACKAGE_FIELD_REFERENCE.md#账本与契约 |
| quant/stage4_gap_register.csv | 10 | 一个未知量和最低补证；10缺口；内部、公开未得及尚未产生的效果分开 | data/PACKAGE_FIELD_REFERENCE.md#账本与契约 |
| data/public/stage4_public_observations.csv | 28 | 一条官方观察或明确未知/访问结果；28行；JPY报价不可比/研究计数/推出陈述；非28用户 | quant/evidence_assumptions.md |
| data/public/stage4_learning_coverage.csv | 2 | 同研究的一条原分组覆盖；人数/百分比；30天；不是全员ITT或全部失访 | quant/evidence_assumptions.md |
| data/public/stage4_economic_readiness.csv | 6 | 一政策×原套餐层；经济均值、差及N为空未知；不是0 | quant/evidence_assumptions.md |
| data/public/stage4_policy_readiness.csv | 2 | 一个候选政策的总体就绪；P1/P2；真实总体值为空未知 | quant/evidence_assumptions.md |
| data/public/stage4_symbolic_sensitivity.csv | 8 | 一条数学或设计关系；8关系；±1为常数；无实证参数域 | quant/evidence_assumptions.md |
| experiments/event_spec.csv | 20 | 一个拟采集记录合同；20规格行；无实际用户事件 | experiments/test_plan.md |
| reports/figure_lineage.csv | 58 | 一个图中数值的来源；58图点；显示变换与原单位分列 | data/PACKAGE_FIELD_REFERENCE.md#图与运行规格 |

各表的完整字段名、主键及SHA-256在根目录MANIFEST.json；运行生成的README_PACKAGE.md给出环境、顺序和验收边界。来源URL在原表/登记中。

## 分享判断

不再分发第三方全文、评论原文、私人记录、认证、v1经济D输入/输出/图。竞品CSV是自行概括的逐主张与来源定位，非原文评论集。298条收到的自选记录不入包，只保留已审核的计数和偏差说明；因此包内不能复算其私有原始标签。

不存在整份第三方内容的开放许可承诺；链接原文，保留来源的原权利。代码/自己的分析也不在本次任务中未经用户指定添加新的开源许可。

## 复现与冻结

执行python -B scripts/rebuild_package_tables.py进行只读数值/图点校验；--rebuild只写公司三个派生和v2四表。桥接三个数值由本脚本独立复算，历史原生成脚本在仓库中。
执行python -B scripts/run_stage3.py --execute-direct、python -B scripts/run_stage4_final.py --execute-direct可重建普通Notebook输出；不等于标准kernel通过。需要现有依赖并记录实际环境。
Word/PDF与Excel监控制作路径见README_PACKAGE.md。原网页和账户资格不自动刷新；输入变化后版本、报告、图与manifest需重新审核。
