# Fidelity and performance

## 1. Fidelity ladder

A generic progression is:

### F0 — interface stub
Use constants, ideal sources, or pass-through behavior to validate architecture and parameter flow.

### F1 — algebraic/static
Use steady-state relationships, characteristic maps, idealized conversions, or quasi-static physics.

### F2 — reduced dynamic
Keep dominant energy/inventory/inertia states and important time constants.

### F3 — detailed native Modelica
Use higher-order physical detail, distributed models, detailed switching, complex media, or detailed mechanics where justified.

### F4 — external implementation
Use C, FMU, external solver, or production/prototype software when integration fidelity is the research/engineering objective.

Fidelity is not a maturity score. F1 may be the correct final system-level choice for a low-impact component.

## 2. Fidelity selection questions

Ask:
- Does this unit materially influence primary KPIs?
- Is its transient behavior within the simulation time scale?
- Does it participate in safety-critical interactions?
- Are parameters/data available to support detail?
- Does added detail change decisions?
- What computational cost does it add?

Increase fidelity only when the answer justifies it.

## 3. Event control

Excessive events commonly come from:
- ideal switches;
- hard thresholds;
- piecewise discontinuities;
- nested state machines;
- zero-crossing-heavy logic;
- detailed PWM/switching when average behavior is sufficient.

Possible remedies:
- hysteresis;
- sampled logic;
- average-value models;
- smoother constitutive laws where physically acceptable;
- separation of fast and slow models;
- reduced-order approximations.

Do not remove events that are essential to the engineering question.

## 4. State control

Audit continuous states periodically.

Remove or reduce:
- duplicated storage states;
- unnecessary sensor dynamics;
- high-order detail outside the bandwidth of interest;
- tiny parasitic components added only to fix numerical structure without physical justification.

## 5. Profile the full pipeline

Measure:
- frontend/translation;
- symbolic processing;
- compile;
- initialization;
- integration;
- output.

A model that integrates quickly but takes minutes to translate is still expensive for iterative engineering.

## 6. Performance regression record

For each release or major change record:
- tool/compiler version;
- hardware/OS if comparisons matter;
- equation/variable/state count;
- event count;
- solver and tolerance;
- simulation horizon;
- output interval;
- translation time;
- simulation time;
- result size.

## 7. Simplification principle

Prefer reducing model complexity over hiding it with solver settings.

A strong system-level model contains **the minimum detail necessary to preserve the interactions and outputs required by the modeling contract**.
