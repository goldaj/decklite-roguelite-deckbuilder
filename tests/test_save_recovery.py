"""DeckLite save recovery tests without loading Pygame or starting a display."""
import ast
import json
import os
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "main.py"


def load_saving_helpers(folder):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
    names = {"project_dir", "load_save", "save_save"}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    assert len(functions) == 3
    namespace = {"os": os, "json": json, "tempfile": tempfile,
                 "SAVE_FILENAME": "save.json", "__file__": str(Path(folder) / "main.py")}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


class SaveRecoveryTests(unittest.TestCase):
    def test_new_game_creates_save(self):
        with tempfile.TemporaryDirectory() as folder:
            mod = load_saving_helpers(folder)
            data = mod["load_save"]()
            self.assertEqual(data["essence"], 0)
            self.assertEqual(json.loads((Path(folder) / "save.json").read_text())["version"], 1)

    def test_truncated_json_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "save.json"
            original.write_text('{"essence":100,', encoding="utf-8")
            mod = load_saving_helpers(folder)
            self.assertEqual(mod["load_save"]()["essence"], 0)
            self.assertEqual((Path(folder) / "save.json.corrupt").read_text(), '{"essence":100,')

    def test_malformed_field_does_not_erase_other_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "save.json"
            original.write_text(json.dumps({
                "essence": "invalid", "upgrades": {"max_hp": "3", "energy": 2},
                "unlocks": {"beam_card": True}, "relics_unlocked": ["alpha", "alpha"]
            }))
            mod = load_saving_helpers(folder)
            loaded = mod["load_save"]()
            self.assertEqual(loaded["essence"], 0)
            self.assertEqual(loaded["upgrades"]["max_hp"], 3)
            self.assertTrue(loaded["unlocks"]["beam_card"])
            self.assertEqual(loaded["relics_unlocked"], ["alpha"])

    def test_failed_serialization_does_not_replace_existing_save(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "save.json"
            original.write_text('{"essence":42}', encoding="utf-8")
            mod = load_saving_helpers(folder)
            with self.assertRaises(TypeError):
                mod["save_save"]({"bad": object()})
            self.assertEqual(original.read_text(), '{"essence":42}')
            self.assertFalse(list(Path(folder).glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
