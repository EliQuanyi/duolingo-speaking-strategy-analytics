# Stage 2.1 来源与工具准入审查

**审查日期：2026-09-28。状态：本地依赖已配置；三个来源均未进行在线试采。**

## 本轮要回答什么

Stage 2 首轮有 33 条去重 VOC，其中只有 19 条直接涉及 Duolingo Video Call，且这些直接样本全来自 Reddit。Stage 2.1 的目标是形成更可追溯、可审核且来源更广的**直接体验证据**，以决定优先验证哪一类用户和产品摩擦。原始候选千级是采集目标，不是质量通过条件；不以公开评论估计功能采用率、留存或收入效果。具体收束规则见 [`docs/STAGE2_EVIDENCE_REFRESH.md`](../docs/STAGE2_EVIDENCE_REFRESH.md)。

## 三个候选工具

| 工具 | 本地版本与代码许可 | 技术接口、覆盖与局限 | 当前数据准入 |
|---|---|---|---|
| [JoMingyu/google-play-scraper](https://github.com/JoMingyu/google-play-scraper) | Python `1.2.7`，2024-06 发布；[MIT](https://github.com/JoMingyu/google-play-scraper/blob/master/LICENSE)。 | [`reviews()`](https://github.com/JoMingyu/google-play-scraper#app-reviews) 接受 app ID、语言、国家、排序、数量并返回续页 token。每页最多 200；可取评论 ID、内容、评分、发表时间和版本，但库未提供可核实的单条评论永久链接。旧版本与页面结构可能失效。 | **暂停在线试采。** 安装包[源码](https://github.com/JoMingyu/google-play-scraper/blob/master/google_play_scraper/constants/request.py)请求 `/_/PlayStoreUi/data/batchexecute`；[Google Play robots.txt](https://play.google.com/robots.txt) 禁止 `/_`，而 [Google 服务条款](https://policies.google.com/terms) 禁止违反机器可读规则的自动访问。不能因 Python 库 MIT 而推断评论可采。 |
| [facundoolano/app-store-scraper](https://github.com/facundoolano/app-store-scraper) | npm `0.18.0`；仓库 [LICENSE](https://github.com/facundoolano/app-store-scraper/blob/master/LICENSE) 为 MIT，但 [package.json](https://github.com/facundoolano/app-store-scraper/blob/master/package.json) 与 npm 元数据标 ISC，许可元数据不一致。 | [`reviews()`](https://github.com/facundoolano/app-store-scraper#reviews) 按国家、页码、最近/有用排序读取 [Apple RSS](https://github.com/facundoolano/app-store-scraper/blob/master/lib/reviews.js)；最多第 10 页。字段有 ID、正文、评分、更新时间、URL，URL 是否指向单条评论未经实测。依赖已弃用的 `request`。 | **暂停在线试采。** [Apple 美国媒体服务条款](https://www.apple.com/legal/internet-services/itunes/us/terms.html) 明确限制用软件或自动流程抓取、复制、测量、分析或监控服务内容。安装工具不改变该限制。 |
| [praw-dev/praw](https://github.com/praw-dev/praw) | Python `8.0.3`；[BSD-2-Clause](https://github.com/praw-dev/praw/blob/main/LICENSE.txt)。 | [PRAW 只读配置](https://praw.readthedocs.io/en/stable/getting_started/authentication.html) 技术上需 client ID、secret、user agent，实际读取需要发起 API 请求；本次未读取任何凭据。 | **暂停在线试采。** [Reddit Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy) 要求 API 访问前获明确批准；[研究用途说明](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data) 指定 Reddit for Researchers（RFR）为官方研究渠道，PRAW/Data API 不能替代。 |

代码的开源许可只允许依许可使用**代码**，没有授予采集、保存或再分发平台评论的权利。以上是对本项目当前来源准入的工作判断；如果后续取得适用许可或授权，需要重新记录准入依据、使用目的、字段和保留期限。第三方评论原文不进入公开仓库。

首轮 19 条 Reddit Video Call 样本是历史探索记录，并非本轮获批 API 数据。正式数据包之前须重新审查保留与引用边界；不得把它们重算为新样本或据此扩大 Reddit 采集。

## 离线配置及安全检查

| 检查 | 2026-09-28 实际结果 |
|---|---|
| Python 隔离环境、锁定依赖 | `.venv` 创建成功；`uv pip sync` 安装 11 个包。`check_python.py` 验证 `google-play-scraper==1.2.7`、`praw==8.0.3` 导入和接口存在。网络请求数为 0。 |
| Node 隔离依赖、锁定版本 | `npm install --ignore-scripts` 安装 `app-store-scraper==0.18.0`；`check_app_store.cjs` 验证 `reviews` 和排序常量存在。网络请求数为 0。 |
| Node 依赖安全 | `npm audit --omit=dev`：6 个报告项，其中 4 moderate、2 critical；涉及 `app-store-scraper`、`request`、`form-data`、`qs`、`tough-cookie`、`uuid`。**未自动执行 `npm audit fix --force`**，也未运行在线采集。 |
| 在线可用性与字段稳定性 | 未验证。不能声称任何平台评论采集成功，也无法报告 Video Call 命中率。 |
| 候选记录质量校验 | `audit_candidates.py` 已准备，接受本地获授权 CSV；目前尚无新增候选记录可运行真实质量检查。 |

## 正式补强的数据与质量合同

若取得可用来源，每条候选记录至少要有 `platform`、`product/app_id`、原始 `record_id`、来源页/单条 URL（若平台有）、发表日期或 `unknown`、采集日期、国家/语言、采样框与排序/查询方式；保留原始记录在 Git 忽略的 `data/raw/`。不采集用户名、头像、个人主页或其他非必要个人字段。来源页而非单条链接时，标明**不可逐条网页复核**，不能伪装成直接链接。

质量审查按平台、国家、时间、`recent` 与关键词定向样本分别报告：采集总数 → 主键去重数 → 实际与 Video Call 直接相关数 → 人工编码数。以 `(platform, app_id, record_id)` 去重；检查日期与评分范围、空正文、重复及失效 URL；人工抽核分类与反例，记录分歧及修正。不同平台或竞品的主题比例不得混算成 Duolingo 用户总体比例。最多把 3 条有反例说明的发现转成 Stage 3/4 可检验假设；达到决策可用性即收束。

## 当前决策

**仅完成工作包 A 的本地工具配置和来源准入审查；工作包 B 的在线试采未启动。** 下一步应先取得可用于研究的评论数据授权或找到可合法分析并按许可引用的独立数据集，再开展小量字段/命中率试验；若缺少合规来源，按 [`docs/DATA_POLICY.md`](../docs/DATA_POLICY.md) 降级结论并继续 Stage 3，不用违规或不可复核的千级评论填数。
