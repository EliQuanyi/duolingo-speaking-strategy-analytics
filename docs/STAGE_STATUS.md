# 阶段状态

更新日期：2026-10-03。此处记录**实际完成情况**，不把计划写成结果。产品证据截止仍为2026-10-02。

| 阶段 | 状态 | 收束证据 | 下一步 |
|---|---|---|---|
| 0 决策与范围 | 通过 | `DECISION_BRIEF.md` 已固定主决策、边界和官方资料起点 | 进入 Stage 1 |
| 1 证据与 KPI | 通过 | `docs/kpi_tree.md` Stage Review；10 个来源、12 个 core 指标、14 条可得性记录及表契约，CSV/链接检查通过 | 进入 Stage 2 |
| 2 市场与用户 | 降级通过 | `market/market_opportunity.md` Stage Review；33 条去重 VOC（仅 19 条直接涉及 Video Call）、3 直接竞品+2 替代、产品价值链与 H1–H3；CSV 汇总复算及独立审阅完成 | Stage 2.1 补强已完成；原 PDF 访问限制仍适用，现进入 Stage 3 |
| 2.1 用户与竞品证据补强 | **降级通过** | 用户确认的 298 条为 Duolingo 自选态度输入，机械质量复核见 `market/voc_quality_review.md`；三家竞品 97 条逐项观察、48 个 URL、34 位可区分体验者中明确尝试目标功能最多 33 位，审计见 `market/competitor_evidence_quality_review.md`；H1–H3 六维比较和一次 Stage Review 见 `market/stage2_decision_memo.md` | 进入 Stage 3；功能效果、留存、成本与权益净值留给 Stage 4/5 的阈值和实验 |
| 3 经营与 Driver | **降级通过（v1.2收束优化）** | `analysis/business_review.md` Stage Review / `analysis/data_quality_report.md`第9节；v1.1公司表/5图与累计18数值+2事件核验保留。新增3行基数桥接、2行研究输入、6行D类选择敏感度；8项收束检查（含1项复用公司QA）、独立Decimal复算、原验证脚本通过；Stage4比较对象契约写定 | 本轮三项优化完成；可进入条件性Stage4。全员ITT、自然使用/经营效果、成本、套餐替代、完整PDF及标准kernel仍未通过 |
| 4 量化机会 | **降级通过（证据约束核算与交接v2.0）** | `quant/stage4_final_delivery.md`；有限官方观察、逐主张/缺口、双臂直接模型、3单元direct输出、符号阈值/敏感度和研究分析覆盖；真实经济参数null，旧D退出正式论证。审核见`quant/stage4_final_validation.json` | 已交接Stage5条件性设计；P1不是预选。真实经济性/总体排名/当前资格、成本、传播、规模与标准kernel仍未通过 |
| 5 决策与实验 | **降级通过（条件性设计与正式产物）** | 一个H1迁移问题/primary、20项事件契约、决策卡；独立复核修正自然题目重合处理；Word COM同版PDF8页逐页检查，记录见experiments/stage5_final_validation.json | 启动资格/权限/评分及匹配baseline/N/MDE/窗口仍未满足；可进入Stage6展示 |
| 6 展示与复盘 | **降级通过（作品优化与本地交付收束）** | 11页Word/PDF商业报告、8页实验方案、2页Excel/PDF监控、81文件/25CSV白名单ZIP v1.1、复盘/SOP/复现与后续规划；实际导出/受影响页检查、58图点、独立解压复算及白名单约束核验，见`reports/final_delivery_validation.json` | 当前版本停止扩展；发布/招募/授权/真实数据集中列`docs/NEXT_PHASE_PLAN.md`。真实效果/Scale未执行；Excel原生Save/PDF仍未通过 |

## 当前下一步

**Stage0–6作品已完成本地整理、优化与收束**。统一入口`docs/FINAL_DELIVERY.md`，复核按`docs/REPRODUCTION_GUIDE.md`；需用户选择或外部授权/数据的事项统一列`docs/NEXT_PHASE_PLAN.md`，本轮不等待确认，不继续扩采或制造预测。H1为待验证的日本市场/日语L1中级英语任务，研究仅确认日语L1与课程条件，居住地区、设备、当前原套餐未知。Stage5唯一primary为延后未练情境盲评口语总分；P1尚未选定为试验。H2机制另列，H3检验净值；真实经济量保持null。日本App Store金额不可配对，资格仍未核；原PDF仍403。Stage4方法与原始来源审核结论保持不变。

**招聘作品公开交付（2026-10-03）**：本轮用户明确授权整理并上传GitHub。仓库首页、`docs/PORTFOLIO_CASE_STUDY.md`与`docs/PUBLICATION.md`提炼三岗位方法/证据/贡献；正式数据包保留既有81文件/25CSV范围。量化README补齐Stage5交接状态，方法/输入/结果未变，对应验收已重新执行。发布不是新的产品事实或试验结果；真实研究仍按下一阶段规划进入。

下一次启动先接真实增量/权限及冻结测量合同。有增量且有实施权限才验证公司权益；无平台权限可进行知情自然任务/学习研究，估计对象不等同权益扩张。Super单层试验不识别原Max传播；未补完整成本/账单/传播不判总体净值或Scale。Stage5已规定primary，但N/MDE/窗口/业务门槛仍须匹配真实数据预设。

**专项补强约束**：DRR完成者短期信号支持H1任务研究，不提供自然留存/收入uplift。当前v2以双臂全员差与符号阈值验收方法，不因无参数而制造三情景。实际经济性未通过；没有真实范围不作稳健排序或参数重要性排名。缺口与最低数据见`quant/stage4_gap_register.csv`。

历史v1共享m/u不能静默接实证；当前v2已允许双臂贡献和成本不同。源引用与契约声明须经人工审核，软件不认证来源或因果。完整政策各层效果与部署人数须对应同一政策曝光；教学预算须覆盖全部增量投入。未测间接层不设零；v1服务分钟/单价/参数域不继承为真实预算。

## 候选待办（不在当前阶段展开）

- 自然使用场景中，日本语母语中级英语学习者以外的人群外推仍需实验；Stage 2 不继续扩充自选 VOC 来替代代表性调查。
- 仅在模型敏感度需要时增加长期用户增长情景。
- 如后续取得同任务、同版本的实机观察或获授权的原始评论与采样框，以新数据版本重新审核竞品体验；不将本轮 34 位自选或目的抽样体验者扩写为总体偏好，其中 Babbel 的明确亲测仍只有 3 位。
- 有实际交互Notebook需求时修复本机ZeroMQ/kernel；当前真实direct执行及图表已可复现，不在本阶段批量升级环境。
