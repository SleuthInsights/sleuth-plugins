#!/usr/bin/env python3
"""Validate source, build one self-contained plugin ZIP, and verify its contents."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "sleuth-insights"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def https_url(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 1024, f"Invalid {label}")
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and parsed.hostname and not parsed.username
            and not parsed.password, f"{label} must be HTTPS without credentials")


def png_dimensions(data):
    require(data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR",
            "Icon must be an actual PNG")
    return struct.unpack(">II", data[16:24])


def validate(files, submission=False):
    manifest = json.loads(files["plugin.json"])
    config = json.loads(files["mcp.json"])
    require(manifest.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "Use the Agent Plugins 1.0 root manifest")
    require(manifest.get("name") == PLUGIN.name, "Manifest name must match its directory")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest["name"]) is not None
            and len(manifest["name"]) <= 64, "Invalid plugin name")
    require(re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", manifest.get("version", ""))
            is not None, "Use an explicit semantic version")
    allowed = {"$schema", "name", "version", "description", "author", "homepage",
               "repository", "license", "keywords", "extensions"}
    require(set(manifest) <= allowed, "Unsupported portable manifest fields")
    require(".app.json" not in files, "Public uploads cannot contain a root .app.json")
    for path, data in files.items():
        if path == "plugin.json" or path.endswith("/plugin.json"):
            extra = json.loads(data)
            require(extra.get("apps") is None and
                    extra.get("extensions", {}).get("com.openai", {}).get("apps") is None,
                    f"Public uploads cannot contain apps bindings: {path}")
        require(not any(part in {".git", ".venv", "node_modules", "__pycache__"}
                        or part.startswith(".env") for part in Path(path).parts),
                f"Unrelated or private file in plugin: {path}")

    settings = manifest["extensions"]["com.openai"]
    interface = settings["interface"]
    for field, limit in (("displayName", 30), ("shortDescription", 30),
                         ("longDescription", 4000), ("developerName", 80)):
        value = interface.get(field)
        require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit,
                f"{field} must be nonblank and at most {limit} characters")
    for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        https_url(interface.get(field), field)
    prompts = interface.get("defaultPrompt", [])
    if isinstance(prompts, str):
        prompts = [prompts]
    require(isinstance(prompts, list) and 1 <= len(prompts) <= 3, "Use one to three prompts")
    for prompt in prompts:
        require(isinstance(prompt, str) and prompt.strip() and len(prompt) <= 128
                and "\n" not in prompt and "\r" not in prompt and "@" not in prompt,
                "Prompts must be nonblank, single-line, <=128 characters, without mentions")
    require(len({" ".join(p.split()) for p in prompts}) == len(prompts), "Duplicate prompts")
    for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
        if key not in interface:
            continue
        path = interface[key]
        require(isinstance(path, str) and path.startswith("./")
                and ".." not in Path(path).parts, f"Invalid contained path: {key}")
        data = files[path[2:]]
        width, height = png_dimensions(data)
        minimum = 256 if key.startswith("logo") else 48
        require(minimum <= width == height <= 4096 and len(data) <= 5 * 1024 * 1024,
                f"Invalid {key} dimensions or size")
    for key in ("brandColor", "brandColorDark"):
        if key in interface:
            require(re.fullmatch(r"#[0-9a-fA-F]{6}", interface[key]) is not None,
                    f"Invalid {key}")

    require(config.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
            "Use the portable MCP schema")
    require(set(config) == {"$schema", "mcpServers"}, "Unsupported MCP configuration fields")
    require(set(config["mcpServers"]) == {"sleuth"}, "Expected one Sleuth MCP server")
    server = config["mcpServers"]["sleuth"]
    require(set(server) == {"type", "url"} and server["type"] == "streamable-http",
            "Use the existing HTTPS server and credential-free OAuth configuration")
    https_url(server["url"], "MCP endpoint")
    require(server["url"] == "https://mcp.sleuthapi.com/mcp", "Unexpected production endpoint")

    skills = [p for p in files if p.startswith("skills/") and p.endswith("/SKILL.md")]
    require(bool(skills), "The package must include the Sleuth skill")
    for path in skills:
        text = files[path].decode()
        require(text.startswith("---\n") and "\n---\n" in text[4:], f"Missing frontmatter: {path}")
        front = text.split("---\n", 2)[1]
        name = re.search(r"^name:\s*(\S+)\s*$", front, flags=re.M)
        require(name is not None and name.group(1) == Path(path).parent.name,
                f"Skill name must match its directory: {path}")
        require(re.search(r"^description:\s*\S", front, flags=re.M) is not None,
                f"Skill needs a trigger description: {path}")

    review = settings["review"]
    cases = review["test_cases"]
    for kind, count in (("positive", 5), ("negative", 3)):
        require(isinstance(cases.get(kind), list) and len(cases[kind]) == count,
                f"Expected {count} {kind} review cases")
        for case in cases[kind]:
            fields = ("description", "prompt", "tools_triggered", "expected_behavior") \
                if kind == "positive" else ("description", "prompt")
            for field in fields:
                require(isinstance(case.get(field), str) and case[field].strip(),
                        f"Review case missing {field}")
    require(isinstance(review.get("commerce"), bool), "Commerce declaration is required")
    publication = settings["publication"]
    require(bool(publication.get("release_notes")), "Release notes are required")
    require(isinstance(publication.get("countries"), list), "Record the country choice")
    demo = review.get("demo_recording_url")
    if demo:
        https_url(demo, "Demo recording")
    if submission:
        require(bool(demo), "Public-submission preparation incomplete: verified demo recording URL missing")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission", action="store_true",
                        help="Also require final local submission metadata; no upload occurs")
    args = parser.parse_args()
    files = {}
    for path in sorted(PLUGIN.rglob("*")):
        require(not path.is_symlink(), f"Symlinks cannot be packaged: {path}")
        if path.is_file():
            files[path.relative_to(PLUGIN).as_posix()] = path.read_bytes()
    manifest = validate(files, submission=args.submission)
    output = ROOT / "dist" / f"{manifest['name']}-{manifest['version']}.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(f"{manifest['name']}/{name}", (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        require(archive.testzip() is None, "ZIP integrity check failed")
        prefix = manifest["name"] + "/"
        require(all(name.startswith(prefix) for name in archive.namelist()), "Unexpected archive root")
        saved = {name[len(prefix):]: archive.read(name) for name in archive.namelist()}
        require(saved == files, "Archive does not match source")
        validate(saved, submission=args.submission)
    print(output)
    print(f"Verified {len(files)} packaged files; SHA-256 {hashlib.sha256(output.read_bytes()).hexdigest()}")
    if not manifest["extensions"]["com.openai"]["review"].get("demo_recording_url"):
        print("Development ZIP built. Public submission still needs the verified demo and review setup.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
