<p align="center">
  <img src="assets/mosaic-logo.png" alt="MOSAIC — Model the Whole as MOSAIC" width="560">
</p>

<h1 align="center">MOSAIC-skill</h1>
<p align="center"><strong>Modelica System-Level Modeling & Engineering Maintenance Skill</strong><br>
面向 AI 编程助手的 Modelica 总体建模、规范检查与工程维护技能</p>
<p align="center"><em>Model the Whole as MOSAIC.</em></p>

<p align="center">
  <a href="https://github.com/Ruizhe-Yang/MOSAIC">📘 MOSAIC 建模规范 · v0.8</a>
  &nbsp;·&nbsp;
  <a href="./SKILL.md">🧭 SKILL.md · 技能入口</a>
  &nbsp;·&nbsp;
  <a href="./VALIDATION.md">✅ 核验记录</a>
  &nbsp;·&nbsp;
  <a href="#english-documentation">English Introduction</a>
</p>

**MOSAIC-skill** 将 [MOSAIC 总体建模规范](https://github.com/Ruizhe-Yang/MOSAIC) 转化为可供 **Codex 及兼容 Agent Skills 的 AI 编程助手**按需使用的工作指导、参考资料与本地辅助工具。它帮助开发者基于实际 Modelica 工程开展**新建、细化、配置、架构审查、文档与图形维护、问题诊断和变更保护**，并明确什么时候可以修改物理行为、什么时候必须保护已有仿真结果。

> **English overview:** MOSAIC-skill is an AI-agent skill for **system-level Modelica engineering**. It operationalizes the [MOSAIC modeling specification](https://github.com/Ruizhe-Yang/MOSAIC) with task-scoped guidance, model-role rules, interface and configuration references, static audit tools, and change-boundary checks. It assists engineering work; it is **not a Modelica library, numerical solver, or a substitute for actual compilation and simulation**.

**当前版本：** MOSAIC-skill **v0.8.0**，对应 **MOSAIC v0.8**；技能标识名为 `mosaic`，入口是仓库根目录的 `SKILL.md`。

## MOSAIC 和 MOSAIC-skill 是什么关系？

| | [MOSAIC 规范仓库](https://github.com/Ruizhe-Yang/MOSAIC) | **MOSAIC-skill（本仓库）** |
|---|---|---|
| 角色 | 定义 Modelica 总体级建模方法、规则和工程约定 | 帮助 AI Agent 在实际 Modelica 项目中执行、检查和维护这些约定 |
| 核心载体 | [完整中文 HTML 规范](https://github.com/Ruizhe-Yang/MOSAIC/blob/main/MOSAIC_v0.8_Modelica_Modeling_Standard.html) | `SKILL.md`、`references/`、`scripts/`、`assets/`、`tests/` |
| 使用方式 | 人工阅读、设计评审、团队建模规范 | 在支持本地 Agent Skills 的宿主中安装，按任务调用 |
| 运行 Modelica 模型 | 不提供求解器 | 使用用户已安装并明确授权的 Modelica 工具，skill 自身不提供求解器 |

**先有工程规范，再有辅助执行规范的 skill。** 规范可独立用于人工建模；使用 skill 时不要求把 MOSAIC 仓库导入 Modelica，更不需要创建一个空的“MOSAIC 库”。当前两个仓库的规范版本均为 **v0.8**。

## 能做什么？

MOSAIC-skill 内置 **M01—M36（26 项必须、9 项建议、1 项参考）** 的规则参考、TB/SB/AB/BU/LU 五类角色要求、MSL 接口参考，以及按任务分离的实施模式。

| 工作模式 | 典型任务 | 变更边界 |
|---|---|---|
| **NEW / REFINE** | 从零建立总体仿真、细化现有系统、改进行为闭环 | 仅在用户授权的范围内修改结构、接口、方程与配置，并真实验证 |
| **CONFIGURE** | 管理设计参数、曲线、单位、离线配置生成及其消费者 | 保持单一权威配置，避免引入第二套默认值 |
| **AUDIT** | 检查模型角色、连接、参数来源与可疑结构 | 默认只读，发现问题不自动改动 |
| **DOCUMENTATION_ONLY** | 清理冗余 Documentation、修正变量说明、统一类说明 | 不修改方程、初始化、端口、图形或结果过滤设置 |
| **CONNECTION_COLOR_ONLY** | 核对 MSL/派生接口与自定义接口的真实连线颜色 | 只允许已授权的 `Line.color` 变更；不修改 `connect` 端点 |
| **VISUAL_ONLY** | 优化模型 Icon、Diagram、Placement 与图形表达 | 不改物理行为、参数、接口字段或实际连接 |
| **RESULTS / DIAGNOSE** | 基于真实仿真结果定位问题、检查闭环与性能 | 区分旧结果、短诊断、完整任务和实际运行状态 |

模式按任务调用，支持在获得明确授权时组合多个辅助模式。**发现不属于当前任务范围的问题时应先报告，不应借“规范升级”擅自重构已认可工程。**

### 规范中的五类模型角色

- **TB（Top-level Box）、SB（System Box）、AB（Assembly Box）**：三者都是白箱，本层负责声明、静态配置及真实连接。
- **BU（Behavior Unit）**：实现内聚的方程、控制算法、状态与必要初始化。
- **LU（Library Unit）**：复用 MSL 组件或未改变行为的静态/呈现别名。

这些名称表达**职责，不是必须写在类名中的前缀**。完整角色合同见 [`references/model_roles.md`](./references/model_roles.md)，主规则见 [`references/standard.md`](./references/standard.md)。默认 Modelica 依赖基线为项目自有源码和 **MSL 4.0.0**；不会自行升级既有项目的冻结依赖。

## 安装

本仓库是**可放入本地 Agent Skills 目录的 skill 源码**，不是通过 ChatGPT 插件商店一键安装的账号插件。以支持此目录发现约定的 Codex 本地环境为例，任选一个安装位置：

| 范围 | 目标目录 |
|---|---|
| 当前工程专用 | `<your-project>/.agents/skills/mosaic/` |
| 当前用户共用 | `$HOME/.agents/skills/mosaic/` |

**方法 A：Git 克隆到工程级位置**（在你的工程根目录执行，需已安装 Git）：

```bash
mkdir -p .agents/skills
git clone https://github.com/Ruizhe-Yang/modelica-system-level-simulation-skill.git .agents/skills/mosaic
```

**方法 B：下载 ZIP：** 在 GitHub 上选择 **Code → Download ZIP**，将仓库内容解压到一个名为 `mosaic` 的目录，并将该目录放入上述位置之一。应能直接看到 `mosaic/SKILL.md`，**不要出现 `mosaic/某个带版本号的文件夹/SKILL.md` 的额外嵌套**。

实际的安装路径、自动发现和调用语法由所用 Agent Skills 宿主决定。完成安装后，必要时重启客户端；不支持此目录约定的宿主需按各自文档配置。本 skill **不会自动安装软件、联网下载 Modelica 库、修改客户端设置或删除旧技能**。

## 怎么调用？（示例）

在支持显式调用的宿主中使用 **`$mosaic`**，并写清目标、允许的修改范围和验收条件。

**示例 1 · 新建/细化总体仿真**

```text
使用 $mosaic（NEW / REFINE）。
为当前 Modelica 工程设计系统级闭环仿真：先明确总体用途、
任务时域、系统边界、TB/SB/AB/BU/LU 角色、接口与状态责任，
再完成必要配置和物理实现。基于实际可用的 Modelica 工具编译、
运行并验证关键指标；保留已认可的有效模型和参数。
输出可加载工程、实际验证记录与未完成项。
```

**示例 2 · 只维护文档和连接线颜色**

```text
使用 $mosaic（DOCUMENTATION_ONLY + CONNECTION_COLOR_ONLY）。
仅清理冗余 Documentation、修正类说明，并核对真实 connect
对应的 MSL/派生/自定义接口线色。不得修改参数、方程、初始值、
端口类型、connect 端点、Icon、Placement 和求解设置。
先输出独立候选，再做精确保护差异检查并报告无法确定的接口。
```

**示例 3 · 只读检查**

```text
使用 $mosaic（AUDIT）。
分析当前模型入口、五类角色、接口与状态归属、配置消费和
运行证据，区分必须项、建议项与未知项。只输出问题清单、
依据、建议和优先级，不修改工程文件。
```

更细的宿主执行、停止条件与交付约束见 [`references/codex.md`](./references/codex.md)。

## 内置参考资料与可执行工具

```text
mosaic/
├── SKILL.md                 # 技能入口及任务路由
├── references/              # 规范、角色、接口、配置、图形、验证等
├── scripts/                 # 本地审查、文档维护和变更保护工具
├── assets/                  # 规则、角色映射、合同和工程报告模板
├── examples/12ucubesat.md   # 已认可工程的使用参考（不含完整模型）
├── tests/                   # 工具自动化测试
├── VALIDATION.md            # 已执行与未执行的验证记录
├── manifest.json            # 发布元数据和文件校验摘要
└── LICENSE / NOTICE.md      # 许可和来源说明
```

| 工具 | 作用 |
|---|---|
| `audit_project.py`、`audit_roles.py` | 只读盘点模型源码、显式角色映射及待核内容 |
| `connection_colors.py` | 检查端点/类型与线色；默认只读，明确加 `--apply` 才写回 |
| `clean_documentation.py`、`enrich_documentation.py` | 在独立候选目录处理说明文本 |
| `verify_aux_only.py` | 对比原工程和候选工程，检查辅助修改是否越界 |
| `inspect_result_metadata.py`、`check_contract.py` | 检查结果元数据及预定结果合同 |
| `run_guarded.py` | 在明确授权且存在外部 Modelica 命令时监督执行与超时 |

在 skill 根目录中可先进行只读试用和工具测试：

```bash
python scripts/audit_project.py /path/to/ModelicaProject --output /path/to/audit.json
python scripts/connection_colors.py /path/to/ModelicaProject --report /path/to/colors.json
python -m unittest discover -s tests -v
```

**环境要求：**核心辅助脚本使用 Python **3.10+** 标准库；MAT 元数据读取另可能需要 `numpy`/`scipy`。若需要编译或仿真，必须另有实际 Modelica 引擎（如 OpenModelica 或 MWorks）及可执行模型，并以实际环境完成验证。

## 实际验证范围与限制

[`VALIDATION.md`](./VALIDATION.md) 记录了发布时在 **Linux / Python 3.13** 环境通过的 **51 项工具单元测试**。覆盖部分源级审查、文档候选生成、角色检查、线色处理及变更保护逻辑；**没有完成真实 Codex/其他宿主的端到端安装测试，也未在该核验中执行 OpenModelica/MWorks 编译、仿真或 GUI 检查**。

本包的静态工具不是完整 Modelica 解析器或物理正确性判定器。对未知接口类型、复杂继承、`redeclare` 和未能展开的模板，应明确报告待核，不将“未发现问题”等同于规范全通过。12UCubeSat 是**方法使用参考**，其具体配置、参数、运行记录与领域结构不构成所有工程必须复制的模板。

完整规则与设计依据以 [MOSAIC v0.8 中文规范](https://github.com/Ruizhe-Yang/MOSAIC/blob/main/MOSAIC_v0.8_Modelica_Modeling_Standard.html) 为准；升级说明参见 [`references/upgrade.md`](./references/upgrade.md)。

## 许可、品牌与交流

本仓库的源码和技能文本按 **GPL-3.0** 发布，详见 [`LICENSE`](./LICENSE) 和 [`NOTICE.md`](./NOTICE.md)。MOSAIC 品牌标识具有独立权属，其图像使用不因源码许可而自动获得额外授权。

欢迎通过 GitHub Issues 提供 Modelica 建模案例、可复现问题、规则改进建议及工具兼容性反馈。

---

<p align="center"><strong>Model the Whole as MOSAIC.</strong><br><sub>One modeling specification · A practical AI-assisted workflow</sub></p>


---

<a id="english-documentation"></a>

# MOSAIC-skill — English Introduction

**Modelica System-Level Modeling & Engineering Maintenance Skill**  
*Model the Whole as MOSAIC.*

**MOSAIC-skill** is an **AI Agent Skill for practical system-level Modelica engineering**. It translates the [MOSAIC modeling specification](https://github.com/Ruizhe-Yang/MOSAIC) into task-oriented guidance, reusable references, static checking scripts, and controlled maintenance workflows for AI coding assistants such as **Codex** and other compatible Agent Skills hosts.

Its purpose is to help engineering teams build and maintain **understandable, configurable, reusable, and verifiable** multi-physics models while respecting the boundary between **authorized behavior changes** and **documentation, diagram, or audit-only work**.

- **Skill name:** `mosaic`
- **Skill version:** `0.8.0`
- **Aligned modeling standard:** **MOSAIC v0.8**
- **Entry point:** [`SKILL.md`](./SKILL.md)
- **Underlying specification:** [MOSAIC v0.8 Chinese HTML document](https://github.com/Ruizhe-Yang/MOSAIC/blob/main/MOSAIC_v0.8_Modelica_Modeling_Standard.html)

> **MOSAIC is the modeling methodology; MOSAIC-skill helps AI agents apply it to real projects.** The skill is not an independent Modelica library, compiler, solver, or automatic physical-validity guarantee.

## Why use MOSAIC-skill?

Developing a system-level Modelica model requires consistent decisions across system structure, internal dynamics, interfaces, parameter sources, diagrams, testing, and ongoing maintenance. These concerns are especially important when an AI assistant changes an existing, already working engineering model.

MOSAIC-skill provides:

- **A concrete set of engineering rules:** M01–M36, including 26 required rules, 9 recommended rules, and 1 reference rule.
- **Clear model responsibilities:** detailed contracts for TB/SB/AB white boxes, BU behavior units, and LU standard-library reuse.
- **Task-scoped workflows:** distinguish new model development from configuration, static audits, diagram updates, documentation work, and result diagnosis.
- **Safer maintenance:** preserve equations, parameters, initialization, connector definitions, and validated connections when the request only concerns presentation or documentation.
- **Reusable checking helpers:** project inventory, role audits, connector color checks, generated documentation, and protected-diff validation.
- **Evidence-aware reporting:** distinguish source-level checks, compilation, full simulation, results, and model fidelity instead of treating them as interchangeable.

The rules support projects in aerospace, energy, vehicles, and other multi-physics domains. They do not prescribe a domain-specific physical architecture or universally valid model parameters.

## MOSAIC model roles

The skill follows the five roles defined by the MOSAIC specification:

| Role | Responsibility |
|---|---|
| **TB — Top-level Box** | Composition-only simulation entry containing the selected scenario, model instances, static configuration, and connections. |
| **SB — System Box** | Composition-only system or subsystem boundary with public interfaces and organized internal components. |
| **AB — Assembly Box** | Composition-only final assembly of BU/LU components and their static connections. |
| **BU — Behavior Unit** | Coherent physical equations, control or mission algorithms, owned states, and initialization. |
| **LU — Library Unit** | Reuse of native MSL components or aliases that only alter static parameters or presentation, not behavior. |

**TB, SB, and AB are all white boxes at their own level.** Their responsibility is declaration, static configuration, and connection. Behavioral equations and state evolution belong to explicitly identified BU/LU components. These are *conceptual roles*, not class-name prefixes.

The default baseline uses project-owned source files and **Modelica Standard Library 4.0.0**; an established project with a frozen, validated dependency version is not automatically upgraded.

See [`references/model_roles.md`](./references/model_roles.md) for the detailed role requirements and [`references/standard.md`](./references/standard.md) for the complete M01–M36 rule set.

## Task modes and modification boundaries

Choose the mode based on the **actual task authorization**:

| Mode | Typical use | Protection principle |
|---|---|---|
| **NEW / REFINE** | Build a new executable system model or refine physical/control behavior | Change only the authorized architecture, implementation, and configuration; validate in a real Modelica tool when available |
| **CONFIGURE** | Update parameters, curves, initial conditions, and offline configuration generation | Maintain a single authoritative source and consistent consumers |
| **AUDIT** | Review roles, interfaces, dependencies, state ownership, and evidence | Read-only by default; findings do not authorize modifications |
| **DOCUMENTATION_ONLY** | Improve class descriptions, Documentation, and result comments | Do not change physics, initialization, connectors, diagrams, or solver settings |
| **CONNECTION_COLOR_ONLY** | Check and correct actual connection-line colors against verified connector types | Only authorized `Line.color` changes; no connection endpoints or diagram geometry changes |
| **VISUAL_ONLY** | Improve native `Icon`, `Diagram`, and component placement | Preserve numerical behavior, connector fields, and actual `connect` topology |
| **RESULTS / DIAGNOSE** | Investigate genuine results, simulation failures, and performance | Distinguish historical runs, diagnostics, and completed validation |

Modes may be combined when explicitly authorized. A newly identified modeling problem must **not** trigger unrequested physical refactoring during a documentation-only or graphics-only task.

## Installation

This repository contains **source files for a local Agent Skill**. It is **not** a one-click ChatGPT account plugin and does not install Modelica or change user settings automatically.

For Codex environments using the supported local skill-discovery convention, choose **one** of these destinations:

| Scope | Install folder |
|---|---|
| Current project | `<your-project>/.agents/skills/mosaic/` |
| Current user | `$HOME/.agents/skills/mosaic/` |

**Option 1 — clone into a project** (run from the project root):

```bash
mkdir -p .agents/skills
git clone https://github.com/Ruizhe-Yang/modelica-system-level-simulation-skill.git .agents/skills/mosaic
```

**Option 2 — ZIP installation:** select **Code → Download ZIP** in GitHub, extract the repository, and place its contents inside a folder named `mosaic` at one of the locations above.

Check that the file is located at `mosaic/SKILL.md`, rather than inside an extra version-named subfolder. Restart the host application if necessary. Other Agent Skills hosts may use different installation and invocation conventions; follow the host's own documentation.

## Using the skill

In hosts that support explicit skill activation, invoke **`$mosaic`** and specify the engineering task, allowed modifications, validation requirements, and deliverables.

**Example A — read-only project review:**

```text
Use $mosaic in AUDIT mode.
Inspect the Modelica project structure, TB/SB/AB/BU/LU responsibilities,
interface types, state ownership, design configuration, and available
simulation evidence. Report required-rule violations, recommendations,
uncertainties, and priorities. Do not modify any project files.
```

**Example B — build or refine an executable model:**

```text
Use $mosaic in NEW / REFINE mode.
Define the system purpose, scenarios, model roles, component interfaces,
parameter sources, and acceptance criteria. Implement the authorized
Modelica components, preserve valid existing behavior, and perform actual
model checking and simulation using the available Modelica engine.
Report what was verified and what remains incomplete.
```

**Example C — strictly scoped documentation and visual maintenance:**

```text
Use $mosaic in DOCUMENTATION_ONLY + CONNECTION_COLOR_ONLY modes.
Clean redundant Documentation and correct verified MSL-derived or custom
connector line colors. Preserve all physical equations, initial values,
parameters, interface fields, connect endpoints, Icon geometry, Placement,
and experiment settings. Generate a separate candidate and a precise
protected-difference report before delivery.
```

For Codex-specific execution and stopping rules, see [`references/codex.md`](./references/codex.md).

## Repository organization

```text
mosaic/
├── SKILL.md                   # Skill identity, routing, and core policy
├── references/                # Standard, roles, architecture, interfaces,
│                              # configuration, visuals, diagnostics, and Codex
├── scripts/                   # Local audits, maintenance, and change checks
├── assets/                    # Rules, contracts, templates, and brand assets
├── examples/12ucubesat.md     # One accepted project use-case explanation
├── tests/                     # Unit tests for bundled helper scripts
├── VALIDATION.md              # Documented testing and verification limits
├── manifest.json              # Release metadata and content digest inventory
└── LICENSE / NOTICE.md        # License and source information
```

Primary tools include:

| Script | Purpose |
|---|---|
| `audit_project.py` | Inventory Modelica project structure and selected source-level elements |
| `audit_roles.py` | Examine explicitly mapped model roles and flag unsupported or uncertain cases |
| `connection_colors.py` | Audit actual line colors against known connector families; apply only when expressly enabled |
| `clean_documentation.py`, `enrich_documentation.py` | Generate reviewed documentation changes into separate candidates |
| `verify_aux_only.py` | Compare the baseline and candidate to identify modifications outside the authorized scope |
| `inspect_result_metadata.py`, `check_contract.py` | Examine available result metadata and declared contracts |
| `run_guarded.py` | Supervise an authorized external command with bounded execution time |

A simple read-only starting point from the skill directory is:

```bash
python scripts/audit_project.py /path/to/ModelicaProject --output /path/to/audit.json
python scripts/connection_colors.py /path/to/ModelicaProject --report /path/to/colors.json
python -m unittest discover -s tests -v
```

Core scripts target **Python 3.10+**. Reading some MAT results additionally requires **NumPy and SciPy**. Actual compilation or numerical simulation requires a separately installed and configured Modelica tool such as **OpenModelica** or **MWORKS.Sysplorer**.

## Verification status and limitations

The published [`VALIDATION.md`](./VALIDATION.md) reports **51 passing unit tests** on **Linux / Python 3.13** for the bundled static tools and checks. This does **not** establish that end-to-end skill installation has been tested in every host or that OpenModelica/MWorks compilation, simulation, and GUI behavior have been verified for the release.

The helper scripts are **not complete Modelica parsers or type checkers**. Unsupported connector families, inheritance, `redeclare` usage, and statically expanded connection patterns require further inspection. A clean static audit does not prove runtime correctness, physical fidelity, or safety compliance.

The included [12UCubeSat example](./examples/12ucubesat.md) documents how the method was applied to an accepted system architecture. It **does not include the complete simulation project or numerical output files**. For a public Modelica application of MOSAIC, see [OneSatSim](https://github.com/Ruizhe-Yang/OneSatSim).

## License, branding, and contributions

The code and skill materials are published under **GPL-3.0**; see [`LICENSE`](./LICENSE) and [`NOTICE.md`](./NOTICE.md). The supplied MOSAIC brand artwork retains its separate ownership and does not automatically receive additional trademark or brand-use permissions through the source-code license.

Issues and contributions are welcome, particularly for real Modelica engineering examples, reproducible failures, clear model-role contracts, and improvements to supported tool workflows.

<p align="center"><strong>Model the Whole as MOSAIC.</strong><br><sub>One engineering specification · A practical AI-assisted modeling workflow</sub></p>
