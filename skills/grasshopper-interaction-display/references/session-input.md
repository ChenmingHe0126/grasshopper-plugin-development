# Session lifetime, scheduling and input

These patterns were inspected in Moyu at commit `d1aa257523e929a6136937cb18aded4548d450a9`. They are implementation evidence, not a promise that the same API signature or Windows mechanism fits every Rhino release.

## Keep two clocks separate

Moyu's numerical solver advances a bounded number of iterations per GH solution; its interactive viewport sessions use a WinForms UI-thread timer outside the GH solution loop. This keeps a frame from triggering arbitrary downstream recomputation.

- Decide whether the product needs a solved-data update, a viewport redraw, or both.
- Measure elapsed time rather than assuming the requested timer interval was achieved. Moyu clamps a stalled frame's delta to 0.1 seconds; that is a product choice, not a universal time step.
- Catch callback failures at the timer/input boundary, stop the session and surface a useful message. A timer exception must not escape into the host's message pump.
- In `MassingStudyComponent.OnSessionChanged`, session results are copied into output state, the canvas is redrawn, and a delayed `ScheduleSolution` expires the component. The heavy downstream solve therefore does not delay the immediate state transition. This demonstrates deferral, not a complete stale-callback guard: inside a newly scheduled callback, re-check the captured document, component membership, closing state and session generation before expiring or publishing.
- Drawing should not advance the simulation: different viewport passes or redraw rates would otherwise change the result.

For a new implementation, select the scheduler and threading model supported by the target Rhino/GH version. Do not access the Rhino document or WinForms UI from an arbitrary worker thread.

## Give the session an explicit owner

Moyu captures the Rhino document, view, viewport ID and starting view settings at startup. Its conduit checks the viewport ID before drawing. It uses transient display geometry rather than adding objects to the Rhino document each frame.

Useful lifecycle:

1. Validate settings and obtain a usable view before capturing input.
2. Record only the state the session will change: camera/projection, viewport flags, maximized view, active layout/view.
3. Install display/input/timer resources with rollback if any installation fails.
4. On owner removal, GH document close/unload, Rhino document close or application shutdown, stop.
5. Stop once: disable the conduit, release native caches, dispose timer and hook, detach handlers, and restore the recorded view if it still exists.

The lifecycle above is a recommendation, not proof that the snapshot handles every startup failure. In the inspected GameSession.Begin, conduit enablement and hook construction precede the protected try block. A new implementation should protect all resource acquisition and roll back any partial startup, including exceptions at those earlier steps.

Moyu sets its `Stopped` flag before disposing, so callbacks cannot re-enter normal work during cleanup. On GH tab unload it stops the owned session, then expires stale output state without immediately solving the disabled document. A resumed tab can recompute normally.

Moyu allows one current session across its tools. A multi-session plugin should instead key sessions by the appropriate document/owner and explicitly arbitrate shared view/input ownership.

## Treat focus and key state as separate questions

Moyu's Windows hook is attached to Rhino's UI thread, not a system-wide keyboard logger. Its handler distinguishes:

- **Notification:** the OS reported a key message, possibly a duplicate or repeat.
- **Action:** the transition should modify state once.
- **Consumption:** this message should or should not reach Rhino.

The hook stores its delegate in a field so native callbacks cannot outlive a collected delegate. It is uninstalled on stop. These details matter only if a native hook is genuinely necessary.

The session takes ordinary input only while its Rhino main window or floating viewport owns focus. GH editor controls, dialogs, commands and Ctrl/Alt shortcuts retain their keys. Nevertheless a key-up that passes through still clears a previously held movement or modifier state. Otherwise the interaction can remain stuck after a shortcut or focus change.

Moyu also tests:

- duplicate notifications and auto-repeat;
- an IME marking a new press as already down;
- scan-code recovery for IME-owned keys;
- left/right modifier normalization;
- losing a release during focus loss;
- releasing modifiers while passing a shortcut through.

Reset held state when a pause/focus transition invalidates it. Avoid resetting a hook indiscriminately on the same key's toggle: Moyu keeps repeat knowledge when its own toggle key caused the transition, so a held key does not immediately toggle back.

The boss/disguise mode is specific to Moyu's product. Reuse its atomic transition and cleanup lessons, not its requirement to hide a game in every plugin.

## Keep native display allocations bounded

`GameConduit` caches sprites, meshes and materials, limits cache growth, and releases them when the session ends. HUD coordinates use a DPI-aware scale capped by available frame height; the 3D scene is not scaled with HUD text.

For a new preview:

- Filter all relevant display/bounding-box callbacks to the owner viewport.
- Rebuild caches when geometry, size, language or theme changes, rather than allocating per primitive per frame.
- Dispose old native resources when replacing a cache entry or ending the session.
- Check real viewport captures and resizing; headless geometry output does not prove text, DPI or depth behavior.

## Source evidence

Pinned source links:

- [GameClock.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/GameClock.cs): UI-thread timer, elapsed time, stalled-frame clamp and callback error boundary.
- [GameSession.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/GameSession.cs): ownership, focus, partially guarded startup, stop, view restoration and state transitions.
- [KeyboardHook.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/KeyboardHook.cs) and [KeyTransitions.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/Core/KeyTransitions.cs): platform hook, deduplication and modifier handling.
- [GameConduit.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/GameConduit.cs): viewport filtering, HUD scale and disposable caches.
- [MassingStudyComponent.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/Massing/MassingStudyComponent.cs): deferred output refresh and GH document lifecycle.
- [SolverComponentBase.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Components/SolverComponentBase.cs): bounded numerical work per GH solve.
