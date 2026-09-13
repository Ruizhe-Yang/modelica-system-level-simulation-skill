# Simulation observation loop

## 1. Principle

Do not treat simulation as a fire-and-forget command.

The agent owns the loop:

```text
validate → run → read → sanity-check → compare → explain → modify → rerun
```

Do not ask the user to inspect a plot or value that the available tools can read directly.

## 2. Canonical case first

Before sweeps, Monte Carlo, variants, fault campaigns, or optimization:

- define one canonical nominal entry model;
- freeze its configuration snapshot;
- record solver/time horizon/output settings;
- record baseline KPIs and runtime;
- confirm the result passes sanity checks.

## 3. Read key outputs immediately after a run

Read only the channels needed to answer the engineering question first. Then expand inspection if something is suspicious.

Typical categories:

- state variables;
- conserved quantities;
- commands and actuator responses;
- modes/events;
- resource margins;
- user-defined KPIs;
- health/safety observers.

## 4. Sanity classes

### Numerical
- finite values;
- sensible sample count/time coverage;
- no unexpected solver abort/restart pattern.

### Physical
- correct units/signs/ranges;
- conservation/reference checks;
- plausible limiting behavior.

### Functional
- correct event/mode ordering;
- commands reach the intended actuator/path;
- outputs respond with the expected causal timing.

### Performance
- runtime and result size within budget;
- no major regression versus baseline.

## 5. Compare deliberately

When changing a model, compare:

- same configuration;
- same experiment horizon;
- same required outputs;
- same solver/tolerance unless the solver is itself the subject of the test.

For a fidelity simplification, report the speedup together with KPI deviation, not speed alone.

## 6. Iteration discipline

Prefer one major cause per iteration. If several unrelated changes are made together, the report must clearly separate them and explain why an A/B comparison was not practical.

## 7. Output discipline

Keep requested result files. Convert intermediate observations into the cumulative `MODEL_ENGINEERING_REPORT.md` rather than emitting separate summary files.
