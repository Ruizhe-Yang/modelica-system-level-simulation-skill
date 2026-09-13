# Visual language for engineering Modelica models

## 1. Visuals are model architecture

Icon and Diagram annotations are not presentation polish. They are a navigable representation of system identity, boundaries, topology, and information flow.

A good visual system lets an engineer answer quickly:

- what kind of thing is this class?
- what are its important ports?
- which direction does the dominant flow or command path run?
- which elements belong together?
- what is a shared network versus a local connection?
- where should I drill down next?

## 2. Classify each class before styling it

Use a role classification first:

| Role | Visual treatment |
|---|---|
| package/category | standard `Modelica.Icons.*` base when appropriate |
| connector/interface | compact domain/semantic symbol; no decorative body |
| source/boundary | clear source/reservoir/environment motif |
| physical equipment | recognizable engineering silhouette/motif |
| controller/logic | functional logic/controller motif; visually distinct from plant |
| sensor/observer | sensing/measurement motif; avoid looking like an actuator |
| adapter/converter | transformation/bridge motif |
| subsystem/assembly | family frame + topology-centered Diagram |
| experiment/example | standard example/experiment identity plus readable runnable Diagram |
| behavior core | simple but purposeful identity; not necessarily a rich public-facing schematic |

Do not give unrelated classes the same generic rectangle merely for consistency.

## 3. Project visual grammar

Define once per project:

- Icon coordinate system, normally a stable `{{-100,-100},{100,100}}` frame unless the library already uses another convention;
- connector side/placement rules by interface family;
- dominant Diagram flow direction;
- a minimal semantic line/color vocabulary;
- label locations and text hierarchy;
- subsystem/family motifs;
- source/sink/sensor/controller/observer treatment;
- shared-network routing corridors;
- rules for live KPI/status display.

Stability across the library matters more than a theoretically perfect local placement.

## 4. Semantic icon synthesis workflow

For every nontrivial custom component:

1. Read class name and one-line description.
2. Inspect connector names/types and identify the primary interaction path.
3. Inspect contained components or equations only to understand engineering function.
4. Identify 1–3 characteristic visual features.
5. Draw a simplified engineering symbol using Modelica vector primitives.
6. Reserve clear edge zones for connectors.
7. Reuse a family motif for sibling models without erasing their unique identity.
8. Add `%name` or a short text label only if the graphic does not identify the class well enough.
9. Inspect at normal and zoomed-out scale.

Preferred primitives:

- `Rectangle`
- `Ellipse`
- `Line`
- `Polygon`
- `Text`

Use filled areas sparingly. Avoid tiny decorative details that disappear when zoomed out.

Raster `Bitmap` use should be exceptional because it weakens portability, scaling, and editability.

## 5. Custom connector graphics

A connector symbol should:

- be small and visually robust;
- preserve the domain/interface category;
- not imply a physical direction if the connector is acausal;
- remain distinguishable from a signal port when semantics differ;
- use the same visual family everywhere it appears.

Do not color-code so many connector types that the palette itself becomes a legend the user must memorize.

## 6. Connector placement

Derive geometry from the dominant engineering path.

Common patterns include:

```text
primary inlet → [ model ] → primary outlet
                   ↑  ↓
             support / control
```

or a project-specific multi-domain arrangement.

For a repeated interface family, keep the edge stable across sibling components unless the physical topology strongly argues otherwise.

Do not place ports merely to make one local line shorter if it makes the library inconsistent.

## 7. Diagram layout from the connection graph

Before moving components, identify:

- source/boundary nodes;
- sink/load nodes;
- the dominant main path;
- branches;
- feedback/strongly-connected groups;
- shared buses/networks;
- supervisory control/observer paths.

Then select a layout pattern:

- linear process → left-to-right or top-to-bottom;
- plant + supervisory control → stacked layers;
- shared utilities/network → lane, matrix, or hub-and-spoke;
- symmetric network → radial/ring if clearer;
- spatially important plant → approximate physical arrangement;
- mixed architecture → combine patterns deliberately.

### Routing rules

Prefer:

- short orthogonal or low-bend routes;
- perimeter boundary ports;
- dedicated shared-network corridors;
- explicit branch points;
- minimal line crossings;
- limited line overlap;
- feedback routes that visibly return rather than wrap unpredictably through the drawing;
- consistent orientation for repeated components.

When a line must cross another domain, keep the crossing visually unambiguous.

## 8. Non-destructive annotation policy

Automated visual changes must be conservative.

Default behavior:

1. analyze current graphics;
2. identify missing/weak areas;
3. preview or diff changes when practical;
4. modify only the intended annotations;
5. preserve existing hand-tuned `Placement`, `Line`, `Icon`, and `Diagram` work;
6. validate the model after the graphics change.

A complete forced regeneration is allowed only when the user explicitly wants to discard/rebuild the existing graphical layout.

Never treat hand-authored graphics as disposable merely because automatic layout is easier.

## 9. Standard icons vs custom icons

Use `Modelica.Icons.*` for package/category/function/record/example identities where the standard convention fits.

Use custom semantic Icons for user-facing engineering equipment where the class identity matters.

If the class is initially unknown, a generic placeholder may be used for architecture bring-up, but the visual quality gate remains open until it is replaced.

## 10. Interaction design

The normal graphical navigation path should be:

```text
experiment → overall system → subsystem/process unit → component → behavior core
```

Use `DynamicSelect` only for a small number of high-value states, for example:

- operating mode;
- one critical temperature/pressure/speed;
- health state;
- primary power/flow indicator.

Do not render a full dashboard inside every Icon. Large output sets belong in observers/result analysis.

## 11. Visual QA checklist

Inspect representative views for:

- semantic recognizability;
- family consistency;
- stable connector edge conventions;
- connector alignment;
- label legibility;
- lines ending on actual pin locations;
- line crossings and wrap-around routes;
- off-canvas or clipped graphics;
- oversized/undersized component bodies;
- empty whitespace vs overcrowding;
- misleading arrows on acausal flows;
- inconsistent source/sink/controller/sensor treatment;
- generic placeholder icons still present;
- accidental damage to existing hand-authored layout.

Use `scripts/audit_modelica_visuals.py` for static heuristics, but treat actual graphical inspection in OMEdit (or screenshots/MCP) as the final gate.
