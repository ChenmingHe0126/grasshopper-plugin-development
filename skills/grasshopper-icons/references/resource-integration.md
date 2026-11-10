# Connect an approved icon to Grasshopper

Inspect the existing project before changing resources. Keep draft masters and contact sheets outside production resources unless the repository explicitly tracks them.

Grasshopper's component `Icon` property supplies a 24×24 bitmap, and Grasshopper caches the result. See the official [GH_Component API](https://developer.rhino3d.com/api/gh1/type/grasshopper.kernel.gh-component/) and [Simple Component guide](https://developer.rhino3d.com/guides/grasshopper/simple-component/).

## Follow the repository's mechanism

Common mechanisms are generated `.resx` properties and assembly-embedded PNGs. Use the one already present instead of introducing a new loader.

For a generated resource, the component typically returns the existing strongly typed bitmap property:

```csharp
protected override System.Drawing.Bitmap Icon
{
    get { return Properties.Resources.ImportGeometry24; }
}
```

The resource namespace and property above are illustrative. Find the actual generated type and key; do not assume a plugin name, absolute file path, or resource naming convention.

If the repository loads embedded streams, preserve that pattern and its image lifetime handling. A bitmap constructed from a stream can retain a dependency on that stream; return a detached copy if the stream is disposed. Confirm the resource's build action and actual manifest name rather than guessing it from the disk path.

## Verify what changed

- Map each component to its intended 24-pixel file; test that similarly named icons were not swapped.
- Confirm the project includes the resource and that its generated property or manifest name resolves.
- Keep component identity, parameter registration, category, and behavior unchanged for an icon-only edit.
- Run an appropriate project build when integration is authorized and feasible.
- When Rhino/Grasshopper is available, inspect the component in the toolbar and on the canvas. A file check or build is not a runtime visual check.

Do not reset component GUIDs to refresh an icon. If a running session still shows an earlier image, investigate reload/cache behavior using the project's supported development workflow.
