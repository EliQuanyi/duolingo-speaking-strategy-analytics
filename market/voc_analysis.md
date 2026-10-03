# VOC 探索性分析：AI Speaking / Video Call

版本：2026-09-28。证据级别：**C（自选公开 VOC）**。分析单位为一条公开用户评论或评价，不是独立用户、使用次数或功能效果。仅为 Duolingo Speaking / Video Call 扩张决策生成待测假设。

## 采样与可复现性

| 项目 | 本次规则与实际结果 |
|---|---|
| 时间窗 | 目标检索窗口为 2026-01-01 至 2026-09-28；采集日 2026-09-28。5 个 Reddit 讨论帖的发帖时间落在该窗口，但所选评论的绝对发表日无法逐条核实，因此不能断言 19 条评论全部落在窗口内。Trustpilot 14 条中，11 条有明确的评价发表日，3 条只显示相对发表/更新时间；后者日期留空。 |
| 平台与产品 | Reddit：19 条 Duolingo Video Call 评论，分属 5 个讨论帖；Trustpilot：14 条评价（Praktika AI 8、Talkpal 5、Duolingo 通用口语体验 1）。合计 **33 条、2 平台、33 个不同单条 URL**。通用 Duolingo 评价不视为 Video Call 使用证据。 |
| 检索入口 | Reddit 网页搜索使用 `site:reddit.com/r/duolingo/comments/` 加 `video call`、`Lily`、`speaking`、`Super`、`worth` 等词；逐帖查看发言，使用评论时间链接获取单条评论 URL。Trustpilot 查看 [Duolingo](https://www.trustpilot.com/review/duolingo.com)、[Talkpal](https://www.trustpilot.com/review/talkpal.ai)、[Praktika 首页](https://www.trustpilot.com/review/praktika.ai)及[第 5 页](https://www.trustpilot.com/review/praktika.ai?page=5)的用户评价，并从评价标题链接取得单条 URL。两个平台的列表或讨论页在采集时可读；Trustpilot 的单条 URL 在本研究工具中被限制直接打开，但列表页显示相应评价及链接。 |
| 纳入 | 单条可定位、与实际口语练习、AI 对话、反馈、可靠性或权益配置直接相关的第一人称体验；保留明确正面、负面与混合评价。 |
| 排除 | 机器人、公司员工回复、广告/推广、无使用经历的泛泛猜测、仅谈棋类或一般付费抱怨、无内容星级、重复链接和大段转述他人。 |
| 去重与隐私 | 以评论/评价 permalink 去重；同帖不同评论为不同项，不推断独立用户。CSV 不存用户名、头像、原文、联系方式或个人经历细节；中文释义只保留与决策有关的意思。 |
| 原始资料限制 | 平台内容可查看不等于可再分发。公开数据包仅包含短释义、代码、日期和链接；不包含评论全文。评论可能被编辑、删除，需以采集日及列表页复核。 |

字段说明：`source_url` 为单条评论/评价 URL；`listing_url` 是可回查的原讨论页或评价列表页；`source_date` **只记评论/评价发表日期**，采用 Trustpilot 评价顶部的绝对日期，不采用正文下方的“体验日期”。例如 T06 顶部为 2026-07-26、下方体验日期为 2026-07-01；T11 顶部为 2026-09-21、下方体验日期为 2026-09-10。仅显示相对日期或更新时间的记录留空，`date_precision=unknown`；Reddit 评论同样留空。`accessed_on` 为采集日期；主题代码和情绪判定是研究者手工编码。所有计数从 [`voc_sample_log.csv`](./voc_sample_log.csv) 按 `primary_theme` 和 `secondary_theme` 计算，结果见 [`voc_theme_summary.csv`](../data/public/voc_theme_summary.csv)。`share` 的分母是该文件内对应分组的采样条数，单位是采样项，不是总体用户比例。

## 编码本

| 代码 | 判定边界 |
|---|---|
| `PRACTICE` | 实际开口、说完整句、练习信心或克服开口阻力。 |
| `FEEDBACK` | 转录、纠错、课后回顾是否帮助识别语言错误。 |
| `FLOW` | 对话自然度、话题重复、用户能否主导话题和交互节奏。 |
| `RELIABILITY` | 语音识别、音频质量、延迟、卡顿、打断及无响应。 |
| `LEVEL` | 语言/水平匹配、初学者脚手架或高阶挑战不足。 |
| `ACCESS` | Super/Max 权益、入口或试用覆盖的体验。 |
| `VALUE` | 订阅价格、付费意愿或替代工具的取舍。 |
| `PRIVACY` | 个人信息询问、对话记录或其他隐私舒适度。 |

每条仅有一个主码，可有一个次码。主码取评论的主要决策问题；次码标显著但非中心的问题。`positive / negative / mixed` 表示该条评论对其核心体验的态度，不能当作满意度调查。

## 计数与反例

| 范围 | N | 主码计数 | 情绪计数 |
|---|---:|---|---|
| 全部 | 33 | PRACTICE 9；FLOW 7；RELIABILITY 5；FEEDBACK 4；LEVEL 4；ACCESS 3；PRIVACY 1；VALUE 0 | 正 14；混合 7；负 12 |
| Duolingo Video Call（均 Reddit） | 19 | PRACTICE 6；FLOW 3；RELIABILITY 3；ACCESS 3；LEVEL 2；FEEDBACK 1；PRIVACY 1 | 正 8；混合 4；负 7 |
| Praktika AI（均 Trustpilot） | 8 | FLOW 4；PRACTICE 2；FEEDBACK 1；RELIABILITY 1 | 正 4；混合 1；负 3 |
| Talkpal（均 Trustpilot） | 5 | LEVEL 2；FEEDBACK 2；PRACTICE 1 | 正 2；混合 2；负 1 |
| Duolingo 通用口语（Trustpilot） | 1 | RELIABILITY 1 | 负 1 |

最有价值的**反例**是同一 Duolingo 技术故障讨论中，[R08](https://www.reddit.com/r/duolingo/comments/1qw8ckv/comment/o3nxezo/)称高等级西语通话大体顺畅且能要求角色放慢重述，而[R09](https://www.reddit.com/r/duolingo/comments/1qw8ckv/comment/o5a81u0/)称安卓端停顿就被截断、转录严重遗漏。这说明体验可能随课程、设备、版本或说话节奏变化；这些解释目前均未被验证。同一 Super 讨论里[R17](https://www.reddit.com/r/duolingo/comments/1uw387t/comment/oxg9b67/)称未获入口，[R18](https://www.reddit.com/r/duolingo/comments/1uw387t/comment/oxfvcfo/)称可用，不能据此推出真实覆盖率或产品规则。

## 决策相关发现与可测假设

1. **开口练习可能是核心价值，但收益取决于是否让用户持续产出目标语言。** 19 条 Duolingo Video Call 评论中，6 条以 `PRACTICE` 为主码；[R01](https://www.reddit.com/r/duolingo/comments/1wc6n05/comment/p8w2e8w/)和[R14](https://www.reddit.com/r/duolingo/comments/1qqlq05/comment/o2iacbu/)描述从点选/听懂转为开口。相反，[R03](https://www.reddit.com/r/duolingo/comments/1wc6n05/comment/p8wwhz1/)认为高等级时内容程式化。**商业含义**：扩大覆盖前要验证活跃练习量和学习价值，而非仅验证功能打开率。**假设**：在合适水平的学习者中，视频通话会增加每周有效口语时长/主动说词量；按入门、中级、高级预设分层，并以课程完成率为护栏。
2. **自然度、水平适配与可靠性是复制价值的限制条件。** Duolingo Video Call 样本中 `FLOW` 与 `RELIABILITY` 主码各 3 条；替代品 Praktika 样本的 `FLOW` 主码 4/8 条，说明自然对话痛点并非 Duolingo 独有，但两平台选样不同，不可比较发生率。[R11](https://www.reddit.com/r/duolingo/comments/1wcf8x8/comment/p8xdnwg/)提供了主动选题改善体验的正例；[R09](https://www.reddit.com/r/duolingo/comments/1qw8ckv/comment/o5a81u0/)是识别与轮替失败反例。**商业含义**：Super 扩张可能放大质量与推理成本压力。**假设**：用户可控话题/停顿模式与入门脚手架可提高完成通话率和有效说词量；按设备和语言设置识别失败、延迟、被打断、投诉及单次成本护栏。
3. **权益可见性与明确试用需要先测。** Duolingo Video Call 样本的 `ACCESS` 主码 3/19 条，呈现有、无、曾有后消失三种互相矛盾的体验。它们是用户观察，不能证明实际分配机制或用户规模。**商业含义**：同一订阅名称下的入口差异可能干扰 Max、Super 或有限免费试用的购买判断。**假设**：对符合条件用户展示清楚的权益与有限试用说明，可减少资格困惑并提高试用后有效练习；需用实际资格日志、曝光与转化数据检验，同时观察投诉/取消。

## 证据边界

这是目的性样本，**不是随机抽样或代表性 VOC**。Reddit 聚集愿意发帖的 Duolingo 用户，Trustpilot 包含主动留评、被邀请或从别处重定向的评价；负面故障与明显满意体验都更容易被留下。五个 Reddit 帖内评论互相关联；产品与平台几乎完全混杂（Video Call 来自 Reddit，替代品主要来自 Trustpilot），不能计算产品间满意率差异。评价中的学习进步是自述，未验证真实能力、留存、转化或因果效果。总量 33 达到 Stage 2 的数量目标，但**结论信心仍为低，仅供生成实验假设**。

## Stage Review

- **阶段与状态**：Stage 2 VOC 子任务已完成；Stage 2 整体状态见 `market_opportunity.md`，为`降级通过`。
- **对应总纲板块**：Market & User Research；交接 3 条可测洞察、编码汇总和反例。
- **本阶段决策问题**：哪些用户口语痛点与 Video Call 机制值得扩张前验证？
- **本阶段产物**：`market/voc_analysis.md`、`market/voc_sample_log.csv`、`data/public/voc_theme_summary.csv`；版本 2026-09-28。
- **交接对象与下一行动**：产品分析和量化分析角色基于这三项提出分层实验与质量/成本护栏；不表示 Duolingo 已接收。
- **数据/图表版本**：33 条公开采样项；无图表。汇总由样本日志计算，主码计数总和应为 33。
- **Findings**：开口练习价值线索；自然度/可靠性限制；权益可见性问题（详见上文三条）。
- **Evidence**：均为 C 级公开 VOC；单条 URL、可读列表页、采集日及 11 条可核实的 Trustpilot 发表日期在日志中；其余 22 条发表日期未知。
- **Business meaning**：可用于明确目标分群、体验护栏与权益信息实验，不能推断总体需求规模。
- **Decision impact**：优先验证中级口语产出及端到端质量，再比较 Super 扩张与有限试用；不根据这 33 条直接选择商业方案。
- **Hypothesis status**：痛点被观察到；收益、留存、付费效果均待验证。
- **Unknowns / fallback**：无内部用户级使用、随机分组、课程/设备覆盖与 AI 成本；下一阶段用实验设计和情景阈值，不填虚构值。
- **Checks actually run**：CSV 解析；33 个不同单条 URL；平台 19+14、产品 19+8+5+1、主码 9+7+5+4+4+3+1=33；汇总按日志重算。
- **Gate**：证据有限通过，仅作探索性使用：有 permalink、列表或讨论页和采样释义，但 Trustpilot 单条页在本研究工具中不可直接打开，22 条绝对发表日未知；业务通过（导出三项风险/价值线索）；决策通过（转为实验假设）；相关性通过（围绕 Speaking / Video Call）。此判断仅限 VOC 子任务。
- **Scope cut**：不扩展更多平台或评论；不估算市场占有率、订阅意愿分布、功能因果 uplift。
- **Next stage input**：样本日志、主题汇总及三条实验假设；Stage 3 不应将 VOC 比例当经营指标。
