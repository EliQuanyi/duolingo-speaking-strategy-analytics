# 可复现分析数据包规范

**状态：Stage6按显式白名单冻结；实际版本、成员/粒度/哈希见`data/FINAL_PACKAGE_MANIFEST.md`和`data/final_package_manifest.json`，验收见`reports/final_delivery_validation.json`。**数据集是本项目的正式交付物，不只是Notebook临时输入。只分享必要公开事实、自己的概括/分析/方法；不含私人原始评论、第三方全文、密钥或历史D经济输出。来源原权利不因打包而转移。

最终移交格式为`reports/generated/duolingo_analysis_data_v1.zip`，包含白名单CSV、正式产物/必要代码、自带`MANIFEST.json`与`README_PACKAGE.md`；仓库CSV/代码为权威源。包内`data/public/MANIFEST.md`为当前冻结清单；仓库同名文件保留历史工作记录并在顶部指向最终清单。逐字段解释见`data/PACKAGE_FIELD_REFERENCE.md`。

## 分阶段形成

| 阶段 | 数据包增量 |
|---|---|
| Stage 1 | 来源登记、指标字典、可得性/缺口矩阵；确定拟建表的主键、粒度和字段。 |
| Stage 2 | 保存 VOC 采样与编码方法；只在许可允许时公开去标识的主题汇总，不公开大批原文评论。 |
| Stage 3 | 形成标准化的公司级季度指标与产品事件时间线，保留从原始来源到整理值的转换记录和质量检查。 |
| Stage 4 | 当前v2收录公开观察、研究分析覆盖、经济/政策就绪与符号敏感度；未知经济结果为空，不要求作者数值情景。 |
| Stage 6 | 冻结可共享版本、补齐清单和重建说明，并与报告中的每张图和每个关键数字对账。 |

Stage3公司表及计算表已形成，详见[清单](public/MANIFEST.md)。VOC公开表限已审阅的去标识汇总。Stage4 v1的`scenario_results.csv`、`stage4_billing_paths.csv`、`stage4_break_even.csv`、`stage4_sensitivity.csv`与D图/参数不进入正式v2证据包；保留原文件只供历史审计。Stage4正式增量以清单第6节五张v2CSV、当前模型与主张/缺口为准，不从目录全量打包。

## 每份正式数据包必须有

1. `data/public/MANIFEST.md`：文件清单、版本/冻结日期、行数、覆盖时间、来源 ID/URL、许可或再分发判断、限制、构建命令和校验结果。
2. 机器可读的 CSV：一行代表什么、主键是什么、时间粒度、单位/币种、缺失值如何表示；字段含义与 `metric_dictionary.csv` 一致。
3. 转换与复现说明：原始资料如何获取、清洗/计算的脚本或 Notebook、依赖版本、运行顺序；无法共享原始文件时说明可复现边界。
4. 质量记录：主键重复、缺失、时间范围、数值范围、单位及报告数字对账的**实际**检查结果。

数据包只回答本项目决策所需问题，不追求收集所有 Duolingo 或竞品数据。可借鉴 [Frictionless Data Package 的元数据思想](https://specs.frictionlessdata.io/data-package/)，但本项目先用 CSV + Markdown 清单，不提前引入额外工具或规范依赖。
