#!/usr/bin/env python3
"""Behavioral tests; all temporary artifacts stay beside this script and are removed."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

import icon_tools as icons


def pixels(image):
    method = getattr(image, "get_flattened_data", None)
    return method() if method else list(image.getdata())


class IconToolsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix=".icon-tests-", dir=Path(__file__).parent)
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def image(self, name: str, color: tuple[int, int, int, int], size=(64, 64)) -> Path:
        # Deliberately nonzero RGB in invisible pixels tests premultiplication.
        image = Image.new("RGBA", size, (255, 0, 255, 0))
        ImageDraw.Draw(image).rectangle((12, 10, size[0] - 13, size[1] - 11), fill=color)
        path = self.root / name
        image.save(path)
        return path

    def manifest(self, entries: list[dict], **extra) -> Path:
        data = {
            "version": 1,
            "provenance": {"method": "code-drawn", "tool": "test geometry", "model": None},
            "master_size": 64,
            "small_size": 24,
            "margin": 1,
            "icons": entries,
        }
        data.update(extra)
        path = self.root / "input.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def export(self, manifest: Path) -> tuple[Path, dict]:
        out = self.root / "output"
        result = icons.export_icons(manifest, out)
        return out / "export-manifest.json", result

    def test_independent_exports_preserve_ice_white_alpha_and_sources(self):
        source = self.image("white.png", (248, 252, 255, 255))
        source_hash = icons.sha256(source)
        manifest = self.manifest([{"name": "PaleSolid", "file": source.name}])
        exported, result = self.export(manifest)
        self.assertTrue(icons.validate_export(exported)["passed"])
        self.assertEqual(icons.sha256(source), source_hash)
        self.assertEqual(result["icons"][0]["source_sha256"], source_hash)
        for size in (64, 24):
            with Image.open(exported.parent / f"PaleSolid_{size}.png") as image:
                self.assertEqual(image.size, (size, size))
                self.assertEqual(image.mode, "RGBA")
                self.assertTrue(icons.border_is_clear(image, 1))
                self.assertGreater(sum(a == 255 and r >= 245 and g >= 248 and b >= 250
                                       for r, g, b, a in pixels(image)), 20)

    def test_premultiplication_prevents_invisible_magenta_fringe(self):
        source = self.image("edge.png", (255, 255, 255, 255))
        with Image.open(source) as opened:
            resized = icons.premultiplied_resize(opened, (19, 19))
        partial = [(r, g, b) for r, g, b, a in pixels(resized) if 0 < a < 255]
        self.assertTrue(partial)
        self.assertTrue(all(min(rgb) >= 250 for rgb in partial))

    def test_mixed_sprite_and_file_entries_with_grid_origin_and_gutter(self):
        sheet = Image.new("RGBA", (135, 69), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sheet)
        draw.rectangle((10, 11, 49, 50), fill=(30, 170, 90, 255))
        draw.rectangle((78, 11, 117, 50), fill=(35, 90, 210, 255))
        sheet.save(self.root / "sheet.png")
        self.image("separate.png", (200, 170, 40, 255))
        manifest = self.manifest(
            [{"name": "Green", "cell": [0, 0]}, {"name": "Blue", "cell": [1, 0]},
             {"name": "Separate", "file": "separate.png", "crop": [2, 2, 62, 62]}],
            sheet="sheet.png",
            grid={"cell_size": [64, 64], "columns": 2, "rows": 1, "origin": [2, 3], "gutter": [3, 0]},
        )
        exported, _ = self.export(manifest)
        result = icons.validate_export(exported)
        self.assertTrue(result["passed"])
        self.assertEqual(result["checked_files"], 6)
        with Image.open(exported.parent / "Green_24.png") as green, Image.open(exported.parent / "Blue_24.png") as blue:
            self.assertGreater(green.getpixel((12, 12))[1], green.getpixel((12, 12))[2])
            self.assertGreater(blue.getpixel((12, 12))[2], blue.getpixel((12, 12))[1])

    def test_margin_two_remains_clear_in_small_output(self):
        self.image("source.png", (40, 160, 90, 255))
        manifest = self.manifest([{"name": "Bordered", "file": "source.png"}], margin=2)
        exported, _ = self.export(manifest)
        with Image.open(exported.parent / "Bordered_24.png") as image:
            self.assertTrue(icons.border_is_clear(image, 2))
            self.assertIsNotNone(image.getchannel("A").getbbox())

    def test_rejects_opaque_matte_and_empty_source_without_partial_exports(self):
        for mode in ("opaque", "empty"):
            with self.subTest(mode=mode):
                image = Image.new("RGBA", (64, 64), (255, 255, 255, 255) if mode == "opaque" else (0, 0, 0, 0))
                image.save(self.root / "source.png")
                manifest = self.manifest([{"name": "Bad", "file": "source.png"}])
                with self.assertRaises(icons.IconError):
                    icons.export_icons(manifest, self.root / mode)
                self.assertFalse((self.root / mode).exists())

    def test_rejects_outside_cells_bad_crops_and_filename_traversal(self):
        self.image("source.png", (40, 160, 90, 255))
        cases = [
            ([{"name": "Cell", "cell": [2, 0]}], {"sheet": "source.png", "grid": {"cell_size": [64, 64], "columns": 1, "rows": 1}}),
            ([{"name": "Crop", "file": "source.png", "crop": [0, 0, 99, 64]}], {}),
            ([{"name": "../Escape", "file": "source.png"}], {}),
            ([{"name": "Duplicate", "file": "source.png"}, {"name": "duplicate", "file": "source.png"}], {}),
            ([{"name": "Both", "file": "source.png", "cell": [0, 0]}], {}),
        ]
        for entries, extra in cases:
            with self.subTest(entries=entries):
                manifest = self.manifest(entries, **extra)
                with self.assertRaises(icons.IconError):
                    icons.export_icons(manifest, self.root / "bad-output")
                self.assertFalse((self.root / "bad-output").exists())

    def test_refuses_unrequested_overwrite_and_keeps_existing_bytes(self):
        self.image("source.png", (40, 160, 90, 255))
        manifest = self.manifest([{"name": "Original", "file": "source.png"}])
        exported, _ = self.export(manifest)
        before = {p.name: icons.sha256(p) for p in exported.parent.iterdir()}
        with self.assertRaises(icons.IconError):
            icons.export_icons(manifest, exported.parent)
        self.assertEqual(before, {p.name: icons.sha256(p) for p in exported.parent.iterdir()})

    def test_validation_detects_missing_changed_dimensions_and_border(self):
        self.image("source.png", (40, 160, 90, 255))
        manifest = self.manifest([{"name": "Icon", "file": "source.png"}])
        exported, _ = self.export(manifest)
        (exported.parent / "Icon_64.png").unlink()
        Image.new("RGBA", (23, 23), (255, 255, 255, 255)).save(exported.parent / "Icon_24.png")
        result = icons.validate_export(exported)
        self.assertFalse(result["passed"])
        errors = "\n".join(result["errors"])
        self.assertIn("missing file", errors)
        self.assertIn("expected 24x24", errors)
        self.assertIn("transparent border", errors)
        self.assertIn("SHA-256", errors)

    def test_preview_preserves_actual_pixels_and_nearest_neighbor_blocks(self):
        self.image("source.png", (248, 252, 255, 255))
        manifest = self.manifest([{"name": "Preview", "file": "source.png"}])
        exported, _ = self.export(manifest)
        preview = self.root / "preview.png"
        self.assertEqual(icons.preview_export(exported, preview), (264, 592))
        with Image.open(preview) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.getpixel((0, 0)), (243, 245, 242))
            self.assertEqual(image.getpixel((0, 300)), (40, 53, 48))
            # Small center pixel is placed at x=16+12, y=56+84+12.
            self.assertEqual(image.getpixel((28, 152)), (248, 252, 255))
            # Big center pixel becomes a uniform 8x8 block.
            block = image.crop((56 + 12 * 8, 56 + 12 * 8, 56 + 13 * 8, 56 + 13 * 8))
            self.assertEqual(len(set(pixels(block))), 1)
        with self.assertRaises(icons.IconError):
            icons.preview_export(exported, preview)
        with self.assertRaises(icons.IconError):
            icons.preview_export(exported, exported.parent / "Preview_24.png", overwrite=True)

    def test_overwrite_flag_never_replaces_input_images(self):
        source = self.image("Protected_64.png", (40, 160, 90, 255))
        source_hash = icons.sha256(source)
        manifest = self.manifest([{"name": "Protected", "file": source.name}])
        with self.assertRaisesRegex(icons.IconError, "cannot replace source"):
            icons.export_icons(manifest, self.root, overwrite=True)
        self.assertEqual(icons.sha256(source), source_hash)
        self.assertFalse((self.root / "Protected_24.png").exists())

    def test_provenance_preserves_image_generation_even_after_code_resize(self):
        self.image("source.png", (40, 160, 90, 255))
        origin = {"method": "image-generated", "tool": "example generator", "model": None}
        manifest = self.manifest([{"name": "Generated", "file": "source.png"}], provenance=origin)
        _, result = self.export(manifest)
        self.assertEqual(result["provenance"], origin)

    def test_invalid_cli_returns_actionable_nonzero_status(self):
        manifest = self.manifest([{"name": "Missing", "file": "missing.png"}])
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = icons.main(["export", "--manifest", str(manifest), "--out", str(self.root / "bad")])
        self.assertEqual(status, 2)
        self.assertIn("Cannot load source", stderr.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
