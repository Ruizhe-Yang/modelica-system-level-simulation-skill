# 来源与适用边界

本版以用户提供的 **MOSAIC v0.8 规范、当前 skill 压缩包、最新建模与交互规则汇总（36项）**为唯一工程要求基线。后者在本包中标为 P06；逐条去向见 release_mapping.md 及 assets/latest_requirements.json。源项目的专用入口、目录、文件删除清单、运行阈值和工具权限不作为通用要求。唯一具名案例沿用 12UCubeSat。

| 标记 | 含义 |
|---|---|
| P01 | 历史 MOSAIC v0.4.2，角色、白箱与接口详表的来源 |
| P02 | 历史 MOSAIC v0.5.0，36主条号和分级来源 |
| P03 | 历史 MOSAIC v0.6，图标与品牌参考 |
| P04 | 本次上传的 MOSAIC v0.8 规范正文 |
| P05 | 本次上传的既有 skill 实现（入口与 manifest 标记为0.8） |
| P06 | 本次上传的最新36项建模与交互要求汇总，2026-10-19 |

历史文本不重复叠加执行；当前正文、明确的融合索引与任务合同共同决定适用范围。工具新增行为是为了落实来源要求，并非新增物理建模标准。保留案例中原有证据的历史属性，不把旧测试改写为本次复跑。

## 技术字段核对，不作为新增工程政策

Modelica 3.6 图形/注解字段及 OpenAI 本地 skill 包装方式于 2026-10-19 核对官方文档。前者只核对 Line、Text、Documentation、HideResult、experiment 等语法/语义边界；后者只核对 SKILL.md 元数据和本地发现位置。用户文件仍决定 MOSAIC 工程要求。

- T01 Modelica Association，Annotations： https://specification.modelica.org/maint/3.6/annotations.html
- T02 MSL 4.0.0 原接口资料： https://github.com/modelica/ModelicaStandardLibrary/tree/v4.0.0/Modelica 。色表继承自上传 skill；本次没有下载或重新编译整个 MSL。
- T03 OpenAI，Build skills： https://learn.chatgpt.com/docs/build-skills

这些链接仅用于来源核对，模型与辅助脚本不依赖在线访问。有限静态扫描不替代语言编译器、完整因果分析或原生 GUI。
