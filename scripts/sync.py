#!/usr/bin/env python3
"""Copy the canonical skill, license, and icon into every plugin folder.

Plugin folders must hold real files (no symlinks) because each marketplace
installs only the plugin folder. Run with --check to fail on drift instead.
"""

import argparse
import filecmp
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = [ROOT / "claude/sleuth-insights", ROOT / "chatgpt/sleuth-insights"]
SHARED = [
    ("skills", "skills"),
    ("LICENSE", "LICENSE"),
    ("assets/sleuth-icon.png", "assets/sleuth-icon.png"),
]


def tree_differs(source, target):
    if source.is_file():
        return not target.is_file() or not filecmp.cmp(source, target, shallow=False)
    if not target.is_dir():
        return True
    compare = filecmp.dircmp(source, target)
    if compare.left_only or compare.right_only or compare.funny_files:
        return True
    _, mismatch, errors = filecmp.cmpfiles(source, target, compare.common_files, shallow=False)
    return bool(mismatch or errors) or any(
        tree_differs(source / name, target / name) for name in compare.common_dirs
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without copying")
    args = parser.parse_args()

    for source, _ in SHARED:
        if any(path.is_symlink() for path in [ROOT / source, *(ROOT / source).rglob("*")]):
            sys.exit(f"{source} contains a symlink; plugin folders need real files.")

    drift = []
    for plugin in PLUGINS:
        for source_rel, target_rel in SHARED:
            source, target = ROOT / source_rel, plugin / target_rel
            if not tree_differs(source, target):
                continue
            drift.append(target.relative_to(ROOT))
            if args.check:
                continue
            if target.is_dir():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copyfile(source, target)

    if args.check and drift:
        print("Out of sync with the canonical copies (run scripts/sync.py):", file=sys.stderr)
        for path in drift:
            print(f"  {path}", file=sys.stderr)
        sys.exit(1)
    print("Updated: " + ", ".join(map(str, drift)) if drift else "All plugin folders in sync.")


if __name__ == "__main__":
    main()
