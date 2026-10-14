#!/usr/bin/env python3
"""Check a Claude plugin folder against Anthropic's directory pre-submission rules.

Mirrors https://claude.com/docs/plugins/pre-submission-checklist. Each finding
uses the portal's result levels: BLOCKS (can't submit), HOLD (a reviewer must
clear it), WARN (submittable). The portal's Validate button stays authoritative;
this catches the same problems before pushing.
"""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
KIB, MIB = 1024, 1024 * 1024
RESERVED_NAMES = {"claude", "anthropic", "official", "plugin", "mcp", "test"}
SYSTEM_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
WINDOWS_DEVICES = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                   *(f"lpt{i}" for i in range(1, 10))}
IMAGE_MAGIC = {b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpeg", b"GIF87a": "gif",
               b"GIF89a": "gif"}
FONT_SUFFIXES = {".ttf", ".otf", ".woff", ".woff2"}
COMPONENT_KEYS = {"skills", "commands", "agents", "hooks", "mcpServers", "lspServers",
                  "outputStyles", "workflows"}
URL_KEYS = ("homepage", "documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl")
PACKAGE_SOURCE_FILES = {".npmrc", "bunfig.toml", "uv.toml", "pip.conf", ".yarnrc", ".yarnrc.yml"}
SECRET_PATTERNS = [
    re.compile(r"\bsk_(?:live|test)?_?[A-Za-z0-9]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"Bearer\s+ey[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}"),
]
ENV_CREDENTIAL = re.compile(r"\$\{?[A-Z][A-Z0-9_]*(?:TOKEN|SECRET|API_KEY|APIKEY|PASSWORD)\}?")


class Report:
    def __init__(self):
        self.findings = []

    def add(self, level, message):
        self.findings.append((level, message))

    def count(self, level):
        return sum(1 for found, _ in self.findings if found == level)


def tracked_files():
    output = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"])
    return [ROOT / name for name in output.decode().split("\0") if name]


def is_image(path, data):
    if path.suffix.lower() == ".svg":
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    return any(data.startswith(magic) for magic in IMAGE_MAGIC)


def is_text(data):
    if b"\0" in data[:8192]:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def frontmatter_description(text):
    """Return (has_frontmatter, description_kind) using a minimal YAML reading."""
    if not text.startswith("---\n"):
        return False, None
    end = text.find("\n---", 4)
    if end == -1:
        return False, None
    lines = text[4:end].splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"description:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        following = lines[index + 1].lstrip() if index + 1 < len(lines) else ""
        if value.startswith(("[", "-")) or (not value and following.startswith("- ")):
            return True, "list"
        return True, "text"
    return True, None


def check_repository(report, plugin):
    files = tracked_files()
    total = sum(path.stat().st_size for path in files if path.exists())
    if total >= 50 * MIB or len(files) >= 10_000:
        report.add("BLOCKS", f"Repository too large to validate ({total / MIB:.1f} MiB, {len(files)} files)")

    seen = {}
    for path in files:
        rel = PurePosixPath(path.relative_to(ROOT).as_posix())
        for part in rel.parts:
            stem = part.split(".")[0].lower()
            if ":" in part or part.endswith((".", " ")) or stem in WINDOWS_DEVICES:
                report.add("BLOCKS", f"File name invalid on Windows or macOS: {rel}")
        key = str(rel).lower()
        if key in seen and seen[key] != str(rel):
            report.add("BLOCKS", f"Names differ only by capitalization: {seen[key]} / {rel}")
        seen[key] = str(rel)

    for part in plugin.relative_to(ROOT).parts:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", part):
            report.add("BLOCKS", f"Plugin path folder has unsupported characters: {part}")

    for attributes in [path for path in files if path.name == ".gitattributes"]:
        text = attributes.read_text()
        if re.search(r"\bexport-(?:ignore|subst)\b", text):
            report.add("BLOCKS", f"{attributes.relative_to(ROOT)} uses export-ignore/export-subst")
        governs_plugin = plugin == attributes.parent or attributes.parent in plugin.parents \
            or plugin in attributes.parents
        if governs_plugin and re.search(r"\bfilter=", text):
            report.add("BLOCKS", f"{attributes.relative_to(ROOT)} rewrites file contents with filter=")


def check_manifest(report, plugin):
    path = plugin / ".claude-plugin/plugin.json"
    if not path.is_file():
        report.add("BLOCKS", "Missing .claude-plugin/plugin.json")
        return {}
    try:
        manifest = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        report.add("BLOCKS", f"plugin.json is not valid JSON: {error}")
        return {}

    name = manifest.get("name", "")
    if not name.isascii():
        report.add("BLOCKS", f"Non-ASCII identifier: {name!r}")
    elif not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", name):
        report.add("WARN", f"name {name!r} isn't lowercase kebab-case of at most 64 characters")
    if name.lower() in RESERVED_NAMES or name.lower().startswith(("claude-", "anthropic-")):
        report.add("BLOCKS", f"Name is reserved: {name!r}")

    for label, value in (("displayName", manifest.get("displayName", "")),
                         ("author.name", manifest.get("author", {}).get("name", ""))):
        if value and not all(char.isascii() and char.isprintable() for char in value):
            report.add("BLOCKS", f"{label} must use one writing system without invisible characters")
    for field in ("description", "author", "version"):
        if not manifest.get(field):
            report.add("WARN", f"plugin.json doesn't set {field}")

    misplaced = COMPONENT_KEYS & set(manifest.get("experimental", {}))
    if misplaced:
        report.add("BLOCKS", f"Component keys inside experimental: {sorted(misplaced)}")
    for key in COMPONENT_KEYS & set(manifest):
        values = manifest[key] if isinstance(manifest[key], list) else [manifest[key]]
        for value in values:
            if isinstance(value, str) and not value.startswith("https://"):
                resolved = (plugin / value).resolve()
                if not value.startswith("./") or plugin.resolve() not in [resolved, *resolved.parents]:
                    report.add("BLOCKS", f"{key} path must start with ./ and stay inside the plugin: {value}")

    icon = manifest.get("icon")
    if icon:
        resolved = (plugin / icon).resolve()
        if not icon.startswith("./") or plugin.resolve() not in resolved.parents or not resolved.is_file():
            report.add("BLOCKS", f"icon must be an image file inside the plugin: {icon}")
        elif not is_image(resolved, resolved.read_bytes()[:16]):
            report.add("BLOCKS", f"icon isn't a PNG, JPEG, GIF, WebP, or SVG image: {icon}")
    for key in URL_KEYS:
        if key in manifest and not str(manifest[key]).startswith("https://"):
            report.add("BLOCKS", f"{key} must be an https:// URL")
    return manifest


def check_readme_and_license(report, plugin, manifest):
    readme = next((p for p in plugin.iterdir() if p.name.lower() in {"readme.md", "readme"}), None)
    if readme is None:
        report.add("BLOCKS", "README missing")
    else:
        prose = re.sub(r"```.*?```", " ", readme.read_text(), flags=re.S)
        words = len(re.findall(r"[A-Za-z0-9][\w'’-]*", prose))
        if words < 40:
            report.add("BLOCKS", f"README too short ({words} words outside code blocks; need 40)")
    if not (plugin / "LICENSE").is_file() and not manifest.get("license"):
        report.add("BLOCKS", "License missing")


def check_files(report, plugin):
    files = [path for path in plugin.rglob("*") if path.is_file() or path.is_symlink()]
    if len(files) > 512:
        report.add("HOLD", f"Plugin has {len(files)} files; keep it to 512 or fewer")
    for path in files:
        rel = path.relative_to(plugin)
        if path.is_symlink():
            report.add("BLOCKS", f"Symbolic link where a regular file is required: {rel}")
            continue
        if path.name in SYSTEM_FILES or "__MACOSX" in rel.parts:
            report.add("BLOCKS", f"This is a macOS or Windows system file: {rel}")
        if path.name in PACKAGE_SOURCE_FILES:
            report.add("HOLD", f"Package-manager source configuration in plugin: {rel}")
        if path.suffix in {".mcpb", ".dxt"}:
            report.add("HOLD", f"Bundled MCP server not inspected: {rel}")
        size = path.stat().st_size
        data = path.read_bytes()
        if size >= 5 * MIB:
            report.add("BLOCKS", f"File over 5 MiB: {rel}")
        if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
            report.add("BLOCKS", f"Git LFS pointer instead of the file: {rel}")
        image, font = is_image(path, data), path.suffix.lower() in FONT_SUFFIXES
        if not image and not font:
            if size >= 256 * KIB:
                report.add("HOLD", f"Non-image file over 256 KiB: {rel}")
            if not is_text(data):
                report.add("HOLD", f"Binary file the validator can't inspect: {rel}")
                continue
            text = data.decode("utf-8")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    report.add("BLOCKS", f"Possible real credential in {rel}")
            if ENV_CREDENTIAL.search(text):
                report.add("HOLD", f"Uses a credential from the user's environment in {rel}")
        if rel.parts[0] == "skills" and path.name.lower() == "skill.md" and path.name != "SKILL.md":
            report.add("BLOCKS", f"Skill file must be named SKILL.md exactly: {rel}")


def check_mcp(report, plugin):
    path = plugin / ".mcp.json"
    if not path.exists():
        return
    try:
        config = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        report.add("BLOCKS", f".mcp.json can't be parsed: {error}")
        return
    servers = config.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        report.add("BLOCKS", ".mcp.json needs a non-empty mcpServers object")
        return
    for name, server in servers.items():
        if "command" in server:
            command = " ".join([server["command"], *server.get("args", [])])
            if "${CLAUDE_PLUGIN_ROOT}" not in command or re.search(r"\s-c\s|\$\(|`|\*", command):
                report.add("HOLD", f"MCP server command wasn't read: {name}")
            continue
        url = server.get("url", "")
        if server.get("type") not in {"http", "sse", "ws"}:
            report.add("BLOCKS", f"MCP server {name} needs type http, sse, or ws")
        if not (url == "" or url.startswith(("https://", "wss://")) or url.startswith("${user_config.")):
            report.add("BLOCKS", f"MCP server URL is not https: {name}")
        for header, value in server.get("headers", {}).items():
            if "${user_config." not in str(value):
                report.add("BLOCKS", f"Secret in MCP headers: {name}.{header}")


def check_components(report, plugin):
    hooks = plugin / "hooks/hooks.json"
    if hooks.exists():
        try:
            if not isinstance(json.loads(hooks.read_text()).get("hooks", {}), dict):
                report.add("BLOCKS", "hooks.json is invalid: hooks must be an object")
        except json.JSONDecodeError:
            report.add("BLOCKS", "hooks.json is invalid")
    documents = list((plugin / "skills").glob("*/SKILL.md")) + list((plugin / "commands").glob("*.md")) \
        + list((plugin / "agents").glob("*.md"))
    for document in documents:
        rel = document.relative_to(plugin)
        has_frontmatter, kind = frontmatter_description(document.read_text())
        if not has_frontmatter:
            report.add("WARN", f"No front matter in {rel}")
        elif kind is None:
            report.add("WARN", f"No description in {rel}")
        elif kind != "text":
            report.add("BLOCKS", f"description must be a single text value in {rel}")
        if document.name == "SKILL.md":
            match = re.search(r"^name:\s*(\S+)\s*$", document.read_text(), flags=re.M)
            if match and match.group(1) != document.parent.name:
                report.add("WARN", f"Skill name {match.group(1)!r} doesn't match its folder in {rel}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", type=Path, help="Folder that contains .claude-plugin/plugin.json")
    parser.add_argument("--strict", action="store_true", help="Also fail on HOLD and WARN findings")
    args = parser.parse_args()
    plugin = args.plugin.resolve()

    report = Report()
    check_repository(report, plugin)
    manifest = check_manifest(report, plugin)
    check_readme_and_license(report, plugin, manifest)
    check_files(report, plugin)
    check_mcp(report, plugin)
    check_components(report, plugin)

    for level, message in report.findings:
        print(f"{level:6}  {message}")
    blocks, holds, warns = report.count("BLOCKS"), report.count("HOLD"), report.count("WARN")
    print(f"{plugin.relative_to(ROOT)}: {blocks} blocking, {holds} held for review, {warns} warnings")
    if blocks or (args.strict and (holds or warns)):
        sys.exit(1)


if __name__ == "__main__":
    main()
