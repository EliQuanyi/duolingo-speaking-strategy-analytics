# Stage 2.1｜竞品证据质量与体量审计

更新：2026-09-30；资料查阅截至 2026-09-29。正式逐项账本为 [`competitor_evidence_v2.csv`](competitor_evidence_v2.csv)，准入标准见 [`competitor_evidence_protocol.md`](competitor_evidence_protocol.md)。该账本**只含 Speak、ELSA AI、Babbel Speak 的竞品侧观察**；Duolingo 用户提供的 298 条记录不计入本表。既有 [`competitor_claims.csv`](competitor_claims.csv) 保留 Duolingo 基准和 ChatGPT Voice / Preply 替代供给；其中与 V2 重复的竞品官网信息不能相加为新增证据。

V2 明列地区、语言/水平、权益、设备/版本、有效日、来源日期与核验状态；来源没有给出的条件写 `unknown`。这些字段表示**文本可证条件**，不是日本或美国真实账号已完成资格测试。

## 实际数量：行、来源和体验者分开

| 产品 | 逐项观察 | 独立 URL | 直接体验单位 | 主要覆盖 |
|---|---:|---:|---:|---|
| Speak | 28 | 18 | 10 位日文发文的个人作者，母语/地区未逐一核验；跨 2025–26 不同 Free Talk / Roleplay 版本 | H1 英语对话与激活；H2 仍仅机制参照；H3 试用规则 |
| ELSA AI | 42 | 18 | 21 位可区分：两篇新增研究中 10 名不同编号受访者，另有个人作者；其中 1 位只谈相邻 AI 对话 | H1 英语角色扮演；H2 目标语不符；H3 权益层级 |
| Babbel Speak | 27 | 12 | 3 位明确亲测：记者 1、公开讨论用户 2（其中一人跨两帖） | H2 西语引导；H3 当前免费 beta 与英语目标语页面边界 |
| **合计** | **97** | **48** | **34 位可区分；明确目标功能尝试最多 33 位** | 不是 97 人，也不是 48 个独立机构 |

来源性质分布：提供方说明/工程解释/内部评估 **52 条、21 URL**；外部研究与第一人称资料 **45 条、27 URL**。后一类中，目标或相邻 AI 对话的第一人称尝试/使用记录是 **39 条、25 URL、34 位**，多条来自同一人；Babbel 的两处 Reddit 记录经作者核对合并为 **1 位**。其中 E21 只谈相邻 AI 对话，E24 已发起目标对话但因故障未完成；故明确目标功能**尝试**者最多 33 位，完成会话人数不能可靠复算。另有 1 条科技媒体作者的**账号可达性**观察，未清楚记录完整 Babbel Speak 会话，`context_only` 且**不计体验者**。账本涉及 **4 篇独立研究、5 条方法/结果观察**：其中三篇质性研究的可定位受访者按**人**计、仍只算各自一篇来源；另一篇 ReCALL 对照研究评估 ELSA 单向纠音，不是 AI Roleplay，标记 `context_only`。旧印尼研究有 30 名问卷受试者、10 人访谈，只提取 3 位；新增悉尼研究 7 人只提取 4 位；新增 IJLTER 20 人只提取 6 位。匿名研究编号可在各研究内去重，跨研究身份无法绝对核验；不把完整研究样本加进 34 位。以上“独立”只指来源不属于对应产品提供方，不意味着代表性抽样或无商业关系。

首轮候选 76 条中剔除 4 条，形成 72 条；复审又纳入 **25 条**逐人体验、账号可达性与研究方法观察，合计 97 条。复审期间另发现 Speak 角色扮演功能名不明、ELSA 疑似扩写推广帖、普通 Babbel 课程与旧 Conversation Partner 等，**未为凑数纳入**。正式账本内 `quality_status=accepted` 52、`caveated` 42、`context_only` 3。`accepted` 只表示可核对的方法或供给事实，**不表示产品效果已证实**。Babbel 编辑评测与 ELSA 部分博客含联盟、赠用或导流利益，逐条降低权重；旧版体验不充作 2026 当前版实机。也剔除了 ELSA Speech Analyzer、聚合星级与无方法 SEO 排名；没有用 Google Play、App Store 或 Reddit API 批量采集新评论。

## 质量核查改变了什么

1. **版本不能拼装**。[Speak 2025 帮助页](https://help.speak.com/en/articles/13182402-free-talk-immersive-roleplay)写明 Immersive Free Talk 第一阶段在独立标签、未进课程；[2026 Live Tutor 公告](https://www.speak.com/blog/live-tutor-lessons-powered-by-openais-gpt-live-1)是英语/西语有限推出。课程、Free Talk 和 Live Tutor 不能拼成所有日本 B1 用户当前都能用的一个功能。内部纠错/打断百分比是提供方配置评估，没有 Duolingo 对照。
2. **入口与权益需要同日、同账户核验**。[ELSA 2026 导航说明](https://blog.elsaspeak.com/en/discover-the-new-elsa-speak-experience/)把 AI Conversation Coach 放在 Coach，而 Role-Play Lab 放 AI Chats，且分批推出；[权益表](https://elsaspeak.com/ema/crm-cs-base/)只写 Free/Pro 的 Roleplay 为 Limited、Premium 为 Unlimited，未给日本账户次数。[Babbel 当前英文页](https://www.babbel.com/babbel-conversation-practice)称注册可免费试 beta，和[2025 首发订阅权益](https://www.babbel.com/press/en-gb/releases/babbel-speak)不同时点；其[美国英语帮助页](https://support.babbel.com/hc/en-us/articles/25875402999826-Babbel-Speak)与落地页对西语变体的列法不同。[西语官网](https://es.babbel.com/babbel-speak)又明确可练英语，故不能断言 Babbel 全球不支持英语，但日本语母语者/日本账号资格仍未知。没有实机账户核验就不作精确资格或价格排名。
3. **外部体验只能指出需要测的断点**。Speak 的 10 位日文发文作者覆盖起步困难、短时通勤练习、Free Talk 与课内任务的替代、自建情境摩擦和主观习惯变化 [SP18–SP28]，但多篇是 2025 旧版，不能映射为 2026 Live Tutor 效果。ELSA 的 21 位中，旧版悉尼与印尼质性研究分别把“开放问答想不出内容”“结束反馈”“难度选择”“历史无法回看”和网络不稳时延定位到不同受访者 [E26–E35]；2026 一位日文作者自购 Premium 的一次 Role-Play Lab 实测同时记录任务完成与角色倒置、短对话评估缺项 [E38]。Babbel 的记者两周亲测与一位跨两帖公开使用者为开口和反馈摩擦提供线索，同时存在漏纠错与场景重复反例 [B20–B24]；第三位只说 A1/A2 会话适用、需要更新 [B27]。这些是自选或目的抽样，不能量化自然人群频率。它们使“首通”“有效主动句”“盲评迁移”“误纠/漏纠”“角色/任务保持”与 W1/W4 回访成为必须分开的指标。

**市场机制的独立背景**：[Hou 与 Min 的 16 项研究、89 个效应量元分析](https://www.cambridge.org/core/journals/recall/article/dialoguebased-computerassisted-language-learning-systems-for-second-language-speaking-development-a-threelevel-metaanalysis/31847710516602398819C5E594038E7B)报告对话式计算机辅助学习的整体口语效应 `g=0.61`、95% CI `[0.34, 0.89]`，同时研究间异质性显著，系统形式和任务约束等可调节结果；[2026 年十项研究的系统综述](https://www.sciencedirect.com/science/article/pii/S2772503026000575)指出交流互动和语篇连贯很少被测。这两篇是**类别机制证据**，不是任何本表产品的独立效果估计；因此 H1/H2 必须有未练情境盲评，不可只看“说了更多词”。

## Gate 判断与最大缺口

**体量关：97 条可核对观察、48 URL，34 位可区分体验者中最多 33 位明确尝试目标对话功能；已达到“数十条”目标，但并非同场景样本。**Speak 10 位主要是日文发文的英语自选作者，母语/地区未逐一核验且版本分散；ELSA 21 位中至少 10 位来自两篇目的抽样质性研究，不能当 10 个独立来源；Babbel Speak 明确亲测共 3 位，其中可定位到西语体验的至少 2 位；三人均缺美国英语界面、iOS、初学程度的完整同条件记录，H2 尤其薄弱。H3 几乎全是供应商权益说明。没有代表性、同任务、同版本跨产品用户研究。因此可比较**可供给选择、入口摩擦、教学机制与待验证风险**，不能比较总体满意度、真实留存、学习提升或净商业价值。

ChatGPT Voice 与 Preply 在本阶段按**替代机制**保留于旧账本：前者是随时语音对话，后者需预约真人辅导。两者缺日本中级英语同任务的独立产品体验和相同权益口径；[Preply 委托 Leanlab 的 2025 摘要](https://avatars.preply.com/inbound/media/20260109/Preply_Efficiency_Research_Platform_Comparison_2025.pdf)明确是不同时间的两组研究，不是受控头对头试验，故不进入竞品效果比较。该缺口已显式留给 Stage 5 的同任务观察，不以跨人群论文或提供方宣传补齐。

最大剩余缺口是**同一用户任务下、记录版本与账户资格的独立实测/对照**。Stage 2.1 按规则一次审阅后收束为**降级通过**：证据体量足以比较供给和形成待测机制，**不足以通过效果或偏好判断**，不再为增加行数搜集低质评论。Stage 5 应优先取得同任务实机观察和 Duolingo 内部随机化事件；若以后取得获授权、带原文/采样框的竞品评论，再作为新数据版本审计，不能追认本账本为代表性样本。
