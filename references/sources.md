# 来源与适用边界

工程政策以用户提供的 MOSAIC v0.4.2、v0.5.0、v0.6、既有 v0.7 及本轮 v0.8 修订要求为依据。旧文用于恢复具体的角色/语法清单，不重新启用角色前缀、MSL 传感器禁令或强制图标样式。当前规则是 `standard.md` 与 `model_roles.md`；历史去向见 `traceability.md`。

具体项目案例只采用用户提供的 12UCubeSat/OneSatSim 源码。案例中的配置、层数、时域和任务数量都不是通用要求；实际使用说明与运行证据分别记载。

## 主条文的来源标记

| 标记 | 对应输入 |
|---|---|
| P01 | MOSAIC v0.4.2：角色与白箱公共语法、接口、状态 |
| P02 | MOSAIC v0.5.0：M01—M36条号、分级与历史索引 |
| P03 | MOSAIC v0.6：Modelica图形与项目视觉参考 |
| P04 | 已有MOSAIC v0.7、12UCubeSat认可架构与辅助维护方法 |
| P05 | 当前v0.8修订要求：具体规范、文稿清理、名称去重、线色和品牌 |

同一条目可能由多个输入合并。来源不构成继续叠加的旧要求，当前正文及分级优先。

## 技术核对资料（2026-10-10）

- Modelica Association，Language Specification 3.6，Annotations：`https://specification.modelica.org/maint/3.6/annotations.html`。Documentation、图元、Line.color 默认、显示与求解相关注解。
- Modelica Association，Connectors and Connections：`https://specification.modelica.org/maint/3.6/connectors-and-connections.html`。语义以语言标准为准；白箱分工是 MOSAIC 工程约定。
- Modelica Standard Library，固定 tag `v4.0.0`：`https://github.com/modelica/ModelicaStandardLibrary/tree/v4.0.0/Modelica`。核对接口族的原始类型和图形颜色，不要求把项目依赖升级到最新库。
- OpenAI 官方 Build skills：`https://learn.chatgpt.com/docs/build-skills`。SKILL.md、可选资源目录、agents/openai.yaml、Codex本地发现路径。
- 前作：`https://github.com/Ruizhe-Yang/modelica-system-level-simulation-skill`。作为既有功能范围和许可的历史来源；本版不依赖旧 skill，也不把旧要求无条件叠加。

静态辅助工具使用有限语法解析和明确类型表，不是完整编译器。无法展开的类型、重声明和模板应保留待核，不能用“没发现”冒充全部符合。这里的 URL 是追溯资料，不是模型运行依赖。
