# Interfaces and observability

## 1. Classify interfaces by semantics

Before coding, classify every boundary as one or more of:
- physical conservation interface;
- command/setpoint;
- measurement;
- state/status;
- event/mode;
- external boundary/environment;
- configuration;
- engineering observer/telemetry;
- external software/co-simulation boundary.

Do not use one anonymous connector for incompatible meanings simply to reduce port count.

## 2. Physical connectors

Prefer acausal Modelica connectors for conservation networks.

Examples include:
- electrical effort/flow;
- mechanical flange/frame;
- heat flow/temperature;
- pressure/mass-flow or other fluid connectors;
- hydraulic/pneumatic effort-flow pairs.

Use directional signals for physical quantities only when the simplification is intentional, valid for the required fidelity, and documented.

## 3. Information and control interfaces

Use explicit semantic structure.

Recommended separation:
- commands/setpoints;
- measurements;
- execution/command status;
- device/system status;
- business/process data where relevant.

Use enums or typed records for modes/status when possible.

Avoid:
- magic array indices;
- multiple aliases of the same authoritative state;
- mixing command and observation ownership.

## 4. External boundary interfaces

External conditions should expose only what downstream models require.

Examples:
- ambient temperature/pressure;
- imposed load;
- reference trajectory;
- schedule;
- upstream/downstream boundary state;
- measured history;
- external disturbance.

Large source datasets may remain behind a boundary-condition provider rather than being propagated through the entire model.

## 5. Read-only observer layer

Recommended pattern:

```text
internal authoritative variables
        ↓
observer / KPI calculation
        ↓
stable engineering output schema
```

Observer responsibilities may include:
- unit conversion;
- naming normalization;
- KPI aggregation;
- health/state classification;
- result grouping.

Observer code should not feed back into physics unless it is intentionally an estimator/controller.

## 6. Traceability table

For each important published variable keep:

| Published field | Source model.variable | Transformation | Unit | Expected range | Sampling/event semantics |
|---|---|---|---|---|---|

This table is especially useful for:
- safety analysis;
- fault injection;
- software integration;
- test correlation;
- HIL/SIL;
- report generation.

## 7. C/FMU/software boundaries

Freeze the interface contract before replacing a native core.

Document:
- inputs/outputs and units;
- update rate or continuous semantics;
- initialization handshake;
- error/status reporting;
- state reset behavior;
- ownership of clocks/events;
- deterministic vs stochastic behavior;
- fallback behavior.

A wrapper should isolate tool-specific integration details from the rest of the Modelica architecture.
