# OpenModelica toolchain guidance

## 1. Preferred execution surfaces

Use the best available surface in this order:

1. connected **OMEdit MCP** when interactive model/graphics/result operations are needed;
2. `omc` with a generated `.mos` script for deterministic headless checks and runs;
3. OMEdit manually only when the task truly requires GUI-only behavior that the agent cannot access.

Do not require MCP for the skill to function.

## 2. OMEdit MCP

Recent OpenModelica releases include an experimental OMEdit MCP server that can expose Modelica editing/running/result-inspection operations to compatible AI clients.

When available:

- inspect existing classes before edits;
- make targeted source/graphical changes;
- run the concrete experiment;
- read results directly;
- use graphical inspection to validate Icon/Diagram quality.

Never assume the local MCP endpoint or permissions are enabled; detect/use it only when present.

## 3. OMC scripting gates

Useful scripting calls include:

```modelica
loadModel(Modelica, {"4.0.0"});
loadFile("/absolute/path/package.mo");
checkModel(MyLibrary.Experiments.NominalCase);
getErrorString();
instantiateModel(MyLibrary.Experiments.NominalCase);
getErrorString();
buildModel(MyLibrary.Experiments.NominalCase);
getErrorString();
simulate(MyLibrary.Experiments.NominalCase,
         startTime=0,
         stopTime=100,
         numberOfIntervals=1000,
         tolerance=1e-6,
         method="ida");
getErrorString();
```

Adapt library version and settings to the project. Do not hard-code MSL 4.0.0 when the project explicitly targets another version.

`checkModel` is useful for variable/equation balance; `instantiateModel` exposes the flattened model; `buildModel` isolates translation/build from runtime; `simulate` returns timing/result information.

## 4. Profiling

When the model is slow and a baseline exists, OpenModelica profiling can record time spent in functions and equation systems. Common compiler options include profiling levels such as `blocks`, `blocks+html`, and `all` depending on version.

Use profiling after basic structural checks, not before.

Generated profiler HTML/XML/SVG is intermediate by default. Extract the highest-cost blocks/functions and record them in the cumulative Markdown report.

## 5. Logging

Enable focused logging only for the suspected problem class, for example nonlinear-system diagnostics, zero crossings, initialization residuals, solver statistics, or simulation statistics.

Avoid enabling every verbose logging stream during ordinary runs because it can distort performance and bury the evidence.

## 6. Runtime ceiling

When the modeling contract states a maximum acceptable run time, enforce a timeout around the OMC/simulation process. A timed-out run is diagnostic evidence, not a reason to wait indefinitely.

After timeout:

1. record where the process spent time if known;
2. shorten to a diagnostic horizon if useful;
3. profile or simplify;
4. rerun under the same ceiling.

## 7. Temporary artifacts

Use a predictable temporary work area such as:

```text
.<project>/.modelica_work/
```

or a system temp directory.

Temporary artifacts may include MOS files, compiler logs, generated C code, profiler reports, and intermediate JSON/XML.

At the end of the task:

- keep files required for actual execution/reproducibility;
- keep explicitly requested result files;
- summarize diagnostic evidence into `MODEL_ENGINEERING_REPORT.md`;
- remove redundant user-facing intermediate reports/logs unless the user requested them.

## 8. Tool independence

Even when OpenModelica is the primary execution environment:

- keep Modelica language usage standard where feasible;
- isolate OpenModelica-specific annotations/options;
- document any extension that prevents another compliant tool from loading the model.
