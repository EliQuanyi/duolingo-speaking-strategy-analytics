# 数据目录

- `source_register.csv`：每个来源的 URL、时间、证据等级、用途及限制。
- `metric_dictionary.csv`：指标定义、粒度、单位、计算方法及适用边界。
- `raw/`、`processed/`、`private/` 已在 `.gitignore` 中排除。后续只提交许可允许再分发、体量适当且来源清楚的必要数据；否则提供获取脚本或步骤和校验值。
- `PACKAGE_SPEC.md`：正式数据包的表、元数据、质量检查与分阶段交接要求。当前整理表进入 `public/`，字段、粒度、来源、校验值和运行边界见 [public/MANIFEST.md](public/MANIFEST.md)。

Stage3已生成并核验公司季度表及派生/补强表。来源登记目前21条；Stage4 v2新增S021日本App Store报价观察，标价不可比，未追认目标账户权益或真实经济参数。派生与管理层归因显式区分。

CSV是分析权威输入，原网页抽取为人工核验；运行不依赖ignored临时JSON或评论原文。`python -B scripts/run_stage3.py --execute-direct`用既有Notebook环境重建3派生表/5图；质量见[报告](../analysis/data_quality_report.md)。Stage6收束冻结为v1.1、81文件/25CSV，实际成员/字段/哈希见[最终清单](FINAL_PACKAGE_MANIFEST.md)与[字段说明](PACKAGE_FIELD_REFERENCE.md)。最小包内复算为`python -B scripts/rebuild_package_tables.py`；[复现指南](../docs/REPRODUCTION_GUIDE.md)说明环境，不含私有298条原始编码或旧D经济输出。

Stage4当前v2正式增量为28行公开观察、2行研究分析覆盖、6行经济就绪、2行政策就绪、8行符号敏感度；后三者是数据契约和数学关系，不是观察样本。经济结果空白，不以作者数值补实证。清单第6节给字段、来源、校验和与重建；第5节v1 D表仅历史审计，排除正式包。
