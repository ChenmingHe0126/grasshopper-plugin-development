---
name: grasshopper-testing
description: Validate Grasshopper components and Rhino plugins with pure-core tests, host integration, saved-definition round trips, and real canvas or viewport checks. Use when testing plugin behavior or diagnosing host-specific test failures.
---

# Grasshopper testing

Choose the cheapest layer that can observe the behavior being changed. A successful build, a headless solve and a real viewport check establish different things.

- Read [Verification layers and GH fixtures](references/verification-layers.md) to choose checks or build repeatable definitions.
- Read [Host identity and crash triage](references/host-triage.md) when a test loads the wrong plugin, crashes in Rhino/GH startup, or appears to ignore keyboard input.

## Select evidence by behavior

| Changed behavior | Useful evidence |
|---|---|
| Numerical algorithm, state transition, parser, replay or key deduplication | Host-free tests with numerical/behavioral invariants |
| Rhino geometry adaptation, GH inputs/outputs, warnings, resource lookup | Real Rhino/GH integration using the exact build under test |
| Wiring, persistence, defaults, migrations, examples | Save, close and reopen a GH definition; solve and inspect restored state |
| Canvas controls, focus, hooks, viewport/HUD, DPI, cancellation and cleanup | Interactive Rhino/GH with the actual UI or genuine input path |
| Runtime/package compatibility | Loading and smoke checks for each supported runtime/package variant |

Keep the test runner's target framework and dependency model compatible with the code it exercises. Moyu compiles its host-free source files directly into a separate runner; a separate core assembly is another valid design.

## Make the run trustworthy

- Identify the exact loaded assembly path, host version and runtime. Refuse or report a stale installed copy instead of testing it as if it were the new build.
- For iterative GH components, expire and solve deliberately. Check initial/paused state, one advance, changed input, reset and completion as relevant; an output merely being non-null is weak evidence.
- Pair positive scenarios with the specific invalid or boundary input the change handles. Use stable numerical or geometry invariants rather than a screenshot alone.
- Treat generated examples as deliverables: reopen the saved file and check links, defaults and execution. Avoid silently overwriting user-edited examples when regenerating fixtures.
- Keep host-specific tests explicit about prerequisites. Missing licensed Rhino or unavailable interactive UI is an unrun layer, not a passing test.

## Report the actual result

State what ran, the build/host used, and what the result establishes. Name meaningful failures or unavailable layers. A software-rendered geometry image from a headless test is useful evidence of data, but is not a captured Rhino viewport or proof that keyboard/focus behavior works.
