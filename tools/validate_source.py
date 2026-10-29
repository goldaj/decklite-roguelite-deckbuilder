"""Offline source and starter-save validation for DeckLite."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> list[str]:
    errors = []
    try:
        ast.parse((root / "main.py").read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, SyntaxError) as exc:
        errors.append(f"main.py: {exc}")

    try:
        state = json.loads((root / "save.default.json").read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            return errors + ["save.default.json: expected a JSON object"]
        if type(state.get("version")) is not int or state["version"] < 1:
            errors.append("save.default.json: invalid version")
        if type(state.get("essence")) is not int or state["essence"] < 0:
            errors.append("save.default.json: essence must be a nonnegative integer")
        upgrades = state.get("upgrades")
        if not isinstance(upgrades, dict) or any(type(v) is not int or v < 0 for v in upgrades.values()):
            errors.append("save.default.json: invalid upgrades")
        unlocks = state.get("unlocks")
        if not isinstance(unlocks, dict) or any(type(v) is not bool for v in unlocks.values()):
            errors.append("save.default.json: invalid unlocks")
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"save.default.json: {exc}")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        raise SystemExit("\n".join(problems))
    print("OK: DeckLite source syntax and default save schema")
