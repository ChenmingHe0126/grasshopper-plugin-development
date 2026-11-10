# Experience distilled from Moyu and QSM work

These are design observations and local lessons, not universal palette or authorization requirements. No original plugin assets are bundled with this skill.

## Moyu: an engineering language

The inspected icon family favored compact flat engineering pictograms: dark outlines, broad colored faces, pale top highlights, and restrained depth. The useful lesson was to match contour, projection, optical scale, and geometry. Recoloring unrelated silhouettes alone did not establish the same quality.

For tube-like objects, a clear continuous exterior and a small number of seams worked better than outlining every overlapping cap. Complete dark ellipses at every junction made branches look like stacked pipe parts and produced knots at 24 pixels.

## QSM: semantics before polish

A scanned-tree family included model fitting, model loading, point-cloud loading, and cutting branches for a truss.

- **Batch fitting:** point clouds become connected-cylinder tree models. Two cylinder trees suggested repeated output but omitted the essential conversion. The correction was a point-cloud tree → arrow → cylinder tree, with both trees using the same simplified branching skeleton.
- **Model loading:** a continuous segmented tree plus an import cue.
- **Cloud loading:** the same tree as separate height-colored points, with the same import cue.
- **Cut matching:** a detached branch piece with a genuine kerf gap, followed by a truss whose assigned member shares the action accent. The metaphor must not imply gluing.

A selected green family used emerald bodies, teal highlights, and small yellow-green action accents. That is an example of a dominant green palette with neighboring hues; it is not a required palette for future plugins.

## What the 24-pixel review changed

The refined masters looked cleaner, yet thin outlines and faint cloud points became soft at actual size. The fix was to increase real contour and point coverage, brighten secondary input points for dark backgrounds, remove satellites that vanished, preserve the arrow's colored core, and enlarge the true cutting gap.

The numbers depended on each icon's scale. The smaller Batch model required a lighter contour than the larger Load tree. Review the final raster rather than assuming one master-space stroke value fits every object.

## Tool choice and reporting

In one task the user restricted all file writes to a single destination, while a generation tool's default save behavior used another directory. Deterministic drawing was chosen for that task and disclosed. This does not make image generation unsuitable or prohibited in later work. Check actual availability, permissions, output behavior, and design requirements each time; report tool failures and provenance honestly.

Preserve existing drafts when the user requests alternatives. Versioning can protect comparisons, but do not infer permission to overwrite original resources, integrate them into a plugin, or publish assets from a design-only request.
