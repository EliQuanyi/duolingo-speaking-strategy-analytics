# 最终数据包字段与单位说明

版本final-v1.0，2026-10-03。具体表的完整列名、主键、行数、粒度和SHA-256在包内根目录MANIFEST.json；仓库镜像为data/final_package_manifest.json。指标意义在data/metric_dictionary.csv。空值表示未知、未披露或该字段不适用，按以下规则区分，不默认零。

## 公司指标与派生

- `period_start/period_end`为覆盖的季度边界；`fiscal_year/fiscal_quarter`为财年和季度；`metric_id`外键到指标字典；`scope`只限global_company。`value`为标准化值、`unit`为百万用户/百万账户/USD百万/比率，`aggregation_type`区分日均、月均、期末存量、季度流量或派生比率。
- `original_value/original_unit`为源显示值及单位；`transformation_note`描述identity/千美元转百万/差分或比率。`source_id/source_url/source_locator`记录出处和定位；`published_on/accessed_on`不是经营发生期。`evidence_label/derivation_type`区分披露与分析师派生；`input_lineage`为差分的两腿JSON，其他为[]。
- `precision_million`为披露步长（差分为两腿步长之和），不是标准误；派生M008值0表示没有另加披露舍入步长，不声称基础值没有误差。`reported_yoy_pct`是原表同比百分比，`reported_yoy_*source_id/locator/precision_pp`保留出处和百分比显示步长；它与分析师复算同比不混用。
- diagnostics的`yoy/qoq_baseline_*`给基期、值和来源；`*_pct`为普通增长百分比；`*_rounding_low/high_pct`只覆盖披露舍入，不是CI。没有连续CURR或功能留存输入。`calculation_label`标派生方式。
- engagement的`comparison`为同比或环比，`baseline_period_end`是对应基期；`dau_log_growth_points = mau_log_component_points + ratio_log_component_points`；残差`identity_residual_points`仅检验算术精度。单位均为100×自然对数增长点，不是普通百分点、增长解释份额或因果贡献。
- commercial的四种bookings/revenue均为季度USD百万；两个`subscription_share_*_pct`分别除对应total；`*_ratio`为无量纲；`bookings_minus_revenue`为USD百万，不是利润、现金流或递延收入变动。
- robustness的`point_change/rounding_low_change/rounding_high_change`为对数项变化及披露舍入范围；`point_direction/direction_survives_disclosure_rounding`为方向判断；`verified_disclosure_corners`是实际枚举端点数，不是样本数；`bound_type/interpretation`限制解释。
- bridge的`current/prior_q1/q2_value`为本年/上年Q1/Q2公开值，`input_unit`逐行；`current/prior_qoq_pct`为普通百分比。`current/prior_qoq_log_points`为各年对数环比，`base_period_contribution_log_points`为上年项的相反数；`yoy_log_change`等于前者加基数项，`identity_residual_log_points`为恒等式残差。`source_ids/source_urls`给全部输入。它不完成季节调整或功能识别。

## 时间线与对账

timeline的`event_id`为一条披露主键；`event_date/event_date_precision/event_date_basis`是发生日期及依据，未知留空；`reported_on`是披露日。`feature/tier/platform/language_or_market/rollout_scope_text`是来源范围；`event_type/claim_type/status`区分计划、报告进度、管理层归因及背景。`not specified/most`不可转精确资格或百分比。

source_cross_checks的`primary/comparison_value`为同指标两次披露，`*_precision_million`为双方步长；`absolute_difference_million`是绝对差；`tolerance_million`为双方步长半和；`consistent_with_rounding`是对账判断。两来源、定位与日期保留；不修改主值迎合对账。

## 账本与契约

source_register的`source_id`是正式来源键，`tier`是A/B/C/D来源等级，`title/publisher/url`是来源元数据，`period_covered/geography_user_scope/source_locator`是使用范围；`planned_use/limitation/redistribution/verification_status`说明用途、局限、分享和核读状态。多条同公司来源不是独立重复研究。

metric_dictionary的`metric/definition/formula/unit/time_grain/population_and_window/aggregation_type`构成指标合同；`priority/source_id/tier/business_meaning/limitation/status`给使用优先及证据边界。availability逐指标列`availability_class/evidence_tier/observed_coverage/source_ids/critical_gap/fallback/allowed_claim/blocked_claim/decision_use`，并非观测事件。

competitor两表的`claim_id`为逐定位观察主键；`product/dimension/hypothesis`定义对象和六维；`region/language_level/tier/device_or_version/feature_scope/valid_as_of`定义目标比较条件，不自证用户实时资格。`claim_text`为自行概括，`claim_kind/evidence_grade/quality_status/verification_status`区分供给、内部研究、外部体验和审核；`source_url/source_locator/source_date/accessed_on`追溯原页。V2的`independent_unit_id`只用于研究/体验者去重，不是App账户样本；多行同人不增N。`comparison_limit`规定不能推断的结论。

driver的`driver_id/claim/claim_type`为诊断主张，`source_ids/data_inputs/calculation`追溯来源与方法，`alternative_explanation/disconfirming_check/unresolved_data`列反证和缺口，`evidence_strength/status/decision_impact`说明用途；不是已识别的因果driver系数。

Stage4主张账本的`claim_type/evidence_tier/support_status/estimand`与`allowed_use/forbidden_extrapolation`控制外推；`evidence_refs/source_urls/evidence_period/unit`提供出处和口径；`decision_impact/linked_gap_ids/reviewed_on`将结论接到缺口。撤销主张保留撤销状态，不成为产品事实。缺口账本逐行写最低数据、内外部路线、许可、关联主张、允许继续/阻止结论、下一步与停止点；字段名的完整原义由各行文本给出，不用数值评分替代重要性。

strategy逐`policy_id`列目标、真实增量、机制、利益、完整成本、风险、KPI、证据、行动、进入/停止Gate及经济状态；都是候选/合同，不是观测净值或实际审批。

Stage4五张公开表字段、时期、单位和未知处理遵循quant/evidence_assumptions.md与stage4_public_evidence_v2.md：公开观察`value`必须与`unit/evidence_type/comparability_status/limitation_code`一起读；公开JPY是未识别SKU的清单金额。研究覆盖人数为`assigned_n/analysed_n/not_in_analysis_n`、比例`not_in_analysis_percent`。经济差为空未知；未来同窗统一币种/原分配账户的贡献、成本与净差，由实际均值核算。N是匹配部署人数。符号系数不是真实弹性或重要性。

## 图与运行规格

figure_lineage的`figure_id/key`为图及原表键；`input_table/raw_value/unit/display_transform`给原值/原单位/显示变换；`source_id/source_url/boundary`给来源与禁用外推。F01比率乘100显示百分比，F03显示两位小数只为排版，原表精度保留。

event_spec的`spec_version/record_name/grain/collection_point/required_fields/unit/denominator_and_join/missing_zero_rule/purpose/access_and_privacy/readiness`分别为版本、拟记录名、粒度、采集点、字段需求、单位、原组连接及分母、缺席与零规则、用途、权限/隐私、未采集状态。20行是规格而非20个事件；所有标not_collected。内部字段清单不含任何实际账户、录音、付款或密钥。

输入JSON是设计合同而非观测：布尔/来源声明须人工核验，null未知，正整数分母与非负绝对成本等软件域检查不证明真实性。完整账单、失败/购后服务、共同观察窗、所有原分配者和跨层政策曝光须满足才允许经济输出。
