# Duolingo AI Speaking｜商业量化、市场调研与数据分析案例

**English summary.** An independent public-source case study assessing Duolingo Video Call expansion. It connects task-based market research, quarterly business diagnostics, evidence-constrained economic accounting, and a conditional experiment plan. The author defined and reviewed the business scope and supplied confirmed Duolingo attitude inputs; Codex assisted with research organization and analysis code. No causal business uplift or realized ROI is claimed.

作者：Quanyi Liu｜整理：2026-10-03｜产品证据截止：2026-10-02｜公司经营窗口：2024 Q3–2026 Q2，财务数据截至2026-06-30。

**项目结论：先确认现行权益与真实新增，再验证自然使用下的学习迁移；目前不能判断扩张盈利或选出权益策略赢家。** 本案例适用于商业量化分析、市场调研和数据分析岗位的作品评审。这里的 Quant 指商业决策量化，包括增量核算、盈亏条件、敏感度与验证设计；研究对象是产品权益与投入，未涉及金融交易策略、投资回测或证券推荐。

快速阅读：[商业报告 PDF](../reports/executive_decision_book.pdf) → [决策卡](../reports/decision_card.md) → [最终交付与验证边界](FINAL_DELIVERY.md)。

## 决策问题与作者贡献

主问题是：**Duolingo 是否值得继续扩大 Speaking / Video Call，下一轮应验证什么？** 候选政策限定为 P0 真实现行权益、P1 候选 Super 新增访问和 P2 候选免费有限试用。P1/P2 必须先证明相对 P0 存在真实增量，不能把已开放权益重复计入扩张机会。

优先任务 H1 是日语母语学习者的中级英语口语练习；日本市场、当前设备、套餐与账户资格仍待核实。任务优先支持继续研究，尚不构成 P1 政策选择。业务范围见[决策简报](DECISION_BRIEF.md)，当前政策边界见[Stage4 最终交付](../quant/stage4_final_delivery.md)。

**已确认的个人贡献**：作者定义并审阅业务范围，提供并确认 Duolingo 侧态度数据。Codex 辅助公开资料整理、分析代码及交付制作。下文的方法和产物说明项目实际包含什么，不将全部 AI 辅助计算表述为作者独立手写实现，也不据此声称公司任职、客户委托或真实产品上线经历。面试讨论可结合具体文件解释业务取舍与方法限制。

## 三类岗位：方法如何落到可审查产物

| 岗位相关能力 | 项目采用的方法 | 可核查产物 | 证据边界 |
|---|---|---|---|
| 商业量化分析：定义增量、收益与投入 | 真实 P0 对照；原套餐分层；同人群、币种、成熟窗口下的全员双臂贡献/服务成本差；符号盈亏平衡；新增固定费只扣一次 | [核算契约](../quant/evidence_assumptions.md)、[模型代码](../quant/evidence_model.py)、[Notebook](../quant/evidence_model.ipynb)、[策略比较](../quant/strategy_comparison.csv) | 真实经济均值、部署人数与固定投入为 `null`；没有真实 ROI、收益金额或盈利排名 |
| 市场调研：从用户任务形成可证伪问题 | 按任务/覆盖、学习机制、体验、激活习惯、订阅替代、成本防御性六维比较；提供方主张与体验反例分开；区分观察、URL 和体验者；审阅自选偏差 | [市场结论](../reports/market_final_review.md)、[六维比较](../market/competitor_scenario_review.md)、[竞品质量复核](../market/competitor_evidence_quality_review.md)、[VOC 质量复核](../market/voc_quality_review.md) | 不是代表性调查或作者亲自进行的全量实机测评；供给目录、评论比例不能证明产品胜负或总体偏好 |
| 数据分析：经营诊断与可复现交接 | 来源/指标口径登记；缺失、重复、单位及跨文件对账；流量与存量分离；同比/环比、订阅结构、对数增长恒等式与当期/基数桥接；图表逐点溯源 | [经营复盘](../analysis/business_review.md)、[Notebook](../analysis/business_review.ipynb)、[季度数据](../data/public/company_quarterly_metrics.csv)、[图表溯源](../reports/figure_lineage.csv)、[质量报告](../analysis/data_quality_report.md) | 公司级描述与算术拆解不能识别 Video Call 因果；CSV 起可复算，网页抽取未自动化 |

实验设计作为三类工作的交接：一个主要学习指标、原分配账户分析、缺测敏感度、课程/质量/成本护栏，以及事前 Scale / Iterate / Stop 规则。见[实验方案](../experiments/test_plan.md)与[事件契约](../experiments/event_spec.csv)。这是可实施条件尚未满足的预案，未执行真实 A/B。

## 关键发现与商业行动

| 发现 | 支撑证据与限制 | 由此改变的行动 |
|---|---|---|
| “课程 + AI 对话”已经有同行供给，差异化须落到有效练习与迁移 | 同任务市场比较支持候选机制；没有统一任务、版本和评分下的效果排名 | 优先验证 H1 的延后未练情境表达；独立测评，保留零使用者与退出者；H2 引导任务另测 |
| 公司活跃结构改善，不能作为功能成功证明 | 2024 Q3–2026 Q2 的 DAU/MAU 从32.9%增至41.7%，是季度平均值之比的参与代理；公司表口径与原始 URL 可追溯 | 把公司趋势作为背景；不把比值称留存，也不将增长填作功能采用或收入提升 |
| 购买金额与收入确认增长分化，需要完整账单核算 | 2026 Q2 订阅 bookings 同比约10.1%，订阅确认收入约22.5%，由披露值复算；二者均为季度流量，期末账户为存量 | 冻结贡献口径、计费与退款成熟窗口；升级/续订去重，不用期末账户推造功能 ARPU |
| 当前权益增量、完整成本与套餐传播仍未知 | 公司总体 Super 扩展陈述不是目标账户资格快照；标价缺同 SKU/期限；单层试验不能识别原 Max 传播 | 先核真实增量与权限；无增量停止该政策定义；缺完整经济证据不判总体净值或批准商业扩张 |

经营数值来源为[季度表及输入溯源](../data/public/company_quarterly_metrics.csv)和[经营复盘](../analysis/business_review.md)；原始官方出处包括[2024 Q3 股东信](https://www.sec.gov/Archives/edgar/data/1562088/000156208824000248/q3fy24duolingo09-30x24shar.htm)、[2025 Q2 股东信](https://www.sec.gov/Archives/edgar/data/1562088/000156208825000165/q2fy25duolingo6-30x25share.htm)及[2026 Q2 10-Q](https://www.sec.gov/Archives/edgar/data/1562088/000162828026053603/duol-20260630.htm)。单位、报告期和转换留在原表，公司来源核读截至2026-09-30；上述增速不是实验效应。

量化交接采用 `Δv_s = Δm_s − Δc_s`，完整政策采用 `V = Σ_s(N_s × Δv_s) − F`。两臂均值含全部原分配账户，直接差不再乘采用率；各原套餐层效果与部署人数必须对应同一政策曝光，未测层不设零。教学投资可按学习/课程挤出护栏与真实批准预算评价，但预算须覆盖完整增量服务、其他及固定投入，教学批准不等于盈利。当前缺失值仍保持未知，具体定义见[当前 v2 方法](../quant/evidence_assumptions.md)。

## 数据体量：每个数字指什么

| 数据或产物 | 数量与期间 | 正确解释 |
|---|---|---|
| Duolingo 态度输入 | 298条自选记录，2026-01-01至09-28；质量审阅截至09-30 | 作者提供并确认的单产品态度输入，不是298位独立用户；原文与编码轨迹不足，不估总体痛点发生率；私人原始内容不收入正式共享包 |
| 三家竞品账本 | 97条逐项观察、48个 URL、34位可区分体验者；查阅截至2026-09-29 | 观察行、URL、体验者分别计数；明确尝试目标功能的最多33位；同人/同研究可有多行，不能相加为独立样本量 |
| 公开公司经营 | 2024 Q3–2026 Q2，共8季度；7个公开数值指标及 DAU/MAU 派生值共64行 | 8个时间点，不是64个独立时间样本；额外比较基期仅用于同比与桥接 |
| 拟采集实验事件 | 20项事件契约，设计日期2026-10-03 | 是未来字段与测量要求，不是20条实测事件、参与者或试验结果 |
| 正式展示 | 11页商业报告、8页实验方案、2页监控视图 | 页数是交付范围，不是证据量；监控是设计快照，未连接生产数据 |

计数方法、原来源 URL 与限制见[市场结论](../reports/market_final_review.md)、[竞品质量复核](../market/competitor_evidence_quality_review.md)、[VOC 质量复核](../market/voc_quality_review.md)、[来源登记](../data/source_register.csv)及[最终交付](FINAL_DELIVERY.md)。已有公司随机设计研究只提供特定完成者短期学习信号；它不是本项目实施的试验，不能代入自然全员经营效果。

## 交付、复现与未完成部分

本作品将市场问题、经营诊断、量化条件、实验和未来监控连成可审查的决策交接。报告/实验有 Word 与 PDF，监控有可编辑 Excel 与两页快照；方法复用见[SOP](reusable_sop.md)，执行取舍见[复盘](retrospective.md)。核心表、图点与 v2 方法的实际检查记录见[最终交付](FINAL_DELIVERY.md)，最小复算路径见[复现指南](REPRODUCTION_GUIDE.md)。

已验证计算起点为共享 CSV，Notebook 普通代码单元的 direct 执行有真实输出；标准 Jupyter kernel 尚未通过。监控 PDF 是最终 Excel 的栅格快照，正文不可搜索；Excel 原生保存/打印验收受本机许可限制。哈希与复算证明文件一致、计算可复现，不认证来源真实性或因果。

当前未完成的是实际权益资格/授权、平行任务与评分校准、匹配 baseline/N/MDE/窗口、真实账单和完整成本、Max 传播与部署规模。需外部资源的事项见[后续规划](NEXT_PHASE_PLAN.md)。无平台权限时，可开展知情学习/任务研究，但估计对象须按实际处理重写，外部结果不能填公司权益收入模型。

## 可用于简历的三条表述

以下为学习项目表述，保留 AI 辅助与贡献范围，不写作实习或工作业绩：

- **商业量化方向**：定义并审阅 Duolingo Video Call 扩张分析范围，借助 Codex 辅助形成现行权益、Super 增量及免费试用的策略比较，明确全员双臂贡献/成本核算、盈亏条件与停止规则；真实经济参数保持未知。
- **市场调研方向**：提供并确认298条 Duolingo 自选态度记录，在 Codex 辅助的同任务竞品研究中结合六维比较与证据质量复核形成学习迁移验证问题，明确观察、URL、体验者与代表性限制。
- **数据分析方向**：围绕产品扩张决策开展 AI 辅助公开数据分析项目，将2024 Q3–2026 Q2经营趋势、当期/基数桥接和订阅购买/收入确认差异连到验证需求，交付可从 CSV 复算的分析材料与商业报告。

## 面试可讨论的四个取舍

1. **为何不估一个 ROI？** 解释缺失账单、完整服务成本、套餐传播与部署规模怎样阻塞净值；展示符号盈亏条件仍如何指导下一条数据请求。
2. **为何不把更多评论等同更强结论？** 用观察/URL/体验者的不同分母说明重复来源、自选偏差、同任务相关性，以及为何应停止扩采。
3. **如何从增长图走到业务判断？** 演示对数恒等式与当期/基数桥接，解释 DAU/MAU 代理、存量/流量和管理层归因的边界。
4. **如何审查 AI 辅助工作？** 说明业务范围由谁确认，选一张表或图追到字段、公式、CSV 与源 URL；区分已复算的方法、未来试验规则和真实尚缺数据，并如实说明个人承担的部分。

本页整理既有作品，不新增产品观测，不更改 Stage4 v2 冻结对象；引用以当前正式入口和源文件为准。
