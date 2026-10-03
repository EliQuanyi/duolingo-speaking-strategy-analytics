# Duolingo Speaking Strategy Analytics

**市场调研 × 数据分析 × 商业量化决策｜AI Speaking / Video Call 扩张评估**

An independent, AI-assisted portfolio case study connecting market evidence, reproducible business diagnostics, evidence-constrained economic modeling, and a prospective experiment. It evaluates what should be tested before expanding an AI speaking product. No internal Duolingo data, measured policy ROI, or executed product experiment is claimed.

**主问题：Duolingo 应如何评估口语权益扩张，下一步验证什么，什么条件下才值得投入？**

产品证据截止 **2026-10-02**；公司分析窗口 **2024Q3–2026Q2**。这是独立外部分析作品。量化部分定位于商业决策与实验分析；金融交易、投资组合和定价模型不在本项目范围。

## 给HR与面试官的阅读入口

| 用时 / 目的 | 推荐入口 | 可以核查什么 |
|---|---|---|
| 2分钟了解项目与岗位能力 | [项目案例与能力证据](docs/PORTFOLIO_CASE_STUDY.md) | 做了什么、为什么做、方法如何支持决策；简历表述与讨论点 |
| 5分钟看核心交付 | [11页商业报告](reports/executive_decision_book.pdf) · [决策卡](reports/decision_card.md) | 市场、经营、量化、试验和监控如何连接 |
| 深入复核 | [最终交付导航](docs/FINAL_DELIVERY.md) · [复现指南](docs/REPRODUCTION_GUIDE.md) | 六类产物、数据口径、来源、验证与局限 |
| 下载正式文件 | [portfolio-v1.0 发布页](https://github.com/EliQuanyi/duolingo-speaking-strategy-analytics/releases/tag/portfolio-v1.0) | 冻结数据包及Word / PDF / Excel |

## 三类岗位能力如何体现

| 岗位方向 | 已完成的分析动作 | 方法与可核查产物 | 可以支持的工作 |
|---|---|---|---|
| **市场调研 / 产品研究** | 将口语痛点拆成H1–H3任务；按同场景六维比较Speak、ELSA、Babbel；逐主张标来源、反例及独立性 | [场景比较](market/competitor_scenario_review.md)、[97条观察账本](market/competitor_evidence_v2.csv)、[证据质量审核](market/competitor_evidence_quality_review.md) | 识别细分任务与产品机制，选择后续研究问题；自选评论不用于总体偏好排名 |
| **数据分析 / 商业分析** | 标准化8季度公开经营指标；分开均值、期末存量和季度流量；对账、基期桥接、增长恒等式及舍入稳健性分析 | [经营复盘](analysis/business_review.md)、[实际输出Notebook](analysis/business_review.ipynb)、[数据质量报告](analysis/data_quality_report.md)、[图点来源](reports/figure_lineage.csv) | 区分活跃结构与获客/回流解释、购买金额与会计收入；避免误归因与错误分母 |
| **商业量化 / 策略分析** | 构建全员双臂贡献与完整成本核算；推导符号盈亏平衡、政策传播与固定费用约束；把缺口转成测量合同 | [Stage4交付](quant/stage4_final_delivery.md)、[模型与Notebook](quant/evidence_model.ipynb)、[核算方法](quant/evidence_assumptions.md)、[缺口账本](quant/stage4_gap_register.csv) | 识别判断盈利所需的最低充分数据、实验及停止条件；未知参数不以模拟值替代 |

技术与方法：**Python标准库 / Decimal / CSV / JSON、matplotlib、Notebook、Excel公式与可编辑图、证据编码、指标治理、描述分解、边界检验、实验设计、决策报告**。SQL、机器学习预测或真实A/B执行不是本项目已完成能力。

## 四项核心判断：发现 → 对决策的作用

1. **任务证据优于功能清单。**97条竞品观察、48个URL对应34位可区分体验者；并非97个独立用户。用户提供的298条Duolingo态度输入另行审查。供给与体验可提出自然开口、引导和净值假设，不能排出跨产品学习效果赢家。[市场收束](reports/market_final_review.md)
2. **参与结构改善，但公司趋势不能证明功能因果。**DAU/MAU从32.9%升至41.7%；最近MAU同比对数项回升中，本期变化与上年比较基数均有作用。进一步验证必须有匹配人群与对照，不能把公司增长填作功能uplift。[经营诊断与基数桥接](analysis/business_review.md)
3. **购买与收入必须分别解释。**2026Q2订阅bookings同比约10.1%，订阅确认收入约22.5%；时点与口径不同。扩张评估需另测套餐替代、退款和完整服务成本。[商业结构](data/public/commercial_structure.csv)
4. **下一步是验证H1任务；权益策略尚未选定。**先确认真实现行权益P0、候选新增与实施权限；学习结果、教学预算和盈利放行分别判断。真实贡献、成本、Max传播、部署人数和固定费未取得时，净值与总体排名保持未知。[量化交接](quant/stage4_final_delivery.md) · [实验方案](experiments/test_plan.pdf)

上述公司数字来自仓库登记的公开披露及派生计算；不是Video Call用户行为数据。引用与精度边界在链接的正文和来源表中。

## 六类交付产物

| 产物 | 文件与形式 |
|---|---|
| Executive Decision Book | [11页PDF](reports/executive_decision_book.pdf) / [Word](reports/executive_decision_book.docx)，4幅报告图，58个图点可对账 |
| 可复现分析数据包 | [冻结清单](data/FINAL_PACKAGE_MANIFEST.md)，81个包内文件、25张CSV；ZIP在发布页下载 |
| Quant Model | [当前v2模型](quant/evidence_model.py) / [Notebook](quant/evidence_model.ipynb)，双臂核算、符号敏感度、3策略比较及未知就绪状态 |
| Experiment Plan与决策卡 | [8页PDF](experiments/test_plan.pdf) / [Word](experiments/test_plan.docx)，[20条拟采集记录合同](experiments/event_spec.csv)，一个主要学习指标 |
| Monitoring Design | [Excel](reports/strategy_dashboard.xlsx) / [2页PDF快照](reports/strategy_dashboard.pdf)，未来输入为空，预设状态与行动 |
| Reusable SOP与复盘 | [SOP](docs/reusable_sop.md) / [复盘](docs/retrospective.md)，角色交接、阶段Gate、修正与停止规则 |

## 复现：不需要内部数据或Office

在仓库或数据包解压根目录，使用Python3.12/3.13：

```bash
python -B scripts/rebuild_package_tables.py
python -B scripts/run_stage4_final.py --check-only
python -B scripts/verify_stage4_final.py --check-only
```

三条命令只读；复算7张派生表、3行基数桥接及58个图点，核验当前v2方法与未知边界。真实经济结果仍应显示未知。Notebook direct、文稿与监控重建使用不同的既有环境，详见[复现指南](docs/REPRODUCTION_GUIDE.md)。[GitHub Actions](https://github.com/EliQuanyi/duolingo-speaking-strategy-analytics/actions/workflows/validate-public-analysis.yml)运行这条标准库复核路径；状态以实际运行记录为准。

## 完成情况与边界

- **已交付**：市场/经营分析、证据约束量化、条件性实验与监控设计、正式文稿、冻结包和复现方法。Stage0–6产物收束，前序降级保持原判定。
- **未识别**：自然使用的全员学习/经营效果、真实ROI、最优权益配置、长期用户预测。试验与生产监控没有执行，现有完成者研究不等于全员ITT。
- **技术限制**：标准Jupyter/ZeroMQ kernel未通过，direct计算已运行；Excel原生Save/PDF因本机许可失败，正式监控PDF为最终xlsx的栅格快照。[完整验收](reports/final_delivery_validation.json)
- **作者与工具**：作者定义并审阅业务范围、提供并确认Duolingo态度输入、确定证据与收束要求；Codex及子agent辅助资料整理、代码、计算、文稿与复核。仓库展示可检查的项目产物，不把AI生成过程改写为未经确认的纯人工经历。[贡献说明](docs/PORTFOLIO_CASE_STUDY.md)

## 仓库导航与文件角色

| 路径 | 内容 |
|---|---|
| `docs/` | 项目案例、决策与主计划、来源政策、交付/复现/发布说明、SOP和后续方向 |
| `market/` | 用户任务、竞品证据与质量审核；公开表限必要事实和自行概括 |
| `data/` | 来源、指标字典、口径、公开CSV、冻结机器清单 |
| `analysis/` | 公司数据分析、实际Notebook、质量/Driver/缺口与方法记录 |
| `quant/` | **当前入口为stage4_final_delivery.md和evidence_model系列**；v1材料仅留作历史审计，明确退出正式论证 |
| `experiments/` | 条件性学习/权益试验方案与未来事件合同 |
| `reports/` | 商业报告、决策卡、监控、来源映射和验收 |
| `scripts/` | 可复现计算、边界检查、报告与数据包构建；Stage2采集工具为可选先导配置 |

私人原始评论、认证、第三方全文及本地自动化接入配置不公开；历史D经济值不进入正式数据包或收益主张。发布范围、权利与历史材料说明见[公开交付说明](docs/PUBLICATION.md)。[后续规划](docs/NEXT_PHASE_PLAN.md)仅保留尚未执行的真实研究路线与输入。

本项目未添加新的开源许可；第三方资料保留原权利。它不代表Duolingo官方观点，也不声称企业采用或已产生营收影响。
