# Moyu: evidence behind the skill collection

This collection extracts reusable development decisions from [Moyu](https://github.com/ChenmingHe0126/moyu), a Rhino 8 / Grasshopper plugin with 2D and 3D topology optimization and interactive viewport studies. It does not redistribute the plugin or imply that its product choices suit every plugin.

## Evidence snapshot and limits

The source inspected for this extraction is commit [`d1aa257523e929a6136937cb18aded4548d450a9`](https://github.com/ChenmingHe0126/moyu/tree/d1aa257523e929a6136937cb18aded4548d450a9). The extraction inspected code and repository documentation. It did not rerun numerical tests, Rhino.Inside, or an interactive Rhino session.

Historical test counts and runtime observations belong to the reports where they were recorded. Do not reuse those counts as a current test result. Verify the intended Rhino runtime and target framework for a new project rather than inheriting Moyu's versions.

## What transferred

| Observed in Moyu | Reusable decision | Evidence |
|---|---|---|
| Rhino-free numerical and game-rule sources are compiled into a standalone runner. | Keep deterministic rules testable without starting the host; keep geometry and UI in adapters. A separate core project is also valid. | [test project](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.Core.Tests/Moyu.Core.Tests.csproj) |
| Stateful solvers advance on trigger ticks; compatible changes retain density, Reset discards it. | Specify continuation, invalidation, reset, and missing-input behavior independently. | [solver](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs), [optimizer](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Core/SimpOptimizer.cs) |
| Time and Escape checks occur between optimizer steps. | A between-step budget cannot interrupt a slow individual step; design yielding/cancellation at a useful work boundary. | [step loop](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs) |
| Custom goo shares payloads on duplication and does not persist them. | Decide immutability and persistence explicitly; detect restored empty payloads and explain recovery. | [goo](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/MoyuGoo.cs) |
| Result creation clones density arrays and copies iteration history. | Publish result snapshots deliberately; do not confuse a duplicated wrapper with an independent mutable result. | [result creation](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/TwoD/SolverComponent.cs) |
| Shared preview handling supplies bounds, selection highlighting, and native-preview opt-out. | Give preview a single owner, correct clipping bounds, and cache invalidation tied to data revisions. | [component base](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/MoyuComponent.cs) |
| Example definitions are embedded and opened as new unnamed documents. | Examples must work after installation and must not be overwritten when a user saves an edited copy. | [loader](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/Examples/ExampleFiles.cs) |
| Icon extraction preserves intentional light faces and resizes premultiplied alpha into a transparent 24px canvas. | Validate actual toolbar assets on light and dark backgrounds, not just large concept art. | [exporter](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tools/make_icons.py), [design record](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/icon-prompts.md) |

## Which historical claims need their context

- [Testing notes](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/testing.md) describe Rhino.Inside crashes caused by other loaded plugins and why posted window messages do not test the actual keyboard hook. These are diagnostic observations, not grounds to disable unrelated plugins automatically.
- [Third-round report](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/third-round-report.md) records an overflowing wall-signature sum that blanked a frame and real mouse tests that exposed gumball angle/crossing issues. This supports targeted hash-boundary tests and real interaction verification, not a requirement to build games or gumballs in every plugin.
- [Contributing notes](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/contributing.md) distinguish build, core tests, icon-resource checks, real-host inspection, and release packaging. Keep those evidence levels separate when reporting completion.

## What remains product-specific

Moyu's game disguises, keyboard capture policy, language menu, numbered ribbon panels, runtime targets, numerical budgets, voxel limits, and release version are examples rather than framework requirements. Apply those patterns only when the new feature has the same need.

This case study is provenance, not an instruction to modify Moyu, copy its identity, publish packages, or change a user's Rhino installation. Each skill should operate on the user's requested project and current authorization.
