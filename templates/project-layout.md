# Adaptable project layout

A strong default is:

```text
MyModelicaProject/
├─ package.mo
├─ package.order
├─ MODEL_ENGINEERING_REPORT.md                  # single cumulative human-facing report
├─ ConfigurationSource.xlsx / .csv / .json     # optional engineer front-end
├─ Foundation/
│  ├─ Interfaces/
│  ├─ Models/
│  ├─ Calculations/
│  ├─ Functions/
│  ├─ Types/
│  ├─ Adapters/
│  └─ Observers/
├─ Configuration/
│  ├─ Defaults/
│  ├─ Cases/
│  ├─ Generated/
│  └─ Resources.mo or resource records
├─ Components/
├─ Systems/
│  ├─ Functional/               # optional name
│  ├─ Coupling/                 # only justified shared networks
│  └─ OverallSystem.mo
├─ Experiments/
│  ├─ NominalCase.mo
│  ├─ Validation/
│  ├─ Variants/
│  └─ Benchmarks/
├─ Resources/
│  ├─ Data/
│  ├─ External/
│  └─ Scripts/
├─ tools/
│  ├─ update_config.py
│  ├─ unit_conversion.py
│  ├─ audit_whiteboxes.py
│  ├─ audit_project.py
│  └─ regression_tests.py
├─ outputs/                      # requested simulation/result artifacts
│  ├─ regression/
│  └─ benchmarks/
└─ .modelica_work/               # optional temporary/internal evidence; not a final deliverable
```

This is a responsibility map, not a mandatory directory list.

## Root reading order

A useful `package.order` normally teaches the conceptual progression, for example:

```text
Foundation
Configuration
Components
Systems
Experiments
```

Rename or omit layers when appropriate, but keep the ownership distinction visible.

## Generated content rule

Keep generated Modelica classes in a dedicated package/folder such as:

```text
Configuration/Generated/
```

Generated files should not be manually edited.

## Experiments vs Simulation

`Experiments` is preferred when the library contains multiple runnable cases, validation models, or benchmarks.

`Simulation` is acceptable when the project intentionally exposes one primary run entry. The semantic requirement is the same: executable context should remain separate from plant/system implementation.


## Single-report handoff rule

Do not add separate architecture, diagnosis, icon, optimization, or validation reports by default. Consolidate human-facing engineering documentation into `MODEL_ENGINEERING_REPORT.md`. Tool-required logs/profiler/debug artifacts belong in temporary/internal generated locations and are summarized into the report.
