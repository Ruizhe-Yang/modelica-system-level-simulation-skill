# MOSAIC-skill v0.8｜核验记录

## 已实际执行

在本次 Linux / Python 3.13 环境运行 `python -m unittest discover -s tests -v`：**51 项通过**。基础工具 21 项、v0.8 辅助保护 20 项、角色审查 10 项。测试文件随包提供，耗时受机器与负载影响，不作为任何 Modelica 工程预算。

测试覆盖词法盘点、文稿写入/清理/幂等、真实限制保留、类说明去重辅助函数、方程/普通字符串/单位/初值保护、Icon/图形/experiment/uses保护、限定的连接线颜色豁免、派生接口与复合成员类型、未知接口停止写回、生成调色白名单、根版本重复项、角色局部行为/输入绑定/初始化/子实例/继承待核、精确目录差异、合同重复键、XML说明读取，以及子进程成功/超时。原21项中保留旧目录版本输入，检查兼容性，不将旧例子的显示约定重新设为新政策。

SKILL.md 的 YAML 名称、description、版本、目录与相对链接已核对。M01—M36与配套HTML使用同一规则JSON，等级为26R/9S/1F。当前包内仅含12UCubeSat作为具体工程案例；品牌图为用户提供的原MOSAIC LOGO，不附字体文件。

12UCubeSat 本次辅助候选的235个 `.mo` 文件还执行了文稿生成钩子的保护token与二次幂等检查；2314条实际连接经过端点/类型/线色核对。这是源级与离线辅助检查，不是数值配置重新生成、Modelica编译或仿真。

## 未执行及适用边界

未在实际 Codex 或其他技能宿主安装并完成端到端建模调用。`tests/behavior_cases.md`是待在宿主核验的路由清单，不能据其存在写成已通过。

未执行 OpenModelica/MWorks 编译、仿真或建模器GUI验证；示例代码未在本环境编译。MOSAIC规范HTML的浏览器排版核对不等于Modelica模型界面检查。

核心脚本以Python3.10+语法编写，实际测试版本为Python3.13；不宣称已在每一个Python版本/操作系统复测。MAT路径需要numpy/scipy，自动测试主要覆盖XML元数据路径，不声称所有MAT布局支持。Windows taskkill分支没有在当前Linux环境实测。

## 工具输出的正确解释

`modelica_support.py` 是保守的源跨度/词法辅助器，不是完整Modelica解析器、类型检查器或求解器。`audit_roles.py`只检查用户提供的角色映射；未映射类、库继承展开、redeclare和静态连接模板保留待核。`connection_colors.py`只覆盖其明确注册的接口族和有限组件端口签名；新族先读库源码，再扩展测试，不能猜测。

`verify_aux_only.py`只证明指定豁免之外的token没有变化。开启连接线颜色豁免并不允许改变Icon、实际connect端点、points或线宽；其他非`.mo`白名单文件仍须逐项内容审查。没有局部发现不等于MainConformance、运行、外部保真或安全验证已经通过。
