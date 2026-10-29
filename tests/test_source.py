import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_source import validate, ROOT


class OfflineSourceTests(unittest.TestCase):
    def test_reference_source(self):
        self.assertEqual(validate(), [])

    def test_invalid_default_save_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'main.py').write_text('pass\n', encoding='utf-8')
            (root / 'save.default.json').write_text(json.dumps({
                'version': 1, 'essence': -4, 'upgrades': {'hp': 0},
                'unlocks': {'card': 'yes'}
            }), encoding='utf-8')
            errors = validate(root)
            self.assertTrue(any('essence' in x for x in errors))
            self.assertTrue(any('unlocks' in x for x in errors))


if __name__ == '__main__':
    unittest.main()
