# Stage 3/4 分析数据清单

**当前冻结包请看[最终清单](../FINAL_PACKAGE_MANIFEST.md)和[机器清单](../final_package_manifest.json)，版本冻结2026-10-03。以下为历史Stage3/4工作记录，含未进入正式包的D表，不是最终成员白名单。**

历史版本：Stage3 v1.2；公司整理2026-09-30；审阅2026-10-02；财季截止2026-06-30。公司事实、研究输入和D假设分表，不替代VOC/竞品审计；Stage4 v2与最终包不读取旧D经济表或选择情景。

## 1. 文件与粒度

| 文件 | 行数 | 主键/一行代表 | 时间与用途 |
|---|---:|---|---|
| company_quarterly_metrics.csv | 64 | period_end + metric_id：一个公司季度指标 | 2024 Q3–2026 Q2；7数值指标+DAU/MAU。含1个Q4收入差分、8个派生比率。 |
| company_comparison_baselines.csv | 28 | period_end + metric_id：一个比较基期指标 | 2023 Q3–2024 Q2；只作同比和首季环比的7数值基期。 |
| product_timeline.csv | 16 | event_id：一条有来源披露 | 发生日期可能缺失，reported_on保留披露日；最晚披露2026-08-05。产品、计划和CURR/streak背景分别标注。 |
| source_cross_checks.csv | 32 | period_end + metric_id + comparison_source_id：重复披露对账 | 主表与后续比较列；保存双方精度与容差，不是新增测量。 |
| business_diagnostics.csv | 64 | period_end + metric_id：标准化指标及同比/环比 | 主窗口；计算基期和官方同比分别保留来源。 |
| engagement_decomposition.csv | 16 | period_end + comparison：一个同比/环比恒等式 | 主窗口；单位100×自然对数增长点。 |
| commercial_structure.csv | 8 | period_end：季度商业结构 | 两种订阅占比分开；同季bookings/revenue比值和差额。 |
| stage3_robustness_checks.csv | 3 | check_id：一个标题方向的舍入敏感度 | 2026Q2同比项减2026Q1同比项；DAU、MAU、参与代理。非因果效果或预测。 |
| stage3_base_period_bridge.csv | 3 | metric_id：一个同比变化的本期/上年基期桥接 | 2026Q1→Q2与2025Q1→Q2；基数项是减去上年变化，非季节调整。 |
| stage3_learning_study_inputs.csv | 2 | study_id + arm：研究一组的分配人数与已分析均值 | DRR-25-06，30天；人数与均值来源分别定位，PDF直接访问限制保留。不是公司经营样本。 |
| stage3_learning_selection_sensitivity.csv | 6 | scenario_id：一个未纳入者均值假设 | D类条件；假设全组后测差及归零阈值，不是全员ITT、成绩变化或显著性结果。 |

辅助权威表：[来源登记](../source_register.csv)、[指标字典](../metric_dictionary.csv)、[可得性/缺口](../data_availability.csv)。Stage 3使用S001、S002、S004–S010、S016–S018，共12份官方文件；URL、报告期、访问日、用途与限制在登记表和输入表。其余登记来源不是Stage 3数值证据。

学习增补另外使用已有S011/S015，同一研究的报告和公司新闻稿，不计为独立重复试验；2行输入不是新增2名受试者。D类表与公司64行事实主表严格分开。

## 2. 字段与缺失约定

### 两张公司指标输入表（相同 schema）

| 字段组 | 含义 |
|---|---|
| period_start / period_end / fiscal_year / fiscal_quarter | 日历财季；YYYY-MM-DD边界、财年整数、季度1–4。 |
| metric_id / value / unit / aggregation_type / scope | 指标字典ID、归一数值、单位、聚合方式、global_company；日均/月均/期末存量/季度流量/派生比率不得互换。 |
| source_id / source_url / source_locator | 对应登记ID、直接原始URL、文档页/表/行/叙述定位；多来源以管道符分隔。来源数不等于独立证据数。 |
| published_on / accessed_on | 披露/访问日期；多来源派生值的published_on为最晚输入披露日，各输入定位保留于lineage。 |
| original_value / original_unit / transformation_note | 原显示值与单位、转换说明；千美元÷1000转百万美元。派生比率original_value空；Q4差分原值为计算值而非直接披露。 |
| evidence_label / derivation_type / input_lineage | 来源事实、官方数值派生显式分类；direct / ratio / annual_minus_ytd。差分lineage为JSON两腿，保留年度/九个月范围、源定位和精度；其余[]。 |
| precision_million | 标准化显示步长，不是标准误或统计CI；Q4差分为两腿步长之和0.002百万美元。M008为0表示确定性计算字段，不表示基础测量无误差。 |
| reported_yoy_pct / reported_yoy_source_id / reported_yoy_locator / reported_yoy_precision_pp | 官方报告同比、独立来源/定位、显示步长（整数百分比为1个百分点）。不得与分析师复算同比混同。 |

指标：M001 DAU、M002 MAU、M004付费账户、M005订阅bookings、M006total bookings、M007total revenue、M008 DAU/MAU、M009订阅revenue。用户/账户为百万，财务为USD million，比率为0–1；没有分市场、订阅层级或功能用户的数据。当前必需数值/来源字段无缺失；派生比率和无官方季度同比的差分行允许原值/官方同比相关字段空值。**空值表示没有该披露，不是0**。

### v1.2增补表字段

- 基数桥接：current/prior_window与四个输入值保留比较期；input_unit区分百万用户与比率。current/prior_qoq_pct为普通百分比，其余log_points为100×自然对数增长点；source_ids/URLs指向原季度来源；evidence_label为官方值派生，不是功能效应。
- 学习输入：assigned_n为原随机分组人数；analyzed_n及pre/post_mean属于最终合规完成者。count/mean_source_id、URL、locator分别保留人数与均值定位；population/window、unit、accessed_on、verification_limit保留外推/访问限制。未纳入人数由两人数相减，不将其自动解释为失访。
- 选择敏感度：shift_assumption和excluded_mean_assumption为明确D类假设；hypothetical_assigned_post_mean及difference为条件加权结果；direction只是均值方向。真实未纳入者成绩、概率、方差、CI、p值和完整ITT均没有填入。computed_on不是原研究采集日。

### 产品事件

event_id、event_date、event_date_precision（day/month/quarter/unknown）、event_window_start/end、reported_on分别标识事件、可能的发生日期/窗口及披露日。16行中2个day、1个month、1个quarter、12个unknown；12个未知发生日期保持空，不能据披露日生成上线效果窗口。

feature、tier、platform、language_or_market、rollout_scope_text为源陈述范围；claim_type、event_type、status区分计划/报告事实/管理层归因与背景；source_id/URL/locator、accessed_on、limitation及event_date_basis保留证据与日期依据。not specified不表示全球全量覆盖，most不转换成精确百分比。事件不是随机干预样本。

### 对账与派生表

- 对账：primary/comparison_value、absolute_difference_million、primary/comparison_precision_million、tolerance_million、consistent_with_rounding、双来源ID/比较定位；容差=(两端步长之和)/2。不修改真实值以迎合对账。
- business_diagnostics：沿用指标/期间/范围；yoy/qoq各保留baseline_period_end/value/source_id、pct、rounding_low/high_pct；calculation_label说明分析师派生；官方同比及其源字段独立保留。M008舍入区间留空，不伪造置信区间。
- engagement_decomposition：comparison与baseline_period_end区分yoy/qoq；dau_log_growth_points、mau_log_component_points、ratio_log_component_points、identity_residual_points；unit/scope、当前/基期source_id与interpretation约束解释。
- commercial_structure：两种订阅/总体bookings与revenue金额均USD million；subscription_share_of_total_bookings_pct与subscription_share_of_total_revenue_pct分别使用对应分母；bookings_to_revenue_ratio无量纲、bookings_minus_revenue为USD million。source_id、calculation_label和interpretation保留。差额不代表利润、现金流或递延收入变动。
- stage3_robustness_checks：check_id、quantity、comparison标记被检验的同比项变化；point_change与rounding_low/high_change为100×自然对数增长点，point_direction及direction_survives_disclosure_rounding记录方向；source_ids列全输入源，bound_type/interpretation明确非统计CI与非因果；verified_disclosure_corners=256为八个DAU/MAU舍入输入端点的实际枚举数，不是256个用户或独立样本。

补强明细位于analysis/：`stage3_source_audit.csv`10行/13字段，check_id主键，列源、值、单位、定位、范围、状态、限制、日期与独立采集者角色；`stage3_gap_register.csv`10行/11字段，gap_id主键，列缺量、现有证据、最低补证、外部可得性、允许/阻止推断、关联阶段、严重性、行动和停止条件。二者分别是人工作业审计与方法需求，不是经营事件数据，也不由Notebook生成。研究方法另见 [因果链复核](../../analysis/stage3_causal_chain_review.md)。

## 3. 获取、使用及复现

原始文件为公开SEC股东信/10-Q/10-K，按来源定位人工读取必要事实并保留转换轨迹；不在包内复制整份文件、大段原文、私人账号信息或评论原文。本项目分享必要数值事实及自己的计算结果；不声称第三方文档或网页受仓库代码许可覆盖，也不附带对其全文的再分发授权。

**可复现边界从这些公开CSV开始**，不是网页抓取自动化。ignored临时抽取JSON不参与运行；不需要Cursor/Reddit凭据。当前运行环境与版本、独立审计覆盖及未达项见 [质量报告](../../analysis/data_quality_report.md)。

```powershell
# 仓库根目录，现有Python环境
python -B scripts/run_stage3.py --check-only
python -B scripts/run_stage3.py --execute-direct
python -B scripts/verify_stage3.py --rebuild
python -B scripts/review_stage3_limits.py
python -B scripts/closeout_stage3.py
python -B scripts/closeout_stage3.py --check-only
```

direct在新Python进程真实执行Notebook普通代码单元，更新3派生CSV、5 PNG、Notebook真实输出及analysis/stage3_validation.json。PNG位于Git忽略目录analysis/figures，Notebook保留真实图输出；其他工作树运行命令后恢复报告图片。标准`--execute`仍使用真正Jupyter，本机ZeroMQ socket失败，kernel验收未通过；依赖安装及其他系统运行尚未验证。

输入变化需重新执行并更新审阅/本清单，不手工编辑派生结果。质量验收：33类本地QA、55官方同比舍入对账、32跨文件对账、累计18数值对象+2事件独立源核验、4错误输入拦截、9单元实际执行；3 CSV/5 PNG再执行哈希一致。补强脚本另生成3行方向稳健性并枚举256端点。公司表计算不识别功能因果、留存、学习或净收益；另有已登记公开学习试验的受限信号，不能当这些表推导的效果。

## 4. 当前CSV的SHA-256

校验值为本次实际读取文件字节计算，变化后必须重算；不是数字签名或来源真实性保证。

| 文件 | SHA-256 |
|---|---|
| company_quarterly_metrics.csv | 937a01ab139393fb92b7826d3a89d800add7d596a58072d5f684062ff6aba2e9 |
| company_comparison_baselines.csv | 565669c38a08de08523e60fceee68061a7fd4a14ef9450c29c7878b2e5b3bbd3 |
| product_timeline.csv | 9b660a4183febadd9d54e331ed00c5d96dc4971d076588635d9120958617d665 |
| source_cross_checks.csv | 37ace655c1dfea7744cb4021d1d43b3249cfa018e9a6c0925712e4f157a8eb02 |
| business_diagnostics.csv | 7b34ca06cdc66b29f3d7ca1a5bb434150dfa5695e4e535439b819dc9145254ca |
| engagement_decomposition.csv | a9882dc9aaf8f7ef4588ec3009caaf81759b99b657faffecfffeb4dcb8133e17 |
| commercial_structure.csv | 2dc34a8d91562a880f203448a4729996201c2263473234dad71185cb1147d882 |
| stage3_robustness_checks.csv | 93c7fb843374836efaf83c757e553d437e48ae61ed8ec865247e81ac2bd79ebf |
| stage3_base_period_bridge.csv | 394c9afad6cf3c140f2654e618d53415c8b5b967a07367907c80b0834bb4fbbe |
| stage3_learning_study_inputs.csv | c12101a41efd2a12b964fa2174488590b5a4809bef0a0cedd66669f3c6bc72b3 |
| stage3_learning_selection_sensitivity.csv | 7786d12f8b7386379e098c3d5644fd99ea33c1df7213f01d9d166d54c758e6f0 |

两份补强明细的当前SHA-256：analysis/stage3_gap_register.csv为3f34c5f690b1bc0bd325feb73531df48b7e4d5a91a4722ac7338a36a1c21a4a8；analysis/stage3_source_audit.csv为94f0c6db9cf5bb3322c9984322aeb1dfd05d549011a178fe95f8b185cf4ae993。它们的人工核查不能由哈希替代。

主表、基期、事件、字典和来源登记的输入哈希也由analysis/stage3_validation.json在实际执行时记录。主表中的公司测量口径、缺口和舍入精度不得因重建而静默修改。


## 5. Stage4 条件性量化增补（2026-10-02）

> **历史v1：本节D表不属于当前Stage4正式交付和数据包。**当前范围见第6节，来源/方法/验证入口均切v2；旧字节和审核记录仅供历史追溯。

前四节保留Stage3事实与质量快照；本节四张表全部D假设派生，与公司/研究事实分开。权威输入为 `quant/scenario_inputs.json`，实际参数 `real_parameters`、总体规模、权重和总固定费留空。来源表新增S019/S020历史官方供给，当前逐账户权益仍未核；原公司数据表未更改。

| 文件 | 行数 | 主键 | 用途与限制 |
|---|---:|---|---|
| scenario_results.csv | 27 | policy_id + scenario_id + original_tier | D每原分配账户的90天贡献/双臂成本与变量归一化；无总体预测 |
| stage4_billing_paths.csv | 81 | policy_id + scenario_id + original_tier + path_id | D完整计费箱边际概率及贡献/工作量；不是观察用户或联合潜在路径 |
| stage4_break_even.csv | 18 | policy_id + scenario_id + original_tier | D条件gain/loss/工程单价阈值；正零负分母及概率可行性 |
| stage4_sensitivity.csv | 360 | policy_id + gain_rate_demo + loss_rate_demo + unit_cost_demo_usd_per_service_minute | D参考赠送工作量下联合扫描；非现实合理域/CI/样本 |

参数与策略表位于quant：`parameter_register.csv`逐标量JSON指针/单位/证据/时期/范围依据；`strategy_comparison.csv`三政策的对象、机制、收益、成本、风险、KPI、强度和停止规则。输入账本中的空值是未知，CSV中未定义阈值为空，P0的相对零值不代表绝对成本为零。

字段：scenario表含gain/loss、control/treatment贡献及服务量、offer/effective量、Δm/Δc、D分摊f和变量每千人；路径表q0/qp/Δq分别守恒，同箱共同m/u是D额外假设；阈值表分开gain可行盈利存在与阈值点可行，约束方向随分母符号；敏感度表不含观测概率。所有表保留evidence_label与input_ref/boundary，统一90天/USD只是设计口径。非赠送调用与赠送调用标签互斥，后续付费成本未遗漏；有效分钟不是服务分钟。

运行：`python -B scripts/run_stage4.py --execute-direct`；只读输入契约：`--check-only`；独立复核：`python -B scripts/verify_stage4.py --check-only`。现有环境6代码单元真实direct执行、3HTML表/2嵌入PNG；标准kernel未通过。派生CSV、参数/策略CSV、Notebook与2PNG共9件重复构建字节一致。实际记录见 [Stage4审核](../../quant/stage4_validation.json)，业务用途与Stage5补证见 [商业复盘](../../quant/stage4_business_review.md)。

### Stage4四表SHA-256

| 文件 | SHA-256 |
|---|---|
| scenario_results.csv | 4b5fa60f06a4c221d08b1022548f7c169254545fc78fdc5ab3cbc13c3dbc1ffb |
| stage4_billing_paths.csv | dc794a2b98bd9ad6fc89c62327d2ae2731f61cd01331531c2ab87656ffc20b1f |
| stage4_break_even.csv | 04951ec6333bb8add8a7fb05ed35ee7e4cdc9b4923b7ccefb6e174a172de738d |
| stage4_sensitivity.csv | 24d397634b8d4b17f3f4545413070f611901366106921596e5f781e51e0ff3da |

这些哈希只检查当前字节一致，不是原来源真实性或实际经济效果认证；后续输入改变后需重新构建、独立审核并更新本清单。Stage6冻结ZIP尚未生成。

## 6. Stage4 v2正式交付（2026-10-02）

当前版本stage4-v2.0；主报告为 [Stage4最终交付](../../quant/stage4_final_delivery.md)。v1经济D文件只供历史审计，不从目录全量打包。当前包只采用下列五表、v2主张/缺口/策略、当前模型及方法；Stage6冻结ZIP仍未生成。

| 文件 | 行数 | 主键 | 用途与边界 |
|---|---:|---|---|
| stage4_public_observations.csv | 28 | observation_id | 官方事实/计划、不可比报价、研究访问/分母；不是28个独立样本 |
| stage4_learning_coverage.csv | 2 | study_id + arm | 同研究人数未纳入比例，非采用/全员ITT/商业uplift |
| stage4_economic_readiness.csv | 6 | policy_id + original_tier | 双臂经济差、范围和缺口；当前经济结果为空未知 |
| stage4_policy_readiness.csv | 2 | policy_id | 总体经济值未知，部署-效果范围匹配也未核 |
| stage4_symbolic_sensitivity.csv | 8 | parameter | 会计与设计约束，无实证扫描域或数字经济门槛 |

### 字段、时间、单位、来源

- 公开观察：question/evidence_type/source_id/URL/发布修改覆盖访问时间、observed_region/device/account_scope和target_scope分开、locator/field/value/unit/comparability/limitation。购买周期、SKU、个人/家庭、当前Lily额度为空；标价单位JPY/未辨识购买项。来源S001/S019/S011/S015及新增S021（保留PEV2别名）。未知输入/访问结果与实际事实分别标类型；不以空值证明不存在。
- 研究覆盖：assigned_n、analysed_n、not_in_analysis_n（人）、not_in_analysis_percent（百分比，1位小数）、四个原观察ID、来源/日期/窗口/人群和解释。仅30天规定使用研究的分析覆盖；精确起止日、居住地及设备未核，原PDF仍403。
- 经济就绪：原套餐层与政策、效果范围、人群、期间/币种、两臂贡献与成本差及变量净差、部署N、缺口和边界。当前均值未知；结果空白不是0。未来单位为同窗统一币种/原分配账户，包含零使用。
- 政策就绪：真实增量声明、部署-效果匹配声明、整体净值/币种/状态及条件，当前未知。整体金额需要所有受影响层、匹配N与新增F，不默认其他层零效果。
- 符号敏感度：parameter/expression/meaning/condition/empirical_status；+1/-1是数学常数，不是估计响应或真实参数重要性。

公开页面按有限官方核读手工整理，必要数值与自行概括可分享；不再分发完整网页、PDF、评论、私人账户或认证。CSV起的转换可复现，网页核查不自动刷新。

### 构建及实际验收

`python -B scripts/run_stage4_final.py --execute-direct`在新Python进程实际执行3个普通单元；`--check-only`只读对账。公开观察是人工输入，其余四表由当前模型与该观察表生成，不读取v1 D输入/结果。研究分母来源须唯一且同窗同单位。符号边界不提供真实收益估计。

`python -B scripts/verify_stage4_final.py --check-only`独立复算与边界检查；`python -B scripts/closeout_stage4_final.py --check-only`检查最终记录及当前引用。记录见 [stage4_final_validation.json](../../quant/stage4_final_validation.json)：表键/字段、主张-缺口-正式源引用、作者文档链接、未知传播、D隔离、Notebook保存输出与当前入口。测试fixture仅验证源码内，不写业务表；标准kernel、真实经济性与试验执行未通过。

四张派生表当前SHA-256：

| 文件 | SHA-256 |
|---|---|
| stage4_learning_coverage.csv | 411f30856b552ba2f728633033476a256b4b318264943322a513ca355ca7d005 |
| stage4_economic_readiness.csv | aac57354e615e0b4d15da4054dfe7533b29ae95533c1dd8bb65056f74148b4e5 |
| stage4_policy_readiness.csv | 28224761bd6153c9fe4d23a0c3e37f49adaba17bf55f407f91c2486bfd0e453b |
| stage4_symbolic_sensitivity.csv | a87b28001bf43434d3cd6587b8847b59b2dcbcb065a54fa4976eb03967684e58 |

公开观察、模型/Notebook、账本/策略/方法/报告/来源等校验值见最终JSON。校验值只能验证字节一致；当前版本仍是工作交付，不能称公司实际权益、经济效果或全量来源鉴证。
