# Moyu patterns worth reusing

Read this when a component becomes stateful, produces custom data, previews geometry, or ships example definitions. These are patterns observed in Moyu, not requirements for every Grasshopper plugin.

Evidence snapshot: Moyu commit `d1aa257523e929a6136937cb18aded4548d450a9`. Source links below pin that snapshot; re-check current source before copying an implementation.

## Keep rules outside the host adapter

Moyu puts numerical algorithms in `Core/` and game rules in `Games/<mode>/Core/`. Their test runner compiles those files without Rhino or Grasshopper references. Rhino geometry conversion, viewport drawing, component wiring, input ownership, and document lifecycle live in adapters.

Use the same separation when a rule can be expressed with plain values. A separate class library is another valid arrangement; Moyu's linked-source test project is a local convention, not a required project layout. Avoid extracting a framework before a second real consumer exists.

Evidence: [core test project](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.Core.Tests/Moyu.Core.Tests.csproj), [optimizer](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Core/SimpOptimizer.cs).

## Specify continuation, reset, and invalidation separately

Moyu's solver persists optimizer state across GH solutions. On a compatible grid it updates loads, supports, passive regions, and settings while carrying densities forward; Reset creates a fresh optimizer. A grid change requires a new optimizer. Changing the problem resets convergence and its iteration budget without necessarily discarding the design.

Before implementing a stateful component, decide:

- Which inputs change only presentation?
- Which inputs can update the current state?
- Which changes invalidate topology, dimensions, caches, or initialization?
- What does an explicit Reset do?
- What happens while required inputs are missing or invalid?

Test transitions, not just a successful first run. Do not retain a previous success label when current outputs are empty.

Evidence: [solver adapter](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs), [optimizer update](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Core/SimpOptimizer.cs).

## Budget work at a boundary that can actually yield

Moyu advances a bounded number of optimizer steps per solution and checks elapsed time and Escape between steps. Its 1.5-second budget and 50-step limit are product choices. The implementation always permits the first step, so the budget is not a hard upper bound on solution duration: a single expensive step can overrun it.

For a new workload, measure the largest individual unit of work. Subdivide or choose a cancellable worker/session architecture if one unit already blocks too long. Do not describe a between-step check as preemptive cancellation. The timer, custom run button, and background-worker models solve different problems; choose for the actual interaction.

Evidence: [step loop and budget](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs).

## Treat published results as snapshots

Moyu clones optimizer density arrays and copies history when creating a result. Result objects are described as immutable snapshots, but their public fields are not language-enforced immutable. `MoyuGoo<T>.Duplicate()` shares the same payload reference.

Therefore, copying a wrapper does not make its payload safe to mutate. Either enforce immutability, create a real deep copy where mutation is expected, or document and test the shared-ownership contract. Cache visualization by data revision and relevant object identity; do not invalidate only on counts or dimensions when values can change.

Evidence: [2D result creation](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/TwoD/SolverComponent.cs), [result type](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/TwoD/Result2D.cs), [goo wrapper](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/MoyuGoo.cs).

## Give preview geometry an explicit owner

Moyu's shared component base discovers output payloads implementing its preview interface, unions their bounds into the clipping box, and draws them with selection highlighting. Components with ordinary geometry outputs opt back into native GH preview.

For a new component, decide whether the component, its output goo, or a session conduit owns the preview. Avoid duplicate drawing. Keep the clipping bounds consistent with what is actually drawn, and avoid rebuilding expensive geometry in every display callback. Copy input geometry before modifying it.

Moyu isolates exceptions in its preview loop to keep drawing failures from breaking the canvas. That is not a reason to hide failures in solving or parsing; retain useful diagnostics at the appropriate boundary.

Evidence: [component preview base](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/MoyuComponent.cs), [geometry conversion](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/ThreeD/Inputs3D.cs).

## Make shipped examples independent of the installation path

Moyu embeds its example `.gh` files and loads them into new unnamed documents. The launcher opens an editable copy without giving it the shipped example's file path. This avoids assuming a source checkout exists after installation and avoids overwriting the original example when a user saves.

Verify resource names, deserialization, missing-resource diagnostics, and opening in a new tab. Resource existence is not evidence that an example solves correctly; run the opened definition too.

Evidence: [embedded example loader](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/Examples/ExampleFiles.cs).

## Separate observation from recommendation

The code evidence above was inspected during skill extraction. This extraction did not rerun Moyu's build, numerical tests, Rhino.Inside tests, or interactive sessions. Historical reports describe their own runs, not verification performed by this skill repository. Product-specific limits, keyboard capture, game disguise modes, panel numbering, and target framework versions should not become defaults for unrelated plugins.
