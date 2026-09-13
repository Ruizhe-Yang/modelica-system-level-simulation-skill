# Architecture rules

## 1. Separate ownership categories

A useful domain-independent architecture distinguishes:

### Foundation
Owns reusable semantics and behavior:
- connectors and types;
- equation cores;
- algorithms/state machines;
- reusable physical primitives not already available in trusted libraries;
- calculations/functions;
- adapters.

### Configuration
Owns static run definition:
- default design records;
- operating cases;
- initial conditions;
- control/calibration records;
- generated overrides;
- external resource metadata.

### Components
Own engineering identity and local composition.

A component should expose stable interfaces and hide implementation detail that its parent does not need.

### Systems
Own aggregation and integration.

Substructure may be organized by:
- function;
- process section;
- equipment train;
- spatial region;
- organizational ownership;
- shared coupling network.

### Experiments
Own execution context:
- nominal case;
- variants;
- validation tests;
- benchmarks;
- fault cases when relevant.

## 2. Architecture is a graph, not only a tree

The package hierarchy is a storage/navigation tree. The engineering system is usually a graph.

Preserve cross-cutting interactions explicitly with connectors and, where useful, dedicated shared-network models.

Do not distort the physics simply to fit the folder hierarchy.

## 3. Functional/process × coupling matrix

Create the matrix before the top diagram.

Example with abstract domains:

| Unit | Primary flow | Support network | Control/data | Environment |
|---|---:|---:|---:|---:|
| A | ✓ | ✓ | ✓ |  |
| B | ✓ |  | ✓ | ✓ |
| C | ✓ | ✓ |  |  |

Use actual domain names in a real project.

The matrix should drive:
- connector presence;
- shared networks;
- boundary adapters;
- top-level routing.

## 4. Boundary ownership rule

For every interface quantity, answer:
- Who owns the state?
- Is it an effort/flow variable, potential, conserved flow, command, measurement, state, or event?
- Which side may write it?
- What unit/frame/reference applies?
- Is it continuous or discrete?
- Does it belong in configuration or runtime state?

If ownership is unclear, do not implement the interface yet.

## 5. Stable boundaries, replaceable internals

Prefer an architecture where a component implementation can move between fidelity levels without parent changes.

A replacement may be:
- another Modelica model;
- a replaceable/redeclare variant;
- C wrapper;
- FMU;
- external controller/software.

Avoid leaking internal states into parent-level logic unless those states are intentionally part of the contract.

## 6. Use inheritance carefully

Inheritance is useful for:
- common icon bases;
- connectors/types;
- partial equation bases when mathematically appropriate;
- standardized interfaces.

Avoid inheritance that hides significant topology in public graphical assemblies. A user opening the Diagram should not need to search a deep inheritance chain to understand what is connected.

## 7. Keep overall models boring

A good overall model primarily:
- instantiates major subsystems/networks;
- injects configuration;
- connects boundaries;
- exposes observers/results.

If the overall model contains detailed equations, repeated modifiers, controller algorithms, data parsing, or ad-hoc result logic, move those responsibilities down to the proper layer.
