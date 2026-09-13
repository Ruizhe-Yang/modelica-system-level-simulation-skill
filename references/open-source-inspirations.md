# Open-source inspirations and adaptations

This custom skill is not a copy of a single upstream skill. It combines domain-independent system-modeling rules from the user's existing v2 skill with selected public agent-workflow ideas, rewritten for an OpenModelica-first environment.

## 1. Wolfram Research — System Modeler AI Toolkit

Repository:

- https://github.com/WolframResearch/system-modeler-ai-toolkit

Ideas adapted:

### `modelica-model-architecture`

- architect before equations;
- reuse standard library components/connectors before rebuilding;
- connector design as the basis of decomposition;
- tool-independent Modelica where possible;
- graphics/documentation/testing belong in definition-of-done.

Adaptation here:

- preserved the user's domain-independent functional/process × coupling-network architecture;
- removed Wolfram System Modeler-specific library shape requirements that are not universal;
- optimized execution guidance for OpenModelica/OMC.

### `annotate-modelica-graphics`

- classify classes before annotation;
- standard icons for package/category classes;
- semantic glyphs for leaf components/connectors;
- graph-aware Diagram layout and orthogonal routing;
- preview/non-destructive workflow;
- validate after annotation changes.

Adaptation here:

- converted these into a project-wide semantic visual grammar rather than depending on Wolfram's bundled annotator;
- strengthened preservation of hand-tuned graphics;
- made final visual QA explicitly include engineering recognizability and library-family consistency.

### `diagnose-modelica`

- diagnose by pipeline stage rather than reading one final error;
- separate flatten/build/simulation failures;
- collect structure/performance evidence;
- trace suspicious variables through their solving dependencies.

Adaptation here:

- mapped the staged workflow to OpenModelica scripting calls and profiling;
- integrated diagnostics into the single cumulative engineering report rather than generating a separate final diagnostic report.

### `simulate-modelica`

- successful execution is not proof of a physically correct result;
- sanity-check trajectories after every important simulation;
- report timing/events/performance evidence.

Adaptation here:

- combined this with observability/KPI traceability and a canonical-case regression loop.

## 2. LunCoSim skills

Repository:

- https://github.com/LunCoSim/lunco-sim

Relevant public skills:

- `skills/run-modelica/SKILL.md`
- `skills/inspect-simulation/SKILL.md`
- `skills/compose-multidomain-twin/SKILL.md`

Ideas adapted:

- the agent should run and inspect the model directly rather than asking the user to click/check;
- keep “run” and “inspect” as a closed loop;
- treat multi-domain composition as explicit boundaries and ports rather than hidden cross-domain state copying.

Adaptation here:

- removed LunCoSim/USD/Rust-specific assumptions;
- retained the principle of explicit ownership and read-after-run inspection for ordinary Modelica/OpenModelica projects.

## 3. OpenModelica

Official documentation:

- https://openmodelica.org/
- https://github.com/OpenModelica/OpenModelica/blob/master/OMEdit/OMEditLIB/MCP/README.md

Ideas/capabilities used:

- `checkModel`, `instantiateModel`, `buildModel`, `simulate`, `getErrorString` staged gates;
- OpenModelica performance profiling of functions/equation systems;
- optional OMEdit MCP server for AI-assisted graphical/model interaction.

These are used as execution mechanisms, not copied as a separate Skill.

## 4. OpenAI Agent Skills conventions

The package follows the Agent Skills shape:

```text
skill-name/
├─ SKILL.md
├─ agents/openai.yaml
├─ references/
├─ scripts/
└─ templates/
```

The `SKILL.md` frontmatter name matches the folder name, and `agents/openai.yaml` provides Codex-facing display/invocation metadata.

## 5. Licensing note

This skill paraphrases workflow ideas and links to upstream projects. It does not bundle Wolfram's documentation corpora or copy their launcher/annotator implementation. If upstream code is later copied into this skill, preserve the applicable upstream license and attribution at that time.
