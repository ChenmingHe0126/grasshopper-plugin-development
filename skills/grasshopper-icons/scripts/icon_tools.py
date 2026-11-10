#!/usr/bin/env python3
"""Export and inspect transparent Grasshopper icon families. Requires Pillow."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

METHODS = {"image-generated", "code-drawn", "mixed", "provided"}
NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
RESAMPLE = Image.Resampling.LANCZOS


class IconError(ValueError):
    """Actionable input or output validation error."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise IconError(f"Cannot read JSON {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise IconError("Manifest must be a JSON object.")
    return value


def integer(value: Any, label: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise IconError(f"{label} must be an integer >= {minimum}.")
    return value


def pair(value: Any, label: str, minimum: int = 0) -> tuple[int, int]:
    if not isinstance(value, list) or len(value) != 2:
        raise IconError(f"{label} must contain exactly two integers.")
    return tuple(integer(v, label, minimum) for v in value)


def text_value(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IconError(f"{label} must be a nonempty string.")
    return value


def provenance(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("method") not in METHODS:
        raise IconError("provenance.method must be image-generated, code-drawn, mixed, or provided.")
    text_value(value.get("tool"), "provenance.tool")
    if value.get("model") is not None:
        text_value(value["model"], "provenance.model")
    if "notes" in value and not isinstance(value["notes"], str):
        raise IconError("provenance.notes must be a string.")
    return {key: value[key] for key in ("method", "tool", "model", "notes") if key in value}


def dimensions(data: dict[str, Any]) -> tuple[int, int, int]:
    master = integer(data.get("master_size", 512), "master_size", 8)
    small = integer(data.get("small_size", 24), "small_size", 4)
    margin = integer(data.get("margin", 1), "margin", 1)
    if master <= small:
        raise IconError("master_size must be larger than small_size.")
    if margin * 2 >= small:
        raise IconError("margin leaves no drawable area in the small icon.")
    return master, small, margin


def premultiplied_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    # RGBa stores premultiplied channels; invisible RGB cannot bleed into edges.
    return image.convert("RGBA").convert("RGBa").resize(size, RESAMPLE).convert("RGBA")


def clear_border(image: Image.Image, margin: int) -> None:
    width, height = image.size
    blank = (0, 0, 0, 0)
    image.paste(blank, (0, 0, width, margin))
    image.paste(blank, (0, height - margin, width, height))
    image.paste(blank, (0, 0, margin, height))
    image.paste(blank, (width - margin, 0, width, height))


def border_is_clear(image: Image.Image, margin: int) -> bool:
    alpha = image.getchannel("A")
    width, height = image.size
    boxes = ((0, 0, width, margin), (0, height - margin, width, height),
             (0, 0, margin, height), (width - margin, 0, width, height))
    return all(alpha.crop(box).getextrema()[1] == 0 for box in boxes)


def alpha_stats(image: Image.Image) -> dict[str, Any]:
    alpha = image.getchannel("A")
    histogram = alpha.histogram()
    return {
        "bbox": alpha.getbbox(),
        "transparent": histogram[0],
        "partial": sum(histogram[1:255]),
        "opaque": histogram[255],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_image(path: Path) -> Image.Image:
    try:
        with Image.open(path) as image:
            return image.convert("RGBA")
    except (OSError, ValueError) as exc:
        raise IconError(f"Cannot load source {path.name}: {exc}") from exc


def crop_source(entry: dict[str, Any], data: dict[str, Any], base: Path) -> tuple[Image.Image, str]:
    has_file = "file" in entry
    has_cell = "cell" in entry
    if has_file == has_cell:
        raise IconError("Each icon needs exactly one of file or cell.")
    source = entry["file"] if has_file else data.get("sheet")
    path = base / text_value(source, "source path")
    image = source_image(path)
    if has_cell:
        if "crop" in entry:
            raise IconError("A cell entry cannot also define crop.")
        grid = data.get("grid")
        if not isinstance(grid, dict):
            raise IconError("Sprite-sheet icons require a grid object.")
        cell_w, cell_h = pair(grid.get("cell_size"), "grid.cell_size", 1)
        cols = integer(grid.get("columns"), "grid.columns")
        rows = integer(grid.get("rows"), "grid.rows")
        origin_x, origin_y = pair(grid.get("origin", [0, 0]), "grid.origin")
        gutter_x, gutter_y = pair(grid.get("gutter", [0, 0]), "grid.gutter")
        col, row = pair(entry["cell"], "cell")
        if col >= cols or row >= rows:
            raise IconError(f"Cell [{col}, {row}] is outside the declared grid.")
        # Check the complete declared grid as well as the selected cell.
        if (origin_x + cols * cell_w + (cols - 1) * gutter_x > image.width or
                origin_y + rows * cell_h + (rows - 1) * gutter_y > image.height):
            raise IconError("Declared sprite grid extends outside the source image.")
        left = origin_x + col * (cell_w + gutter_x)
        top = origin_y + row * (cell_h + gutter_y)
        image = image.crop((left, top, left + cell_w, top + cell_h))
    elif "crop" in entry:
        box = entry["crop"]
        if not isinstance(box, list) or len(box) != 4:
            raise IconError("crop must be [left, top, right, bottom].")
        left, top, right, bottom = [integer(v, "crop coordinate", 0) for v in box]
        if left >= right or top >= bottom or right > image.width or bottom > image.height:
            raise IconError("crop must be nonempty and inside the source image.")
        image = image.crop((left, top, right, bottom))
    alpha = image.getchannel("A")
    if alpha.getbbox() is None:
        raise IconError("Source icon is fully transparent.")
    if alpha.getextrema()[0] != 0:
        raise IconError("Source icon has no fully transparent background; supply real alpha, not a white matte.")
    # Trim by alpha only. Opaque white is subject content, not a masking key.
    return image.crop(alpha.getbbox()), sha256(path)


def render_pair(subject: Image.Image, master: int, small: int, margin: int) -> tuple[Image.Image, Image.Image]:
    safe = math.ceil(master * margin / small)
    drawable = master - 2 * safe
    scale = min(drawable / subject.width, drawable / subject.height)
    size = (max(1, round(subject.width * scale)), max(1, round(subject.height * scale)))
    resized = premultiplied_resize(subject, size)
    large = Image.new("RGBA", (master, master), (0, 0, 0, 0))
    large.alpha_composite(resized, ((master - size[0]) // 2, (master - size[1]) // 2))
    tiny = premultiplied_resize(large, (small, small))
    # Lanczos can create a faint alpha fringe beyond the reserved margin.
    clear_border(large, 1)
    clear_border(tiny, margin)
    return large, tiny


def export_icons(manifest: Path, out: Path, overwrite: bool = False) -> dict[str, Any]:
    data = read_json(manifest)
    if type(data.get("version")) is not int or data["version"] != 1:
        raise IconError("Unsupported manifest version; expected 1.")
    origin = provenance(data.get("provenance"))
    master, small, margin = dimensions(data)
    entries = data.get("icons")
    if not isinstance(entries, list) or not entries:
        raise IconError("icons must be a nonempty array.")
    names: set[str] = set()
    prepared = []
    targets = [out / "export-manifest.json"]
    protected_inputs = {manifest.resolve()}
    # Validate all inputs and collisions before creating output files.
    for entry in entries:
        if not isinstance(entry, dict):
            raise IconError("Every icon entry must be an object.")
        name = text_value(entry.get("name"), "icon name")
        if NAME_RE.fullmatch(name) is None:
            raise IconError("Icon names must start with a letter and use only letters, digits, hyphens, or underscores (max 64).")
        if name.casefold() in names:
            raise IconError(f"Duplicate icon name: {name}")
        names.add(name.casefold())
        subject, source_hash = crop_source(entry, data, manifest.parent)
        source_path = entry["file"] if "file" in entry else data["sheet"]
        protected_inputs.add((manifest.parent / source_path).resolve())
        images = render_pair(subject, master, small, margin)
        prepared.append((name, source_hash, images))
        targets.extend(out / f"{name}_{size}.png" for size in (master, small))
    if any(path.resolve() in protected_inputs for path in targets):
        raise IconError("Output destinations cannot replace source images or the source manifest.")
    if not overwrite:
        collisions = [path.name for path in targets if path.exists()]
        if collisions:
            raise IconError("Outputs already exist; choose a new folder or pass --overwrite: " + ", ".join(collisions))
    result: dict[str, Any] = {
        "version": 1, "provenance": origin, "master_size": master,
        "small_size": small, "margin": margin, "icons": [],
    }
    out.mkdir(parents=True, exist_ok=True)
    for name, source_hash, images in prepared:
        record: dict[str, Any] = {"name": name, "source_sha256": source_hash, "files": []}
        for size, image in zip((master, small), images):
            path = out / f"{name}_{size}.png"
            image.save(path, format="PNG")
            record["files"].append({
                "file": path.name, "size": size, "sha256": sha256(path),
                "alpha": alpha_stats(image),
            })
        result["icons"].append(record)
    (out / "export-manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def validate_export(manifest: Path) -> dict[str, Any]:
    data = read_json(manifest)
    if type(data.get("version")) is not int or data["version"] != 1:
        raise IconError("Unsupported export manifest version; expected 1.")
    provenance(data.get("provenance"))
    master, small, margin = dimensions(data)
    records = data.get("icons")
    if not isinstance(records, list) or not records:
        raise IconError("Export manifest icons must be a nonempty array.")
    errors: list[str] = []
    checked = 0
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("files"), list):
            raise IconError("Each exported icon must contain a files array.")
        sizes = []
        for item in record["files"]:
            if not isinstance(item, dict):
                raise IconError("Export file entries must be objects.")
            filename = text_value(item.get("file"), "export file")
            if Path(filename).name != filename or "/" in filename or "\\" in filename:
                raise IconError("Exported file names must be simple filenames.")
            if filename.casefold() in seen:
                raise IconError(f"Duplicate output file: {filename}")
            seen.add(filename.casefold())
            size = integer(item.get("size"), "export size")
            sizes.append(size)
            path = manifest.parent / filename
            checked += 1
            if not path.is_file():
                errors.append(f"{filename}: missing file")
                continue
            try:
                with Image.open(path) as opened:
                    if opened.format != "PNG":
                        errors.append(f"{filename}: expected PNG")
                    if opened.mode != "RGBA":
                        errors.append(f"{filename}: expected RGBA, got {opened.mode}")
                    image = opened.convert("RGBA")
            except (OSError, ValueError) as exc:
                errors.append(f"{filename}: cannot load image ({exc})")
                continue
            if image.size != (size, size):
                errors.append(f"{filename}: expected {size}x{size}, got {image.size}")
            required_margin = margin if size == small else 1
            if min(image.size) <= 2 * required_margin or not border_is_clear(image, required_margin):
                errors.append(f"{filename}: transparent border is missing or too narrow")
            if image.getchannel("A").getbbox() is None:
                errors.append(f"{filename}: empty alpha")
            if sha256(path) != item.get("sha256"):
                errors.append(f"{filename}: SHA-256 differs from export manifest")
        if sorted(sizes) != sorted([master, small]):
            errors.append(f"{record.get('name', '?')}: expected one master and one small file")
    return {"passed": not errors, "checked_files": checked, "errors": errors}


def default_font(size: int, font_path: str | None = None) -> ImageFont.ImageFont:
    if font_path:
        return ImageFont.truetype(font_path, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Compatible with older Pillow without hard-coded OS fonts.
        return ImageFont.load_default()


def preview_export(manifest: Path, out: Path, overwrite: bool = False, font_path: str | None = None) -> tuple[int, int]:
    validation = validate_export(manifest)
    if not validation["passed"]:
        raise IconError("Preview requires a valid export: " + "; ".join(validation["errors"]))
    if out.exists() and not overwrite:
        raise IconError("Preview already exists; choose another filename or pass --overwrite.")
    # Prevent a valid export asset or its manifest from being replaced by a review sheet.
    data = read_json(manifest)
    protected = {manifest.resolve()}
    protected.update((manifest.parent / item["file"]).resolve() for record in data["icons"] for item in record["files"])
    if out.resolve() in protected:
        raise IconError("Preview destination cannot replace an exported asset or its manifest.")
    small = data["small_size"]
    zoom = 8
    pad = 16
    column_width = small + small * zoom + 3 * pad
    row_height = small * zoom + 104
    sheet = Image.new("RGBA", (column_width * len(data["icons"]), 2 * row_height))
    title_font = default_font(16, font_path)
    label_font = default_font(14, font_path)
    backgrounds = (("#F3F5F2", "#173E35", "LIGHT"), ("#283530", "#E2EBE4", "DARK"))
    for row, (background, foreground, label) in enumerate(backgrounds):
        y = row * row_height
        sheet.paste(background, (0, y, sheet.width, y + row_height))
        draw = ImageDraw.Draw(sheet)
        draw.text((pad, y + 12), f"{label} | actual {small}px + 8x nearest-neighbor", fill=foreground, font=title_font)
        for col, record in enumerate(data["icons"]):
            x = col * column_width
            item = next(item for item in record["files"] if item["size"] == small)
            image = source_image(manifest.parent / item["file"])
            sheet.alpha_composite(image, (x + pad, y + 56 + (small * zoom - small) // 2))
            sheet.alpha_composite(image.resize((small * zoom, small * zoom), Image.Resampling.NEAREST),
                                  (x + 2 * pad + small, y + 56))
            name = record["name"]
            # Keep labels inside their column without a platform-specific font.
            while name and draw.textbbox((0, 0), name, font=label_font)[2] > column_width - 2 * pad:
                name = name[:-2] + "~" if len(name) > 2 else ""
            draw.text((x + pad, y + row_height - 30), name, fill=foreground, font=label_font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out, format="PNG")
    return sheet.size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="Export a transparent family from a source manifest.")
    export.add_argument("--manifest", type=Path, required=True)
    export.add_argument("--out", type=Path, required=True)
    export.add_argument("--overwrite", action="store_true")
    validate = sub.add_parser("validate", help="Verify an exported family against its manifest.")
    validate.add_argument("--manifest", type=Path, required=True)
    preview = sub.add_parser("preview", help="Create light/dark actual-size and 8x review panels.")
    preview.add_argument("--manifest", type=Path, required=True)
    preview.add_argument("--out", type=Path, required=True)
    preview.add_argument("--overwrite", action="store_true")
    preview.add_argument("--font", help="Optional user-supplied font file.")
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            result = export_icons(args.manifest, args.out, args.overwrite)
            print(json.dumps({"exported_icons": len(result["icons"]), "manifest": str(args.out / "export-manifest.json")}))
        elif args.command == "validate":
            result = validate_export(args.manifest)
            print(json.dumps(result, indent=2))
            return 0 if result["passed"] else 1
        else:
            size = preview_export(args.manifest, args.out, args.overwrite, args.font)
            print(json.dumps({"preview": str(args.out), "size": size}))
    except (IconError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
