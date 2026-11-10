# Persisting custom Goo without losing the value

Read this for internalised custom data, duplicate/copy behavior, or migration of saved definitions.

## Choose what is durable

A component's settings and its output payload are different archive owners. Serializing a Run toggle in the component does not serialize an internalised result in a parameter. Keep transient resources (timers, hooks, conduits, native display caches and live document references) out of the durable payload; reconstruct those through the appropriate lifecycle.

If a result intentionally must be recomputed, represent that state explicitly and provide recovery guidance. Do not deserialize to an apparently valid wrapper holding an empty payload.

## Implement an explicit schema

The default `GH_Goo<T>.Write(GH_IWriter)` and `Read(GH_IReader)` return success without saving your custom payload. Override the appropriate methods in the actual custom type; implementing `Duplicate()` does not add persistence. The base copy constructor also does not deep-copy a reference-type payload. See the [official Goo API](https://developer.rhino3d.com/api/gh1/type/grasshopper.kernel.types.gh-goo-1/).

For a type that should survive internalisation:

1. Decide which fields reconstruct a valid value, including units, dimensions and array lengths. Use a small named chunk or stable keys for this payload and a schema-version field.
2. Write primitives and structured chunks using the SDK's writer methods; do not assume an arbitrary C# object or a wrapper is serialized automatically.
3. Read into temporary local values. Use existence checks or the reader's typed TryGet methods where optional/legacy fields are expected. Validate lengths, numeric ranges, finite values, and count/resource limits before allocating or publishing the result.
4. Define handling for missing schema keys, old schemas and unsupported future versions. Missing data must not silently retain a previous unrelated payload. Assign the reconstructed value only after it passes validation.
5. Preserve any relevant base-type serialization contract. Report failures at the owning component/parameter or archive-log boundary rather than quietly returning success with corrupt data.

The [writer API](https://developer.rhino3d.com/api/grasshopper/html/Methods_T_GH_IO_Serialization_GH_IWriter.htm) provides typed values and child chunks. The [reader API](https://developer.rhino3d.com/api/grasshopper/html/Methods_T_GH_IO_Serialization_GH_IReader.htm) provides corresponding reads and existence/TryGet methods. Match overloads to the installed SDK; these notes are not a compiled C# implementation.

## Prove the archive path

Check two layers when persistence is part of the change:

- Exercise write/read on a fresh instance and compare the meaningful fields, including an empty value, a representative nonempty value, malformed counts, missing legacy keys, and an unsupported schema version.
- In the actual supported GH host, put the value in the intended persistent parameter, internalise it, save a definition, close and reopen it, then solve a downstream consumer. Confirm the value survives rather than being recomputed by an upstream component.

Separately test duplication: mutate a duplicated value if mutation is allowed and check whether it affects the original according to the ownership contract. Timers and viewport sessions must not be duplicated or revived merely by reading the document.

Moyu's inspected wrapper shares its payload on duplication and does not implement payload persistence. That is a limitation of that implementation, not a general inability of Grasshopper to archive custom data. See [Moyu patterns](moyu-patterns.md) for the source-inspected evidence.
