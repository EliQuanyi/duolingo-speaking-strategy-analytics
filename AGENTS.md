# 本仓库执行规则

遵循用户提供的通用 AGENTS.md；本文件只补充 Duolingo 项目的范围与收束条件。

1. 先读 `docs/DECISION_BRIEF.md`、`docs/MASTER_PLAN.md`、`docs/STAGE_STATUS.md`、`docs/DATA_POLICY.md` 和 `git status`。只做当前阶段，按 `docs/STAGE_TEMPLATE.md` 记录验收。
2. 决策问题固定为 Speaking / Video Call 的扩张评估。市场、经营、量化分析优先；长期用户增长点预测仅作可选情景，不建立无依据的精确预测模型。
3. 每个重要数字保留来源 URL、报告期、口径、单位、采集日期。事实、管理层归因、代理指标、模型假设、模拟数据必须显式区分。
4. 公开公司级指标不能证明 Video Call 的因果效果。缺少用户级数据时，只做实验设计、条件性建议和敏感度分析；不得声称真实实验结果。
5. 每阶段严格执行 `docs/MASTER_PLAN.md` 的数量上限与 Gate。超出范围的材料记入阶段模板的“待办/舍弃”，不继续扩展。
6. 后续新增代码时，先使用现有依赖；仅为实质性计算添加必要依赖。验证运行结果后更新 README 和阶段状态。
