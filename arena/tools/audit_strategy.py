"""Audit a strategy for calendar leakage (SPEC §4.2): 4-digit years, `season ==` constants,
literal date lists, and (warning only) long numeric literal lists that may be memorised outcomes.

    python3 -m arena.tools.audit_strategy path/to/strategy.py
Exit code 1 on a hard violation. Also used by `submit_strategy`.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_YEAR = re.compile(r"(?<![\d.])(19[89]\d|20[0-4]\d)(?![\d.])")
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/(?:19|20)\d\d\b")


def audit(src: str) -> tuple[list[str], list[str]]:
    """Returns (violations, warnings)."""
    errs, warns = [], []
    for m in _YEAR.finditer(src):
        line = src.count("\n", 0, m.start()) + 1
        errs.append(f"line {line}: 4-digit year {m.group(0)}")
    for m in _DATE.finditer(src):
        line = src.count("\n", 0, m.start()) + 1
        errs.append(f"line {line}: literal date {m.group(0)}")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"syntax error: {e}"], warns
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            names = [n for n in ast.walk(node.left) if isinstance(n, (ast.Name, ast.Attribute))]
            if any((isinstance(n, ast.Name) and n.id == "season") or (isinstance(n, ast.Attribute) and n.attr == "season") for n in names):
                for op, right in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Eq, ast.NotEq, ast.In, ast.NotIn)) and isinstance(right, (ast.Constant, ast.List, ast.Tuple, ast.Set)):
                        errs.append(f"line {node.lineno}: comparison of `season` with a constant (season-specific rule)")
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            nums = [e for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) and not isinstance(e.value, bool)]
            if len(nums) >= 12 and len(nums) == len(node.elts):
                warns.append(f"line {node.lineno}: literal list of {len(nums)} numbers (memorised table?)")
    return errs, warns


def main(argv=None) -> int:
    path = Path((argv or sys.argv[1:])[0])
    errs, warns = audit(path.read_text())
    for w in warns:
        print("WARN", w)
    for e in errs:
        print("FAIL", e)
    print("ok" if not errs else f"{len(errs)} violation(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
