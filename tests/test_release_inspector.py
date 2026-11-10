import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "grasshopper-build-release" / "scripts" / "inspect_package.py"
spec = importlib.util.spec_from_file_location("release_inspector", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
inspect = module.inspect

MANIFEST = """name: canopy
version: 1.2.3
authors: [Example Author]
description: Fixture, not a real plugin.
icon: icon.png
"""


class ReleaseInspectorTests(unittest.TestCase):
    def make(self, directory, extra=None, manifest=MANIFEST):
        path = Path(directory) / "canopy.yak"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("manifest.yml", manifest)
            z.writestr("icon.png", b"fixture image; no image validation claimed")
            z.writestr("net8.0/Canopy.gha", b"fixture binary; no assembly validation claimed")
            for name, data in (extra or {}).items():
                z.writestr(name, data)
        return path

    def test_expected_payload_and_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            report = inspect(self.make(temp), yak=True, expect_name="canopy",
                             expect_version="1.2.3", required=["net8.0/Canopy.gha"])
            self.assertTrue(report["ok"])
            self.assertEqual(64, len(report["sha256"]))
            self.assertIn("No assembly metadata", report["limits"])

    def test_stale_manifest_version(self):
        with tempfile.TemporaryDirectory() as temp:
            report = inspect(self.make(temp), yak=True, expect_version="1.2.4")
            self.assertFalse(report["ok"])
            self.assertTrue(any("version does not match" in e for e in report["errors"]))

    def test_unintended_sdk_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make(temp, {"net8.0/Grasshopper.dll": b"unexpected"})
            self.assertFalse(inspect(path)["ok"])
            self.assertTrue(inspect(path, allow_host_sdk=True)["ok"])

    def test_path_escape_and_case_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make(temp, {"../other.txt": b"x", "ICON.PNG": b"x"})
            report = inspect(path)
            self.assertTrue(any("Unsafe" in e for e in report["errors"]))
            self.assertTrue(any("case-colliding" in e for e in report["errors"]))

    def test_utf16_private_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make(temp, {"notes.bin": "sample build workstation".encode("utf-16-le")})
            report = inspect(path, forbidden=["build workstation"])
            self.assertFalse(report["ok"])

    def test_missing_expected_file_and_unresolved_version(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make(temp, manifest=MANIFEST.replace("1.2.3", "$version"))
            report = inspect(path, yak=True, required=["LICENSE.txt"])
            self.assertTrue(any("Missing required" in e for e in report["errors"]))
            self.assertTrue(any("placeholder" in e for e in report["errors"]))

    def test_invalid_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            report = inspect(self.make(temp, manifest="["), yak=True)
            self.assertFalse(report["ok"])
            self.assertTrue(any("Invalid manifest" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
