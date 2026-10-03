# Stage 4 量化机会

**当前版本v2.0：核算与决策交接降级通过，真实经济机会未通过。**最终交付不使用作者经济数值、D热图或无来源的数值门槛。Stage5条件性设计已交付，真实试验尚未执行；最终状态见[阶段状态](../docs/STAGE_STATUS.md)。

## 阅读与交付

1. [Stage4最终交付](stage4_final_delivery.md)：证据→实际增量→经济条件→最低数据→条件行动。
2. [有限公开补证](stage4_public_evidence_v2.md)与[观察CSV](../data/public/stage4_public_observations.csv)：权益、不可比报价、同研究访问与分母。
3. [逐主张](stage4_claim_ledger.csv)与[缺口](stage4_gap_register.csv)：事实/推断/设计、关联板块及获取与停止点。
4. [核算契约](evidence_assumptions.md)、[真实输入](evidence_inputs.json)、[代码](evidence_model.py)与[Notebook](evidence_model.ipynb)：未知留null，双臂直接核算，3单元实际direct输出。
5. [策略比较](strategy_comparison.csv)、[经济就绪](../data/public/stage4_economic_readiness.csv)、[政策就绪](../data/public/stage4_policy_readiness.csv)、[符号敏感度](../data/public/stage4_symbolic_sensitivity.csv)、[研究覆盖复算](../data/public/stage4_learning_coverage.csv)。
6. [最终验证记录](stage4_final_validation.json)：实际计算、独立复核、来源范围、文档一致性与未达项。

## 复现

从仓库根目录使用既有环境（[依赖版本](../analysis/requirements.txt)）：

```powershell
python -B scripts/run_stage4_final.py --execute-direct
python -B scripts/run_stage4_final.py --check-only
python -B scripts/verify_stage4_final.py --check-only
```

运行使用当前Notebook源单元，不静默覆盖用户编辑。direct为新Python进程顺序执行，标准Jupyter kernel仍未验收。v2不读v1输入/派生表，不需要认证或安装；公开来源核验是有限人工操作，非运行命令自动刷新。

四张v2派生CSV由代码生成；公共观察与主张/策略/缺口表是可审计人工整理。观察/输入变化后须重建并审核。测试fixture仅在验证源码，不进入业务CSV。

## v1历史边界

`opportunity_model.*`、`scenario_inputs.json`、`parameter_register.csv`、四张D派生表、两张D图和`stage4_validation.json`均属v1方法演示，**不在正式v2证据包**。旧报告与假设已标历史，原始快照在`history/`。原v1审核证明当时计算，不证明参数合理；当前`strategy_comparison.csv`已切为v2，旧比较快照单列。后续不运行旧D构建或继承其经济门槛。
