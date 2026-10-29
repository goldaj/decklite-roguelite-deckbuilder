"""Offline contract tests for real DeckLite combat, using a fake pygame import.

No graphics, save file, or game loop is initialized.
"""
import importlib.util
from pathlib import Path
import random
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
GAME_PATH = ROOT / "main.py"
SAVE = {"version": 1, "essence": 0, "upgrades": {"max_hp": 0, "energy": 0},
        "unlocks": {"beam_card": False}, "relics_unlocked": []}


def load_game():
    fake_pygame = types.ModuleType("pygame")
    spec = importlib.util.spec_from_file_location("decklite_rules_under_test", GAME_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"pygame": fake_pygame}):
        spec.loader.exec_module(module)
    return module


class DeckLiteBossTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game()

    def setUp(self):
        random.seed(20261029)
        self.run = self.module.Run(SAVE)

    def test_dead_enemy_cannot_attack_after_lethal_card(self):
        self.run.enemy.hp = 0
        self.run.enemy.intent = ("atk", 999)
        hp_before = self.run.player.hp
        outcome = self.run.end_turn()
        self.assertEqual(self.run.player.hp, hp_before)
        self.assertEqual(self.run.floor, 2)
        self.assertEqual(outcome, "reward")
        self.assertFalse(self.run.done)

    def test_live_enemy_still_attacks_normally(self):
        self.run.enemy.intent = ("atk", 8)
        self.run.player.block = 3
        before = self.run.player.hp
        self.run.end_turn()
        self.assertEqual(self.run.player.hp, before - 5)
        self.assertEqual(self.run.floor, 1)

    def test_normal_boss_ends_at_a_real_player_choice(self):
        self.run.floor = 10
        self.run.enemy = self.module.enemy_for_floor(10)
        self.run.enemy.hp = 0
        self.run.enemy.intent = ("atk", 999)
        before = self.run.player.hp
        self.assertEqual(self.run.end_turn(), "extreme_choice")
        self.assertTrue(self.run.awaiting_extreme)
        self.assertEqual(self.run.player.hp, before)
        self.assertEqual(self.run.floor, 10)
        self.assertFalse(self.run.done)
        self.assertIsNone(self.run.end_turn())
        self.assertEqual(self.run.floor, 10)

    def test_retirement_banks_a_victory_without_extreme(self):
        self.run.floor = 10
        self.run.enemy.hp = 0
        self.run.end_turn()
        self.assertTrue(self.run.retire_victory())
        self.assertTrue(self.run.done)
        self.assertTrue(self.run.win)
        self.assertEqual(self.run.essence_gain(), 228)
        self.assertFalse(self.run.retire_victory())
        self.assertFalse(self.run.accept_extreme())

    def test_accept_extreme_gets_fresh_hand_energy_and_partial_heal(self):
        self.run.floor = 10
        self.run.enemy.hp = 0
        self.run.player.hp = 10
        self.run.end_turn()
        self.assertTrue(self.run.accept_extreme())
        self.assertFalse(self.run.awaiting_extreme)
        self.assertEqual(self.run.floor, 11)
        self.assertEqual(self.run.player.hp, 10 + self.run.player.max_hp // 4)
        self.assertEqual(self.run.player.energy, self.run.player.energy_base)
        self.assertGreater(len(self.run.player.hand), 0)
        self.assertGreater(self.run.enemy.hp, 0)
        self.assertFalse(self.run.accept_extreme())

    def test_extreme_boss_can_still_be_defeated(self):
        self.run.floor = 10
        self.run.enemy.hp = 0
        self.run.end_turn()
        self.run.accept_extreme()
        self.run.enemy.hp = 0
        self.run.enemy.intent = ("atk", 999)
        remaining_hp = self.run.player.hp
        self.run.end_turn()
        self.assertTrue(self.run.done)
        self.assertTrue(self.run.win)
        self.assertEqual(self.run.player.hp, remaining_hp)

    def test_ordinary_floor_four_event_remains_available(self):
        self.run.floor = 3
        self.run.enemy = self.module.enemy_for_floor(3)
        self.run.enemy.hp = 0
        self.assertEqual(self.run.end_turn(), "event")
        self.assertEqual(self.run.floor, 4)


if __name__ == "__main__":
    unittest.main()
