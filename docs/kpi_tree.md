# Stage 1 — KPI 树与数据可得性审计

核查日：2026-09-28。这里定义**要衡量什么、哪里有数据、哪里必须停止推断**；本阶段尚未抽取完整季度数值，也没有真实功能实验结果。

## 1. 决策驱动的 KPI 树

本项目把“持续活跃且得到有效口语练习的学习者”作为**分析方向**，不将它冒充 Duolingo 官方 North Star，也不在缺少用户级学习数据时虚构该人数。公司级 DAU 是规模背景；口语行为与学习质量需要独立观察。

```text
主决策：Max 维持 / Super 扩张 / 有限免费试用，先验证哪一个？
│
├─ A. 权益覆盖（可用）
│  └─ M010 Video Call eligibility rate [公司仅定性；精确值需内部]
├─ B. 实际口语行为（机制）
│  ├─ M011 7-day effective adoption [内部]
│  └─ M012 28-day spoken words / assigned eligible account [内部]
├─ C. 学习与留存价值
│  ├─ M013 randomized D30 retention effect [内部实验]
│  └─ M003 CURR [公司公开但非本功能效果]
├─ D. 订阅与经济性
│  ├─ M014 90-day incremental net contribution / assigned account [内部实验]
│  ├─ M004 paid subscribers + M005 subscription bookings + M009 subscription revenue [公司背景]
│  └─ 续费/试用转化、AI 单次成本、退款、渠道费、套餐替代 [按策略设指标；内部输入]
└─ E. 公司经营背景与护栏
   ├─ M001 DAU + M002 MAU + M008 DAU/MAU [公司背景]
   ├─ M006 total bookings + M007 GAAP revenue [辅助背景]
   └─ 学习完成率、客观口语测评、失败率、投诉、免费用户活跃 [未来实验护栏]
```

**12 个 core 指标**由 `data/metric_dictionary.csv` 的 `priority=core` 标记；M006、M007 为 supporting。权益 → 使用 → 练习 → 留存/付费 → 增量贡献是一条**待检验机制链**，不是已验证因果链。口语词数衡量练习行为，不等于语言能力提升；学习质量需要独立测评或护栏。

## 2. 公开资料可以支持到哪里

| 层级 | 已核实状态 | 后续允许的用法 |
|---|---|---|
| 官方数值 | 2024 Q3 至 2026 Q2 的八份股东信可提供 DAU、MAU、期末付费订阅、subscription/total bookings、GAAP revenue 的公司级季度原表。定义见 `S002`。 | Stage 3 抽取逐季数值、检查口径后做公司趋势与结构分析。 |
| 官方派生 | DAU/MAU = 季度日均 DAU ÷ 季度月均 MAU。 | 只作参与频率的方向性背景；不是官方 cohort 留存，也不是每月比率的平均。 |
| 官方有限披露 | `S001` 在 2026-08-05 信中陈述 CURR 约 84% 及 Video Call 向新增 Super 订阅用户扩展；`S010` 在 2026-05-04 信中陈述开始向 Super 扩展。两者不自动等于相应财季的期末值。 | 用带披露日期的陈述与产品事件，不补成连续指标序列或精确覆盖率。 |
| 需要内部数据 | 权益账户、通话完成、验证过的说词数、随机分组、D30、账单、退款与 AI 成本。 | Stage 5 定义埋点与实验；Stage 4 只做显式参数的情景/盈亏平衡。 |

`data/data_availability.csv` 逐项列出可得性、缺口、降级和禁止性推断。A/B/C/D 代表**证据等级**，`official_numeric / official_derived / official_qualitative / internal_required` 代表**可得性类别**；二者不可混为一列。内部尚无观测，证据等级留空。

## 3. 口径风险与数据质量边界

1. **时间分母不同**：DAU 是日均、MAU 是月均、付费订阅者是期末存量、bookings/revenue 是季度流量。DAU/MAU 和“期末付费订阅者 ÷ 季度平均 MAU”最多是背景比率，后者不能当真实转化率。
2. **CURR 不是 Cohort 留存**：官方定义中的 current user DAU 在此前七天还活跃过一次；Q2 2026 的约 84% 未给出可复算的聚合窗口。本阶段将它标作 `reported snapshot`，不作为八季序列。[原始定义](https://www.sec.gov/Archives/edgar/data/1562088/000162828026053299/q2fy26duolingo6-30x26share.htm)。
3. **交易额与会计收入不同**：subscription bookings 是订阅购买收到的金额，subscription revenue 是按会计准则确认的收入；total bookings 还包括广告、English Test 与 IAP。[10-Q 的定义](https://www.sec.gov/Archives/edgar/data/1562088/000162828026053603/duol-20260630.htm)。
4. **公司级指标不能识别功能效果**：产品推进与 DAU 同期变化，仍可能受其他产品、营销和一次性活动影响。公司的驱动解释标“管理层归因”；Video Call 的因果估计留给真实随机实验。
5. **数据获取不等于可再分发**：来源登记只放官方链接；Stage 3 若发布整理表，逐行标来源与转换，不复制整份 SEC 文件或受限第三方数据。

## 4. Stage 3 拟建数据表契约（Stage 1 只定义结构）

| 表 | 一行含义 / 主键 | 最小字段 | 注意 |
|---|---|---|---|
| `data/public/company_quarterly_metrics.csv` | 公司总体的一个财季 × 一个指标；主键 `(period_end, metric_id, scope)` | `period_start,period_end,fiscal_year,fiscal_quarter,metric_id,value,unit,aggregation_type,scope,source_id,source_locator,accessed_on,transformation_note` | `aggregation_type` 区分 `daily_average`、`monthly_average`、`period_end_stock`、`quarterly_flow`、`derived_ratio`；CURR 仅在报告期与聚合可比时入表。保留原始报告值和百万/千单位转换说明。 |
| `data/public/product_timeline.csv` | 一条披露的产品事件；主键 `event_id` | `event_id,event_date,event_date_precision,reported_on,feature,tier,platform,language_or_market,rollout_scope_text,claim_type,source_id` | 披露日与实际生效日分开；未知日期留空，不把“多数”换算为百分比。 |

计划窗为 2024 Q3–2026 Q2 八个财季，原始来源逐季列在 `data/source_register.csv` 的 `S004–S010` 与 `S001`。**本阶段没有生成以上两张数据表，也没有运行其质量检查。**

## 5. Stage Review

- **阶段与状态**：Stage 1，通过（2026-09-28）。
- **对应总纲板块**：04 KPI & Data System；交给 Stage 2 市场研究和 Stage 3 经营分析的指标口径与可得性边界。
- **本阶段决策问题**：哪些公开数字足以建立公司级背景，哪些产品效果必须通过内部实验验证？
- **本阶段产物**：`data/source_register.csv`、`data/metric_dictionary.csv`、`data/data_availability.csv`、本文件。
- **交接对象与下一行动**：市场研究者据此限定可测产品假设；数据分析者随后按表契约抽取八季公司级数据。此为模拟交接。
- **数据/图表版本**：指标和表结构 v1；本阶段无实际数值表、图表或复现命令。
- **Findings**：①八季官方季度来源可支撑公司级趋势；② CURR 和权益覆盖只能做有限的披露点；③ 用户级使用、留存效果与经济性需要内部数据。
- **Evidence**：`S001–S010`；定义以 `S002` 和 `S001` 为准，八份季度股东信均为 A 级原始披露；见可得性矩阵。
- **Business meaning**：经营分析能描述增长背景，却不能用来宣称 Video Call 带来的增量；策略价值需靠情景阈值和后续实验判断。
- **Decision impact**：Stage 2 优先验证需求和机制；Stage 3 建公司基线；Stage 4 做条件性经济性；Stage 5 预注册试验。
- **Hypothesis status**：Video Call → 更多练习 → 更好学习/留存/商业价值，均为待验证机制；公开披露只支持推进方向。
- **Unknowns / fallback**：功能使用、实验效果与 AI 成本未知；按 `DATA_POLICY.md` 使用定性披露、显式假设范围和实验设计，不补造数。
- **Checks actually run**：逐份打开八个 SEC 股东信链接，并核对 Q2 2026 10-Q 的 DAU/MAU/付费订阅/bookings 定义和 Q2 股东信的 CURR/Video Call 表述；SEC filing index 核对八份股东信的提交日。用 Python 标准库解析三张 CSV：10 个来源、14 个指标（12 core）、14 条可得性记录；检查列数、唯一 ID、跨表 ID、日期、来源引用及不存在虚构的季度成品表，均通过。检查仓库 Markdown 本地链接通过；独立只读复核提出的 CURR 时点与验收状态问题已修正。
- **Gate**：证据通过（原始链接、口径、缺口可追溯）；业务通过（区分可诊断的公司趋势与不可识别的功能效果）；决策通过（Stage 2/3 的研究输入与 Stage 4/5 的内部数据需求已界定）；相关性通过（指标均服务于 Speaking / Video Call 扩张或必要经营背景）。
- **Scope cut**：未抽取季度数值、未做市场 VOC、未估计功能效果。
- **Next stage input**：Stage 2 使用本指标树、来源登记、可得性矩阵定义目标用户与价值链；Stage 3 再抽取八季数值并实际运行数据质量检查。
