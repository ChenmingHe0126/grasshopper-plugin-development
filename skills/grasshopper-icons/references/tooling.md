# PNG pipeline

Requires Python 3.10+ and Pillow. Install Pillow into an appropriate environment if needed; the scripts do not install packages or call an image API.

```console
python scripts/icon_tools.py export --manifest manifest.json --out output
python scripts/icon_tools.py validate --manifest output/export-manifest.json
python scripts/icon_tools.py preview --manifest output/export-manifest.json --out output/24px-preview.png
python scripts/test_icon_tools.py
```

Paths are illustrative and relative to the current directory. Source paths in a manifest resolve relative to that manifest. Choose destinations allowed by the current task. Source images and the source manifest are protected even with overwrite enabled. Export refuses to replace other existing outputs unless `--overwrite` is supplied; preview does the same.

## Manifest

[manifest.example.json](manifest.example.json) documents a mixed input: one icon from a transparent sprite sheet and another from an independent PNG. Replace its nonexistent illustrative source names with actual inputs.

```json
{
  "version": 1,
  "provenance": {
    "method": "code-drawn",
    "tool": "original vector drawing",
    "model": null,
    "notes": "Original geometry; rendered to transparent PNG."
  },
  "master_size": 512,
  "small_size": 24,
  "margin": 1,
  "sheet": "sources/sheet.png",
  "grid": {
    "cell_size": [512, 512],
    "columns": 2,
    "rows": 1,
    "origin": [0, 0],
    "gutter": [0, 0]
  },
  "icons": [
    {"name": "ImportSamples", "cell": [0, 0]},
    {"name": "SolveFrame", "file": "sources/solve.png"}
  ]
}
```

Each icon has a unique portable filename stem. Use either `file` or a zero-based `cell: [column, row]`. A file entry may optionally include `crop: [left, top, right, bottom]`, with right/bottom exclusive. All referenced cells and crops must be inside the source image. Sources must already contain real transparency; this tool deliberately does not guess a background mask.

Provenance methods are `image-generated`, `code-drawn`, `mixed`, or `provided`. Supply the actual production tool. Use a model name only when exposed by the tool; leave it null otherwise and explain if useful. Exporting or resizing model output does not turn it into code-drawn artwork.

## Export behavior

The exporter trims by alpha, fits the subject without distortion, reserves a safe border proportional to the small output, and creates `Name_512.png` and `Name_24.png` by default. It resizes in premultiplied-alpha mode to avoid colored fringes from invisible pixels. It never keys out white: fully opaque white and pale engineering surfaces are retained.

The small file is downscaled from the exported master. A final one-pixel transparent edge is enforced after filtering. `margin` can reserve a larger transparent edge if requested; it must be at least one pixel. Large padding or a source with a shadow may change the subject's optical scale, so inspect the result.

`export-manifest.json` records provenance, the source-byte hash, output names, dimensions, alpha statistics, and hashes. It records no resolved machine-specific source paths.

## Validation and preview

Validation checks expected PNG files, exact square dimensions, RGBA mode, nonempty content, fully transparent required borders, partial transparency, and output hashes. A source with only hard opaque edges is allowed; partial alpha is reported rather than required. The exported manifest is the expected inventory: missing or changed files fail.

The preview composites the actual small PNG at 1:1 and at 8× nearest-neighbor on both light and dark backgrounds. Labels use Pillow's bundled default font; an optional `--font` path can select a user-supplied font. A preview is an opaque review sheet, not a toolbar icon.

These checks cannot judge semantic correctness, accurate geometry, good taste, or a successful Grasshopper runtime integration. Inspect the preview and report those checks separately.
