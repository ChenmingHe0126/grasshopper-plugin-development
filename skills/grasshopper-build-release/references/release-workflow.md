# Build and release workflow

Read the parts relevant to the task; this is not a requirement to publish whenever code changes.

## Runtime and project configuration

Inspect the actual host before choosing a target. The current McNeel guide differentiates Rhino 8's .NET 8 runtime from Rhino 9's .NET 10 direction, while allowing specific legacy configurations. Recheck it for the exact release being supported.

Moyu's inspected project targets net7.0-windows, net7.0, and net48. That captures its compatibility history. Its own documentation says Windows only and Mac untested; the presence of a net7.0 target does not establish cross-platform support.

Relevant Moyu project choices:

- A .gha target extension and dynamic loading support.
- A Grasshopper package reference with runtime assets excluded, so the host supplies its own SDK assemblies.
- Explicit icon/example EmbeddedResource logical names.
- One Version property read back by assembly information and packaging.
- Deterministic build paths mapped away from the developer's own directory.
- A user-local overridable Rhino executable setting rather than committing a personal path.

Adapt these choices to the current SDK/template and actual platform. Do not blindly copy all warning suppressions or enable optimization in every project because Moyu does.

## Loaded and stale assemblies

A normal rebuild may fail because Rhino or a compute/Hops process still holds a .gha. Distinguish this output-copy failure from compilation failure. Preserve the live document and use the project's restart or isolated-output workflow.

A test can load an older installed assembly even after building another one. Log assembly location and version in the host runner; reject a mismatch before attributing results to the current change. Replacing a resource file or icon may require restarting the process because caches retain the old resource.

## Version agreement

Moyu's packaging script rejects a .gha whose ProductVersion disagrees with the project Version, ignoring build metadata after '+'. It also rejects a conflicting Yak content-version warning even when the Yak process exits successfully.

The reusable lesson is to compare the actual binary version to the intended release, not merely the existence or timestamp of a Release folder. Choose an inspection method suited to the host OS or .NET metadata tools. The bundled archive inspector does not read .NET assembly versions.

## Staging and archive content

Build in a dedicated staging directory containing only intended payload. The official Yak CLI packages its directory contents; an unrelated log or development binary may otherwise ship.

Agree on a manifest and expected file list before packaging:

- Plug-in assembly per supported runtime and its required dependencies.
- Root manifest and package icon.
- License and concise installation instructions.
- Examples and documentation when they are part of the intended distribution.

Moyu packages runtime-specific assemblies, examples, and guides, then produces SHA-256 checksums and inspects the ZIP/Yak members. It treats already-published versions as immutable.

For paths or private markers, scan the actual distributed bytes, including text encodings used by metadata and example files. A source-path mapping alone does not remove arbitrary user paths in documentation or embedded data.

## Manifest and platform

Use the actual SDK references and support policy to choose the distribution tag. A plain managed target does not mean platform 'any' if the plug-in calls Windows APIs.

Moyu observed server rejection of malformed keywords that local Yak build did not reject; its package script checks those keywords, including the GUID keyword used by Grasshopper restore. Verify current server requirements and preserve the real plug-in GUID. Never reuse Moyu's GUID or package name.

## Acceptance and publication

Inspect the final package, install it in the intended host/runtime, open a representative definition, and verify resources and dependencies when those checks are within the task's scope. On a limited machine, report missing host checks explicitly.

Keep publication distinct from preparation; authorization comes from the user's task. Respect an explicit publication request, and do not assume that ordinary 'build this' work authorizes a public release.
