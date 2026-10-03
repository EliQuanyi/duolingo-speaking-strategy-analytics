# Stage 3 经营与 Driver

Stage 3 已降级通过。入口：[经营复盘](business_review.md)、[质量验收](data_quality_report.md)、[实际输出 Notebook](business_review.ipynb)。数据与字段见 [清单](../data/public/MANIFEST.md)，三项诊断的主张及反例见 [Driver 账本](driver_evidence.csv)。

v1.1专项补强：[因果链](stage3_causal_chain_review.md)、[10项缺口及传导](stage3_gap_register.csv)、[新增10对象源审计](stage3_source_audit.csv)、[3行披露舍入稳健性](../data/public/stage3_robustness_checks.csv)。公司表/原5图未改；学习信号限定随机设计完成者样本，不当全员ITT或经营效果。

v1.2收束优化（2026-10-02）：[3行当期/基期桥接](../data/public/stage3_base_period_bridge.csv)、[2行研究事实输入](../data/public/stage3_learning_study_inputs.csv)、[6行D类选择敏感度](../data/public/stage3_learning_selection_sensitivity.csv)、[新增计算验收](stage3_closeout_validation.json)。经济策略的共同对照/人群/套餐分层契约见经营复盘第5节；完成/替代/未达说明见质量报告第9节。H1/H2/H3不能当互斥ROI方案，学习阈值不是恢复ITT。

在仓库根目录运行：

```powershell
python -B scripts/run_stage3.py --check-only
python -B scripts/run_stage3.py --execute-direct
python -B scripts/verify_stage3.py --rebuild
python -B scripts/review_stage3_limits.py
python -B scripts/closeout_stage3.py
python -B scripts/closeout_stage3.py --check-only
```

实际运行使用 Python 3.13.5 / Anaconda 与已安装版本（requirements.txt），没有新增安装。direct 模式在新 Python 进程执行真实代码单元并保存实际输出，生成 3 CSV、5 PNG 和机器校验记录。标准 `--execute` 是 nbclient/Jupyter；本机 ZeroMQ 失败，kernel 验收未通过，不能称普通 Run All 已验证。

生成图位于 Git 忽略目录 `figures/`，Notebook 内保存真实图输出；从公开 CSV 可重建图片。源网页到 CSV 为人工抽取，临时 ignored JSON 不是运行依赖。公司级指标不能识别 Video Call 因果效果、分群转化或单位成本；报告只用于经营背景和下一阶段条件性分析。
