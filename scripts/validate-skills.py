#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN_PATH = ROOT / ".codex-plugin" / "plugin.json"

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
INSTALL_METADATA_RE = re.compile(r"^\s*github-[A-Za-z0-9_-]+:")
OPENAI_INTERFACE_RE = re.compile(
    r'^\s{2}(display_name|short_description|default_prompt):\s*["\'](.*)["\']\s*$'
)


def error(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)


def read_frontmatter(path: Path) -> tuple[list[str], dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc

    frontmatter = lines[1:end]
    fields: dict[str, str] = {}
    current_key: str | None = None

    for line in frontmatter:
        if line and not line.startswith((" ", "\t")):
            match = FRONTMATTER_KEY_RE.match(line)
            if match:
                current_key = match.group(1)
                fields[current_key] = (match.group(2) or "").strip()
                continue
            current_key = None
        elif current_key:
            fields[current_key] = f"{fields[current_key]}\n{line.strip()}".strip()

    return frontmatter, fields


def clean_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def validate_skill(skill_dir: Path) -> list[str]:
    problems: list[str] = []
    skill_path = skill_dir / "SKILL.md"

    if not skill_path.exists():
        return [f"{skill_dir.relative_to(ROOT)} is missing SKILL.md"]

    try:
        frontmatter, fields = read_frontmatter(skill_path)
    except ValueError as exc:
        return [f"{skill_path.relative_to(ROOT)}: {exc}"]

    for required in ("name", "description", "license"):
        if required not in fields:
            problems.append(f"{skill_path.relative_to(ROOT)}: missing required '{required}' frontmatter")
        elif not clean_yaml_scalar(fields[required]):
            problems.append(f"{skill_path.relative_to(ROOT)}: empty '{required}' frontmatter")

    name = clean_yaml_scalar(fields.get("name", ""))
    if name:
        if not NAME_RE.fullmatch(name):
            problems.append(f"{skill_path.relative_to(ROOT)}: invalid skill name '{name}'")
        if name != skill_dir.name:
            problems.append(
                f"{skill_path.relative_to(ROOT)}: skill name '{name}' must match directory '{skill_dir.name}'"
            )

    allowed_tools = fields.get("allowed-tools")
    if allowed_tools is not None:
        stripped = allowed_tools.strip()
        if not stripped:
            problems.append(f"{skill_path.relative_to(ROOT)}: allowed-tools must be a non-empty string")
        if stripped.startswith(("[", "{")):
            problems.append(f"{skill_path.relative_to(ROOT)}: allowed-tools must be a string, not YAML collection")

    for line_number, line in enumerate(frontmatter, start=2):
        if INSTALL_METADATA_RE.match(line):
            problems.append(
                f"{skill_path.relative_to(ROOT)}:{line_number}: remove installed-source metadata '{line.strip()}'"
            )

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        problems.append(f"{skill_dir.relative_to(ROOT)}: missing agents/openai.yaml")
    else:
        contents = openai_yaml.read_text(encoding="utf-8")
        for required in ("display_name:", "short_description:", "default_prompt:"):
            if required not in contents:
                problems.append(f"{openai_yaml.relative_to(ROOT)}: missing interface.{required.rstrip(':')}")
        interface = dict(OPENAI_INTERFACE_RE.findall(contents))
        short_description = interface.get("short_description", "")
        if short_description and not 25 <= len(short_description) <= 64:
            problems.append(
                f"{openai_yaml.relative_to(ROOT)}: interface.short_description must be 25-64 characters"
            )
        default_prompt = interface.get("default_prompt", "")
        if default_prompt and f"${name}" not in default_prompt:
            problems.append(
                f"{openai_yaml.relative_to(ROOT)}: interface.default_prompt must mention '${name}'"
            )

    return problems


def validate_marketplace() -> list[str]:
    problems: list[str] = []

    if not MARKETPLACE_PATH.exists():
        return [".claude-plugin/marketplace.json is missing"]

    try:
        marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{MARKETPLACE_PATH.relative_to(ROOT)}: invalid JSON: {exc}"]

    if marketplace.get("name") != "basemachina":
        problems.append(".claude-plugin/marketplace.json: marketplace name must be 'basemachina'")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        return problems + [".claude-plugin/marketplace.json: plugins must be a non-empty list"]

    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            problems.append(f".claude-plugin/marketplace.json: plugins[{index}] must be an object")
            continue
        for required in ("name", "source", "description", "version", "license", "homepage", "repository"):
            if not plugin.get(required):
                problems.append(f".claude-plugin/marketplace.json: plugins[{index}] missing '{required}'")
        skills_path = plugin.get("skills")
        if isinstance(skills_path, str) and not (ROOT / skills_path).exists():
            problems.append(f".claude-plugin/marketplace.json: plugins[{index}].skills path does not exist")

    return problems


def load_json_object(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"{path.relative_to(ROOT)} is missing"]
    except json.JSONDecodeError as exc:
        return None, [f"{path.relative_to(ROOT)}: invalid JSON: {exc}"]

    if not isinstance(payload, dict):
        return None, [f"{path.relative_to(ROOT)}: root must be an object"]
    return payload, []


def validate_plugin_manifests() -> list[str]:
    problems: list[str] = []
    claude, claude_problems = load_json_object(CLAUDE_PLUGIN_PATH)
    codex, codex_problems = load_json_object(CODEX_PLUGIN_PATH)
    problems.extend(claude_problems)
    problems.extend(codex_problems)

    for path, manifest in ((CLAUDE_PLUGIN_PATH, claude), (CODEX_PLUGIN_PATH, codex)):
        if manifest is None:
            continue
        for required in ("name", "version", "description", "author", "homepage", "repository", "license"):
            if not manifest.get(required):
                problems.append(f"{path.relative_to(ROOT)}: missing '{required}'")
        version = manifest.get("version")
        if isinstance(version, str) and SEMVER_RE.fullmatch(version) is None:
            problems.append(f"{path.relative_to(ROOT)}: version must use semantic versioning")
        skills_path = manifest.get("skills")
        if not isinstance(skills_path, str) or not (ROOT / skills_path).is_dir():
            problems.append(f"{path.relative_to(ROOT)}: skills must point to the skills directory")

    if claude is not None and codex is not None:
        for field in ("name", "version", "description"):
            if claude.get(field) != codex.get(field):
                problems.append(f"plugin manifests must use the same '{field}'")

    if codex is not None:
        interface = codex.get("interface")
        if not isinstance(interface, dict):
            problems.append(".codex-plugin/plugin.json: interface must be an object")
        else:
            for required in (
                "displayName",
                "shortDescription",
                "longDescription",
                "developerName",
                "category",
                "capabilities",
                "defaultPrompt",
            ):
                if not interface.get(required):
                    problems.append(f".codex-plugin/plugin.json: interface missing '{required}'")

    marketplace, _ = load_json_object(MARKETPLACE_PATH)
    if marketplace is not None and claude is not None:
        for index, plugin in enumerate(marketplace.get("plugins", [])):
            if isinstance(plugin, dict) and plugin.get("name") == claude.get("name"):
                if plugin.get("version") != claude.get("version"):
                    problems.append(
                        f".claude-plugin/marketplace.json: plugins[{index}].version must match plugin.json"
                    )
                if plugin.get("strict") is not True:
                    problems.append(
                        f".claude-plugin/marketplace.json: plugins[{index}].strict must be true"
                    )

    return problems


def main() -> int:
    problems: list[str] = []
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())

    if not skill_dirs:
        problems.append("skills directory has no skill folders")

    for skill_dir in skill_dirs:
        problems.extend(validate_skill(skill_dir))

    problems.extend(validate_marketplace())
    problems.extend(validate_plugin_manifests())

    if problems:
        for problem in problems:
            error(problem)
        return 1

    print(f"validated {len(skill_dirs)} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
