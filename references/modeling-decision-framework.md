# Modeling decision framework

Use this document before implementing or refactoring a system-level Modelica project.

## 1. Modeling contract table

Create a table like this:

| Question | Decision |
|---|---|
| Primary use | design exploration / control verification / energy analysis / safety analysis / virtual commissioning / other |
| System boundary | ... |
| Main outputs | ... |
| Simulation horizon | ... |
| Fastest relevant dynamics | ... |
| Accuracy needs | ... |
| External integrations | ... |
| Maximum acceptable runtime | ... |
| Main configuration source | ... |
| Required traceability | ... |

The model should be judged against this contract, not against maximum possible detail.

## 2. Choose decomposition from engineering questions

### Functional/process decomposition
Use when engineers ask:
- which subsystem owns a function?
- where is a failure/function located?
- which equipment belongs to which process section?
- which team is responsible for a model?

### Coupling-domain decomposition
Use when engineers ask:
- which shared network couples otherwise separate subsystems?
- where is conservation closed?
- where are common references/sources/distribution buses?
- which interaction is hard to understand when repeated locally?

### Geometric/spatial decomposition
Use when physical location is itself important:
- distributed thermal systems;
- piping networks;
- structural networks;
- building/plant layouts;
- transport networks.

### Control/automation decomposition
Use when controller architecture is a first-class object:
- plant vs controller;
- supervisory vs local control;
- estimator/observer layers;
- software partitions.

A project may use several views, but only materialize a view as Modelica hierarchy if doing so improves traceability, coupling clarity, or replaceability.

## 3. Decide whether a shared coupling network deserves its own model

Create a dedicated overall network when most answers are yes:

- Does it connect three or more functional/process units?
- Does it own shared physical closure/reference/source behavior?
- Would local point-to-point connections duplicate the same infrastructure?
- Do engineers need to inspect the network independently?
- Will the network have alternative architectures or fidelity variants?
- Does it improve visual routing significantly?

If most answers are no, keep the coupling local.

## 4. Select fidelity per component, not per project

For each unit, score:
- impact on primary outputs;
- coupling strength;
- dominant time scale relevance;
- uncertainty;
- safety/decision criticality;
- availability of parameters/data;
- computational cost.

Use higher fidelity where impact and evidence justify it. Keep low-impact units reduced.

## 5. Decide white-box strictness

Use **strict white box** when:
- topology itself is part of the engineering communication;
- users need to inspect internal connections;
- the class primarily composes other components.

Use **black-box core** when:
- equations/algorithm are the primary responsibility;
- topology would not add useful engineering meaning.

Use **hybrid adapter** only for small, transparent glue behavior.

## 6. Define completion metrics early

Examples:
- KPI accuracy/range;
- conservation residual;
- initialization robustness;
- simulation runtime;
- maximum event count;
- number of manual configuration edits;
- documentation coverage;
- visual QA status;
- regression stability.
