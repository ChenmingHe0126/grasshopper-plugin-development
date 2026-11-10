# Component contracts and custom data

Use this reference when adding or changing GH inputs, outputs, state, serialization, or result ownership.

## Write the wire contract before implementing the solve

For each input, state its data type, item/list/tree access, required/optional status, units or coordinate frame, accepted range, and missing-value behavior. For each output, state its type and ownership, whether it is a snapshot or live state, and which operation makes it stale.

Preserve existing component GUIDs and inspect saved-definition compatibility before changing parameter order or meaning. A new display name is different from a new component identity. Record intentional breaking changes and provide a migration path when existing definitions must continue to work.

A persistent component can be called more than once in one GH solution because of data matching. Decide whether it supports that. Moyu's solver explicitly rejects `DA.Iteration > 0` because one component owns one mutable optimizer. This guard is appropriate to that ownership model; do not apply it to a stateless component intended to process every matched item.

Evidence: [solver parameter registration and iteration guard](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs), [stable concrete component identity](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/TwoD/SolverComponent.cs).

## Empty, wrong type, and invalid saved data are different cases

An optional unconnected input can use a documented default. A connected value of the wrong type should not silently select that default. A wrapper restored from a file with no payload should explain how to recover it.

Moyu centralizes unwrapping from raw payloads, its own goo, and compatible `IGH_Goo.ScriptVariable()` values. Its material input uses the default only when empty; a wired incompatible value produces an error.

Moyu's generic goo does not serialize its payload. Internalising such a value can save the wrapper but reload an empty payload. Its diagnostic tells the user to reconnect the producer. This is a known limitation of that wrapper, not a general Grasshopper restriction.

Choose the new type's actual persistence behavior:

- Implement and test an appropriate round-trip when internalisation is part of the feature.
- Otherwise, make unsupported persistence explicit and provide an actionable recovery message.
- Do not claim that a value round-trips merely because its wrapper appears in the saved file.

Evidence: [goo behavior](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/MoyuGoo.cs), [shared diagnostics](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/MoyuComponent.cs), [optional material validation](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/TwoD/SolverComponent.cs).

## Validate before the expensive allocation

Check geometry validity and closure/planarity where those are semantic requirements; reject empty or degenerate results after conversion too. Validate finiteness before range clamping: NaN does not behave like an ordinary out-of-range number. Explain the corrective action using the user's input names.

Moyu's solver substitutes documented defaults for non-finite numerical settings, warns about clamping, and catches specific resource/solver failures at the component boundary. Its domain builder rejects open curves, nonplanar boundaries, zero area, and a resolution producing no inside cells.

Fallback versus rejection is a product decision. For geometric dimensions, file paths, or structural inputs where a fallback could hide a serious mistake, prefer an explicit rejection. Do not copy Moyu's exact limits to a different algorithm without measuring it.

Evidence: [numeric checks and runtime messages](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs), [domain builder](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/TwoD/PixelDomain2D.cs).

## Make coordinate and geometry ownership visible

Moyu's 2D domain stores its plane and cell size, with named world-to-grid and grid-to-world conversions. It distinguishes grid corners from cell-center sampling and stores density in row-major order. That explicit contract prevents previews, conditions, and algorithms from each inventing their own coordinate convention.

For a new data type, document axis order, indexing, units, origin, sampling position, and transform direction when relevant. Copy Rhino curves/meshes before mutation; sharing a reference is appropriate only with a deliberate read-only contract. A preview mesh cache is not automatically an editable output mesh.

Evidence: [2D coordinate mapping](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/TwoD/PixelDomain2D.cs), [input mesh/curve duplication](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/ThreeD/Inputs3D.cs).

## Test the boundary that changed

For a changed contract, choose the smallest meaningful checks: missing input, incompatible goo, null restored payload, non-finite settings, changed topology, repeated matched calls, snapshot independence, and save/reopen when supported. Select cases relevant to the actual change rather than making every task run a universal checklist.

Use separate evidence labels for pure core behavior, GH document execution, and visible Rhino interaction. A successful build does not verify the wire contract, and a headless solution does not verify focus or viewport appearance.
