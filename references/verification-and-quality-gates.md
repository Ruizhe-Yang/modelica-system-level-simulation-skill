# Verification and quality gates

## Gate A — project architecture

Check:
- package dependency direction;
- no accidental higher-layer dependency from Foundation;
- generated and handwritten code are separated;
- one or more clearly identified canonical experiments exist;
- public class responsibilities are understandable.

## Gate B — strict graphical assemblies

For models designated strict white boxes:
- equation section contains only `connect(...)`;
- important connections have visible `annotation(Line(...))`;
- no algorithm/dynamics/control equations are hidden in the assembly;
- significant topology is not hidden through inheritance;
- Icon, Diagram, and Documentation exist as required by the project.

Use `scripts/audit_whiteboxes.py` on the declared directories.

## Gate C — interface semantics

Check:
- compatible connector types;
- meaningful units;
- clear state ownership;
- no duplicate authoritative producers;
- frame/reference conventions documented;
- causal signals are not being used accidentally where conservation is required.

## Gate D — configuration

Check:
- source schema/version;
- unique parameter keys;
- valid target paths;
- supported units;
- baseline vs override status;
- valid ranges and cross-field constraints;
- deterministic regeneration;
- generated-file provenance.

## Gate E — initialization and physical consistency

Check as applicable:
- successful initialization;
- conservation residuals;
- positive/physical capacities, masses, inertias, volumes, resistances, efficiencies, etc.;
- meaningful network references/boundaries;
- finite states;
- no unintentional over/under-constrained connectors;
- plausible initial energy/inventory.

## Gate F — component/core verification

For important behavior cores:
- unit tests or focused experiments;
- limiting-case checks;
- monotonicity/sign checks where expected;
- comparison against analytic solution, source data, higher-fidelity model, or trusted library when available.

## Gate G — system regression

Check:
- nominal KPIs;
- key envelopes/trajectories;
- expected operating-mode transitions;
- expected events;
- observer/KPI availability;
- no new numerical warnings;
- selected alternative/fault cases when in scope.

Do not overfit regression to every floating-point sample. Use tolerances and physically meaningful metrics.

## Gate H — performance regression

Track:
- translation time;
- integration time;
- state/event growth;
- nonlinear system changes;
- result size;
- memory where relevant.

Investigate structural changes before relaxing solver settings.

## Gate I — visual QA

Open representative public classes in the target Modelica GUI.

Inspect:
- icon recognizability;
- connector placement consistency;
- diagram routing;
- line crossings;
- label overlap;
- navigation hierarchy;
- readability at normal zoom;
- consistency across equipment families.

Visual QA cannot be replaced by regex/source checks.

## Release evidence

Preserve as appropriate:
- source version/commit;
- resolved configuration;
- generated artifacts;
- external resource versions/hashes;
- verification summary;
- performance metrics;
- toolchain version.


## Gate J — handoff and reporting

Check:
- final source/model artifacts are the intended current versions;
- requested result files correspond to the documented canonical runs;
- one cumulative `MODEL_ENGINEERING_REPORT.md` describes the current final state;
- architecture, visual, diagnosis, simulation, performance, verification, limitations, evaluation, and reproduction information are consolidated there;
- redundant human-facing diagnostic/icon/optimization/test-summary reports are not left behind unless explicitly requested;
- temporary logs and profiler outputs are cleaned or clearly treated as internal/generated evidence.
