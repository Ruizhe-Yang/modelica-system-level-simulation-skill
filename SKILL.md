---
name: mosaic
description: Build and maintain Modelica system-level models using the concrete MOSAIC modeling standard. Use for TB/SB/AB whitebox composition, BU behavior and MSL reuse, interface/state/configuration reviews, Documentation and result comments, Modelica Icon/Diagram and connection-color maintenance, diagnostics, simulation, and scoped auxiliary patches. Preserve the requested change boundary and accepted working source; do not trigger physics refactoring for documentation or graphics work.
license: GPL-3.0; see LICENSE
compatibility: Python 3.10+ for bundled static helpers. A separately installed Modelica engine is required for compilation and simulation. MAT metadata inspection additionally needs scipy/numpy. No automatic network or software installation.
metadata:
  version: "0.8.0"
  standard: "MOSAIC v0.8"
---

# MOSAIC｜Modelica 总体建模规范

**Model the Whole as MOSAIC.**

按实际系统组织模型，把装配、行为、接口、状态、配置和维护内容写清楚。规范是工程分工约定，不是另一个需要导入的 Modelica 库，不承诺仅遵守形式就自动达到实机精度。

## 1. 先确定任务范围

读取当前用户要求、实际源代码、工程说明、配置和已认可基线。当前明确指令优先于旧提示词；不能从规范升级推导出源码全面重构的授权。默认中文说明，合法类名和已有入口保持。

| 工作模式 | 允许内容 | 保护边界 |
|---|---|---|
| NEW / REFINE | 已授权的模型、接口、配置、行为及闭环验证 | 原有有效用途；不擅自降低验收条件 |
| CONFIGURE | 权威配置、离线生成、单位和消费者核对 | 不静默新增第二套默认值 |
| AUDIT | 默认只读；记录角色、依赖、源事实与未知项 | 不因为发现差异直接改模型 |
| DOCUMENTATION_ONLY | Documentation、声明字符串说明、明确发布元数据 | 所有行为、实际连接、图形与求解注解 |
| CONNECTION_COLOR_ONLY | 实际 connect 的 Line.color | connect 端点、points、线宽、图标图案、所有行为 |
| VISUAL_ONLY | 用户明确授权的 Icon/Diagram/Placement/Line | 字段类型、参数、初始化、状态、实际 connect |
| RESULTS / DIAGNOSE | 真实结果、分层排查与必要的有限复现 | 不造数据，不把短诊断拼成完整任务 |

多个辅助模式可由用户明确组合。发现范围外行为缺陷时记录位置与影响，不擅自修复。辅助维护不自动进入仿真调参循环。

## 2. 规范等级与角色底线

先读 [完整 M01—M36](references/standard.md)，涉及架构时再读 [角色详细合同](references/model_roles.md)。本版 **26 项 R 必须、9 项 S 建议、1 项 F 参考**。A/B/C/D 附录均为参考；只有项目明确选用的附加要求才加入该任务检查集。

**TB、SB、AB 全部是白箱，不存在默认宽松、可选严格两套定义。** 有效本层只声明、配置和连接；检查继承与 modifier，不只搜索当前文件的 equation。物理/控制行为必须有明确承担者。

| 角色 | 应有内容 | 不应有内容 |
|---|---|---|
| TB 顶层盒 | 完整实验、生效配置、对象/边界/必要上下文、connect、实验设置 | 本层控制律、积分、任务算法、初始补方程；被当作功能子实例 |
| SB 系统盒 | 实际集成边界、公开接口、静态配置分配、SB/AB/BU/LU 和可导航 Diagram | 本层胶水计算、隐藏状态、跨层穿透 |
| AB 装配盒 | 末级 BU/LU 装配、共同边界和 connect；两个及以上有实际作用的叶子 | 本层行为、AB/SB 嵌套却仍称末级装配、无意义实例凑数 |
| BU 行为单元 | 内聚方程/算法、参数、端口、变量、必要状态与初始化 | 独立运行 model/block 子实例，包括 MSL 运行组件 |
| LU 库复用单元 | 原始 MSL，或只改静态参数/呈现的别名；原库内部结构保留 | 新增本构/状态/输出计算后仍称纯库别名 |

固定维数、仅含 connect、可确定展开的静态 for/if 连接模板和经检查的白箱继承可用。它们不是允许在白箱加入计算的例外。常量运行输入也采用显式源连接，`component(u=1)` 不是参数配置。已认可工程可以继续保留；角色重新识别不等于本次授权改动行为。

TB/SB/AB/BU/LU 是概念，不是命名前缀。允许 MSL 传感器；图标、逐类说明、语言和目录习惯按建议，不复活旧禁令。默认以自有源码与 MSL 4.0.0 为原生依赖；既有冻结版本不擅自升级。外部集成仅按明确批准的项目 profile。

## 3. 按任务读取，不把所有长文一次塞入上下文

| 任务 | 参考文件 |
|---|---|
| 架构、五角色、白箱语法、支撑类内容 | [model_roles.md](references/model_roles.md)、[architecture.md](references/architecture.md) |
| 接口、状态、参数与输出最小合同 | [interfaces_contracts.md](references/interfaces_contracts.md)、[MSL 接口目录](references/msl_interfaces.md) |
| 配置与曲线生成、消费、单位 | [configuration.md](references/configuration.md) |
| 文档清理、名称去重、结果字段说明 | [documentation.md](references/documentation.md) |
| 模型图标、父层布局、MSL 派生/自定义线色 | [visuals.md](references/visuals.md) |
| MOSAIC 自己的品牌与文档样式 | [brand.md](references/brand.md) |
| 诊断、编译、结果与性能 | [verification.md](references/verification.md)、[evolution.md](references/evolution.md) |
| Codex 执行、范围、停止与交付 | [codex.md](references/codex.md) |
| 旧条号/旧 skill 迁移 | [traceability.md](references/traceability.md)、[upgrade.md](references/upgrade.md) |
| 唯一具体项目案例 | [12ucubesat.md](examples/12ucubesat.md) |

## 4. 新建或行为改进

明确用途、任务时域、构型、边界、关键结果、必需检查与预算。列实际组成、必要物理/信息耦合、每个状态的唯一拥有者，再设计公开接口和数据合同。

先做最小真实闭环，再局部细化。装配层只连接；传感、单位转换、仲裁、积分和查表各归明确行为/库单元。命令、实际作用、测量、估计和只读诊断分别定义。单位换算、额定基准、曲线和初态同源消费。为满足目标直接令真实状态等于参考值不是建模。

实际验证按加载/依赖 → 展开/平衡 → 编译 → 初始化/积分 → 原始结果 → 项目指标/独立守恒 → 必要性能定位推进。单次超时、短诊断和旧结果不冒充当前完整任务。没有引擎就标 NOT_RUN，不制造 MAT 或 PASS。具体硬秒数、状态规模和图数不是通用规范。

## 5. 文档、名称与线色维护

文档写用途、必要接口/配置、组成或行为、真实状态和使用限制。不逐类生成通用的“连接与责任”统计、“仿真后如何查看”教程或“Documentation 辅助更新……”免责声明。删套话不等于删真实限制、许可、初始化或有效域说明。

模型树由工具显示 `ClassName (description)` 时，声明只写中文用途：`model Device "设备中文用途"`。不要写成 `"Device（设备中文用途）"`。不改 ClassName、within、实例名或结果路径。结果栏注释用原声明的 string-comment，不新增输出方程、改 unit/HideResult/保存过滤器；旧结果不会自动更新描述。

连线先追溯两个端点的真实类型、别名/extends、成员路径。MSL 及其派生用原族默认色；自定义整体连接用已核对主色。自定义总线内 MSL 类型成员仍按该成员的 MSL 颜色，不能跟随整个总线。仅修改真实 connect 的 Line.color，不改图标内装饰线。不能通过一律删除 color 指望工具必然恢复原色。未知类型先报告，不凭名称或相邻线猜测。

生成器的文档后处理与调色白名单须和本次新约定同步，防止下次生成恢复旧套话。输入数值/数学摘要与生成字节摘要分别维护，原 RunId 仍是历史证据。

## 6. 可执行辅助工具

所有命令以本 skill 为当前目录；模型路径由当前任务填写。工具默认不安装软件、不联网、不运行物理模型。

```bash
# 只读盘点；不是编译器或完整符合性证明。
python scripts/audit_project.py /path/to/Project --output /path/to/audit.json
python scripts/audit_roles.py /path/to/Project --roles /path/to/role-map.json --output /path/to/roles.json

# 仅清理指定文稿内容，输出必须是新的独立候选目录。
python scripts/clean_documentation.py /path/to/source /path/to/new-candidate --report /path/to/doc-cleanup.json

# 先只读线色核对；确认任务允许后才增加 --apply。
python scripts/connection_colors.py /path/to/Project --report /path/to/line-colors.json

# 精确辅助保护比较：颜色豁免仅在已授权调色时打开。
python scripts/verify_aux_only.py /path/to/baseline /path/to/candidate \
  --allow-root-version --allow-connection-colors \
  --allowlist /path/to/exact-aux-files.json --output /path/to/protected-diff.json

# 已审查类目录生成文稿，或读取现有结果元数据。
python scripts/enrich_documentation.py /path/to/source /path/to/new-candidate --catalog /path/to/catalog.json
python scripts/inspect_result_metadata.py /path/to/model_init.xml --csv /path/to/descriptions.csv
python scripts/check_contract.py /path/to/results-contract.json
python -m unittest discover -s tests -v
```

只有 Documentation 的任务**不加** `--allow-connection-colors`；只增声明说明时连根版本开关也可不加。其他非 `.mo` 变更逐文件列白名单，白名单不等于文件内容已经人工正确。`audit_roles` 只核对提供的角色映射与有限静态结构；不可解析的 MSL 展开、redeclare 和静态模板保留待核，不报完整符合性 PASS。更多接口族需读取真实库源码扩充规则，不猜颜色。

需要实跑且已获授权时，用 `run_guarded.py --cwd ... --timeout <项目秒数> --log ... --metadata ... -- <实际命令>` 做外部监督。工具可用状态、编译状态和运行状态分别登记。

## 7. 最后交付

按用户指定格式交付有效工程、必要配置/结果和一份累积总结；默认不额外做数据图。报告实际变更、静态核对、真实运行、R/S/F 状态、已知限制和精确加载入口。ZIP 内保留一个活动语言根；版本化文件名不改变类目录。不清理未获授权资源，不替用户删除旧 skill 或改账号设置。
