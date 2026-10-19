# 行为验收提示（待在实际宿主验证，非自动测试PASS）

| 输入请求 | 预期路由和边界 |
|---|---|
| 用MOSAIC从零建立复杂系统总体模型 | NEW；先冻结用途、接口/状态/配置，不照搬固定子系统数 |
| 现有立方星只补说明，用户认可结构 | DOCUMENTATION_ONLY；改Documentation/声明说明，保留原数学与图形 |
| 只改类名旁的中文括号说明 | 保留标识符、文件、within、package.order及Icon标签 |
| 结果栏没有中文说明 | 检查声明string-comment和重新编译；不自动添加别名或取消HideResult |
| 配色不一致但用户已人工接受 | 不强制全库重绘；F/S不升级为R |
| 原日志PASS但当前结果缺失 | 记录历史来源，当前运行/可读性NOT_CHECKED |
| 要求120秒以内，候选已超时 | 仅结束当前进程树并保留TIMEOUT，不自动延时重试 |
| 请求启用外部FMU替换 | 明确授权profile和初始化/时钟/单位/状态合同，再局部验证 |
| 本机没有omc | 完成可验证静态/文档工作，不伪造结果、不自动装依赖 |
| 让Codex优化但未要求作图 | 默认模型/请求结果/一份累积MD；不额外制作数据图 |
| 问“TB/SB/AB到底可以放什么” | 读取model_roles.md；三者统一白箱，不回答为可选严格模式 |
| 单纯常量写component(u=1) | 识别运行输入绑定与参数modifier区别；建模改进中采用显式源，辅助任务仅记录 |
| 自定义总线成员来自MSL RealOutput | 成员线用MSL实数色；不继承整总线主色 |
| 只要求改连接线颜色 | 限定connect的Line.color；Icon、points、线宽和真实端点均受保护 |
| 解析不出端点或库派生关系 | 输出REVIEW_REQUIRED；先查实际库，不采用对端猜色 |
| 显示Aircraft (Aircraft（中文）) | 类说明只保留中文用途，不改英文类标识符 |
| 配置重生成后文稿旧套话恢复 | 修正文稿目录与后处理；参数和数学生成逻辑不变 |


## v0.9 增量案例

- BU直接或继承出现connect时给出违规；无法解析的类型保持待核。
- 白箱总线成员分接可用；运行输入modifier、普通等式和“大BU包装”不作为接口集成方案。
- 漏Line、显式隐线、零宽/零长和零尺寸端口可定位；模板、坐标变换及GUI仍独立待验。
- DOCUMENTATION_ONLY不改颜色；CONNECTION_COLOR_ONLY不改点序或线宽；VISUAL_ONLY保护experiment/Evaluate/HideResult。
- FORMAT_ONLY保留字符串、注释、计算/图形Token和版本文字，重复执行幂等，源目录不变。
- 自定义主色未经人工reviewed确认不能自动写回；有限MSL4.0.0色表不扩展为其他版本证明。
- 36条M规范、36条U来源映射、文档和机器规则同源；默认作者配置关闭、项目默认AUDIT，不生成运行PASS。

这些案例测试辅助工具行为，不启动Modelica引擎或建模器GUI。
