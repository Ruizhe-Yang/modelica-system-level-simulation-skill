---
name: mosaic
description: Build, review and maintain Modelica system-level models with the MOSAIC standard. Use for TB/SB/AB whitebox composition, BU behavior and MSL reuse, business composite interfaces, visible connections, state/configuration contracts, Documentation and result metadata, Modelica Icon/Diagram and connection colors, formatting-only patches, interface refactoring, diagnosis and regression. Read the actual project, preserve approved baselines, and keep every action inside the requested change scope.
license: GPL-3.0; see LICENSE
compatibility: Python 3.10+ for static helpers. Compilation and simulation require a separately installed Modelica engine. MAT metadata inspection additionally requires numpy/scipy. No automatic network access or software installation.
metadata:
  version: "0.9.0"
  standard: "MOSAIC v0.9"
---

# MOSAIC｜Modelica 总体建模规范

**Model the Whole as MOSAIC.**

按实际系统组织模型，把装配、行为、接口、状态、配置和维护内容写清楚。MOSAIC 是工程分工规范，不是必须导入的运行库。按规则组织工程有助于复用与交接，物理可信度仍须按用途和实际证据判定。

## 1. 先选任务模式，再确定修改集合

读取当前用户要求、实际源码、配置、工作规则和已认可基线。当前明确指令优先于旧提示词；规范升级不产生自动重构授权。使用 `assets/project_contract.json` 明确模式、白名单、结果合同、工具权限和停止条件；模板默认只读 AUDIT。

| 模式 | 可以处理 | 必须保护 |
|---|---|---|
| NEW / REFINE | 获授权的结构、行为、配置与真实闭环 | 原有有效用途和冻结验收条件 |
| INTERFACE_REFACTOR | 获授权的端口、因果方向、访问范围、成员映射与 connect | 其余行为；验证展开网络、初始化、状态和结果路径，不能归类为绘图 |
| CONFIGURE | 权威配置、离线生成、单位和消费者 | 不新增第二套默认值；生成器不回灌旧结构 |
| AUDIT | 只读盘点、审查、缺陷和未知项登记 | 不能因发现差异就写入模型 |
| DOCUMENTATION_ONLY | 类级 Documentation 与原声明 string-comment | 普通注释、计算、字段属性、图形、connect、求解与结果设置 |
| CONNECTION_COLOR_ONLY | 真实 connect 的 Line.color | 端点、points、线宽、图标内 Line、所有行为与其他注解 |
| VISUAL_ONLY | 明确授权的 Icon / Diagram / Placement / 连接 Line | connector 类型、方向、访问范围、参数、初态、connect 端点、求解和结果设置 |
| AUXILIARY_ONLY | 明确组合的文稿和真实连接色 | 不自动豁免其他图形或任何行为 |
| FORMAT_ONLY | 字符串和注释之外的空白排版 | 字符串、普通注释、计算与图形 Token、语句顺序和所有版本文字 |
| RESULTS / DIAGNOSE | 真实结果、分层定位及获授权的必要复现 | 不造数据，不把短诊断拼为完整任务 |

根发布版本仅在用户要求时额外允许，MSL 依赖版本不能一起替换。发现范围外缺陷，报告事实与影响，不擅自修改。未授权仿真的辅助工作不进入调参循环。

## 2. 规范等级与角色底线

先读 [完整36条主规范](references/standard.md)。**26项R必须、9项S建议、1项F参考**；[36项新要求映射](references/release_mapping.md) 是来源索引，不是额外36条主规范。U-A01—U-H05、主条号 M01—M36、Codex C01—C10 和历史 G01—G136 各自区分。

**TB、SB、AB 全部是白箱。BU 禁止 connect 和独立运行 model/block 子实例。LU 原库内部结构保留。** 检查本类、继承、重声明与 modifier，不能只查文件名或当前 equation 段。

| 角色 | 应有内容 | 不应有内容 |
|---|---|---|
| TB 顶层盒 | 完整实验、配置、对象/环境/任务/结果边界、必要上下文、connect、实验设置 | 本层控制律、积分、任务算法、初始化补方程；作为系统的功能子实例 |
| SB 系统盒 | 真实集成边界、公开端口、静态配置、SB/AB/BU/LU、可导航 Diagram | 本层胶水计算、隐藏状态、跨层穿透 |
| AB 装配盒 | 两个及以上有实际作用的 BU/LU、共同边界与 connect | 本层行为、系统/装配嵌套、无意义实例凑数 |
| BU 行为单元 | 不可再分的内聚机制或必要转换；参数、端口、方程/算法、状态、初态 | connect；独立运行子组件；为接口集成把已有系统装进“大BU” |
| LU 库复用单元 | 原生MSL或只改静态参数/呈现的别名 | 修改原库；新增行为后仍标纯库别名 |

优先 **多SB＋多AB＋多LU＋尽可能少BU**，不设数量占比。静态参数、可静态展开且只含 connect 的 for/if 模板可用；`child(u=source.y)` 和 `child(u=1)` 都是禁止的白箱运行输入绑定。普通转换优先 MSL，必要自有行为才建 BU。

角色不是命名前缀。允许MSL传感器。接口整合、图标外框、左入右出、中文文稿和 Scripts 目录属建议作者配置；需要时显式选用 `assets/authoring_profile.json` 为 PROJECT_REQUIRED，不暗中改变R/S/F。已经选用的真实类型、语义、来源和可见拓扑仍满足R条。

## 3. 按任务读取参考

| 任务 | 文件 |
|---|---|
| 五角色、18类白箱语法与支撑类明细 | [model_roles.md](references/model_roles.md)、[architecture.md](references/architecture.md) |
| 具名复合接口、局部分接、字段合同、幽灵端口 | [interfaces_contracts.md](references/interfaces_contracts.md)、[24类MSL接口](references/msl_interfaces.md) |
| 离线配置、纯模型执行、生成器防回退 | [configuration.md](references/configuration.md) |
| 文档、名称、结果注释、纯排版 | [documentation.md](references/documentation.md) |
| 图标、全部连线可见、端点、默认线色 | [visuals.md](references/visuals.md) |
| 原MOSAIC标识与蓝白文档样式 | [brand.md](references/brand.md) |
| 诊断、分层证据、接口回归与性能 | [verification.md](references/verification.md)、[evolution.md](references/evolution.md) |
| Codex实施、最终回归、失败后继续修复 | [codex.md](references/codex.md) |
| v0.9融合与替换旧skill | [release_mapping.md](references/release_mapping.md)、[upgrade.md](references/upgrade.md) |
| 历史索引和来源边界 | [traceability.md](references/traceability.md)、[sources.md](references/sources.md) |
| 唯一具体项目案例 | [12ucubesat.md](examples/12ucubesat.md) |

## 4. 接口集成与模型更新

同一业务的多个量优先采用具名复合接口，在边界整接口连接；接收者只消费所需字段。在所属 SB/AB 中以 `connect(bus.field, component.port)` 接入MSL标量口，不用白箱等式或BU内connect作分接。删除“总线→多余边界标量→再次汇总”的无意义回路时，保留必要父子边界转发；不要退回密集外露端口来掩盖问题。

逐层、逐成员核对生产者、消费者、单位、维数、方向、时间及有效性。不能把混合总线全改为output，也不能删方向消除告警。物理势/flow/stream/参考关系不改为普通Real总线。

每条源级connect在声明白箱的有效Diagram有可辨Line；protected本地端口仍在本层可见。禁止visible=false、零线宽、零尺寸/画布外端口掩盖接线。数组模板与继承需要进一步展开核对，不以源级扫描冒充展开检查。

删除接口、调整因果性/访问范围或重写connect属于语义修改，即使公式和方程数没变。冻结可信基线和回归合同，按初始化、连续轨迹、离散顺序及结果路径验收。参数和曲线在准备阶段固化到.mo；生成器不得恢复旧接口、旧文稿、幽灵端口或旧配色。

## 5. 文稿、名称、图形与格式

说明根据实际源码写用途、接口/参数、组成或行为、真实初态和有效限制；不写不存在成员，不逐类堆重复路径、版本、通用查看教程与审计套话。保留许可与真实限制。模型树自动显示类名时，string-comment只写中文用途，不重写英文标识符。结果注释写在真实声明上，不新增输出方程、状态或结果别名；未生成新结果只能声明源码注释已更新。

MSL/派生端口沿类型继承使用本族默认线色；自定义整体线用已审查主色，其中MSL成员仍使用成员的标准色。不凭图标第一块色或类名猜色；不以删除color证明恢复默认色。工具写入仅对已确认4.0.0的有限色表开放，其他版本须查实际源码扩展注册表。

原生Icon、黑线微色、同族有区别、因果左入右出、核心模型突出是绘图建议。已认可图形不为无关补丁全面重绘；删低价值装饰不等于删除实际运行显示。移动实例须联动真实端点和父层画布，不能改connect端点来修正像素位置。

纯排版保留必要单个分节空行，不追求零空行。任何注释/字符串/图形Token改动都超出FORMAT_ONLY。图形参数按具体图元核对；空graphics的规避只针对确有兼容问题的目标软件。

## 6. 可执行工具

下列路径以本skill目录为当前目录；所有输出应放在审核工程之外。脚本不安装软件、不联网；只读核对不调用Modelica求解器。

```bash
# 只读基础、显式角色和源级连接审查
python scripts/audit_project.py /path/to/Project --output /path/to/audit.json
python scripts/audit_roles.py /path/to/Project --roles /path/to/role-map.json --output /path/to/roles.json
python scripts/audit_connections.py /path/to/Project --output /path/to/connections.json

# 安全格式候选：只整理非字符串/注释区域的尾空白和冗余空行，不承诺全语法缩进
python scripts/format_modelica.py /path/to/source /path/to/new-candidate --report /path/to/format.json
python scripts/verify_change_scope.py /path/to/source /path/to/new-candidate \
  --mode format-only --output /path/to/protected-diff.json

# 真实连接色审查；自定义主色先填表并人工确认reviewed=true
python scripts/connection_colors.py /path/to/Project --msl-version 4.0.0 \
  --palette /path/to/reviewed-palette.json --report /path/to/colors.json
# 获授权后才在独立候选目录增加 --apply；未知或冲突连接时不写入

# 文稿清理候选及精确保护
python scripts/clean_documentation.py /path/to/source /path/to/new-doc-candidate --report /path/to/docs.json
python scripts/verify_change_scope.py /path/to/source /path/to/new-doc-candidate \
  --mode documentation-only --output /path/to/doc-diff.json

# 根据已审查目录生成说明、核对真实结果元数据和合同结构
python scripts/enrich_documentation.py /path/to/source /path/to/new-candidate --catalog /path/to/catalog.json
python scripts/inspect_result_metadata.py /path/to/model_init.xml --csv /path/to/descriptions.csv
python scripts/check_contract.py /path/to/results-contract.json
python -m unittest discover -s tests -v
```

`verify_change_scope.py`支持format-only、documentation-only、connection-color-only、visual-only及auxiliary-only五种辅助保护模式；没有通用“忽略全部annotation”开关。根发布版本用明确的`--allow-root-version`；FORMAT_ONLY不允许该开关。非.mo文件的改动需要精确路径白名单，标为AUX_FILE_REVIEW另审，不等于通过。

保留的`verify_aux_only.py`供旧生成钩子兼容；v0.9新任务优先用按模式隔离的`verify_change_scope.py`。这些检查是有限词法/源结构工具，不是完整解析器、因果证明、继承展开器或GUI验证器。未支持语法、未知端口、展开未核实应保持REVIEW_REQUIRED/NOT_CHECKED。

## 7. 终止条件与交付

源码检查、编译展开、动态结果和原生GUI四组证据分别记录，每个引擎/版本单独记状态。没有omc或目标软件时交付实际可完成的源检查并标NOT_RUN，不能把静态预览当软件截图。

项目启用“最终一次完整回归”时，最终候选必须完成该任务并按预先冻结路径、容差与离散事件比较；必要诊断/失败后的修复不受“一次”数量限制。缺失列不填零，不删失败路径，不放宽阈值凑通过。当前任务未启用硬预算时，不继承案例秒数、方程数或连接数量。

仅交付当前任务需要的工程、配置、真实结果和一份累积总结；Codex默认不制作仿真数据图。删除目录/根文件、启动GUI、推送仓库、安装或替换旧skill分别需要当前授权，不从任何案例的操作清单复制权限。
