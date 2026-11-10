# Verification layers and saved GH fixtures

This reference extracts source-inspected patterns from Moyu commit `d1aa257523e929a6136937cb18aded4548d450a9`. The commands are Moyu examples; adapt paths, frameworks and options to the plugin under test.

## 1. Host-free computation

Moyu's `Moyu.Core.Tests` executable compiles the same core algorithm, simulation and parser source files as the plugin without Rhino dependencies. A nonzero exit code reports failed assertions. It includes analytical patch tests, solver comparisons, contours/surfaces, live input changes, size guards, deterministic simulation and parser/input transitions.

Useful invariants depend on the change:

- compare an element/solver against an analytical case or trusted independent method;
- verify contour closure or mesh topology with explicit geometry checks;
- run invalid/nonfinite inputs through the recovery path and observe a valid later state;
- replay the same seed/input sequence and check state;
- test press/release/auto-repeat/IME transitions without installing an OS hook;
- round-trip persisted setting codes independently of UI labels.

Moyu example:

```text
dotnet run -c Release --project tests/Moyu.Core.Tests
```

This runner is a custom executable, not an xUnit/NUnit project; replacing `run` with `test` would not mean its assertions ran. Use the actual test entrypoint discovered in the target repository. Source-linking the core into a runner is Moyu's arrangement, not a requirement for other plugins.

## 2. Rhino/GH integration

Moyu initializes the Rhino.Inside resolver before touching RhinoCommon or Grasshopper types, enters through an STA main thread, and starts an in-process Rhino core with no window. It then loads actual GH components, wires a document, sets persistent inputs and runs solutions.

Moyu example:

```text
dotnet build src/Moyu/Moyu.csproj -c Release
dotnet run -c Release --project tests/Moyu.RhinoTests
```

Its runner requires a licensed installed Rhino and a compatible build. The bootstrap and runtime flags are tied to that target; check the target SDK/runtime before reusing them. Moyu's historical target frameworks are not defaults for new plugins: use the installed host and the [Rhino runtime migration guide](https://developer.rhino3d.com/guides/rhinocommon/moving-to-dotnet-core/) to select compatible test/build targets.

Observe behavior through outputs and runtime messages:

- incorrect input should produce the intended warning/error without a host crash;
- a solver's Run-off state should remain idle;
- a deliberate expiration plus new solution should advance work;
- changing inputs should invalidate/rebuild the appropriate state;
- reset should restore initial conditions;
- bounded ticking should reach the expected termination or convergence state.

Moyu's `Canvas.Tick` expires the target with `ExpireSolution(false)`, then calls `doc.NewSolution(false)`; it simulates GH Timer-driven recomputation without requiring a visible canvas.

The inspected harness enables the process-wide `GH_Document.EnableSolutions` state and uses the shared component server; interactive code also has `GameSession.Current`. Those fixtures are not automatically isolated just because each creates a new GH document. Tests that mutate such host-wide state should restore it and stop owned sessions, or run in separate host processes. Avoid parallelizing those cases inside one host unless isolation is deliberate.

Resource checks may load and inspect icons or embedded examples through the actual assembly. Moyu's embedded example scenario compares loaded resource bytes with packaged source examples, detecting stale embedded content. Loading a resource does not prove that its UI appearance is correct.

## 3. Save/reopen definitions

A fixture that worked in memory can still save broken wiring or external references. Moyu's fixture generators build documents with native GH inputs, save them and reopen them for verification.

Check the persisted artifact rather than only the object graph used to create it:

- expected component GUIDs and counts;
- relevant wire/source connections and Timer targets;
- saved Run toggles off and an idle initial state where the example is meant to open safely;
- no unexpected warnings/errors after reopening and solving;
- actual progress after toggling Run and deliberately ticking;
- no overlapping component bounds or groups when layout is part of the deliverable.

Use the actual product's expected startup behavior; do not force every interactive tool to have a Run toggle.

Internalize example geometry or generate it from GH-native geometry components when the file must travel independently of a Rhino document. Referenced Rhino object IDs are not the underlying geometry and may fail in another document.

For settings/schema changes, include old and new files, not just a same-version round trip. Assert the restored value and its effect. Moyu's language parser unit tests cover text codes; full document migration and live UI still need their own appropriate checks.

## 4. Interactive acceptance

Headless tests do not contain a real game viewport in Moyu. Its `Render.cs` and `Render3D.cs` draw geometry outputs with GDI/software rendering. Label those artifacts accordingly.

Use a real Rhino/GH session for the changed UI path:

- Run/Stop or custom control hit testing at relevant zoom/DPI;
- viewport selection and drawing isolation;
- main versus floating viewport, GH canvas, dialogs and Rhino commands;
- pause, resume, focus loss, key-up and modifier release;
- actual keyboard path and an input method where supported;
- owner removal, GH tab unload/close, Rhino document close and repeated stop;
- restored camera/view state and absence of leaked conduits/hooks.

Scope the checks to the changed behavior. A localized setting change does not justify rerunning every physics benchmark; a display-only edit does need visual evidence that a core test cannot provide.

## Source evidence

- [Core runner project](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.Core.Tests/Moyu.Core.Tests.csproj), [Program.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.Core.Tests/Program.cs): host-free linked sources and actual test entrypoint.
- [Rhino runner Program.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Program.cs): resolver, STA, startup and prerequisite behavior.
- [Canvas.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Canvas.cs): load, wire, expire, solve and inspect.
- [Scenarios.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Scenarios.cs), [Scenarios3D.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Scenarios3D.cs): component/error and geometry scenarios.
- [GhBuilder.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/GhBuilder.cs): reopen checks, layout, idle state and simulated Timer ticks.
- [Render.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Render.cs), [Render3D.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Render3D.cs): software-rendered, not viewport-captured images.
