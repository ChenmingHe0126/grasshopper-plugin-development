# Repository guidance

This is a collection of independently installable Grasshopper development skills.

- Keep each skill self-contained. Runtime references and helper scripts belong inside that skill directory; root docs may provide optional provenance and maintenance information.
- Distinguish framework requirements, observed Moyu behavior, project conventions, and recommendations. Do not turn one failure or one user's palette into an unconditional rule.
- Link primary sources or pin Moyu source links to the inspected commit. Recheck current Rhino/runtime documentation before prescribing new target frameworks.
- Preserve the user's actual scope: adding an icon does not authorize changing component IDs; preparing a package does not itself authorize publishing it.
- Do not include credentials, private transcripts, machine-specific user paths, build outputs, or copied brand assets.
- Keep entrypoints concise. Put substantial procedures in linked references. Do not require all skills to be installed together.
- Test observable behavior of helper scripts. State what validation does and does not establish.
- Before publishing changes, run the repository validator and relevant helper tests. Keep the GitHub workflow consistent with these commands.
