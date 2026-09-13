# External configuration and generation pipeline

## Goal

Provide an engineer-friendly configuration front-end while preserving deterministic, auditable, local Modelica execution.

The front-end may be Excel, CSV, JSON, YAML, a database export, or another controlled source.

## 1. Separate semantic parameter groups

Recommended groups:

### Design
Geometry, ratings, capacities, material/property choices, component options, installation data.

### Operating case
Loads, profiles, schedules, ambient/boundary conditions, mission/process recipe, duty cycle.

### Initial conditions
Initial inventories, temperatures, pressures, positions, speeds, states of charge, modes.

### Control/calibration
Gains, thresholds, calibration maps, protection limits, controller variants.

### Simulation
Start/stop time, solver/tolerance, output interval, experiment switches.

### External resources
Lookup tables, measured histories, maps, binaries, FMUs, data files.

Keep semantics separate even if several groups share one workbook.

## 2. Recommended design-table schema

A generic row schema is:

```text
Group
SubsystemOrSection
Instance
ModelOrType
Category
Parameter
DisplayName
Value
Unit
DefaultValue
UseDefault
TargetPath
GeneratedConfigKey
Description
ValidationRule
Changed
```

Only include columns that serve a real workflow.

## 3. Generator sequence

A robust generator should:

1. validate input schema/version;
2. parse metadata;
3. reject duplicate keys;
4. validate model/target mapping;
5. validate units and convert centrally;
6. compare external defaults with the Modelica baseline where relevant;
7. resolve baseline vs explicit override;
8. validate ranges and cross-field constraints;
9. validate referenced resources;
10. optionally precompute weakly coupled external data;
11. generate Modelica records/tables/adapters;
12. generate derived aggregate properties if required;
13. write a fully resolved snapshot;
14. write mapping/validation audit data;
15. report warnings/errors and final status.

Prefer transactional generation: validate and stage first, then replace production generated artifacts only if the full update succeeds.

## 4. Central unit conversion

Maintain one conversion registry.

Typical classes:
- length/area/volume;
- angle/angular velocity;
- mass/inertia;
- pressure/flow;
- temperature;
- energy/power;
- electrical quantities;
- rotational speed;
- data rates if relevant.

Reject unknown units. Never silently infer a conversion from a similar-looking string.

## 5. Modelica baseline pattern

```modelica
record DefaultSystemDesignConfig
  ...
end DefaultSystemDesignConfig;

constant DefaultSystemDesignConfig defaultSystemDesignConfig =
  DefaultSystemDesignConfig();
```

Generated records should avoid duplicating unchanged baseline literals unnecessarily.

## 6. Runtime isolation

Unless runtime file I/O is part of the intended model behavior, the experiment should not:
- parse Excel;
- invoke Python merely to resolve parameters;
- access the internet;
- rewrite configuration files;
- download missing resources.

All required artifacts should already be local and resolved.

## 7. Reproducibility artifacts

Preserve as appropriate:
- resolved parameter snapshot;
- generator version;
- input source version/hash;
- mapping audit;
- external resource metadata;
- generated file list;
- validation report;
- experiment identifier.

This enables design studies, safety evidence, and regression analysis to reproduce the exact configuration.
