# Stage 2 竞品矩阵说明（2026-09-28）

> **Stage 2.1 更新（2026-09-29）**：逐主张官方来源、适用地区/权益/时间及 H1–H3 同场景商业评审见 [`competitor_claims.csv`](competitor_claims.csv) 和 [`competitor_scenario_review.md`](competitor_scenario_review.md)。本页保留 Stage 2 的早期观察；后续决策以新评审为准。Speak 和 ELSA 也有课程或学习路径内的 AI 对话，因此不能把“课程整合”写成 Duolingo 独有优势。

`competitor_matrix.csv` 以产品为粒度，仅覆盖 3 个直接口语产品、2 个替代方案和 Duolingo Video Call 基准。字段均为 UTF-8 文本；`source_urls` 用 `|` 分隔完整官方 URL；`access_date` 为页面查阅日期。`evidence_A_company_statement` 表示 Duolingo 的披露和产品陈述，`evidence_B_official_product` 表示竞品自己的产品/帮助页面；两者均不等于独立效果验证。`target_job` 和 `access_and_friction` 含基于所列功能的分析者归纳，其余字段尽量描述页面可核对的产品事实。价格仅记录收费机制，因为币种、地区、优惠、渠道和导师可改变标价。官方网页内容版权归各公司，CSV 只保留概括性事实和链接，不收录评论原文、宣传语或页面截图。

## 可交接的竞争观察（均为待验证机会）

1. **无压力 AI 对话已是可替代能力。** [Babbel Speak](https://support.babbel.com/hc/en-us/articles/25875402999826-Babbel-Speak) 提供带场景任务的 AI 对话，[Speak](https://help.speak.com/en/articles/5358417-what-s-the-difference-between-premium-and-premium-plus) 有情境角色扮演与课程。因此下一步值得测试的不是“能否对话”，而是 Duolingo 的课程内入口和 [Lily / Falstaff 两种引导强度](https://blog.duolingo.com/beginner-video-call-with-falstaff/) 能否让目标用户更常完成有效口语练习。反面解释：竞品页面只说明功能存在，不说明用户是否持续使用；Duolingo 的课程整合也尚无可公开比较的增量证据。
2. **反馈深度与不中断对话之间存在可测试的设计选择。** [ELSA](https://elsaspeak.com/ema/crm-cs-base/) 强调发音、流利度、语法、词汇反馈，[Speak](https://www.speak.com/) 宣称逐句反馈；[Babbel](https://support.babbel.com/hc/en-us/articles/25875402999826-Babbel-Speak) 在通话后给任务/词汇反馈且不在中途打断。Duolingo [已加入通话后反馈](https://blog.duolingo.com/product-highlights/)，[Falstaff](https://blog.duolingo.com/beginner-video-call-with-falstaff/) 也有实时引导。可以按初学者与较熟练者分别验证反馈时机、针对性和说词量/完成率的关系。反面解释：更密集的纠错可能打断开口意愿；官方功能描述不能证明哪种反馈更有效。
3. **降低试用门槛可能帮助识别真实口语需求。** [Babbel](https://www.babbel.com/babbel-conversation-practice) 目前允许注册用户免费尝试样本课和对话练习，但保留未来收费的权利；[ChatGPT Voice](https://help.openai.com/en/articles/20001274-chatgpt-voice) 有有限免费语音额度。Duolingo 在 [2026 Q2 股东信](https://www.sec.gov/Archives/edgar/data/1562088/000162828026053299/q2fy26duolingo6-30x26share.htm) 中称大多数新 Super 订阅用户已有 Video Call 权益，现有 Super 用户预计随后开放。可研究有限试用如何影响目标用户的首次开口及后续使用。反面解释：免费/更广覆盖带来 AI 成本和付费层级替代风险，且公开资料未给出功能级成本与转化效果。真人 [Preply](https://preply.com/en/courses/english/english-conversation-course) 可提供目标化辅导，但需选导师和预约；它既是替代选择，也可能服务不同使用时刻。

**边界**：本矩阵只比较公开产品设计与交易摩擦，不比较真实学习效果、市场份额或 Video Call 对经营指标的因果作用。价格、支持语言和订阅权益会变化；正式策略判断需再核对目标地区、平台及用户分群。
