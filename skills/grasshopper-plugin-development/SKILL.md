---
name: grasshopper-plugin-development
description: Develop or revise C# Grasshopper plug-ins for Rhino, including component contracts, custom data, state and persistence. Use for new components, architecture changes, or diagnosing host integration; use the focused icon, interaction, testing, or release skills for those specific tasks.
---

# Grasshopper plug-in development

Build the requested behavior in the existing plug-in's conventions. Inspect the repository before choosing a project layout, target framework, dependency version, or loading strategy.

## Establish the component contract

Read [component-contracts.md](references/component-contracts.md) when adding or changing parameters, custom data, persistent state, or component identity. Establish:

- The actual Rhino version, OS, selected .NET runtime, project target frameworks, and SDK references.
- Which existing component is the closest host-integration example.
- Inputs and outputs, units, item/list/tree access, empty and invalid-data behavior, and when state continues, invalidates, or resets.
- Component and assembly identities, archived definitions that must keep loading, and resource naming.

For internalised custom values, read [custom Goo persistence](references/custom-goo-persistence.md) before choosing archive ownership and schema.

Keep released component GUIDs stable. Changes to parameter order/types or serialization keys require a compatibility decision and a save/reopen check, not just a successful compile.

## Separate computation from the host

Use [Moyu patterns](references/moyu-patterns.md) for source-inspected examples and their limitations.

Keep algorithms and simulation state independent of Rhino when that improves testability. Let components own input translation and published outputs; let session/display adapters own host callbacks and their lifetime. A stateless component does not need a session abstraction.

For iterative computation, establish invalidation and ownership before adding a timer. Bound work where it can actually be interrupted. A wall-clock check between iterations cannot interrupt one long iteration.

Do not expose mutable solver buffers as historical results. Decide whether custom Goo duplicates own their data and whether internalised values can survive archive loading. Shared references and immutable-by-convention snapshots need explicit treatment.

## Route only the work needed

The following are independently usable companion skills in this collection:

- `grasshopper-interaction-display`: custom GH attributes, Rhino display, input, focus, live sessions, DPI, language, and UI persistence.
- `grasshopper-testing`: core tests, host integration, document round trips, and actual UI acceptance.
- `grasshopper-build-release`: runtime matrix, resources, packaging, and release evidence.
- `grasshopper-icons`: function-first icon families and real 24px export.

If a companion skill is unavailable, inspect the project's own implementation and authoritative SDK documentation; do not pretend it was loaded or block unrelated work.

## Complete with evidence

Run validation appropriate to what changed. Report the resulting behavior, the artifacts changed, the checks actually executed, and any remaining host-only verification. Preserve the user's existing authorization and scope when installing, publishing, or modifying other applications.
