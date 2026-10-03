# Stage 2.1｜H1–H3 同场景竞品比较与逐主张证据

更新：2026-09-30；资料查阅截至 2026-09-29。主决策是 **Duolingo 应先对谁、用哪种 Video Call 权益做下一轮验证**。本报告比较可进入的用户任务、教学机制和交易摩擦；Duolingo 基准与两类替代供给在 [`competitor_claims.csv`](competitor_claims.csv)，三家直接竞品的 **97 条逐项观察、48 个 URL**在 [`competitor_evidence_v2.csv`](competitor_evidence_v2.csv)，来源/体验者去重及限制见 [`competitor_evidence_quality_review.md`](competitor_evidence_quality_review.md)。原产品级 [`competitor_matrix.csv`](competitor_matrix.csv) 仅作目录。比较采用 Duolingo 基准、Speak / ELSA / Babbel Speak 三家直接产品、ChatGPT Voice / Preply 两类替代选择；**覆盖不符的产品保留为边界，不参与同场景优劣判断**。用户提供的 298 条评论只代表 Duolingo 一侧，绝不计入竞品证据量。

## 结论与决策顺序

1. **H1 先测，但竞争优势须重新表述。**日本语母语者学习中级英语这一场景有 Duolingo 的特定人群短期对照研究信号 [C03]，Speak 有日本英语 B1 课程与 Free Talk [SP01–SP04]，ELSA 的新版 Coach 与 Role-Play Lab 分别有入口 [E06–E08]。因此“有课程、有 AI 对话”是共同供给；各产品是否把学过的内容转成**有效开口、独立口语迁移和持续练习**仍须同任务验证。Speak 的日文第一人称体验 [SP18–SP28]、ELSA 的角色扮演受访者与日文个人体验 [E19–E42]提供了起步/提示/质量的正反线索，均非总体偏好排名。
2. **H2 是独立机制，不是 H1 的低水平外推。**英语界面、美国 iOS、初学西班牙语任务下，Falstaff 与 Babbel Speak 有可定位的场景与提示供给 [C14][B02–B08]；Speak 旧版 Live Roleplays 只作机制参照 [C20]，该任务的当前账号可用性尚未核实。Babbel 当前免费 beta、两周记者亲测及两位不同公开使用者的体验 [B14–B24][B27]给开口和质量风险提供线索；其中仅两人明确西语、三人的美国英语界面 iOS 资格都未核实，不能当严格 H2 同场景样本或估发生率。Falstaff 的公司摘要显示使用者在短语口头翻译测试（含练过短语）中高于无通话者 [C16]；要另测首通完成、延后回忆和**未练场景迁移**。ELSA 的英语角色扮演不在该目标语场景 [C21]。
3. **H3 暂不作扩大免费权益的商业结论。**新 Super 覆盖是公司披露的分批进度 [C22]；公司所称“更长免费试用”的早期结果没有指明 Video Call [C25]。Speak 需绑付款方式的七天试用 [SP10–SP11]、ELSA 有限额角色扮演 [E11–E14]、ChatGPT 有限免费语音 [C29]，以及 **Babbel 当前免费 beta（日本语母语者学英语的账号资格未证实）** [B14–B17][B26]，说明进入摩擦差异大，不能统一叫“免费”。仍无 Duolingo 的首通 uplift、Max 降级、续费净效应或通话单位成本；先取得 H1/H2 的有效练习和成本基线，再随机验证试用额度。

**证据语义**：`A_company_disclosure` 是公司当期披露；`A_company_research_abstract` 是公司研究摘要，须按实际样本和结果限制使用；`provider_supply` 是提供方的功能/权益说明；`provider_internal_evaluation` 是其内部评估。V2 新增外部第一人称亲测与两篇独立研究，均按具体功能和研究设计限制使用；**没有任何可给三产品同口径效果排名的独立研究**。所有动态页面以 2026-09-29 查阅版为准，未标发布日期的页面写 `undated`。账本的 `region` 是目标比较场景，**不表示每家该地区实时账号资格已验证**；只有明确的覆盖主张才能证明页面所列范围。V2 每行对应一个来源定位，`comparison_limit` 规定其不能推出什么；一篇研究/一位体验者的多行不增加独立样本。

## 固定比较场景与覆盖

| 场景 | 固定的用户任务和条件 | 可直接比较的选择 | 边界 |
|---|---|---|---|
| **H1 有效开放对话** | 日本语母语、目标英语、约中级课程、手机，一次短时口语任务；以共同前测重分层并记录实际时长 | Duolingo Lily、Speak、ELSA；ChatGPT Voice 是通用即时语音替代 | Duolingo Score 60–71 与 Speak B1 不是可直接互换的能力尺；Speak 新 Live Tutor 有限推出 [SP13] 且 2025 Immersive Free Talk 与课程分开 [SP04]；ELSA 新版分批 [E08]；Babbel 英文页未列英语，但西语/法语官网列英语，故日本语母语账号资格仍未知 [C30][B26]；Preply 要预约真人 |
| **H2 初学者引导** | 美国英语界面、iOS、初学西班牙语，完成一次日常任务 | Duolingo Falstaff、Babbel Speak | Speak 旧版 Live Roleplays 仅作机制参照 [C20]，该账户场景的当前覆盖未核实；Babbel 的美式英语帮助页列 Mexican Spanish [C17]，与其他西语课程不保证完全一致；ELSA 所查 AI 产品面向英语 [C21]；Falstaff 研究受试者母语未披露 [C16] |
| **H3 有限试用** | 日本语母语学英语、手机、同日比较“能否进入一次有效练习”及后续权益 | Duolingo 新 Super / Max、Speak、ELSA、ChatGPT Voice；Preply 为须预约的真人替代 | Babbel 当前免费 beta 仅作入口机制参照：英语作为目标语存在 [B26]，但日本语母语者/日本账号资格未核实；不同国家、渠道、促销与额度不可拼成价格排名；现有 Super 和 Falstaff 权益不能从新 Super 披露推断 [C15][C22] |

## 六维证据矩阵：供给事实与需要验证的结果分开

| 维度 | H1 中级开放对话 | H2 初学引导 | H3 有限试用 |
|---|---|---|---|
| 用户任务与可达覆盖 | Speak 有日语母语英语课程 [SP01–SP02]；Duolingo 路径/练习区有入口 [C02]；ELSA 新版分批 [E08]。**未知**：同用户同设备实际资格与曝光 | Falstaff 公告为 iOS Max [C15]；Babbel 为移动端 beta 且美式英语界面对应墨西哥西语 [B01–B02]，落地页另列西班牙西语 [B17]。**未知**：同一入组用户真实可用率 | 大多数新增 Super 有 Video Call、现有 Super 后续扩展属预期 [C22]。**未知**：按课程/设备/批次的实际资格 |
| 学习机制与效果 | Lily 可自由对话 [C01]；Speak 有日本 B1 课程与 Free Talk，但新版 Immersive Free Talk 第一阶段在独立标签 [SP02–SP04]；ELSA Coach 与 Role-Play Lab 分入口 [E06–E07]。Duolingo 特定高频组有短期测试信号 [C03]，无跨产品效果 | Falstaff、Babbel 有任务/提示 [C14][B03–B06]；Speak 旧版仅作机制参照 [C20]；Falstaff 对无通话组的摘要报告短语翻译测试，包含练过短语，未报告独立新情境迁移 [C16]。**未知**：迁移与延后保留 | 试用只是接触教学机制的入口；**未知**：试用者是否完成有效练习及学习收益 |
| 体验与信任 | Duolingo 加入 Push-to-Talk 和事后反馈 [C05]；ELSA 列多维反馈 [C12]；Speak 内部停顿和纠错评估 [SP14–SP16]。日文发文的 Speak/ELSA 体验有难起步、提示帮助、延迟及角色失配等**个别反例** [SP18–SP28][E22–E40]；无同测试集故障率 | Babbel 选择不在对话中打断纠错 [B07]；一位记者与一位跨两帖的公开使用者分别提出反馈不足、错误未被指出及重复感 [B21–B24]；Falstaff 实时提示 [C14]。**未知**：哪种反馈时机对初学者更有利 | 首通失败、过度纠错、隐私不安会改变试用净价值；公开页面无可比故障率 |
| 获取、激活与习惯 | Duolingo 课程节点可跳过 [C02]；Speak Free Talk 与 ELSA AI Chats 有独立入口 [SP04][E07]；Speak 一位作者延后数周才首次尝试 [SP22]。**未知**：曝光→首通→W1/W4 | Babbel 的任务预览与脚手架可核 [B03–B06]；Speak 旧版仅供机制参照 [C20]；一位记者亲测可起步 [B20]。**未知**：真实首句与首通完成 | Speak 绑付款方式试用 [SP10]；ELSA/ChatGPT 免费有限额 [E11][C29]；Babbel 当前免费 beta 只作未核实日本账号资格的入口参照 [B14–B17][B26]。**未知**：Duolingo VC 专属试用增量 [C25] |
| 订阅与替代关系 | 同地区同日期价格、支付意愿、课程练习挤出均未知 | Falstaff 的 iOS Max 公告不能套用 Lily 的新 Super 覆盖 [C15][C22] | Speak 两档都有角色扮演 [SP07]；ELSA Free/Pro 限额而 Premium 宣称无限 [E11–E13]；Babbel 的免费 beta 只适用于其支持语言且未来可能变更 [B14–B16]。**未知**：Super 升级与 Max 降级的净额 |
| 单位经济与可防御性 | 课程、反馈、开放对话三者都非独家 [SP03][E06–E07]；差异须在同任务行为与结果上验证 | 课程单元匹配与提示依赖可能影响有效分钟，需计费口径一致 | 公司称 AI 扩张节奏和效率影响毛利 [C24]；公司级毛利不能算通话成本。Speak 工程文仅给语音架构相对成本取舍 [SP17]，无通话级数字；真人 Preply 的常规试课需先付费预约 [C32] |

### H1：日本中级英语，开放对话

**竞争实际变化。**[Speak 日本课程](https://www.speak.com/jp/content)列出 B1 内容并宣称课内表达可用于实时 Free Talk [SP02–SP03]；但[其 2025 沉浸式 Free Talk 帮助页](https://help.speak.com/en/articles/13182402-free-talk-immersive-roleplay)明确第一阶段只在 Free Talk 标签，**没有进入 Course lessons** [SP04]。[ELSA 的 2026 新版导航](https://blog.elsaspeak.com/en/discover-the-new-elsa-speak-experience/)把 AI Conversation Coach 放 Coach，Role-Play Lab 放独立 AI Chats，且分批推出 [E06–E08]。Speak 2026-09 的 Live Tutor Lessons 把教学目标与开放回答结合，但仍有限推出 [SP13]。故 Duolingo 的潜在优势应写成**“在具体资格与入口下更高的课程用户有效练习转化”假设**，不能写成独占课程整合。

Duolingo 的公司研究摘要在日语母语、Score 60–71、至少日均两次通话的英语学习者中报告一个月后标准化测试改善更多 [C03]。这是 H1 优先于其他场景的理由，但研究强度仍受高频使用条件、完成者选择和官方全文本次 403 限制；它不能说明一般用户自愿打开通话后的平均效果。Speak 日文发文作者还分别描述一分钟通勤练习可坚持、从 Free Talk 转向课内 Roleplay、自建场景较费力 [SP24][SP26][SP28]；ELSA 越南/印尼两篇目的抽样研究中的具体受访者（非日本同人群）描述开放问答卡住、反馈有帮助、网络不稳时识别和延迟问题 [E26–E35]，一位日文作者 2026 自购 Premium 的一次新 Role-Play Lab 实测同时记录目标完成与角色倒置 [E38]。这些是**不同人群、版本、自选来源**，只用来设首通和独立表达测量。Speak 的内部停顿/纠错评估 [SP14–SP16]是质量风险定义，不是与 Duolingo 口语成绩同口径的胜负比较。ChatGPT Voice 提供自由语音 [C13]，可在临时聊天时替代专用练习，但课程目标和学习效果尚无同口径证据。

**判别设计**：先做同任务、同能力前测、同设备的产品任务观察，记录进入时间、有效主动语句、犹豫被抢话、错误纠正准确度、完成和主观负担；再在 Duolingo 合格用户内对“可见且可用的 Lily 通话”与现有课程做随机比较，按最初分组报告首通、每周有效口语分钟、W1/W4、独立盲评新情境表达及常规课程时长。产品任务观察不能代替随机化；公司 DAU 不能代替功能因果。

### H2：美国英语界面初学西语，引导式任务

Falstaff 提供按水平提问、短语/翻译和母语实时反馈 [C14]；[Babbel Speak 帮助页](https://support.babbel.com/hc/en-us/articles/25875402999826-Babbel-Speak)提供情境任务预览、提示/翻译和事后反馈 [B03–B08]。[Speak Live Roleplays 的旧版博文](https://www.speak.com/blog/live-roleplays)描述按水平安排任务和提示 [C20]，但尚未确认当前美国英语界面 iOS 初学西语账号能否进入，因此只用于机制参照。Falstaff 与 Babbel 的引导强度、纠错时点也没有同一初学者样本的学习与完成率比较。[Tom's Guide 的两周亲测](https://www.tomsguide.com/ai/i-spent-2-weeks-speaking-to-a-spanish-ai-in-babbel-heres-why-it-could-be-the-future-of-learning-languages)描述 Babbel 情境与提示使低水平尝试可行，同时报告对错误过度宽容和任务重复 [B20–B22]；**同一位**公开使用者在两帖中对漏纠错、发音评分提出主观不满 [B23–B24]；另一位 A1/A2 使用者只给适用及需更新的简短判断 [B27]。这是研究**质量护栏**的理由，不是证明 Babbel 用户普遍不满。Falstaff 公司摘要只对“有通话/无通话”以及测试中包含已练短语给出方向，未披露样本、随机化、效应量 [C16]，更不能证明优于 Lily、Babbel 或 Speak。

**判别设计**：在同资格初学者中随机分配 Falstaff 引导、Lily 开放、常规课程/无通话；预先核对两种角色的真实权益和课程可用性。Stage 5 预设**首通完成率**为唯一 primary KPI，**延后未练情境的盲评表达**为关键学习验证指标；同时看提示使用后是否独立说出目标短语、W1 回访、技术失败及每有效分钟成本。若只提高题库相同短语的即时翻译成绩，不据此扩大到泛口语能力。

### H3：日本学英语，有限试用与订阅净价值

不同入口不可简单拼成“谁最便宜”：Speak 的七天试用需要先选方案与付款方式 [SP10–SP11]；ELSA 的免费层给有限 AI 角色扮演，七天通用试用是否含足量 Roleplay 未知 [E11–E14]；ChatGPT 免费语音有动态额度 [C29]；Preply 常规试课需预约并付费 [C32]。Babbel **当前**免费 beta [B14–B16]在西语/法语官网列出英语目标语 [B26]，但日本语母语/日本账号资格未核验，故只作入口机制参照；其 2025 首发订阅权益 [B13]不能当今天价格。Duolingo 2025 Q4 提出的“纳入 Super 使可触及用户约为十倍”是前瞻计划 [C23]；2026 Q2 信息只支持“大多数新增 Super 已可用 Video Call” [C22]，没有 Video Call 专属免费试用的观察结果；公司所谓更长试用的早期好结果是**整体付费试用陈述** [C25]。

**待算的商业量**：以互斥用户状态计算订阅贡献变化，单列 Super 升级/续费和 Max 降级，再加非订阅贡献变化、减去增量 AI/服务成本；常规课程练习是否被挤出另作学习和留存护栏，避免重复计入收入。当前每一项与自然试用采用率均缺功能级数据，Stage 4 只设区间与盈亏平衡阈值，不填点预测。Stage 5 在 H1/H2 有有效练习基线后，**在同一免费资格人群内**随机比较无 Video Call 试用与一次/少量通话试用；Super 新旧用户和 Max 用户分别设计权益推出或报价试验，不能把不同付费层级直接当随机对照。各试验按原分组报告资格→曝光→首通→有效完成→W1/W4→升级/续费/Max 降级，成本以**每有效练习分钟**而非仅每次点击计。若无法区分新 Super 与现有 Super 及 Falstaff/Lily，先修埋点再读结果。

## Duolingo 侧用户样本如何进入判断（不计竞品证据）

用户已确认所交 `samples.csv` 的来源和真实性；本次直接复算其**提交标签**，不是重新访问平台或做独立编码。文件 SHA-256、保存位置和平台构成见 [`STAGE2_INPUT_INTAKE.md`](../docs/STAGE2_INPUT_INTAKE.md)。298 条被标记为相关，其中 244 条标记第一人称；来源为 Reddit 帖子 194、同平台评论 12、X 58、Google Play 30、App Store 4。Reddit 评论不能当独立讨论帖，平台分布也不允许用总体百分比估计需求或比较竞品满意度。

| 提交标签中的主题 | 样本内条数；其中第一人称 | 哪个试验问题因此更重要 | 不能推出什么 |
|---|---:|---|---|
| 权益/推出 `access_rollout_super` | 54；42 | H3 按账户、课程、设备记录**真实资格与曝光** | Super 用户总体不可用率、Max 降级率 |
| 对话质量/反馈 `conversation_quality_feedback` | 44；38 | H1/H2 做盲评与纠错准确度、完成护栏 | 与 Speak/ELSA 的横向质量胜负 |
| 技术故障 `bugs_tech_issues` | 36；29 | 首通失败与有效分钟需同设备记录 | 全体用户故障率 |
| 识别/打断 `speech_recognition_interrupts` | 20；20 | 将抢话、漏转录列为质量护栏 | 与 Speak 内部停顿指标同口径比较 |
| Max 价格/付费墙 `paywall_price_max` | 30；23 | H3 同时看试用激活与 Max 权益替代 | 支付意愿、价格弹性 |
| 学习价值/信心 `learning_value_confidence` | 23；22 | 学习盲评与主观信心必须分别测量 | 真实能力提升或总体好评率 |

例如 `access_rollout_super` 的 54 条分布为 Reddit 帖子 42、Reddit 评论 6、Google Play 5、X 1；`conversation_quality_feedback` 的 44 条为 Reddit 帖子 35、X 5、Google Play 3、App Store 1。**这是来源内提交标签计数，未按各平台活跃用户或曝光量标准化。**`tier=unknown` 为 200/298、`level=unknown` 为 279/298，因此这些评论不能被可靠地切成 H1 与 H2 人群；即使来源真实，也不能据此推断各人群痛点发生率。评论的用途是给指标、反例和故障条件排序。

## 三条闭合业务主张与交接

| 待证伪主张 | 证据支持到哪一环 | 下一环的决策性检查 | 反例与停止条件 |
|---|---|---|---|
| **H1：课程基础上的开放对话增加有效练习** | 目标任务有特定人群研究信号 [C03]；Duolingo、Speak、ELSA 都具备课程/对话供给，但后两者版本与入口须分开 [C04][SP02–SP04][E06–E08]；用户样本有质量和打断反例 | 内部随机资格/曝光→有效开口→独立口语迁移→W4→净成本，记录常规课程挤出 | 若只增加应用时长或通话次数而无盲评迁移，或质量失败抵消完成率，不扩大 |
| **H2：引导降低初学者第一句门槛** | Falstaff、Babbel 的对应供给可核 [C14][B03–B08]；Speak 旧版机制参照的当前资格未核 [C20]；Falstaff 研究仅覆盖短语翻译 [C16] | Falstaff/Lily/无通话随机对照，先测首通，再测延后未练情境 | 若提示依赖高、即时练过的短语改善但新情境没有改善，迭代引导而非扩张 |
| **H3：有限试用的净价值为正** | 竞品低门槛入口不同 [C26][C28][C29]；Duolingo Super 扩展真实发生 [C22] | 同用户资格下测有限额度的增量有效练习、订阅净额、Max 降级、单位成本；Stage 4 先给盈亏平衡阈值 | 若免费使用主要替代既有付费或成本超过预设阈值，停止扩大额度 |

**交接与收束**：竞品供给、外部体验与研究边界已按 [`competitor_evidence_quality_review.md`](competitor_evidence_quality_review.md) 审计；没有任何跨产品学习效果、留存、满意度、市场份额或价格优胜结论。下一轮按 [`stage2_decision_memo.md`](stage2_decision_memo.md) 将 H1/H2/H3 机制交给 Stage 3/4/5：Stage 3 用公司数据做背景，Stage 4 算成本/替代阈值，Stage 5 取真实分组与对照。Stage 2.1 已完成一次总审阅，因独立体验者、分层与功能级数据缺口**降级通过**；不因缺少内部指标而无限扩大竞品名单。
