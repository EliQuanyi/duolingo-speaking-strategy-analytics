# 阶段交付物与文件格式（定稿）

这里规定**最终要交哪些文件**，内容与通过门槛仍以`MASTER_PLAN.md`为准。Stage0/1通过，Stage2/2.1、Stage3、Stage4和Stage5降级收束；Stage6正式展示完成。Stage4为证据约束核算和交接，真实经济机会未通过；Stage5只完成条件性设计。全部实际文件、验收与限制见`docs/FINAL_DELIVERY.md`，没有真实实验结果文件。

## 格式原则

- `.csv`（UTF-8）：可检查、可复用的数据表；每张表必须有字段/单位/来源说明。
- `.ipynb`：可运行的数据清洗、图表或量化计算源文件；生成的数值以 CSV 导出，避免只留在 Notebook 中。
- `.md`：阶段内可版本管理的研究记录、假设、方法和复盘。
- `.docx`：需要业务人员修改或批注的正式文稿；对应 `.pdf` 是对外阅读的固定版，二者内容一致。
- `.xlsx`：最多两页的监控视图及其可编辑图表；对应 `.pdf` 是快照，不能写成真实上线的自动化看板。
- `.zip`：最终数据移交包；只装许可允许共享的文件。Git 仓库中的 CSV 与代码是权威源，ZIP 从它们生成，不手工维护另一套数据。

## 每阶段必须交付

| 阶段 | 必交文件及格式 | 阶段收束时的交接 |
|---|---|---|
| **0 决策与范围** | `docs/DECISION_BRIEF.md` | 一份可版本管理的决策简报；已完成。正式 Word/PDF 决策摘要统一进入 Stage 6 的 Decision Book，避免重复出稿。 |
| **1 证据与 KPI** | `data/source_register.csv`、`data/metric_dictionary.csv`、`data/data_availability.csv`、`docs/kpi_tree.md` | 已通过；三张 CSV 分别说明来源、指标、可得性/缺口；KPI 树交给市场与经营分析。Stage 3 更新公开数据覆盖与来源。 |
| **2 市场与用户** | `market/market_opportunity.md`、`market/voc_analysis.md`、`market/competitor_matrix.csv`、`data/public/voc_theme_summary.csv` | Markdown 给出洞察与方法；CSV 给出可检查的竞品维度和去标识 VOC 主题计数，不交付大量评论原文。若再分发受限，在文档中给出获取和聚合方法，受限数据不进入公开包。 |
| **3 经营与 Driver** | `data/public/company_quarterly_metrics.csv`、`data/public/product_timeline.csv`、`analysis/business_review.ipynb`、`analysis/business_review.md`、`analysis/data_quality_report.md` | 已降级通过并补强；五文件齐备，另有基期/对账/派生表、有限源审计、稳健性与缺口账本。Notebook在新Python进程真实执行/5图；标准kernel、自然经营效果和成本未通过，特定研究短期学习有受限对照信号。最终报告在Stage6汇总。 |
| **4 量化机会** | `quant/stage4_final_delivery.md`、`quant/evidence_model.ipynb`、`quant/evidence_assumptions.md`、`quant/strategy_comparison.csv`、`quant/stage4_claim_ledger.csv`、`quant/stage4_gap_register.csv`、五张v2公开CSV | 当前v2完成证据约束核算与交接；未知经济参数保持null，符号盈亏平衡与敏感度替代无依据三情景。有限公开核验、直接双臂方法与实际独立验证完成；真实机会/当前资格未通过。v1经济D输出不进入正式包。 |
| **5 决策与实验** | `experiments/test_plan.docx`、`experiments/test_plan.pdf`、`experiments/event_spec.csv`、`reports/decision_card.md` | 可批注和可分发的实验方案、埋点/指标需求表及一张条件性决策卡。没有真实随机实验数据时，不生成“实验结果”文件。 |
| **6 展示与复盘** | `reports/executive_decision_book.docx`、`reports/executive_decision_book.pdf`、`reports/strategy_dashboard.xlsx`、`reports/strategy_dashboard.pdf`、`reports/generated/duolingo_analysis_data_v1.zip`、`docs/retrospective.md`、`docs/reusable_sop.md` | 给决策者的 Word/PDF 商业报告、最多两页的 Excel/PDF 监控视图、可移交数据包，以及实际工作复盘与复用方法。ZIP 内的清单必须列出版本、来源、许可、字段和重建方式。 |

`reports/generated/` 是 Git 忽略的导出目录；最终需分享 ZIP 或 PDF 时，使用正式交付渠道或 GitHub Release 附件。仓库保留可审查的源文件，不把导出文件误当独立数据源。

## 最终给读者的五个入口

1. **商业结论**：`reports/executive_decision_book.pdf`（对应可编辑 `.docx`）。
2. **可视化监控**：`reports/strategy_dashboard.pdf`（对应可编辑 `.xlsx`）。
3. **数据与复现**：`reports/generated/duolingo_analysis_data_v1.zip`，以及仓库中的 CSV、Notebook、来源登记和 `data/public/MANIFEST.md`。
4. **量化依据**：`quant/evidence_model.ipynb`、`quant/evidence_assumptions.md`、`data/public/stage4_economic_readiness.csv`与`stage4_symbolic_sensitivity.csv`；实证未知不填假数。
5. **可执行验证**：`experiments/test_plan.pdf`、`reports/decision_card.md`；复盘与 SOP 保留在 `docs/`。

Stage 6 只汇总和校对前面已经验收的材料，不重新发明数据或结论。每份正式文档都标版本、数据截止日、负责人/作者、来源和未验证事项。
