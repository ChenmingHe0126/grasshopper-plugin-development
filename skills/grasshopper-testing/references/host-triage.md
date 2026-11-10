# Host identity and crash triage

Moyu source evidence is pinned to `d1aa257523e929a6136937cb18aded4548d450a9`. Prefer inspecting the actual target installation over assuming a historical workaround is needed.

## Establish which plugin is running

Installed packages and development builds can share an assembly name and component GUIDs. A successful load or solve does not identify which copy ran.

Moyu's integration loader checks an already loaded assembly's absolute location against the requested GHA before accepting it. It refuses a mismatch instead of returning plausible results from an older installed version. Apply an equivalent identity check to the target runner.

Use a fresh host process when the loaded assembly cannot be replaced. If a build fails to replace a GHA currently locked by Rhino, do not call the old running assembly the new build. Closing a user's live Rhino session or discarding its unsaved work requires the user's applicable authorization; prefer an isolated test session when possible.

Moyu's loader uses reflection for a non-public `GH_ComponentServer.ParseGHA` entrypoint. That is a version-sensitive test-harness technique, not a stable SDK contract. Prefer a supported loading path where available and verify compatibility before reusing the reflected call.

## Separate product bugs from environment crashes

Starting GH may load third-party libraries configured in the user's installation. Moyu documented a case where a third-party finalizer missing its own native dependency killed the entire process during garbage collection.

A useful diagnostic sequence is:

1. Capture the host/runtime, loaded plugin paths and failure phase.
2. Start GH without loading or solving the plugin under test.
3. Compare with a run that loads and solves it.
4. If the crash happens during cleanup/GC, collect relevant native dependency/finalizer evidence rather than treating a passing assertion before the crash as success.
5. Restrict any dependency preload workaround to the identified library and test environment.

Moyu's `--probe-gc` harness starts GH, optionally exercises a saved test definition, then forces collection/finalizers. `MOYU_TEST_PRELOAD` is an explicit semicolon-separated list of native libraries used as a local diagnostic workaround. Do not copy a machine's DLL paths into a new skill or automatically preload arbitrary libraries for every test.

Moyu example commands:

```text
dotnet run -c Release --project tests/Moyu.RhinoTests -- --probe-gc
dotnet run -c Release --project tests/Moyu.RhinoTests -- --probe-gc --with-moyu
```

A crashed process is a failed/incomplete run even when the crash appears external. Report the diagnosis separately from the plugin behavior that was actually observed.

## Keyboard tests must reach the code path

Moyu's thread-level keyboard hook does not receive `PostMessage`-injected key messages through the same path as genuine keyboard input; the project documents that those injected messages can instead reach Rhino's command line. A unit test of `KeyTransitions` validates its state rules, not hook installation, focus routing or IME recovery.

For host UI verification, use a real input path supported by the automation environment or manual input. Confirm the foreground/focus owner immediately before sending keys and stop when another application owns focus. Do not steal the user's foreground window merely to finish an automated check.

Verify that releases still clear held state when shortcuts pass through or focus changes. Include a release under Ctrl/Alt and a lost-release recovery scenario if that behavior changed.

## Source evidence

- [Canvas.LoadPlugin](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Canvas.cs): already-loaded path guard and version-sensitive reflection.
- [Probe.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.RhinoTests/Probe.cs) and [testing.md](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/testing.md): third-party/finalizer crash triage and native preloads.
- [TestsKeys.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tests/Moyu.Core.Tests/TestsKeys.cs): duplicate notifications, IME flags, lost releases and modifiers.
- [KeyboardHook.cs](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Games/Common/KeyboardHook.cs): hook installation and input path.
- [contributing.md](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/contributing.md) and [game-workflow.md](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/game-workflow.md): historical UI test workflow. Treat the original project's game/style/publishing preferences as product-specific.
