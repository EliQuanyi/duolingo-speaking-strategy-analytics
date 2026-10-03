# 复现与交付使用指南

更新2026-10-03；事实截止2026-10-02；公司窗口2024Q3–2026Q2。本指南同时适用于仓库和解压后的最小数据包，先选择所需层级，避免为阅读报告配置整套Office或Jupyter。

## 1 先阅读 再核验

- 业务读者：[最终交付](FINAL_DELIVERY.md) → [商业报告](../reports/executive_decision_book.pdf) → [决策卡](../reports/decision_card.md)。
- 复核者：[字段说明](../data/PACKAGE_FIELD_REFERENCE.md)、[公共清单](../data/public/MANIFEST.md)及来源登记，随后执行下方只读命令。
- 下一轮执行者：[后续规划](NEXT_PHASE_PLAN.md) → 选定一条路线 → 按授权/测量Gate启动。没有授权或数据时不自动实施试验。

仓库的`data/public/MANIFEST.md`是带历史说明的工作记录，顶部指向最终清单；**包内同名文件是当前冻结清单**。包内根目录`MANIFEST.json`为逐文件哈希/表结构，仓库镜像为`data/final_package_manifest.json`。ZIP本身和仓库最终验收JSON不收入ZIP，避免循环打包和循环哈希。

## 2 最小复核 仅需Python标准库

在仓库或解压后的根目录，选一个可用的Python3.12或3.13环境执行：

```powershell
python -B scripts/rebuild_package_tables.py
python -B scripts/run_stage4_final.py --check-only
python -B scripts/verify_stage4_final.py --check-only
```

三条命令都不写业务文件。第一条从实际CSV复算7张派生、3行基数桥接及58图点，另两条核当前v2一致性和独立方法/边界。真实经济结果应继续显示unknown/空白；这也是正确运行结果。不是零利润，也没有实验效果。

本轮在bundled Python3.12.14的新解压目录真实执行通过。复现起点是所供公开CSV；原网页抽取、人工编码、私有298条记录、访问资格与数据真实性不由这些命令认证。

**仓库交付核验**：使用下方文稿环境运行`python -B scripts/verify_final_delivery.py --check-only`，需要pypdf及仓库最终验收JSON。此命令不适用于最小包。`python -B scripts/build_final_data_package.py --check-only`需要仓库里已构建的ZIP；检查授权白名单、版本、CRC/哈希，并再解压复算。包的成员不能仅靠自己的清单宣称合法。

## 3 需要重建时再选择环境

| 任务 | 实际环境与依赖 | 命令 / 写入范围 |
|---|---|---|
| 只重建当前派生表 | Python标准库 | `python -B scripts/rebuild_package_tables.py --rebuild`；只重写3张公司和4张v2派生表，不写原始事实/旧D |
| Notebook direct | 既有Anaconda Python3.13.5；matplotlib3.10.0、nbformat5.10.4、IPython8.30.0等，完整版本见analysis/requirements.txt | `python -B scripts/run_stage3.py --execute-direct`与`python -B scripts/run_stage4_final.py --execute-direct`；重建Notebook输出/相关CSV、图及运行记录 |
| Word/报告图 | bundle26.909.12148 Python3.12.14；python-docx1.2.0、matplotlib3.11.2；Windows Microsoft YaHei | `python -B scripts/build_final_documents.py --book-only`或`--test-plan-only`；分别改对应Word，报告路线同时重建4图和figure_lineage |
| 同版Word PDF | Word COM16.0 | `./scripts/export_final_documents.ps1`；默认重新导出两份Word的PDF；可用RelativePaths只处理一份 |
| PDF视觉验收 | bundled Poppler、pypdf6.10.0、Pillow12.3.0 | `python -B scripts/render_final_pdfs.py reports/executive_decision_book.pdf experiments/test_plan.pdf`；输出PNG后仍须实际查看，程序不自动认定排版通过 |
| 监控重建 | bundled Node/artifact-tool与Python、Excel COM16.0 | `./scripts/build_monitoring_dashboard.ps1`；重建xlsx、实际视图/PDF和QA；技术限制见监控说明 |
| 冻结包 | Python标准库 | `python -B scripts/build_final_data_package.py`；只从显式白名单读入并生成ZIP、仓库清单，然后解压验证 |

环境不可混用：bundled Python没有nbformat/IPython，不能冒充Notebook环境；Anaconda版本清单也不是文稿依赖清单。Windows运行时分别位于`%USERPROFILE%/anaconda3/python.exe`和`%USERPROFILE%/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。其他机器须自行提供相应既有环境；本项目没有自动安装步骤或跨系统Office排版保证。

执行写入命令前保留当前版本，在新解压副本或明确工作目录重建；不要将重建当只读检查。修改内容/数据后，刷新受影响验收记录，再冻结新包并运行最终只读核验，不能只保留旧哈希收据。

## 4 已接受的技术边界

- 标准Jupyter/ZeroMQ kernel未通过；实际direct执行已通过。读报告及最小计算不要求交互kernel。只有需要交互交付时再定位该问题，不因它无限扩大当前任务。
- Excel原生重算/配色/图编辑已检查；Save与原生PDF导出因本机许可过期失败。正式监控PDF为最终xlsx重导入渲染的两页栅格快照，正文不可搜索，编辑使用xlsx。详情在[监控说明](../reports/monitoring_design.md)。
- Word内公式、中文和PDF需要真实目视；文本一致/哈希一致不等于排版或研究效应通过。软件边界用例不进入业务数据。
- 完整研究PDF、实时账户资格、真实成本/账单、Max传播和部署规模仍缺；不因工程可运行而放行商业Scale。

## 5 文件角色与分享范围

报告解释商业判断；Notebook与CSV保留计算；事件表是未来规格；监控是拟实施规则；SOP沉淀方法。[后续规划](NEXT_PHASE_PLAN.md)集中列发布/招募/授权/测量/经济数据的待输入事项。当前整理不联系参与者、不改变权益、不加入新License、不发布到外部服务。

最小包不收私人原始评论、第三方全文或历史D经济/选择情景。历史记录可能引用仅在仓库保留的材料，先按包内README_PACKAGE和本指南的可用命令运行。来源原权利不因打包变成开放许可；需要公开发布时再按所选范围核共享清单。
