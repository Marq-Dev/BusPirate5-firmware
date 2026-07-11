#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "tools" / "apply_deep_format.py"

text = PATCHER.read_text(encoding="utf-8")

replacements = {
    "updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)":
        "updated, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.DOTALL)",
    'if "host-tests:" not in workflow:':
        'if False and "host-tests:" not in workflow:',
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"automation patch anchor missing: {old}")
    text = text.replace(old, new, 1)

old_write = '''def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8", newline="\\n")
'''
new_write = '''def write(path: str, content: str) -> None:
    target = ROOT / path
    raw = target.read_bytes()
    newline = b"\\r\\n" if b"\\r\\n" in raw else b"\\n"
    normalized = content.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    encoded = normalized.encode("utf-8")
    if newline == b"\\r\\n":
        encoded = encoded.replace(b"\\n", b"\\r\\n")
    target.write_bytes(encoded)
'''
if old_write not in text:
    raise SystemExit("newline-preserving writer anchor missing")
text = text.replace(old_write, new_write, 1)

# Avoid a translation-table migration for one option description. The format
# usage lines remain explicit, while the option reuses the existing format help
# key. This keeps the change focused and avoids unrelated translation churn.
text = text.replace("T_HELP_DISK_FORMAT_DEEP", "T_HELP_DISK_FORMAT")

PATCHER.write_text(text, encoding="utf-8", newline="\n")
subprocess.check_call([sys.executable, "-m", "py_compile", str(PATCHER)])
subprocess.check_call([sys.executable, str(PATCHER)], cwd=ROOT)

runner = ROOT / "tests" / "host" / "run_host_tests.sh"
os.chmod(runner, runner.stat().st_mode | 0o111)
subprocess.check_call(
    ["git", "-c", "core.whitespace=cr-at-eol", "diff", "--check"],
    cwd=ROOT,
)
