#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

# The GitHub Actions token can push source changes but cannot update workflow
# files. Workflow cleanup is performed afterward through the authorized GitHub
# connector in one atomic commit.
for relative in (
    "tools/apply_deep_format.py",
    "tools/run_deep_format_gate.py",
    "tools/finalize_deep_format.py",
    "docs/deep-format-ci-trigger.txt",
    "deep-format-finalize.log",
):
    path = ROOT / relative
    if path.exists():
        path.unlink()

for cache_dir in sorted(ROOT.rglob("__pycache__"), reverse=True):
    if cache_dir.is_dir():
        shutil.rmtree(cache_dir)

for relative in (
    "build-host",
    "build/rp2350-final",
    "build/rp2040-final",
):
    path = ROOT / relative
    if path.exists():
        shutil.rmtree(path)

subprocess.check_call(
    ["git", "-c", "core.whitespace=cr-at-eol", "diff", "--check"],
    cwd=ROOT,
)
