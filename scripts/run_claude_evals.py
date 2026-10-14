#!/usr/bin/env python3
"""Run the Claude plugin's eval suite against a temporary copy of the plugin.

The suite lives in claude/evals so it never ships inside the submitted plugin
folder, but `claude plugin eval` only reads suites inside the plugin. This
copies both into a temporary directory, passes --trust-plugin because the code
comes from this repository, keeps the HTML report local (--no-publish), and
writes results under dist/claude-evals/. Every other argument goes straight to
`claude plugin eval`, for example:

    python3 scripts/run_claude_evals.py --runs 1 --case dataset-rows
"""

from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "claude/sleuth-insights"
EVALS = ROOT / "claude/evals"


def main():
    if shutil.which("claude") is None:
        sys.exit("The claude CLI is not on PATH. Install Claude Code 2.1.283 or later.")

    output = ROOT / "dist/claude-evals" / datetime.now().strftime("%Y%m%d-%H%M%S")
    with tempfile.TemporaryDirectory(prefix="sleuth-evals-") as temp:
        plugin = Path(temp) / PLUGIN.name
        shutil.copytree(PLUGIN, plugin)
        shutil.copytree(EVALS, plugin / "evals")
        command = [
            "claude", "plugin", "eval", str(plugin),
            "--trust-plugin", "--no-publish", "--output-dir", str(output),
            *sys.argv[1:],
        ]
        print("Results:", output.relative_to(ROOT), flush=True)
        sys.exit(subprocess.run(command).returncode)


if __name__ == "__main__":
    main()
