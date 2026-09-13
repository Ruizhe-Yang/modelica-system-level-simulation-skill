# Output and reporting contract

## 1. Default final artifact policy

After each completed Codex modeling/refactoring/optimization cycle, the user-facing final project should contain only:

1. model/source/configuration artifacts required to use the model;
2. requested simulation/result artifacts;
3. one cumulative Markdown engineering report.

Default report name:

```text
MODEL_ENGINEERING_REPORT.md
```

If the project already uses another established report filename, update it instead of adding a second report.

## 2. Why one report

The report is the human-readable engineering history and handoff package. It replaces scattered architecture notes, icon reports, simulation summaries, optimization reports, and diagnostic notes.

It should allow a new engineer to answer:

- what was the model supposed to do?
- what existed initially?
- what changed and why?
- how are the subsystems connected?
- what assumptions and fidelity decisions were made?
- how was the model diagnosed?
- what simulations were run?
- what are the important results?
- did performance improve?
- what remains uncertain?
- what should be done next?

## 3. Cumulative update rule

Do not write a thin “today's changes” report.

Update the report so it describes the **current final model state**, while retaining a concise change/history section for important iterations.

When replacing earlier statements that are no longer true, update them rather than leaving contradictions.

## 4. Required report sections

Use `templates/engineering-report-template.md` and include applicable sections:

1. Executive summary
2. Task and engineering objectives
3. Baseline/model inventory
4. Toolchain and dependencies
5. Modeling contract
6. System boundary and architecture
7. Interface and parameter semantics
8. White-box/black-box/fidelity strategy
9. Configuration pipeline
10. Observability and KPIs
11. Visual design (Icon/Diagram)
12. Changes performed
13. Diagnostic history and root causes
14. Simulation setup and execution
15. Result analysis
16. Performance analysis and before/after comparison
17. Verification/quality gates
18. Limitations and unresolved issues
19. Engineering evaluation
20. Next-step recommendations
21. Final deliverable inventory and reproduction procedure

## 5. Change documentation granularity

For material changes include:

| File/Class | Change | Reason | Evidence/Effect |
|---|---|---|---|
| ... | ... | ... | ... |

Do not list trivial whitespace-only edits.

## 6. Diagnostic documentation

Use the pattern:

```text
symptom → stage → evidence → root cause → correction → retest → residual risk
```

Do not paste whole compiler logs. Include only short representative messages and point to internal/temp evidence if it must be retained.

## 7. Results documentation

For each canonical run record:

- entry model;
- resolved configuration/case;
- start/stop time;
- solver/tolerance/output interval;
- tool version;
- result file;
- key KPIs;
- sanity/physical checks;
- runtime/performance metrics;
- interpretation.

## 8. Engineering evaluation

At the end, score or qualitatively evaluate as appropriate:

- correctness/consistency;
- architectural clarity;
- interface stability;
- visual readability;
- configuration traceability;
- observability;
- fidelity appropriateness;
- simulation robustness;
- performance;
- maintainability;
- replaceability/extensibility;
- reproducibility.

State evidence and caveats. Avoid unsupported “excellent/complete” claims.

## 9. Intermediate evidence policy

Compiler logs, temporary MOS files, profiler HTML/XML/SVG, test JSON, and debug dumps are not separate final reports by default.

If required by automation, keep them in an internal/generated location, not as parallel user-facing documents.

Summarize all relevant conclusions into the Markdown report.

## 10. Explicit user requests override the default

If the user explicitly asks for an additional HTML, PDF, Excel, diagnostic log, image, or other artifact, produce it. The one-report rule is the default for ordinary Modelica optimization/handoff, not a prohibition against explicit deliverables.
