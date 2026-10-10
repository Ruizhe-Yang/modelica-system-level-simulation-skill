# MSL 4.0.0 接口目录参考

保留早期 MOSAIC 的 24 类接口词汇。并非所有工程必须使用，也不表示线色工具支持全部类。

| 编号 | 关系 | MSL 路径 | 核心内容 | 使用语义 |
| --- | --- | --- | --- | --- |
| I01 | 瞬时电气 | Modelica.Electrical.Analog.Interfaces.PositivePin / NegativePin | v [V]；flow i [A] | 节点电位协调、电流平衡。需要电势参考和回路；正负不是I/O；线阻用组件。 |
| I02 | 多相电气 | Modelica.Electrical.Polyphase.Interfaces.PositivePlug / NegativePlug | pin[m] | 逐相电气连接；相数、相序及星点应相容。 |
| I03 | 准静态单相 | Modelica.Electrical.QuasiStatic.SinglePhase.Interfaces.PositivePin / NegativePin | 复v、flow复i；reference | 保留相量与相位参考；不得直接接Analog.Pin或ComplexOutput。 |
| I04 | 准静态多相 | Modelica.Electrical.QuasiStatic.Polyphase.Interfaces.PositivePlug / NegativePlug | 准静态pin[m]及参考 | 逐相相量与参考连接；不得用于表示已省略的瞬时开关细节。 |
| I05 | 一维转动 | Modelica.Mechanics.Rotational.Interfaces.Flange_a / Flange_b / Support | phi [rad]；flow tau [N.m] | 转角协调、转矩平衡；转速是角度变化率。不得以转速指令代替轴反作用。 |
| I06 | 一维平动 | Modelica.Mechanics.Translational.Interfaces.Flange_a / Flange_b / Support | s [m]；flow f [N] | 位移协调、力平衡；初始位移、速度和固定约束应相容。 |
| I07 | 三维承载 | Modelica.Mechanics.MultiBody.Interfaces.Frame_a / Frame_b | r_0[3]、R、flow f[3]、flow t[3] | 位置、姿态、力和力矩；含过约束处理。参考系和作用点应明确。 |
| I08 | 三维分解参考 | Modelica.Mechanics.MultiBody.Interfaces.Frame_resolve | 继承Frame字段；用于参考 | 用于矢量分解参考，不作为普通载荷传递链的替代品。 |
| I09 | 热交换 | Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a / HeatPort_b | T [K]；flow Q_flow [W] | 温度协调、热流率平衡；Q_flow自身为功率。热阻、热容须由组件提供。 |
| I10 | 流体输运 | Modelica.Fluid.Interfaces.FluidPort_a / FluidPort_b | p；flow m_flow；stream h_outflow、Xi_outflow、C_outflow | Medium、组分、焓基准应兼容；保留stream和模型声明的反流能力。 |
| I11 | 简化热流体 | Modelica.Thermal.FluidHeatFlow.Interfaces.FlowPort_a / FlowPort_b | p、h；flow m_flow、H_flow；medium | 普通量/flow式简化接口，无Fluid的stream语义；两族不得混连。 |
| I12 | 集总磁路 | Modelica.Magnetic.FluxTubes.Interfaces.PositiveMagneticPort / NegativeMagneticPort | V_m [A]；flow Phi [Wb] | 磁势协调、磁通平衡；不得把V_m×Phi当作通用功率。 |
| I13 | 基波磁场 | Modelica.Magnetic.FundamentalWave.Interfaces.PositiveMagneticPort / NegativeMagneticPort | 复V_m；flow复Phi | 明确空间基波、复数基和绕组约定；不与实数磁端口混接。 |
| I14 | 空间相量 | Modelica.Electrical.Machines.Interfaces.SpacePhasor | v_[2]；flow i_[2] | 电机空间相量接口；变换基和归一化应一致，不等于因果复数数据。 |
| I15 | 实数信息 | Modelica.Blocks.Interfaces.RealInput / RealOutput | input/output Real | 单位、quantity、尺寸、值提供者和时序应明确。可用固定尺寸实例数组。 |
| I16 | 布尔信息 | Modelica.Blocks.Interfaces.BooleanInput / BooleanOutput | input/output Boolean | 命令、条件、有效位；应定义true含义、初始值与更新机制。 |
| I17 | 整数信息 | Modelica.Blocks.Interfaces.IntegerInput / IntegerOutput | input/output Integer | 模式码、计数、序列号；应固定码表，不能仅凭相同数值判兼容。 |
| I18 | 复数信息 | Modelica.ComplexBlocks.Interfaces.ComplexInput / ComplexOutput | input/output Complex | 明确实虚含义、单位与时间语义；不作为物理电气连接。 |
| I19 | 数字逻辑 | Modelica.Electrical.Digital.Interfaces.DigitalInput / DigitalOutput | Logic多值枚举 | 明确未知态、高阻态及多源解析；不得与Boolean直接等价。 |
| I20 | 同步时钟 | Modelica.Clocked.ClockSignals.Interfaces.ClockInput / ClockOutput / ClockVectorInput | Clock或Clock数组 | 声明时钟来源、周期、相位与速率转换；不是单位为秒的Real。 |
| I21 | 状态步骤协议 | Modelica.StateGraph.Interfaces.Step_in / Step_out | 多路Boolean握手 | 应连接匹配Transition端口；不直接替换为Boolean条件。 |
| I22 | 状态转移协议 | Modelica.StateGraph.Interfaces.Transition_in / Transition_out | 多路Boolean握手 | 保持Step→Transition→Step协议；触发条件与协议连接分开。 |
| I23 | 总线图形基底 | Modelica.Icons.SignalBus / SignalSubBus | 无预置业务字段的expandable connector图形基底 | 使用前应定义业务字段；不构成已经可用的通信协议。 |
| I24 | 电池业务总线 | Modelica.Electrical.Batteries.Interfaces.CellBus / StackBus | 电池测量/状态成员 | 按所用类和配置检查成员、层级与生产者；不作为总体万能总线。 |
