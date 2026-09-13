---
name: modelica-system-level-simulation
description: Build, refactor, parameterize, visualize, diagnose, simulate, verify, and optimize domain-independent Modelica system-level models, especially with OpenModelica. Use for multi-subsystem architecture, graphical white-box + localized behavior-core design, Icon/Diagram engineering, Excel/CSV/JSON configuration generation, observability/KPIs, staged diagnostics, simulation/performance optimization, C/FMU/software replacement, regression, and engineering handoff. Derive domains, interfaces, layout, and fidelity from the real system; never force a fixed domain template. After each completed optimization cycle, keep user-facing deliverables to model/source artifacts, requested simulation/result artifacts, and one cumulative Markdown engineering report.
compatibility: Optimized for OpenModelica/OMC and tool-independent Modelica. OMEdit MCP is optional. Python 3 is used by bundled audit/diagnostic helpers.
metadata:
  version: "3.0.0"
---

# Modelica System-Level Simulation

## Purpose

Build Modelica projects that are not only executable, but also **readable, configurable, replaceable, observable, diagnosable, verifiable, visually coherent, and efficient enough for iterative engineering**.

Core principle:

> **Make topology visible, localize equations and algorithms, derive interfaces from the real system, separate configuration generation from solver execution, inspect the model instead of trusting a successful run, and make every optimization cycle reproducible from one cumulative engineering report.**

This skill is deliberately domain-independent. Do not assume fixed physical domains, connector sides, subsystem counts, package names, or a universal top-level layout.

### Preferred toolchain

- Prefer **OpenModelica/OMC** for validation, translation, simulation, diagnostics, and profiling when available.
- If the **OMEdit MCP server** is connected, use it to inspect/edit graphical models, run models, and read results without asking the user to click through OMEdit.
- If MCP is not available, use `omc`/MOS scripting and the bundled Python helpers.
- Keep generated Modelica standard-compliant unless a tool-specific extension is explicitly justified.
- When an MSL class name, parameter, connector, or language semantic is uncertain, verify it from the installed Modelica/OpenModelica documentation instead of guessing from memory.

Read `references/openmodelica-toolchain.md` when tool interaction or staged diagnosis is required.

---

## 1. Start with a modeling contract

Before detailed modeling or optimization, establish:

- engineering purpose and decisions the model must support;
- system boundary and external environment;
- authoritative outputs/KPIs/events;
- simulation horizon and relevant time scales;
- required fidelity and acceptable simplifications;
- expected C/FMU/software/data integrations;
- configuration ownership;
- runtime/translation performance budget;
- verification evidence required for release;
- final deliverable scope and the name/location of the single cumulative Markdown report.

If these are unclear, resolve architecture before adding model detail.

Read `references/modeling-decision-framework.md` when deciding boundary, decomposition, fidelity, or completion criteria.

---

## 2. Reuse before rebuilding

Before creating a new component, connector, type, or utility:

1. inspect the Modelica Standard Library version actually used by the project;
2. inspect reusable classes already present in the repository;
3. inspect explicitly approved third-party libraries;
4. create a new class only when the existing options do not provide the required semantics or boundary.

Prefer standard physical connectors for conserved networks and standard signal interfaces where they fit.

Do not invent a connector merely to make a Diagram convenient. A boundary is justified by semantics and ownership, not by drawing convenience.

For any external class used, record the dependency and version in the cumulative engineering report.

---

## 3. Separate responsibilities into layers

Use this as a **default responsibility model**, not a mandatory folder template:

```text
<Project>/
├─ Foundation/       # interfaces, reusable behavior cores, functions, types
├─ Configuration/    # defaults, cases, generated records, resource metadata
├─ Components/       # user-facing equipment/unit models and wrappers
├─ Systems/          # subsystem/process assemblies and justified shared networks
└─ Experiments/      # runnable cases, validation, variants, benchmarks
```

Recommended dependency direction:

```text
Foundation → Components → Systems → Experiments
     ↑            ↑          ↑
     └────── Configuration / generated artifacts ──────┘
```

### Ownership rules

- **Foundation** owns equations, algorithms, connectors, types, reusable calculations, adapters, state machines, reduced-order cores.
- **Configuration** owns static design/case/initial/control/resource choices and generated overrides.
- **Components** own engineering identity, stable boundaries, and local visible composition.
- **Systems** own aggregation and integration.
- **Experiments** own execution context and experiment settings, not plant/system physics.

Rename, merge, or omit packages when appropriate, but preserve ownership clarity and dependency direction.

Read `references/architecture.md` for detailed layering rules.

---

## 4. Decompose by the real system, not by a template

Use two independent questions when they improve clarity.

### Functional / process / ownership view

Ask:

> Which subsystem, process section, equipment train, or engineering responsibility owns this behavior?

### Shared coupling view

Ask:

> Which interactions cross several functional boundaries and become clearer as a shared network?

Possible coupling domains may include mechanics, electrical power, thermal transport, fluid/gas path, hydraulics, pneumatics, material flow, information/control, structural load paths, external boundary distribution, or others.

**Never create a domain layer only because another project had one.**

Create a shared coupling network only when it materially helps with one or more of:

- global conservation/reference/closure;
- repeated distribution infrastructure;
- cross-subsystem coupling visibility;
- independent network inspection;
- alternative network architecture/fidelity;
- Diagram routing and maintainability.

Otherwise keep the connection local.

### Build an interaction matrix first

Use actual project domains:

| Functional/process unit | Domain A | Domain B | Domain C | External boundary |
|---|---:|---:|---:|---:|
| Unit 1 | ✓ |  | ✓ |  |
| Unit 2 | ✓ | ✓ |  | ✓ |
| Unit 3 |  | ✓ | ✓ |  |

Use this matrix to derive required ports, shared networks, adapters, and top-level routing.

---

## 5. Use white-box / black-box separation by responsibility

### Strict graphical white box

Use for classes whose main purpose is **composition and topology**.

Preferred rules:

- equation section contains only `connect(...)`;
- important connections have visible `annotation(Line(...))`;
- behavior is delegated to contained components/cores;
- no hidden dynamics, control law, `der(...)`, `when`, or algorithm;
- avoid inheritance that hides significant public topology;
- provide purposeful Icon, readable Diagram, and Documentation.

Typical candidates are subsystem assemblies, process trains, integration models, shared networks, and component wrappers whose internal topology matters.

### Equation / algorithm black box

Use for classes whose main purpose is **behavior**.

A strong core:

- has narrow, stable interfaces;
- owns one coherent equation/algorithm responsibility;
- documents states, assumptions, valid range, and fidelity;
- exposes verification-relevant outputs;
- can be tested independently;
- can be replaced without parent-topology redesign.

### Hybrid adapter

Allow small local glue equations only when they are transparent interface adaptation, unit conversion, aliasing, or mapping and extracting them would reduce readability.

Do not let “hybrid” become an excuse to hide dynamics or control behavior in architecture classes.

### Replaceability test

A stable boundary should support replacement by another native Modelica model, a reduced/detailed fidelity variant, C implementation, FMU, or external software wrapper without changing the parent architecture.

Use `scripts/audit_whiteboxes.py` only on directories/classes explicitly designated as strict graphical white boxes.

---

## 6. Design interfaces before internals

For every boundary define:

- semantic meaning;
- physical quantity and unit where applicable;
- reference frame/reference state where applicable;
- acausal vs causal semantics;
- state ownership;
- command/measurement/status/event/configuration role;
- expected update semantics for software/FMU interfaces.

### Physical networks

Prefer acausal Modelica connectors for true conservation networks when the domain supports them.

Do not replace conservation behavior with directional signal approximations merely to simplify wiring unless that reduction is intentional and documented.

### Information/control

Prefer typed records, buses, expandable connectors, enums, or explicit signal interfaces.

Avoid ambiguous raw arrays when field meaning matters. Keep command, measurement, status, and engineering observation semantics distinguishable.

### External boundaries

Keep imposed ambient conditions, load profiles, schedules, measured histories, reference trajectories, and other boundary data distinct from internal command/status semantics when that improves traceability.

Read `references/interfaces-and-observability.md` for interface and software-boundary rules.

---

## 7. Treat Icon and Diagram engineering as part of the model

Do not postpone graphics until the end and do not use generic boxes as the finished state for meaningful engineering components.

### 7.1 Classify before drawing

Before adding graphics, classify the class as one of:

- package/category;
- connector/interface;
- physical source or boundary;
- physical component/equipment;
- controller/logic/state machine;
- sensor/observer/KPI publisher;
- adapter/converter;
- subsystem/assembly/shared network;
- experiment/example/benchmark;
- behavior core not intended as a primary graphical object.

The visual treatment follows the role.

### 7.2 Reuse standard visual conventions where appropriate

- For package-like/category classes, prefer suitable `Modelica.Icons.*` bases rather than inventing decorative package symbols.
- For leaf engineering components, create a semantic custom Icon when a standard icon does not convey the identity.
- For custom connectors, use a compact, distinctive symbol that remains legible at small scale.
- Do not copy a visual convention from another domain when it misrepresents the component.

### 7.3 Semantic icon synthesis

For each nontrivial custom Icon:

1. read the class name and description;
2. inspect connectors and their semantics;
3. inspect equations/contained components only as needed to understand function;
4. identify 1–3 characteristic engineering features;
5. draw those features with Modelica vector primitives;
6. reserve connector zones so graphics do not collide with ports;
7. preserve family resemblance across related classes;
8. keep the result legible when zoomed out.

Use `Rectangle`, `Ellipse`, `Line`, `Polygon`, `Text`, and other native Modelica primitives where practical. Avoid raster `Bitmap` graphics unless there is a strong engineering reason.

A generic rounded rectangle is acceptable only as a temporary F0 placeholder. Do not declare visual completion while recognizable components still use placeholders.

### 7.4 Preserve hand-tuned graphics

Graphical regeneration must be **non-destructive by default**.

- Analyze before modifying.
- Preview/diff graphical changes where the toolchain permits.
- Fill missing annotations or make targeted edits.
- Never erase existing hand-tuned `Placement`, `Line`, `Icon`, or `Diagram` annotations merely to re-layout the model unless the user explicitly requests regeneration.
- After graphics-only edits, validate that the model still loads/flattens and that no physical/equation semantics changed.

### 7.5 Diagram layout

Treat Diagram as an engineering navigation surface, not decoration.

Prefer:

- a clear dominant flow or information direction;
- external ports on the perimeter;
- grid-aligned components;
- functional grouping and domain/network lanes where useful;
- short, mostly orthogonal routes;
- dedicated corridors for shared networks/buses;
- minimal crossings and wrap-around lines;
- feedback loops placed deliberately rather than left to accidental routing;
- sufficient whitespace;
- intuitive drill-down from experiment → system → subsystem → component → core.

When the model has many connections, reason from the connection graph: identify main paths, strongly connected/feedback groups, branches, and shared buses before placing components.

Use live `DynamicSelect` displays only for a small number of high-value operating states/KPIs. Keep large telemetry sets in results/observers rather than crowding Icons.

### 7.6 Visual quality gate

Do not claim the graphics are complete until you have checked:

- semantic recognizability;
- family consistency;
- connector alignment and stable port-side conventions;
- label legibility;
- off-canvas objects;
- line crossings and unnecessary bends;
- misleading direction or domain styling;
- readability at normal and zoomed-out views;
- preservation of existing hand-authored detail.

Use `scripts/audit_modelica_visuals.py` for static heuristics, then perform visual inspection through OMEdit/MCP or available screenshots when possible.

Read `references/visual-language.md` for the full visual grammar.

---

## 8. Use Excel/CSV/JSON as configuration front-ends, not solver dependencies

A robust flow is:

```text
engineering configuration source
          ↓
schema / unit / range / mapping validation
          ↓
resolve baseline + explicit overrides
          ↓
optional derived or precomputed artifacts
          ↓
generated Modelica records + local data
          ↓
resolved snapshot + audit summary
          ↓
Modelica experiment
```

### Separate parameter semantics

Distinguish at least:

1. design parameters;
2. operating case/scenario;
3. initial conditions;
4. control/calibration;
5. simulation settings;
6. external resource metadata.

They may share one workbook, but should not share ambiguous ownership.

### One baseline, explicit overrides

Keep one authoritative Modelica-side baseline.

Generated configuration should identify baseline vs override, convert engineering units centrally, avoid duplicating all default literals in generator code, and emit a resolved run snapshot when needed for reproducibility.

### Runtime isolation

Unless file I/O is intentionally part of modeled behavior, the solver run should not need to:

- parse Excel;
- invoke Python merely to resolve parameters;
- access the internet;
- mutate source configuration;
- download missing resources.

Use deterministic local generated artifacts.

Read `references/configuration-pipeline.md`.

---

## 9. Keep derived quantities single-sourced

Do not maintain the same physical or logical fact independently in several places.

Examples:

- total properties derived from component properties;
- pressure/flow from the physical network instead of duplicate status variables;
- voltage/current from the electrical model instead of mirrored parameters;
- temperature from the thermal state;
- operating mode from the authoritative state machine;
- KPIs from authoritative source variables.

Never use Icon/Diagram coordinates as physical installation geometry.

For important outputs preserve traceability:

```text
source variable(s) → transformation → published quantity
```

---

## 10. Make observability a first-class layer

Recommended pattern:

```text
authoritative internal states
          ↓
   read-only observer(s)
          ↓
named engineering outputs / KPIs / health states
          ↓
results, dashboards, safety analysis, external software
```

Observers may rename, convert units, aggregate KPIs, and classify health/status.

Observers should not reimplement physics or feed back into the system unless they are explicitly a controller/estimator.

Maintain field-level traceability for important published variables.

When running a model, the agent should inspect relevant outputs directly instead of asking the user to “look at the plot” or “check whether it moved.”

---

## 11. Manage fidelity deliberately

Do not maximize detail everywhere.

Use a replaceable fidelity ladder where useful:

- **F0** — interface stub / architecture bring-up;
- **F1** — algebraic/static/map model;
- **F2** — reduced dynamic model with dominant states;
- **F3** — detailed native physical model;
- **F4** — C/FMU/external solver/software implementation.

Not every component needs every level.

Choose fidelity from:

- effect on required KPIs;
- coupling strength;
- relevant time scales;
- safety/decision criticality;
- available parameters/data;
- computational budget.

F1 may be the correct final model for a low-impact unit.

Read `references/fidelity-and-performance.md`.

---

## 12. Diagnose Modelica in stages, not by trial-and-error

A successful simulation is not proof of a correct model, and a failed simulation is not automatically a solver problem.

Use this staged diagnostic ladder:

```text
D0  static inventory / dependency / visual audit
 ↓
D1  load + checkModel / basic balance and lookup
 ↓
D2  instantiate / flatten
 ↓
D3  translate + build
 ↓
D4  initialize + nominal simulate
 ↓
D5  inspect trajectories, invariants, events, KPIs
 ↓
D6  profile expensive blocks/functions/nonlinear systems if needed
 ↓
D7  trace a suspicious variable/path back to authoritative sources
```

### 12.1 Failure classification

Classify the primary failure before changing code:

- package/load/path/library-version problem;
- unresolved name/type/unit/connector mismatch;
- under-/over-determined or structurally singular model;
- initialization inconsistency;
- algebraic loop or nonlinear-system convergence;
- excessive switching/zero-crossings/events;
- stiffness/time-scale problem;
- duplicated or unnecessary state/physics;
- result-writing/output overhead;
- external file/C/FMU/software boundary problem;
- graphics-only source corruption/regression.

### 12.2 OpenModelica staged gates

When using OMC, prefer the scripting sequence `checkModel` → `instantiateModel` → `buildModel` → `simulate`, reading `getErrorString()` after each gate.

If a model is slow, use OpenModelica profiling only after a normal run establishes the baseline. Record frontend/backend/codegen/compile/simulation/total times when available.

If an explicit runtime budget exists, enforce it. Do not allow a known-bad simulation to run indefinitely; stop it at the agreed ceiling, diagnose, simplify, and retry.

### 12.3 Diagnose before tuning

Do **not** start with:

- loosening tolerance;
- changing solver randomly;
- disabling warnings;
- increasing iteration limits blindly.

First identify structural, event, initialization, or modeling causes. Solver changes are justified only after the model-level cause is understood.

### 12.4 Preserve evidence

Record in the single cumulative report:

- which diagnostic stage failed or passed;
- exact error/warning class and representative message;
- root-cause interpretation;
- file/class changed;
- corrective action;
- re-test result;
- remaining risk.

Use `scripts/diagnose_openmodelica.py` as a lightweight OMC staged runner when appropriate, and `scripts/audit_modelica_project.py` for static inventory.

Read `references/diagnostics-and-performance.md`.

---

## 13. Simulate as a closed observation loop

Use the loop:

```text
build/validate
    ↓
simulate canonical case
    ↓
read key states + KPIs + events
    ↓
sanitary/physical checks
    ↓
compare with baseline/requirements
    ↓
modify one justified cause
    ↓
repeat
```

### Required post-run sanity checks

For important variables/KPIs, check as relevant:

- NaN/Inf or missing result channels;
- impossible sign/range/unit behavior;
- values pinned at initialization or saturation unexpectedly;
- monotonic drift where equilibrium is expected;
- unexpected discontinuities or event chatter;
- violated conservation/reference constraints;
- incorrect mode sequencing;
- result trajectories inconsistent with known limiting cases;
- KPI regression against the baseline.

A clean solver exit means **execution passed**, not **engineering validity passed**.

For parameter sweeps or variants, establish one stable canonical nominal case first.

Read `references/simulation-observation-loop.md`.

---

## 14. Precompute only weakly coupled expensive inputs

External preprocessing is appropriate for data that does not need tight feedback from simulated states, such as long reference histories, ambient profiles, schedules, geometry preprocessing, measured boundary data, or other expensive static resources.

Keep strongly coupled dynamics inside Modelica.

For precomputed data preserve source/version, units, time semantics, coverage, interpolation assumptions, and deterministic regeneration as appropriate.

---

## 15. Treat performance as an architecture requirement

Track separately where possible:

- load/check/flatten time;
- translation/frontend time;
- symbolic/backend time;
- code generation/compile time;
- initialization time;
- integration/output time;
- total wall time;
- equations/variables/states;
- zero crossings/events;
- linear/nonlinear/mixed systems;
- result size and stored sample count.

Optimize in this order:

1. remove duplicated/unnecessary states and physics;
2. reduce detail not required by the modeling contract;
3. replace unjustified event-heavy switching with valid averaged/reduced behavior;
4. simplify accidental algebraic complexity through architecture;
5. reduce unnecessary cross-boundary coupling;
6. precompute weakly coupled expensive data;
7. reduce unnecessary result output;
8. improve initialization/start values when evidence indicates this is the bottleneck;
9. tune solver/settings only after structural issues are understood.

For each performance change, compare **before vs after** on the same canonical case and confirm that required KPIs remain within acceptable deviation.

Never use loose tolerance as a substitute for sound modeling.

---

## 16. Verify more than “simulation completed”

Use project-appropriate gates for:

- **architecture** — dependency direction and ownership;
- **strict white boxes** — visible connect-only topology where declared;
- **interfaces** — compatibility, unit/reference semantics, ownership;
- **configuration** — mapping, units, baseline/override, determinism;
- **physical consistency** — valid ranges, conservation, references, initialization;
- **behavior cores** — focused tests and limiting cases;
- **system regression** — KPIs, envelopes, events, modes, observers;
- **performance regression** — time/state/event/result growth;
- **visual QA** — icons, routing, labels, navigation, readability;
- **handoff reproducibility** — toolchain, configuration, command/entry point, results, and report agree.

Preserve release evidence such as source version, resolved configuration, generated artifacts, external-resource metadata, verification summary, performance metrics, and toolchain version as needed.

Read `references/verification-and-quality-gates.md`.

---

## 17. Final-output contract: one cumulative Markdown report

This is a mandatory default for this custom skill.

### 17.1 User-facing final deliverables after an optimization cycle

Unless the user explicitly requests additional deliverables, leave only:

1. **the modeling/source artifacts** needed to use the model;
2. **the requested simulation/result artifacts** needed to inspect/reproduce the results;
3. **one complete cumulative `.md` engineering report**.

Default report name:

```text
MODEL_ENGINEERING_REPORT.md
```

If a project already has an established report filename, update that file instead of creating a second report.

### 17.2 Do not scatter reports

Do not create separate user-facing files such as:

```text
architecture_report.md
icon_report.md
diagnosis_report.md
optimization_notes.md
test_summary.md
simulation_summary.txt
final_assessment.html
```

unless the user explicitly asks for them.

Tool-generated temporary logs, build folders, profiler HTML, intermediate JSON/XML, compiler output, and caches may exist during work. Treat them as **intermediate evidence**, summarize what matters into the cumulative Markdown report, and clean them up or keep them in an explicitly internal/generated area if the toolchain requires them. Do not present them as separate final deliverables by default.

### 17.3 The report is cumulative, not a thin change log

Every completed cycle updates the same report so a new engineer can understand the final state without reconstructing previous chats.

The report should include, as applicable:

1. project/task objective and scope;
2. starting baseline and source inventory;
3. toolchain/library/version information;
4. modeling contract and performance budget;
5. architecture and decomposition;
6. key assumptions and simplifications;
7. interface semantics and state ownership;
8. white-box/black-box/fidelity decisions;
9. configuration/parameter pipeline;
10. Icon/Diagram visual grammar and graphical changes;
11. all material model/code/config changes, organized by class/file;
12. diagnostic process, failures, root causes, and fixes;
13. simulation setup and canonical entry point;
14. key result/KPI interpretation;
15. before/after performance comparison;
16. verification and regression evidence;
17. known limitations, residual warnings, and unresolved issues;
18. engineering evaluation: correctness, readability, maintainability, replaceability, observability, fidelity, performance, and extensibility;
19. recommended next steps, ordered by value/risk;
20. final deliverable inventory and reproducibility instructions.

Do not paste large source files or full solver logs into the report. Summarize them and cite file/class/result paths inside the project.

Use `templates/engineering-report-template.md` as the default structure and read `references/output-and-reporting.md` for detailed rules.

---

## 18. Workflow for a new project

1. Write the modeling contract, including report path and performance budget.
2. Inventory available libraries, equations, data, code, and tool constraints.
3. Verify key Modelica/MSL names instead of guessing them.
4. Define system boundary and authoritative KPIs.
5. Define functional/process decomposition.
6. Identify actual shared coupling domains; do not assume them.
7. Build the interaction matrix.
8. Define interfaces and state ownership.
9. Define project visual grammar.
10. Establish package/layer ownership.
11. Build F0/interface-stub architecture first.
12. Establish one canonical executable nominal case.
13. Run D0–D4 staged diagnostics before adding detail.
14. Replace high-priority stubs with F1/F2 behavior cores.
15. Build configuration generation and resolved snapshots.
16. Add observers/KPIs and traceability.
17. Add strict graphical white boxes where topology should be inspectable.
18. Upgrade semantic Icons/Diagrams after interface geometry stabilizes.
19. Add F3/F4 fidelity only where justified.
20. Add static, physical, behavioral, visual, and performance regression checks.
21. Freeze stable boundaries before external C/FMU/software integration.
22. Update `MODEL_ENGINEERING_REPORT.md` and remove/suppress redundant final reports.

Validate **architecture and parameter flow before detailed fidelity**.

---

## 19. Workflow for refactoring an existing project

1. Inventory classes, connectors, equations, scripts, resources, runnable entries, and current result files.
2. Establish the existing canonical run and record baseline KPIs/performance if it runs.
3. Identify duplicated physics, duplicated parameters, hidden topology, unstable interfaces, and weak graphics.
4. Classify each class as interface/type, behavior core, graphical assembly, hybrid adapter, configuration, or experiment/test.
5. Run staged diagnosis to separate structural errors from runtime/performance problems.
6. Extract hidden behavior from architecture classes into cores.
7. Consolidate defaults and external configuration.
8. Redesign overloaded interfaces.
9. Derive true shared coupling domains from the actual connection graph.
10. Standardize and then semantically strengthen Icons/Diagrams after interface geometry stabilizes.
11. Add observers and source traceability.
12. Establish nominal regression and performance baselines.
13. Simplify high-cost/low-value detail.
14. Re-run the canonical case and compare KPI/performance changes.
15. Add new fidelity or co-simulation only after the architecture is stable.
16. Update the one cumulative report with baseline, changes, evidence, evaluation, and next steps.

---

## 20. Workflow for diagnosing and optimizing a slow model

1. Record the runtime ceiling and canonical experiment.
2. Run static inventory; count states/equations/`when`/`der`/connections/visual coverage.
3. Run load/check/flatten/build gates without a long simulation.
4. Run a short or nominal simulation under the runtime ceiling.
5. Record translation, compile, initialization, simulation, event, and result-writing evidence.
6. If the bottleneck is unclear, enable OpenModelica profiling and inspect the highest-cost functions/equation systems.
7. Rank candidate causes by estimated cost × engineering expendability.
8. Apply one structural/fidelity/output change at a time.
9. Re-run the same case and compare performance + KPIs.
10. Reject “optimizations” that materially corrupt required behavior.
11. Repeat until the performance budget is met or the report clearly explains the remaining constraint.
12. Put all diagnostic and optimization evidence into `MODEL_ENGINEERING_REPORT.md`; do not leave separate final diagnostic reports.

---

## 21. Anti-patterns

Avoid:

- forcing every system into the same physical domains;
- adding empty shared networks solely for symmetry;
- one giant top model containing architecture, equations, controller logic, parsing, and UI;
- hundreds of manual top-level modifiers;
- direct Excel parsing during ordinary solver execution;
- using graphical coordinates as physical geometry;
- copying baseline values independently into Modelica and generator scripts;
- generic identical icons for unrelated equipment;
- deleting hand-tuned graphical annotations during automated re-layout without explicit approval;
- decorative icons that do not represent engineering function;
- dynamic text dashboards inside every component;
- signal approximations of real conservation networks without justification;
- hidden public topology through inheritance;
- maximum fidelity before interface validation;
- random solver changes as the first debugging step;
- solver-tolerance changes as the first performance fix;
- claiming success because the solver exited cleanly;
- asking the user to inspect results that the agent can read itself;
- generated files that users must manually edit;
- published telemetry/KPIs with no authoritative source trace;
- multiple fragmented final reports after one optimization cycle.

---

## 22. Definition of done

Adapt this checklist to project scope:

- [ ] purpose, boundary, fidelity, outputs, and performance budget are documented;
- [ ] layer responsibilities and dependency direction are clear;
- [ ] functional/process decomposition is explicit;
- [ ] shared coupling domains come from the actual system rather than a template;
- [ ] interface semantics and state ownership are documented;
- [ ] public architecture is understandable through Icon/Diagram navigation;
- [ ] meaningful engineering components use semantic icons rather than generic placeholders;
- [ ] Diagram routing is readable and major connections are visually traceable;
- [ ] graphics-only edits preserve model semantics and hand-tuned work unless regeneration was requested;
- [ ] strict white boxes are connect-only, or hybrid exceptions are deliberate and documented;
- [ ] behavior cores own equations/algorithms and state their fidelity boundary;
- [ ] at least one reproducible canonical experiment exists;
- [ ] configuration has an authoritative baseline and traceable overrides;
- [ ] generated artifacts are deterministic and runtime-local;
- [ ] important derived quantities have one source of truth;
- [ ] observers/KPIs are read-only and traceable;
- [ ] fidelity choices are intentional and replaceable;
- [ ] staged load/check/flatten/build/simulate diagnostics pass or remaining failures are explicitly characterized;
- [ ] successful simulations have undergone sanity/physical checks;
- [ ] architecture, physical, behavioral, visual, and performance gates pass to the required level;
- [ ] C/FMU/software integration can use stable boundaries when required;
- [ ] final user-facing artifacts obey the one-report contract;
- [ ] `MODEL_ENGINEERING_REPORT.md` contains the complete process, evidence, summary, evaluation, limitations, and next steps;
- [ ] a new engineer can configure, run, inspect, diagnose, and extend the model without reverse-engineering the entire library or chat history.

---

## 23. References and tools

Read only what the task requires:

- `references/modeling-decision-framework.md` — boundary, decomposition, domains, fidelity, completion criteria.
- `references/architecture.md` — layering and functional/process × coupling architecture.
- `references/visual-language.md` — semantic Icon/Diagram grammar, non-destructive visual workflow, routing and visual QA.
- `references/configuration-pipeline.md` — external configuration → generated Modelica/local artifacts.
- `references/interfaces-and-observability.md` — connector semantics, observers, C/FMU/software boundaries.
- `references/fidelity-and-performance.md` — fidelity ladder, simplification, profiling principles.
- `references/diagnostics-and-performance.md` — staged OpenModelica diagnosis, failure taxonomy, profiling and variable tracing strategy.
- `references/simulation-observation-loop.md` — run/read/check/compare/iterate closed-loop workflow.
- `references/openmodelica-toolchain.md` — OMC/OMEdit MCP usage, scripting gates, profiling, temporary evidence handling.
- `references/output-and-reporting.md` — one cumulative Markdown report contract and cleanup policy.
- `references/verification-and-quality-gates.md` — quality and release gates.
- `references/open-source-inspirations.md` — public projects whose ideas informed this custom skill and how they were adapted.
- `templates/modelica-patterns.md` — adaptable Modelica skeletons.
- `templates/project-layout.md` — adaptable project layout.
- `templates/engineering-report-template.md` — required default structure for the single final/cumulative `.md` report.
- `scripts/audit_whiteboxes.py` — strict graphical-assembly checker; pass directories explicitly.
- `scripts/audit_modelica_project.py` — static project inventory and coverage metrics.
- `scripts/audit_modelica_visuals.py` — static visual-annotation heuristics.
- `scripts/diagnose_openmodelica.py` — lightweight staged OMC check/flatten/build/simulate/profile runner.

When a task ends, consolidate evidence into the one cumulative report instead of emitting separate diagnostic, visual, optimization, and validation documents.
