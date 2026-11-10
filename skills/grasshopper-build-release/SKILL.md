---
name: grasshopper-build-release
description: Build, package, or prepare releases of Rhino Grasshopper C# plug-ins. Use for target-runtime compatibility, embedded resources, locked or stale assemblies, version agreement, Yak distributions, dependency layout, and installation checks.
---

# Grasshopper build and release

Read [release workflow](references/release-workflow.md) for the relevant build, packaging, and installation steps. [Sources](references/sources.md) distinguishes the Moyu snapshot from current official guidance.

## Resolve the host before changing targets

Inspect the actual Rhino build, OS, active runtime, installed SDK, project targets, and managed/native dependencies. Moyu's historical `net7.0-windows;net7.0;net48` is evidence, not a template for a new plug-in. Check the current McNeel runtime guide when proposing targets.

Treat Windows APIs, WinForms, native libraries, and display behavior as platform constraints. Successfully compiling another target does not establish Mac support.

## Make build and package provenance explicit

- Use the project's authoritative version and propagate it into assembly information, manifest, package filename, installation notes, and release page.
- Verify which assembly path the test host actually loaded. Rebuild after changing resources or versions; a successful `--no-build` invocation can package an old binary.
- Account for Rhino/Hops holding the loaded assembly open. Do not terminate or discard an active user's document merely to clear a file lock; use a fresh output directory or arrange a normal restart.
- Exclude Rhino/Grasshopper host assemblies from normal dependency copying; include the plug-in's required managed/native dependencies with the appropriate platform/runtime layout.
- Inspect final archive contents rather than trusting the staging directory.

## Use the offline inspector when it helps

`scripts/inspect_package.py` checks a built Yak/ZIP archive's required members, Yak manifest fields/version, accidental SDK DLLs, duplicate/unsafe member names, and explicitly supplied private markers. It prints the archive hash and observed contents.

```text
python scripts/inspect_package.py package.yak --yak --expect-name myplugin --expect-version 1.2.3 --require net8.0/MyPlugin.gha --require LICENSE.txt
```

Run the script relative to this skill's directory, or use its absolute path. It requires PyYAML for Yak manifest parsing. It never starts Rhino, reads assembly metadata, runs Yak, publishes a release, or proves runtime compatibility.

## Release evidence and scope

State separately what built, what was inspected, what loaded in a matching host, and what was manually exercised. A package may be prepared before publication is authorized. If the user already requested publication, honor that authorization without inventing another confirmation step.

A Yak build does not establish server acceptance. Inspect the actual server response. Do not repeatedly push an already-published version; use a new version for changed content.
