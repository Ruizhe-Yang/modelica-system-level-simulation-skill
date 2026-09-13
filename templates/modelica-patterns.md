# Reusable Modelica patterns

These are structural templates. Replace connector names, domains, and layouts with those derived for the actual system.

## 1. Strict graphical component/assembly

```modelica
within MyLibrary.Components;
model ExampleUnit "Graphical composition model"
  parameter MyLibrary.Configuration.ExampleConfig config;

  MyLibrary.Foundation.Interfaces.PrimaryPort primaryIn
    annotation(Placement(
      transformation(extent={{-110,-10},{-90,10}}),
      iconTransformation(extent={{-110,-10},{-90,10}})));

  MyLibrary.Foundation.Interfaces.PrimaryPort primaryOut
    annotation(Placement(
      transformation(extent={{90,-10},{110,10}}),
      iconTransformation(extent={{90,-10},{110,10}})));

  MyLibrary.Foundation.Interfaces.ControlPort control
    annotation(Placement(
      transformation(extent={{-10,90},{10,110}}),
      iconTransformation(extent={{-10,90},{10,110}})));

  MyLibrary.Foundation.Models.ExampleCore core(config=...)
    annotation(Placement(transformation(extent={{-30,-20},{30,20}})));

equation
  connect(primaryIn, core.primaryIn)
    annotation(Line(points={{-100,0},{-30,0}}, color={...}));
  connect(core.primaryOut, primaryOut)
    annotation(Line(points={{30,0},{100,0}}, color={...}));
  connect(control, core.control)
    annotation(Line(points={{0,100},{0,20}}, color={...}));

  annotation(
    Icon(
      coordinateSystem(extent={{-100,-100},{100,100}}),
      graphics={
        // semantic vector graphics
      }),
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, grid={2,2})),
    Documentation(info="<html>...</html>"));
end ExampleUnit;
```

The sides shown above are an example only. Use the project's visual grammar.

## 2. Equation/algorithm core

```modelica
within MyLibrary.Foundation.Models;
model ExampleCore "Localized behavior core"
  parameter Real gain = 1;
  Modelica.Blocks.Interfaces.RealInput u;
  Modelica.Blocks.Interfaces.RealOutput y;
  Real x(start=0);

equation
  der(x) = -x + u;
  y = gain*x;

  annotation(Documentation(info="<html>
    <h4>Responsibility</h4><p>...</p>
    <h4>States and equations</h4><p>...</p>
    <h4>Assumptions</h4><p>...</p>
    <h4>Valid range</h4><p>...</p>
    <h4>Fidelity</h4><p>F2 reduced dynamic.</p>
    <h4>Replaceability boundary</h4><p>...</p>
  </html>"));
end ExampleCore;
```

## 3. Functional/process subsystem

```modelica
within MyLibrary.Systems.Functional;
model SubsystemA
  parameter MyLibrary.Configuration.SubsystemAConfig config;

  MyLibrary.Foundation.Interfaces.Domain1Port domain1 ...;
  MyLibrary.Foundation.Interfaces.Domain2Port domain2 ...;
  MyLibrary.Foundation.Interfaces.ControlBus control ...;

  MyLibrary.Components.UnitA unitA(config=config.unitA) ...;
  MyLibrary.Components.UnitB unitB(config=config.unitB) ...;

equation
  connect(..., ...) annotation(Line(...));
end SubsystemA;
```

Only declare the domain ports this subsystem genuinely uses.

## 4. Optional shared coupling-domain network

```modelica
within MyLibrary.Systems.Coupling;
model SharedNetworkA
  MyLibrary.Foundation.Interfaces.DomainAPort branch[nBranches];
  // common source/reference/distribution components as needed

equation
  // visible connection topology
end SharedNetworkA;
```

Do not create this model if local connections are clearer.

## 5. Overall system

```modelica
within MyLibrary.Systems;
model OverallSystem
  parameter MyLibrary.Configuration.SystemDesignConfig designConfig;
  parameter MyLibrary.Configuration.OperatingCase operatingCase;

  Functional.SubsystemA subsystemA(...);
  Functional.SubsystemB subsystemB(...);

  // Instantiate only justified shared networks.
  Coupling.SharedNetworkA sharedA(...) ...;

  MyLibrary.Foundation.Observers.SystemObserver observer(...);

equation
  connect(..., ...) annotation(Line(...));
end OverallSystem;
```

## 6. Canonical experiment

```modelica
within MyLibrary.Experiments;
model NominalCase
  parameter MyLibrary.Configuration.GeneratedSystemDesignConfig designConfig =
    MyLibrary.Configuration.GeneratedSystemDesignConfig();
  parameter MyLibrary.Configuration.GeneratedOperatingCase operatingCase =
    MyLibrary.Configuration.GeneratedOperatingCase();

  MyLibrary.Systems.OverallSystem system(
    designConfig=designConfig,
    operatingCase=operatingCase);

  annotation(experiment(
    StartTime=0,
    StopTime=1000,
    Interval=1,
    Tolerance=1e-6));
end NominalCase;
```

Keep the experiment simple. Do not put system physics or configuration parsing here.

## 7. Replaceable fidelity pattern

```modelica
partial model PartialUnitBehavior
  // stable external interfaces
end PartialUnitBehavior;

model ReducedUnit
  extends PartialUnitBehavior;
  // F2 behavior
end ReducedUnit;

model DetailedUnit
  extends PartialUnitBehavior;
  // F3 behavior
end DetailedUnit;
```

Use replaceable/redeclare only where it improves fidelity management and does not hide user-facing topology.
