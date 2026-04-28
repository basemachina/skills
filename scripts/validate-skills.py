#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
INSTALL_METADATA_RE = re.compile(r"^\s*github-[A-Za-z0-9_-]+:")


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

    for required in ("name", "description"):
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
        for required in ("name", "source", "description", "version", "license", "homepage", "repository", "skills"):
            if not plugin.get(required):
                problems.append(f".claude-plugin/marketplace.json: plugins[{index}] missing '{required}'")
        skills_path = plugin.get("skills")
        if isinstance(skills_path, str) and not (ROOT / skills_path).exists():
            problems.append(f".claude-plugin/marketplace.json: plugins[{index}].skills path does not exist")

    return problems


def main() -> int:
    problems: list[str] = []
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())

    if not skill_dirs:
        problems.append("skills directory has no skill folders")

    for skill_dir in skill_dirs:
        problems.extend(validate_skill(skill_dir))

    problems.extend(validate_marketplace())

    if problems:
        for problem in problems:
            error(problem)
        return 1

    print(f"validated {len(skill_dirs)} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
