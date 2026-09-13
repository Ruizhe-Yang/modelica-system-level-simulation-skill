# Diagnostics and performance workflow

## 1. Goal

Diagnose a Modelica problem by locating the failing stage and identifying the engineering cause before changing solver settings.

Use the staged ladder:

```text
D0 static inventory
D1 load / checkModel
D2 instantiate / flatten
D3 translate / build
D4 initialize / simulate
D5 trajectory + KPI sanity
D6 performance profiling
D7 variable/source trace
```

Do not run the most expensive stage when an earlier gate already fails.

## 2. D0 — static inventory

Use `scripts/audit_modelica_project.py` and, when relevant, `scripts/audit_modelica_visuals.py` / `scripts/audit_whiteboxes.py`.

Record:

- Modelica file/class count;
- models/blocks/connectors/records/functions;
- `connect`, `der`, `when`, algorithm occurrence counts;
- Icon/Diagram/Documentation coverage;
- likely runnable experiment(s);
- package dependencies and external resources;
- obvious duplicated generated artifacts.

D0 does not prove semantic correctness. It narrows the search space.

## 3. D1 — load and check

With OpenModelica:

- load the required MSL version and project package;
- call `checkModel(Target.Class)`;
- immediately read `getErrorString()`.

Classify name/path/version errors separately from structural equation errors.

Typical D1 causes:

- wrong class path;
- unloaded dependency;
- MSL version mismatch;
- invalid modifier;
- connector/type mismatch;
- structurally unbalanced model.

## 4. D2 — instantiate / flatten

Call `instantiateModel(Target.Class)` only after D1 is meaningful.

Use flattening to expose:

- actual resolved parameters;
- inherited equations/components;
- conditional component selection;
- generated connection equations;
- replaceable/redeclare resolution.

If flattening fails, do not spend time tuning the simulation solver.

## 5. D3 — build

Use `buildModel` to isolate translation/code generation/compilation from runtime simulation.

If D2 passes but D3 fails, inspect:

- unsupported external C/C++ integration;
- compiler/toolchain availability;
- generated-code issues;
- external library linkage;
- tool-specific unsupported constructs.

## 6. D4 — initialize and simulate

Use the canonical experiment and the agreed runtime ceiling.

Record OpenModelica `SimulationResult` timing fields where available:

- frontend;
- backend;
- sim-code generation;
- templates;
- compile;
- simulation;
- total.

Keep the same experiment settings for before/after comparisons.

## 7. D5 — inspect trajectories and engineering sanity

A successful simulation is only an execution gate.

Check important states/KPIs for:

- NaN/Inf;
- missing channels;
- impossible signs/ranges;
- frozen signals that should move;
- unexpected saturation;
- monotonic drift where settling is expected;
- excessive discontinuities;
- mode/event sequencing;
- conservation/reference consistency;
- baseline/requirement deviation.

When a quantity is suspicious, trace it back through its observer/transformation to the authoritative source state rather than fixing the published KPI directly.

## 8. D6 — performance profiling

Profile only when a normal baseline shows a meaningful performance problem.

OpenModelica supports compiler profiling options such as `--profiling=blocks`, `--profiling=blocks+html`, and `--profiling=all` depending on the installed version/toolchain.

Use profiling to identify expensive:

- functions;
- linear systems;
- nonlinear systems;
- mixed systems;
- equations/blocks.

Also inspect:

- event/zero-crossing activity;
- initialization convergence;
- result-writing volume;
- number of stored variables/samples;
- repeated expensive external calls.

Profiler HTML/XML/SVG outputs are intermediate evidence by default. Summarize the findings into `MODEL_ENGINEERING_REPORT.md` rather than leaving a separate final profiling report unless the user requests it.

## 9. D7 — variable/source trace

For a suspicious variable, document:

```text
published KPI
  ← observer/conversion
  ← subsystem output
  ← component state/equation
  ← boundary/parameter/input source
```

Trace both initialization and runtime ownership when they differ.

The goal is to answer: **what equation/source owns this value, what influences it, and where is the least invasive correction?**

## 10. Failure taxonomy and preferred response

| Failure | First response |
|---|---|
| missing class/path | verify dependency/version/name |
| equation imbalance | inspect boundary/conditional equations |
| initialization failure | inspect start/fixed constraints, incompatible initial equations |
| nonlinear convergence | inspect scaling, discontinuities, initial guesses, coupled structure |
| event explosion | identify discontinuous switching and chatter source |
| slow translation | reduce accidental symbolic complexity / huge modifiers / generated structure |
| slow simulation | profile blocks/functions/events; reduce unjustified fidelity |
| huge result files | reduce variable filter/sample count without hiding required evidence |
| external integration failure | isolate wrapper and test boundary independently |

## 11. Performance optimization hierarchy

Prefer:

1. eliminate duplicated facts/states;
2. remove unnecessary detailed physics;
3. reduce event-heavy detail when an averaged model is valid;
4. simplify accidental algebraic coupling;
5. reduce result output;
6. improve initialization based on evidence;
7. then tune numerical method/settings.

Always compare the same canonical case and confirm KPI preservation.

## 12. Reporting

Every diagnostic loop should end with a compact evidence chain in the cumulative report:

```text
symptom → failing stage → evidence → root cause → change → retest → residual risk
```

Do not create a second user-facing diagnostic report.
