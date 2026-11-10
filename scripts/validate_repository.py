"""Validate independently installable skills, metadata and local Markdown links."""
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
if not skills:
    errors.append("No skill entrypoints found")
for path in skills:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", content, re.S)
    if not match:
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        continue
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {e}")
        continue
    name = metadata.get("name", "")
    if name != path.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append(f"{path.relative_to(ROOT)}: invalid/mismatched name")
    if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
        errors.append(f"{path.relative_to(ROOT)}: missing description")
    ui = path.parent / "agents" / "openai.yaml"
    if not ui.exists():
        errors.append(f"{path.relative_to(ROOT)}: missing UI metadata")
        continue
    config = yaml.safe_load(ui.read_text(encoding="utf-8"))
    interface = config.get("interface", {})
    if not interface.get("display_name"):
        errors.append(f"{ui.relative_to(ROOT)}: missing display name")
    short = interface.get("short_description", "")
    if not 25 <= len(short) <= 64:
        errors.append(f"{ui.relative_to(ROOT)}: short description must be 25-64 characters")
    if "$"+name not in interface.get("default_prompt", ""):
        errors.append(f"{ui.relative_to(ROOT)}: invocation does not mention skill name")
    if config.get("policy", {}).get("allow_implicit_invocation") is False:
        errors.append(f"{ui.relative_to(ROOT)}: implicit invocation disabled without a repository requirement")

for path in ROOT.rglob("*.md"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    prose = re.sub(chr(96)*3 + r".*?" + chr(96)*3, "", text, flags=re.S)
    for target in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", prose):
        if re.match(r"^[a-zA-Z][\w+.-]*:", target) or target.startswith("#"):
            continue
        destination = target.split("#", 1)[0].strip("<>")
        if not destination:
            continue
        linked = (path.parent / destination).resolve()
        if not linked.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {target}")
        skill_root = next((s.parent for s in skills if path.is_relative_to(s.parent)), None)
        if skill_root and not linked.is_relative_to(skill_root):
            errors.append(f"{path.relative_to(ROOT)}: install-time dependency outside its skill: {target}")
    if re.search(r"[A-Za-z]:[\\/]Users[\\/]", text, re.I):
        errors.append(f"{path.relative_to(ROOT)}: machine-specific user path")
    if re.search(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}", text):
        errors.append(f"{path.relative_to(ROOT)}: possible access token")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print(f"Validated {len(skills)} self-contained skills and local documentation links.")
