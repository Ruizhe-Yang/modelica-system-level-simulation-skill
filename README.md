# Modelica System-Level Simulation Skill

**An OpenModelica-first Agent Skill for engineering, diagnosing, visualizing, validating, and optimizing system-level Modelica models.**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](./SKILL.md)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](./LICENSE)
[![Modelica](https://img.shields.io/badge/Modelica-system--level-orange.svg)](https://modelica.org/)
[![OpenModelica](https://img.shields.io/badge/OpenModelica-first-0B5CAD.svg)](https://openmodelica.org/)

This repository contains a reusable Agent Skill for **system-level Modelica engineering**. It is designed for Codex and other Agent Skills-compatible environments, with an emphasis on **OpenModelica/OMC**, graphical white-box architecture, localized equation/algorithm cores, semantic Icon/Diagram design, staged diagnostics, simulation-result inspection, performance optimization, external configuration, and reproducible engineering handoff.

The skill is deliberately **domain-independent**. It does not force every project into a fixed mechanical/electrical/thermal/control template. Domains, interfaces, subsystem boundaries, graphical layout, and fidelity are derived from the real system being modeled.

> **Core principle:** make topology visible, localize equations and algorithms, derive interfaces from the real system, separate configuration generation from solver execution, inspect the model instead of trusting a successful run, and make every optimization cycle reproducible from one cumulative engineering report.

---

## Why this skill exists

Large Modelica projects often fail for reasons that are not captured by “does it compile?” or “did the solver finish?” A system model also needs to be understandable, configurable, replaceable, observable, diagnosable, maintainable, and fast enough for iterative engineering.

This skill treats the following as one integrated workflow rather than separate afterthoughts:

- system architecture and subsystem decomposition;
- physical and information interface design;
- graphical white-box / behavioral black-box separation;
- semantic `Icon` and readable `Diagram` annotations;
- parameter/configuration generation from engineering front-ends;
- observability, KPIs, health states, and result traceability;
- staged Modelica/OpenModelica diagnosis;
- simulation-result sanity and physical checks;
- translation, initialization, event, and runtime performance analysis;
- fidelity management and replaceable implementations;
- C/FMU/external-software boundaries;
- regression, verification, and engineering handoff;
- one cumulative Markdown report as the default final documentation artifact.

It is intended for projects ranging from compact multi-subsystem models to large multidisciplinary system simulations.

---

## Key capabilities

### 1. System-level architecture before equation growth

The skill starts from a modeling contract: engineering purpose, system boundary, required KPIs, time scales, fidelity, configuration ownership, runtime budget, external integrations, and verification evidence.

It then separates responsibilities into reusable foundations, components, systems, configuration, and executable experiments without forcing one rigid folder layout.

### 2. Real-system decomposition instead of a fixed domain template

The agent reasons from two complementary views:

- **functional/process/ownership view** — which subsystem or engineering responsibility owns the behavior;
- **shared coupling view** — which interactions genuinely cross subsystem boundaries and benefit from an explicit shared network.

A coupling network is created only when it improves conservation/reference closure, cross-subsystem visibility, repeated distribution infrastructure, replaceability, or diagram maintainability.

### 3. Graphical white-box + localized behavior-core modeling

The skill encourages a clear separation between:

- **graphical white boxes** whose purpose is composition and visible topology;
- **equation/algorithm black boxes** that own coherent behavior;
- **small hybrid adapters** used only for transparent interface mapping or unit conversion.

Stable boundaries should allow replacement by another native Modelica model, a different fidelity level, C code, an FMU, or an external-software wrapper without redesigning the parent topology.

### 4. Semantic Icon and Diagram engineering

Graphics are treated as part of the model, not decoration added at the end.

The workflow includes:

- class-role classification before drawing;
- semantic icon synthesis from engineering function and connector semantics;
- consistent visual families across related components;
- preservation of connector space and port conventions;
- connection-graph-aware Diagram layout;
- short, readable routing with deliberate feedback paths and shared-network corridors;
- non-destructive edits that preserve hand-tuned annotations;
- visual QA for recognizability, consistency, alignment, crossings, labels, and zoomed-out readability.

Generic rectangles are acceptable as temporary architecture placeholders, not as the finished visual state for meaningful engineering components.

### 5. Engineering configuration without solver-time spreadsheet dependence

Excel/CSV/JSON can act as engineering configuration front-ends, but ordinary solver execution should consume deterministic local Modelica data rather than parse spreadsheets or invoke external scripts at runtime.

The recommended flow is:

```text
engineering configuration source
          ↓
schema / unit / range / mapping validation
          ↓
baseline + explicit overrides
          ↓
generated Modelica records / local artifacts
          ↓
resolved snapshot
          ↓
Modelica experiment
```

Design parameters, operating cases, initial conditions, control/calibration values, simulation settings, and external-resource metadata are kept semantically distinct.

### 6. Observability and KPI traceability

Important engineering outputs should remain traceable to authoritative model states:

```text
authoritative internal states
          ↓
   read-only observers
          ↓
engineering outputs / KPIs / health states
          ↓
results / dashboards / safety analysis / external software
```

Observers may aggregate or convert information, but should not silently reimplement the underlying physics.

### 7. Staged `diagnose-modelica` workflow for OpenModelica

The skill avoids trial-and-error solver tuning. It diagnoses the model by pipeline stage:

```text
D0  static inventory / dependency / visual audit
 ↓
D1  load + checkModel
 ↓
D2  instantiate / flatten
 ↓
D3  translate + build
 ↓
D4  initialize + nominal simulate
 ↓
D5  inspect trajectories / invariants / events / KPIs
 ↓
D6  profile expensive blocks / functions / nonlinear systems
 ↓
D7  trace suspicious variables back to authoritative sources
```

Typical failure classes include structural imbalance, unresolved names/types, initialization inconsistency, algebraic/nonlinear convergence, event chatter, stiffness, unnecessary states, excessive result output, external-resource problems, and graphics-related source regressions.

When OpenModelica is available, the preferred sequence is based on `checkModel` → `instantiateModel` → `buildModel` → `simulate`, with `getErrorString()` inspected after each gate.

### 8. Simulation as a closed observation loop

A solver exit code is not treated as proof of engineering validity.

After each important run, the agent should inspect relevant states, KPIs, events, ranges, limiting behavior, conservation/reference constraints, unexpected saturation, discontinuities, and regressions before deciding that the model is correct.

```text
validate/build
    ↓
simulate canonical case
    ↓
read states + KPIs + events
    ↓
physical/sanity checks
    ↓
compare with baseline/requirements
    ↓
modify one justified cause
    ↓
repeat
```

### 9. Performance as an architecture requirement

The skill distinguishes, when possible:

- load/check/flatten time;
- frontend/translation time;
- symbolic/backend time;
- code generation and compilation;
- initialization;
- numerical integration and result writing;
- total wall time;
- equation/state counts;
- zero crossings/events;
- linear/nonlinear/mixed systems;
- result size and sample count.

Optimization prioritizes structural simplification and justified fidelity reduction before random solver changes or loose tolerances.

Every performance change should be compared against the same canonical case, including both runtime evidence and KPI deviation.

### 10. One cumulative engineering report

A defining feature of this skill is its default final-output contract.

After a completed modeling or optimization cycle, user-facing deliverables should normally be limited to:

1. the model/source artifacts required to use the model;
2. requested simulation/result artifacts;
3. **one cumulative Markdown engineering report**.

Default report name:

```text
MODEL_ENGINEERING_REPORT.md
```

The report accumulates project purpose, baseline, architecture, assumptions, interfaces, fidelity decisions, configuration, graphical changes, diagnostics, simulation setup, KPI interpretation, before/after performance, verification evidence, limitations, engineering evaluation, next steps, and reproducibility instructions.

The skill intentionally avoids scattering the final handoff across separate `architecture_report.md`, `icon_report.md`, `diagnosis_report.md`, `optimization_notes.md`, and similar files unless explicitly requested.

---

## Repository structure

```text
modelica-system-level-simulation/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ references/
│  ├─ architecture.md
│  ├─ configuration-pipeline.md
│  ├─ diagnostics-and-performance.md
│  ├─ fidelity-and-performance.md
│  ├─ interfaces-and-observability.md
│  ├─ modeling-decision-framework.md
│  ├─ open-source-inspirations.md
│  ├─ openmodelica-toolchain.md
│  ├─ output-and-reporting.md
│  ├─ simulation-observation-loop.md
│  ├─ verification-and-quality-gates.md
│  └─ visual-language.md
├─ scripts/
│  ├─ audit_modelica_project.py
│  ├─ audit_modelica_visuals.py
│  ├─ audit_whiteboxes.py
│  └─ diagnose_openmodelica.py
├─ templates/
│  ├─ engineering-report-template.md
│  ├─ modelica-patterns.md
│  └─ project-layout.md
├─ manifest.txt
└─ LICENSE
```

`SKILL.md` contains the main workflow. The supporting references are loaded only when the task requires them, while the Python scripts provide deterministic project auditing and lightweight OpenModelica diagnosis.

---

## Installation

### Option A — install with Codex Skill Installer

Codex includes a skill installer that can install skills from external repositories. Invoke:

```text
$skill-installer
```

Then ask it to install:

```text
https://github.com/Ruizhe-Yang/modelica-system-level-simulation-skill
```

If the skill does not appear immediately, restart Codex.

### Option B — install as a personal skill

Clone the repository into your personal Agent Skills directory:

```bash
git clone https://github.com/Ruizhe-Yang/modelica-system-level-simulation-skill \
  "$HOME/.agents/skills/modelica-system-level-simulation"
```

The personal location is:

```text
$HOME/.agents/skills/modelica-system-level-simulation/
```

### Option C — install for one repository

Place or add the skill under the target repository's `.agents/skills` directory:

```text
<your-project>/.agents/skills/modelica-system-level-simulation/
```

For a Git-managed project, a submodule is one possible approach:

```bash
git submodule add \
  https://github.com/Ruizhe-Yang/modelica-system-level-simulation-skill \
  .agents/skills/modelica-system-level-simulation
```

Codex scans `.agents/skills` from the working directory up to the repository root.

---

## Usage

### Explicit invocation

In Codex CLI or the IDE extension, invoke the skill directly:

```text
$modelica-system-level-simulation
Inspect this Modelica project end to end. Establish the current architecture,
run staged OpenModelica diagnostics, improve the system model and graphics,
validate a canonical simulation, optimize performance where justified, and
update the cumulative MODEL_ENGINEERING_REPORT.md.
```

You can also inspect available skills with:

```text
/skills
```

### Implicit invocation

`agents/openai.yaml` enables implicit invocation. Codex may automatically use this skill when the task clearly matches system-level Modelica modeling, diagnosis, visualization, simulation, or optimization.

### Example prompts

**Refactor an existing system model**

```text
$modelica-system-level-simulation
Refactor this project into clear graphical assemblies and localized behavior
cores. Preserve existing interfaces where possible, validate the canonical
experiment, and document all decisions in the cumulative report.
```

**Diagnose a slow model**

```text
$modelica-system-level-simulation
The canonical simulation is too slow. Diagnose the bottleneck by stage,
establish a performance baseline, simplify only high-cost/low-value detail,
and compare runtime and KPI behavior after every justified optimization.
```

**Improve icons and diagrams**

```text
$modelica-system-level-simulation
Audit all user-facing Modelica graphics. Replace placeholder icons with
semantic engineering icons, improve Diagram routing non-destructively, keep
family conventions consistent, and validate that graphical edits do not
change model semantics.
```

**Build an external configuration workflow**

```text
$modelica-system-level-simulation
Create a deterministic Excel-to-Modelica configuration pipeline with one
Modelica-side baseline, validated overrides, generated local artifacts, and a
resolved run snapshot. Do not make the solver parse Excel during simulation.
```

---

## Toolchain

The skill is **OpenModelica-first but not OpenModelica-only**.

### Recommended

- Modelica project/source code;
- OpenModelica / `omc` for check, flatten, build, simulation, and profiling;
- Python 3 for bundled audit and diagnostic helpers.

### Optional

- OMEdit for graphical inspection/editing;
- OMEdit MCP for agent-driven model/diagram interaction where available;
- external C implementations, FMUs, or software interfaces when the project requires higher-fidelity or replaceable implementations.

The core architectural and modeling guidance remains useful even when the OpenModelica-specific helper scripts are not used.

---

## Bundled helper scripts

| Script | Purpose |
|---|---|
| `scripts/audit_modelica_project.py` | Static project inventory and Modelica coverage/structure metrics |
| `scripts/audit_modelica_visuals.py` | Static heuristics for Icon/Diagram annotation coverage and visual issues |
| `scripts/audit_whiteboxes.py` | Checks explicitly designated strict graphical white-box assemblies |
| `scripts/diagnose_openmodelica.py` | Lightweight staged OpenModelica check/flatten/build/simulate/profile workflow |

These scripts support the workflow; they do not replace engineering judgment or physical validation.

---

## Modeling philosophy

This skill intentionally avoids several common anti-patterns:

- forcing every system into the same physical-domain hierarchy;
- hiding significant public topology behind inheritance;
- putting architecture, physics, controller logic, parsing, and UI into one giant model;
- maximizing fidelity before interfaces and parameter flow are validated;
- replacing true conservation networks with directional signals only to simplify drawings;
- using generic identical icons for unrelated engineering components;
- erasing hand-tuned graphics during automated re-layout;
- treating Excel as a runtime solver dependency;
- duplicating the same physical fact in several variables or configuration sources;
- tuning solver tolerances before identifying structural/modeling causes;
- claiming success only because the simulation completed;
- producing many fragmented final reports instead of one reproducible engineering handoff.

---

## Open-source inspirations

This skill is not a copy of a single upstream project. It combines an independent system-level Modelica workflow with selected public agent-engineering ideas adapted for an OpenModelica-first environment.

Important inspirations include:

- [Wolfram Research — System Modeler AI Toolkit](https://github.com/WolframResearch/system-modeler-ai-toolkit): model architecture, semantic graphical annotation, staged diagnosis, and simulation-result inspection concepts;
- [LunCoSim](https://github.com/LunCoSim/lunco-sim): run/inspect closed-loop agent workflows and explicit multidomain boundaries;
- [OpenModelica](https://openmodelica.org/): execution, diagnostics, profiling, and optional OMEdit MCP capabilities;
- [OpenAI Agent Skills](https://developers.openai.com/codex/skills/): skill packaging, progressive disclosure, local skill discovery, explicit/implicit invocation, and `agents/openai.yaml` conventions.

See [`references/open-source-inspirations.md`](./references/open-source-inspirations.md) for the detailed adaptation notes.

---

## What this repository is — and is not

This repository is:

- an engineering workflow for AI-assisted Modelica development;
- a reusable Agent Skill;
- a set of modeling, visualization, diagnosis, optimization, verification, and handoff conventions;
- a small set of helper scripts and templates.

It is **not**:

- a replacement for the Modelica language specification;
- a new Modelica component library;
- a fixed physical-domain architecture;
- a guarantee that a numerically successful simulation is physically valid;
- tied to one application such as aerospace, energy, thermal-fluid systems, vehicles, or industrial control.

---

## Version

Current skill metadata version: **3.0.0**.

The main behavior contract is defined in [`SKILL.md`](./SKILL.md). Changes that materially alter workflow semantics should update both the skill metadata and this README.

---

## License

This repository is released under the **GNU General Public License v3.0**. See [`LICENSE`](./LICENSE).

Third-party projects referenced by this skill retain their own licenses and copyrights. Upstream ideas are paraphrased and adapted; upstream implementations are not bundled unless explicitly stated.

---

## Contributing

Issues and pull requests are welcome, especially for:

- additional OpenModelica diagnostic evidence and profiling workflows;
- stronger static checks for Modelica architecture and annotations;
- cross-platform improvements to the helper scripts;
- examples from different engineering domains;
- regression and verification patterns;
- improvements to semantic Icon/Diagram generation and visual QA.

When proposing a change, prefer domain-independent rules unless the contribution is clearly documented as an optional domain-specific extension.