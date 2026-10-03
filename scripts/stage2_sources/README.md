# Stage 2.1 来源工具准备

本目录只固定三个候选项目的依赖并检查本地接口。**离线检查不调用 Google Play、App Store 或 Reddit，不证明评论可获取。**平台准入结论见 [`market/source_access_review.md`](../../market/source_access_review.md)。

## 安装与离线检查（PowerShell，仓库根目录）

```powershell
uv venv .venv --python python
uv pip sync --python .venv\Scripts\python.exe scripts/stage2_sources/requirements.lock
.venv\Scripts\python.exe scripts/stage2_sources/check_python.py

cd scripts/stage2_sources
npm ci --ignore-scripts --no-fund
npm run check:offline
npm audit --omit=dev
```

`requirements.txt` 是直接依赖，`requirements.lock` 固定传递依赖；`package-lock.json` 固定 Node 依赖。`.venv/` 和 `node_modules/` 均不进 Git。不要运行 `reviews()`、`store.reviews()` 或 PRAW listing 作为安装测试：那会向平台发出真实请求。不要用 `reviews_all()` 扫描 Duolingo 全部评论。

取得可用于研究的候选 CSV 后，先置于被 Git 忽略的 `data/raw/`，按 [`candidate_columns.csv`](candidate_columns.csv) 的表头整理，运行 `.venv\Scripts\python.exe scripts/stage2_sources/audit_candidates.py data/raw/候选文件.csv`。该脚本只检查结构、主键、日期、评分与链接粒度；**直接相关性、评论真实性和主题仍须人工抽核**，并分别记录采集框与关键词定向框。脚本不会输出原文。

当前 App Store 依赖树有已报告的安全问题，且 Apple 条款限制自动抓取与分析；保留依赖只是为可复核的技术评估，不作为在线采集许可。PRAW 在本研究中也不作为 RFR 授权渠道。若以后存在合法可使用的数据源，先在 `market/source_access_review.md` 更新准入依据，再按 [`docs/STAGE2_EVIDENCE_REFRESH.md`](../../docs/STAGE2_EVIDENCE_REFRESH.md) 的采样与质量规则执行。
