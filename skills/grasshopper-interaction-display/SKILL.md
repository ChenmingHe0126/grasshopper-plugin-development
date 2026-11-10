---
name: grasshopper-interaction-display
description: Build or debug Grasshopper canvas controls, Rhino viewport previews, interactive sessions, keyboard or mouse handling, and persisted display preferences. Use for host-integrated interaction rather than standalone application or game development.
---

# Grasshopper interaction and display

Implement the interaction in the correct host layer: component attributes for GH canvas controls, a document-owned session for long-lived work, and preview/display callbacks for drawing. Keep computation and input-state rules separately testable.

Read only the reference needed for the change:

- [Session lifetime, scheduling, focus and input](references/session-input.md): continuous previews, animation, keyboard capture, viewport takeover or cleanup.
- [Canvas controls and persisted preferences](references/canvas-preferences.md): Run buttons, menu settings, localization, undo, serialization and migration.

## Choose the update path

- A GH solve computes and publishes data. Bound expensive work per solve or use an appropriate cancellable background design for the target API; an endless loop in `SolveInstance` blocks the host.
- A UI-thread frame callback can update an interactive preview without recomputing the entire GH graph. Use elapsed time, account for stalls, and redraw only the owning view.
- If a session changes component outputs, queue the GH recomputation after the callback rather than recursively solving in the drawing or input callback. Confirm the owner and document are still alive when the queued work runs.
- Keep display callbacks observational: prepare expensive geometry outside the drawing path and reuse/dispose cached native display resources.

## Preserve host ownership

Capture the document, viewport and owner when a session starts. Scope drawing and input to them. Let dialogs, Rhino commands and other documents retain their own interaction. Make startup failure and stop both release resources; make repeated stop calls harmless.

A global single-session manager was useful in Moyu. Use that only when the product calls for one active session; it is not a Grasshopper requirement.

Separate key transitions from key consumption. A key that must pass through to Rhino may still need to release held interaction state. Prefer host events for ordinary shortcuts; install a platform-specific hook only when the required behavior needs it.

## Verify the changed behavior

Check the concrete transition affected by the change, including cancellation or owner removal. For viewport sessions, include another viewport/document, focus loss, command/dialog focus, and the original view after stopping. For settings, include save/reopen and undo/redo, not just live display.

Report the host/runtime tested and distinguish a headless data check from a real canvas or viewport check.
