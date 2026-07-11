#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build.yaml"

base_workflow = subprocess.check_output(
    ["git", "show", "origin/main:.github/workflows/build.yaml"],
    cwd=ROOT,
).decode("utf-8")

anchor = "jobs:\n  build:\n"
replacement = '''jobs:
  host-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run host and contract tests
        run: |
          python3 -m unittest tests/test_deep_format_contract.py -v
          bash tests/host/run_host_tests.sh

  build:
    needs: host-tests
'''
if base_workflow.count(anchor) != 1:
    raise SystemExit(
        f"expected one final-workflow anchor, found {base_workflow.count(anchor)}"
    )
WORKFLOW.write_text(base_workflow.replace(anchor, replacement, 1), encoding="utf-8")

for relative in (
    "tools/apply_deep_format.py",
    "tools/run_deep_format_gate.py",
    "tools/finalize_deep_format.py",
    ".github/workflows/deep-format-diagnostic.yml",
    "docs/deep-format-ci-trigger.txt",
):
    path = ROOT / relative
    if path.exists():
        path.unlink()

for relative in (
    "build-host",
    "build/rp2350-final",
    "build/rp2040-final",
):
    path = ROOT / relative
    if path.exists():
        shutil.rmtree(path)

subprocess.check_call(["git", "diff", "--check"], cwd=ROOT)
