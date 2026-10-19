# MOSAIC-skill v0.9

**基于 Modelica 的复杂系统总体建模通用架构与规范。**

Model the Whole as MOSAIC.

技能入口为 `SKILL.md`，技能名 `mosaic`，发布版本 `0.9.0`。本包以提供的 v0.8 规范和既有 skill 为基线，融合最新36项建模与交互要求。面向新建、细化、审查和持续维护 Modelica 总体工程；不是新的 Modelica 运行依赖。

## 这版具体补了什么

| 内容 | v0.9 实施落点 |
|---|---|
| 装配和行为 | TB/SB/AB白箱只声明、配置、连接；BU无connect和独立运行子实例；MSL优先，不把系统装配藏进大BU |
| 接口集成 | 按业务组织复合接口，边界完整连接，局部白箱分接；逐层逐成员核对因果与生产/消费，不退回冗余端口墙 |
| 可见拓扑 | 每条源级connect在声明白箱可见，端点正确；protected不能隐藏接线；不通过零尺寸、零线宽、画布外位置伪造简洁 |
| 文稿和再生成 | 声明说明与真实成员对应；模板不恢复已删接口、旧文稿、幽灵端口和旧色；结果描述需要实际元数据证据 |
| 变更保护 | 新增FORMAT_ONLY和INTERFACE_REFACTOR边界；按精确节点豁免，不把全部annotation删去后宣称计算未变 |
| 辅助工具 | 新增按模式保护、保守空白整理和源级连接可见性检查；BU connect与自定义调色色表加强核对 |

完整主规范仍是 **M01—M36：26必须、9建议、1参考**；**U-A01—U-H05**是最新来源36项的完整映射，不重复计为36条新硬规范。角色明细、18类白箱语法、24类MSL接口、绘图/品牌/文稿/Codex参考一并保留。具体案例仅含12UCubeSat。

## 安装与调用

将ZIP里的整个 `mosaic/` 放在**一个**需要的位置：项目的 `<repo>/.agents/skills/mosaic/`，或用户的 `$HOME/.agents/skills/mosaic/`。`SKILL.md`直接位于该目录下，不再套一层版本目录。宿主发现方式参考OpenAI官方[Build skills](https://learn.chatgpt.com/docs/build-skills)（2026-10-19核对）；未显示时按宿主文档重新启动或刷新。其他Agent Skills宿主按自己的加载方式使用。

替换前备份旧skill，只保持一个活动 `mosaic`；同名副本不会自动合并。此ZIP没有执行安装，不更改本机或账号设置。

```text
使用 $mosaic，先只读审查本工程。按M05/M07/M08核对真实角色和继承后的实现，
检查复合接口、全部connect的可见性及生成器回退风险。
按R必须、S建议、F参考分别列出事实和未知项；本轮不修改源码、不启动GUI、不仿真。
```

```text
使用 $mosaic，采用FORMAT_ONLY。只删除不必要空行和尾空白，保留注释、字符串、
计算/图形Token及语句顺序。输出独立候选与保护比较结果；再次格式化应无新变化。
```

接口删除、方向/访问范围或connect改写应选择INTERFACE_REFACTOR，明确语义验收；不能借VISUAL_ONLY授权执行。建议作者配置见 `assets/authoring_profile.json`，默认未启用；选用后才形成项目附加要求。

## 入口与目录

| 入口 | 用途 |
|---|---|
| `SKILL.md` | 任务模式、关键规则、按需加载、工具与交付 |
| `references/standard.md` + `assets/rules.json` | 同一份36条主规范的可读/机器形式 |
| `references/model_roles.md` | 五角色、白箱语法、支撑类和检查卡 |
| `references/release_mapping.md` + `assets/latest_requirements.json` | 最新36项来源→主规范→等级的追溯 |
| `references/interfaces_contracts.md` | 接口、状态、参数、结果合同与集成方法 |
| `references/visuals.md` / `documentation.md` / `codex.md` | 绘图、文稿、自动化参考，按任务独立启用 |
| `assets/` | 项目/角色/结果/接口/作者配置、审查色表、报告模板及原品牌图 |
| `scripts/` | 保守静态辅助工具；不替代Modelica编译器 |
| `tests/` / `VALIDATION.md` | 可重跑测试及本次实际核验记录 |
| `examples/12ucubesat.md` | 仅作工程方法参照，不复制其参数与专属操作 |

## 自测与边界

```bash
python -m unittest discover -s tests -v
```

静态辅助工具使用Python 3.10+标准库；MAT元数据需要numpy/scipy。编译/仿真必须另外安装真实Modelica引擎。本包不会自动联网、安装软件、运行模型或删除旧skill。工具会将未支持的解析/展开事项保留为待核，而不是发出完整工程符合性证明。

本次只更新规范与skill。Modelica项目源码、仿真结果和原生GUI没有随此发布重新验证。实际测试见 `VALIDATION.md`，完整文件摘要见 `manifest.json`。升级说明见 [upgrade.md](references/upgrade.md)。

## English overview

MOSAIC v0.9 is a concrete, source-oriented standard for maintainable Modelica system-level projects. It separates whitebox composition (TB/SB/AB), cohesive project behavior (BU), and unchanged MSL reuse (LU). The upgrade covers business composite interfaces, visible source connections, scoped documentation/graphics/formatting maintenance, generator stability, and evidence-based interface refactoring. Mandatory rules, recommendations and references remain distinct. The bundled Python helpers provide conservative static assistance, not compiler or simulation certification.

The only named engineering example is 12UCubeSat. Install one active `mosaic/` folder with `SKILL.md` directly inside, then invoke `$mosaic` in a compatible host.

## 许可

沿用GNU GPL version 3，完整条文见 `LICENSE`，来源与品牌边界见 `NOTICE.md`。用户提供的MOSAIC LOGO原样保留，品牌权属与代码许可区分；不分发字体文件。
