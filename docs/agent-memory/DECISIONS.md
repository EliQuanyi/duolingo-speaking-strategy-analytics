# 已验证决策

- 2026-10-03：最终分析/设计移交沿用Stage4证据约束v2，唯一primary为全原组baseline调整的延后未练情境盲评口语总分；H1任务优先不等于P1预选。N/MDE/窗口/门槛须真实匹配数据与权限冻结，学习和成熟账单窗口分开。商业报告与监控不声明试验效果、真实经济性或生产上线。依据：experiments/test_plan.md、reports/decision_card.md与docs/FINAL_DELIVERY.md。

- 2026-10-02，Stage4 v2覆盖同日v1的交付与研究顺序：作者经济参数/数值阈值退出正式论证及包；当前采用双臂全员贡献/成本差、符号阈值和未知传播。先确认实际增量及实施路线，再选择问题；H1任务优先不等于P1预选。标价无法替代贡献，完成者研究不能填商业uplift。依据：`quant/stage4_final_delivery.md`、`quant/evidence_assumptions.md`。
- 完整政策各原层的效果与部署人数须匹配同一政策曝光，间接层未知不设零。自然任务/学习研究可由知情外部参与者开展，权益变更及公司经营试验需授权；教学投资预算应覆盖完整增量投入，学习成绩不货币化。依据：Stage4 v2商业与量化独立复核。

以下同日v1记录为历史方法决定；窗口/配额/单价/P1排序不作为当前设计输入。

- 2026-10-02：Stage4条件模型以P0/P1/P2与原套餐层、共同90天D窗结算，实际权益/净贡献/成本/部署规模/F/权重仍未知，D参数域不支持现实排名。P1研究优先级来自H1与公司推进方向，必须先核真实增量；没有未覆盖Super则停止该分支。依据：`quant/stage4_business_review.md`、`quant/stage4_validation.json`。
- 2026-10-02：成本包括两臂赠送/非赠送付费后工作量；原Max传播与Free潜在Max购买分流分开，Super单层试验不能估总体政策传播。共享路径m/u是D假设，真实双臂均值不同时必须改变模型，不只换概率；工程分钟不等于学习时间。依据：Stage4独立数学/业务审阅与`quant/assumptions.md`。

- 2026-10-02：H1/H2是用户任务与教学机制，H3是商业净值假设，不能当三个互斥ROI方案。权益策略以实际现行政策为共同对照，不预设目前仅Max可用；Super只计新增覆盖/额度。固定共同任务、期间和原套餐分层，权重未知不汇总排名；免费用户潜在Max购买分流与原Max实际降级分开。依据：`analysis/business_review.md`第5节、`docs/MASTER_PLAN.md`。
- 2026-10-02：同比变化需区分当期季度变化和上年比较基数；算术桥接不是季节调整或功能效果。完成者与未纳入者均值条件加权只能描述选择风险，不恢复ITT，不检验原调整模型显著性，也不提供商业uplift。依据：`scripts/closeout_stage3.py`、`analysis/stage3_causal_chain_review.md`及本次原来源核读。

- 2026-09-30：Stage3专项补强将证据按环节而非笼统“功能效果”交接：DRR-25-06随机分组价值保留，完成者选择/差异未纳入限制其ITT与自然使用外推；Falstaff英文提示不证明母语，含练过短语不等于全部题目练过。学习测试成绩不能转换商业uplift；单位成本和套餐替代缺口阻塞真实净收益排序，但不阻塞条件性阈值分析。参数域内结论翻转时不强选赢家。依据：`analysis/stage3_causal_chain_review.md`、`analysis/data_quality_report.md`及原始研究说明。

- 2026-09-30：Stage 3 的公司经营数据与算术结构只支持描述和条件性量化交接；DAU/MAU 不能替代留存，对数拆解不能写因果贡献，订阅 bookings/确认收入/期末账户不得混为转化或 ARPU。Q4 收入可用同口径年度减九个月，但必须保留两腿来源并传播两腿舍入精度；公开 CSV 起的计算复现与原网页自动抽取是不同验收项。依据：`analysis/business_review.md`、`analysis/data_quality_report.md` 及实际计算/复核。

- 2026-09-28：项目只研究 Speaking / Video Call 扩张决策；分析重点为市场、经营 Driver、经济性阈值和实验设计。依据：用户目标及 Duolingo 2026 Q2 股东信中的产品方向。
- 2026-09-28：公开公司级指标仅用于描述经营趋势；功能影响须留待真实对照实验。依据：公开 10-Q 的数据粒度与项目可得性边界。
- 2026-09-28：仓库先不引入代码依赖或复制外部项目实现；等实际分析方法确定后选最小工具链。对照了公开作品库的结构与许可说明，当前没有可直接复用且必要的代码。
- 2026-09-28：以 `docs/MASTER_PLAN.md` 作为项目总纲；保留 12 个业务板块的完整闭环，用 7 个较小执行阶段交付，所有阶段都要把结论接回 Speaking / Video Call 扩张决策。依据：用户要求及最终确定的业务流程方案。
- 2026-09-28：Stage 1 以八份季度股东信构建后续公司级趋势来源窗（2024 Q3–2026 Q2）；CURR 的公开 84% 仅按披露时点记录，不组成连续季度序列；Video Call 采用、因果留存和单位成本保留为内部数据需求。依据：SEC 股东信和 2026 Q2 10-Q 的披露口径，详见 `docs/kpi_tree.md`。
- 2026-09-28：Stage 2 将日本语母语中级英语学习者作为**优先验证人群**，不是确定的最终扩张市场；初学者引导式 Falstaff 与中级开放式 Lily 分开验证。依据：2024 Q3 英语细分使用披露、DRR-25-06 完成者研究及 Falstaff 摘要，详见 `market/market_opportunity.md`。
- 2026-09-28：市场/产品判断同时看开口参与、独立口语能力、体验质量、权益曝光与成本；自评信心、说词量或公司级 DAU 单独均不足以证明产品价值。VOC 仅用于提出假设，Stage 2 因直接 Video Call 样本与原 PDF 访问限制降级通过。依据：Stage 2 来源审阅、VOC 编码与独立复核。
- 2026-09-29：Stage 2.1 竞品与市场补强按 H1/H2/H3 的相同用户任务做六维比较，使用逐主张来源账本和条件性商业价值链；不以功能清单、跨平台 VOC 比例或无同口径的综合分替代证据。用户已亲自确认所供数据的真实性与来源；自选、编码可复算性及分层缺失仍限定结论。依据：`docs/STAGE2_REINFORCEMENT_STANDARD.md`、`docs/STAGE2_INPUT_INTAKE.md`。
- 2026-09-29：Speak 有日本 B1 课程与 Free Talk，但 2025 Immersive Free Talk 第一阶段不在 Course lessons；ELSA 2026 新版把 AI Conversation Coach 与 Role-Play Lab 分置 Coach / AI Chats 且分批推出。不能把不同入口/版本的功能拼成一个已普遍可用的竞品体验，也不能把“有课程与 AI 对话”当 Duolingo 独家。依据：`market/competitor_evidence_v2.csv`、`market/competitor_scenario_review.md`。
- 2026-09-30：Stage 2.1 经一次审阅**降级通过**。用户确认的 298 条是 Duolingo 自选态度样本，竞品另建 97 条逐项观察/48 URL；34 位可区分外部体验者中明确尝试目标对话功能最多 33 位，Babbel 亲测仅 3 位。H1 先测自然有效开口与盲评迁移，H2 单独测引导/纠错，H3 等成本和订阅替代阈值后测有限试用。Babbel 西语/法语页面列英语目标语，但日本账号资格未核实；两条 Babbel 讨论来自同一作者，按一位算。无跨产品效果或满意度排名。依据：`market/voc_quality_review.md`、`market/competitor_evidence_quality_review.md`、`market/stage2_decision_memo.md`。
