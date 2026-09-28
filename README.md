# Duolingo Speaking Strategy Analytics

围绕一个管理决策开展的公开数据商业分析作品：**Duolingo 应如何评估 AI Speaking / Video Call 扩张，下一步优先验证哪种覆盖策略？**

重点展示市场调研、经营数据分析和量化决策支持。当前是**仓库初始化**：已有范围、证据规则和阶段验收门槛；尚未完成市场研究、经营分析、实验或 Dashboard。

## 阅读顺序

1. [总纲与主计划](docs/MASTER_PLAN.md)：完整业务闭环、12 个业务板块与 7 个执行阶段的映射、各阶段交接和通过门槛。
2. [决策简报](docs/DECISION_BRIEF.md)：问题、对象、边界与已核实的事实。
3. [数据与缺口规则](docs/DATA_POLICY.md)：证据等级、缺失数据处理和结论措辞。
4. [阶段状态](docs/STAGE_STATUS.md)：当前进度和下一阶段。

## 仓库结构

| 路径 | 用途 |
|---|---|
| `docs/` | 决策、计划、数据规则、验收记录与项目记忆 |
| `data/` | 来源登记、指标字典；后续存放可再分发的数据与处理说明 |
| `market/` | 市场、竞品与 VOC 研究 |
| `analysis/` | 公开经营指标的清洗、可复现分析与 Driver 诊断 |
| `quant/` | 情景、敏感度、单位经济与盈亏平衡模型 |
| `experiments/` | 对照实验方案；真实结果须有真实实验数据 |
| `reports/` | 决策卡、简报与监控视图 |

## 执行方式

每次只推进 [总计划](docs/MASTER_PLAN.md) 中的**当前阶段**：读取阶段状态 → 产出最小交付物 → 按 [阶段模板](docs/STAGE_TEMPLATE.md) 自检 → 更新阶段状态。门槛通过后再进入下一阶段；不可获得的数据按数据政策降级，不为填满图表而造数。

初始化阶段没有代码依赖或测试命令。后续引入分析代码时，再记录环境、数据获取方式、运行命令和实际验证结果。

## 资料起点

- [Duolingo 2026 Q2 股东信](https://www.sec.gov/Archives/edgar/data/1562088/000162828026053299/q2fy26duolingo6-30x26share.htm)
- [Duolingo 2026 Q2 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1562088/000162828026053603/duol-20260630.htm)
- [Duolingo IR 季度报告索引](https://investors.duolingo.com/financial-information/quarterly-results)

这是独立研究作品，不代表 Duolingo 官方观点。外部数据、评论与第三方代码的许可需要逐项检查；目前未复制外部项目代码或数据集。
