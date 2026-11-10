# From behavior to a 24-pixel family

## 1. Establish semantic differences

For each component, write a short sentence with its input, action, and output. Check source or documentation when the name hides a distinction.

Choose the smallest visible contrast that matters:

| Behavior | Useful visual distinction |
| --- | --- |
| Load geometry vs load samples | Continuous geometry vs separate points; repeat the import arrow |
| Fit a model to samples | Samples → model, with matching input/output silhouette |
| Batch processing | Repeated inputs, a processing cue, or a compact transformation; avoid obscuring the main operation |
| Cut and assign material | Real cut gap, separated piece, destination member in the same action color |
| Solve or optimize | The relevant object plus a restrained operation cue |

Do not put every input, file extension, graph, and output into the icon. Text such as CSV is usually too small at 24 pixels. Reject a plausible but incorrect metaphor before polishing it.

## 2. Establish a family

Inspect the plugin's existing icons when supplied or authorized. Learn its rules rather than copying a distinctive brand asset into an unrelated project.

Record a few decisions: silhouette, projection, outline weight, body color, top-face highlight, action color, and action placement. Keep these consistent across the family. For compact engineering pictograms, broad colored faces, pale exposed ends, and a dark contour can communicate more than texture or glow.

Compare palette variants with unchanged geometry. Separate a dominant hue from a monochrome restriction: “green-themed” can include teal, yellow-green, or a small complementary accent. When the user selects a variant, keep that choice while refining geometry.

## 3. Draw for the final size

The following are starting points, not framework requirements or rules for every style. The [official icon guide](https://developer.rhino3d.com/guides/grasshopper/grasshopper-icons/) discusses 24-pixel assets and commonly uses a two-pixel empty border; choose padding to suit the target family:

- Work inside roughly 22×22 pixels for a 24-pixel asset.
- Try approximately 0.8–1.2-pixel outer contours for a large central object. Smaller secondary objects may need 0.6–0.8 pixels so their fills remain visible.
- Keep important gaps around one pixel or larger. A cutting icon needs a real gap after downsampling.
- Use thinner internal seams than exterior contours. At cylinder junctions, draw rear branches first and let the trunk cover the join. Use complete end ellipses at exposed ends and partial seam arcs at connected segments.
- Give important points enough solid area to survive resampling. Points around 1.7–2 pixels wide with a restrained outline are often more readable than numerous tiny samples.
- Leave a colored core in arrows after outlining. Use the same arrow proportions, direction, and role across related operations.
- Match the centerline and branching arrangement of an input cloud and its reconstructed model; the material change becomes legible without explanation.

The large master may need fewer details than a standalone illustration. Use optical judgment when small members become black knots or empty contours.

## 4. Review and refine

Compare four views: master, actual 24 pixels on a light background, actual 24 on a dark background, and 8× nearest-neighbor enlargement. The enlarged view helps diagnose pixel coverage; it is not a replacement for actual-size viewing.

Check:

- Can the family members be distinguished without their labels?
- Does the silhouette express the correct transformation?
- Do points remain discrete and branches remain connected?
- Do arrows retain direction and a visible fill?
- Does the cut remain open?
- Do pale faces remain visible and opaque?
- Is the icon balanced at toolbar size?

Fix the demonstrated issue: contour width, point diameter, gap, or arrangement. Do not keep adding decorative detail once the semantic and pixel checks pass.
