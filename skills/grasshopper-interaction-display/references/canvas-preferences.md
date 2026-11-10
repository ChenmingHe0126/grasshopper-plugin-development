# Canvas controls and persisted preferences

Moyu evidence below is pinned to commit `d1aa257523e929a6136937cb18aded4548d450a9`.

## A button is part of the component's layout

In `RunButtonAttributes`:

- Call the base layout, calculate the button rectangle from the component bounds, then extend the bounds to contain the button.
- Render the control in the intended GH canvas channel. Reuse GH's capsule visual states for selected and locked components.
- Hit-test in canvas coordinates, handle only the intended mouse button, and return a handled response only for the control itself.
- A locked component should not start using settings that never solved or are stale. Moyu still permits its Stop action while locked.
- Refresh the canvas after the action so the visible Run/Stop state follows actual session ownership.

Do not copy Moyu's exact pixel dimensions as a universal standard. Check the target application's zoom/DPI behavior, port locations and neighboring objects. A visually placed button whose extended bounds were never registered will break layout and hit testing.

## Menu preferences are document state

A right-click preference need not become an extra input wire. In Moyu the language menu replaced a short-lived input port because it is a UI preference, while geometry and solve parameters remain data inputs.

For a document-owned setting:

1. Record an undo event before changing the value.
2. Mark the GH document modified even if the UI-only change causes no solve.
3. Update the live display/session if this component owns one.
4. Serialize a stable code, not the localized display label.
5. In `Read`, use a sensible default when the key is absent or unknown.
6. Apply restored state to the live session when undo/redo deserializes the owning component.

Moyu represents Auto as a nullable language choice and stores `auto`, `ch` or `en`. Resolving Auto to the system language is a runtime decision; saving the resolved language would silently stop following the system.

The languages offered, the default and which screens are translated are product decisions. Moyu's English-only disguise screens are not a generic localization rule.

## Migrate old definitions without pretending wires survived

Moyu reads a known old persistent Language input chunk only when the new menu key is absent. It accepts a recognizable unwired value; if the old value came through a wire that the removed port no longer preserves, it reports that limitation and falls back. Malformed legacy chunks do not prevent the definition opening.

When evolving a real component:

- Inspect the old persisted shape before writing migration code.
- Keep migration narrow to the known schema/version.
- Preserve stable component identities and normal base-class serialization.
- Test a fresh file, a file from before the setting existed, a known legacy value, malformed/unknown data, and undo/redo of the new setting.
- Do not infer successful migration solely because the file opens; check the restored setting and observable output.

## Source evidence

- [RunButtonAttributes.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/RunButtonAttributes.cs): layout, render channel, hit testing and lock-state behavior.
- [GameComponent.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/GameComponent.cs): menu, undo, modified document, live language update, serialization and old-input migration.
- [UiLanguage.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/Core/UiLanguage.cs): stable codes and parsing.
- [TestsLanguage.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.Core.Tests/TestsLanguage.cs): accepted aliases, rejected values and code round trips.
