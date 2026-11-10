"""Offline Yak/ZIP content inspector; not an assembly or Rhino runtime verifier."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile


def inspect(path, *, yak=False, expect_name=None, expect_version=None,
            required=(), forbidden=(), allow_host_sdk=False):
    path = Path(path)
    errors = []
    manifest = None
    with zipfile.ZipFile(path) as archive:
        infos = [i for i in archive.infolist() if not i.is_dir()]
        names = [i.filename for i in infos]
        seen = set()
        for name in names:
            normalized = name.replace("\\", "/")
            parts = PurePosixPath(normalized).parts
            if (normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized)
                    or ".." in parts or "\x00" in name):
                errors.append("Unsafe archive member: " + repr(name))
            if "\\" in name:
                errors.append("Use POSIX separators in archive member: " + name)
            if normalized.casefold() in seen:
                errors.append("Duplicate/case-colliding archive member: " + name)
            seen.add(normalized.casefold())
            if not allow_host_sdk and PurePosixPath(normalized).name.casefold() in {
                    "rhinocommon.dll", "grasshopper.dll", "rhino.ui.dll"}:
                errors.append("Unexpected host SDK assembly: " + name)
        for name in required:
            if name not in names:
                errors.append("Missing required member: " + name)
        if not names:
            errors.append("Archive is empty")
        corrupt = archive.testzip()
        if corrupt:
            errors.append("CRC failure: " + corrupt)
        if yak or expect_name is not None or expect_version is not None:
            if "manifest.yml" not in names:
                errors.append("Missing root manifest.yml")
            else:
                try:
                    import yaml
                except ImportError as exc:
                    raise RuntimeError("Install PyYAML to inspect a Yak manifest") from exc
                try:
                    manifest = yaml.safe_load(archive.read("manifest.yml").decode("utf-8-sig"))
                except (ValueError, UnicodeError, yaml.YAMLError) as exc:
                    errors.append("Invalid manifest: " + str(exc))
                if not isinstance(manifest, dict):
                    errors.append("Manifest must be a mapping")
                else:
                    for key in ("name", "version", "authors", "description"):
                        if not manifest.get(key):
                            errors.append("Missing manifest field: " + key)
                    if not isinstance(manifest.get("authors"), list):
                        errors.append("Manifest authors must be a list")
                    if expect_name is not None and manifest.get("name") != expect_name:
                        errors.append("Manifest name does not match expected name")
                    if expect_version is not None and str(manifest.get("version")) != expect_version:
                        errors.append("Manifest version does not match expected version")
                    ver = str(manifest.get("version", ""))
                    if "$version" in ver or "{" in ver or "}" in ver:
                        errors.append("Unresolved version placeholder in built archive")
                    icon = manifest.get("icon")
                    if icon and (not isinstance(icon, str) or icon not in names):
                        errors.append("Manifest icon is not present in archive")
        markers = [(m, m.encode(enc).lower()) for m in forbidden
                   for enc in ("utf-8", "utf-16-le") if m]
        if markers:
            overlap = max(len(encoded) for _, encoded in markers) - 1
            for info in infos:
                tail = b""
                found = set()
                with archive.open(info) as member:
                    while chunk := member.read(1 << 20):
                        data = (tail + chunk).lower()
                        for _, encoded in markers:
                            if encoded in data:
                                found.add(encoded)
                        tail = data[-overlap:] if overlap else b""
                if found:
                    errors.append("Forbidden marker found in member: " + info.filename)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return {"archive": path.name, "sha256": h.hexdigest(), "members": names,
            "manifest": manifest, "errors": errors, "ok": not errors,
            "limits": "No assembly metadata, Yak server, Rhino load, or UI check performed."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=Path)
    ap.add_argument("--yak", action="store_true")
    ap.add_argument("--expect-name")
    ap.add_argument("--expect-version")
    ap.add_argument("--require", action="append", default=[])
    ap.add_argument("--forbid-marker", action="append", default=[])
    ap.add_argument("--allow-host-sdk", action="store_true")
    args = ap.parse_args()
    try:
        result = inspect(args.archive, yak=args.yak, expect_name=args.expect_name,
                         expect_version=args.expect_version, required=args.require,
                         forbidden=args.forbid_marker, allow_host_sdk=args.allow_host_sdk)
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        ap.exit(2, str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
