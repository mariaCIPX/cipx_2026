""Regression tests for the Traditional Mahjong game.

Run with: python -m unittest -v testcases.py
"""
import contextlib
import io
import unittest
from unittest.mock import patch

import play


class FixedRng:
    """Small deterministic RNG used to make draw tests repeatable."""
    def __init__(self, tile):
        self.tile = tile

    def choice(self, available):
        if self.tile not in available:
            raise AssertionError(f"{self.tile} is not available to draw")
        return self.tile


def make_state(computer_hand=None, human_hand=None):
    """Build a minimal valid game state for isolated turn tests."""
    computer_hand = computer_hand or ["d1", "d5", "d7", "d9"]
    human_hand = human_hand or ["d2", "d3", "d4", "d8"]
    dots = {f"d{i}": 4 for i in range(1, 10)}
    for tile in computer_hand + human_hand:
        dots[tile] -= 1
    dots = {tile: count for tile, count in dots.items() if count}
    return {
        "DOTS": dots,
        "play_tile": [list(computer_hand), list(human_hand)],
        "open_tile": [],
        "discard_tile": [[], []],
        "melds": [[], []],
        "current_player": play.COMP_PLAYER,
        "last_discard": None,
        "last_discarder": None,
        "round_over": False,
        "winner": None,
    }


class TestTileAndWinningRules(unittest.TestCase):
    def test_valid_tiles(self):
        self.assertTrue(play.valid_tile("d1"))
        self.assertTrue(play.valid_tile("D9"))
        self.assertFalse(play.valid_tile("d0"))
        self.assertFalse(play.valid_tile("d10"))

    def test_chow_and_pung(self):
        self.assertTrue(play.check_chow(["d3", "d4", "d5"]))
        self.assertFalse(play.check_chow(["d3", "d5", "d6"]))
        self.assertTrue(play.check_pung(["d2", "d2", "d2"]))
        self.assertFalse(play.check_pung(["d2", "d2", "d3"]))

    def test_pair_plus_chow_win(self):
        self.assertTrue(play.check_win(None, tiles=["d4", "d5", "d6", "d4", "d4"]))

    def test_pung_plus_pair_win(self):
        self.assertTrue(play.check_win(None, tiles=["d6", "d6", "d2", "d2", "d2"]))

    def test_non_winning_hand(self):
        self.assertFalse(play.check_win(None, tiles=["d1", "d3", "d5", "d7", "d9"]))


class TestDrawAndDiscard(unittest.TestCase):
    def test_draw_reduces_wall(self):
        state = make_state()
        before = sum(state["DOTS"].values())
        drawn = play.dist_tile(state, 1, FixedRng("d6"))
        self.assertEqual(drawn, ["d6"])
        self.assertEqual(sum(state["DOTS"].values()), before - 1)

    def test_discard_updates_hand_and_public_pile(self):
        state = make_state()
        self.assertTrue(play.discard_tile(state, play.COMP_PLAYER, "d1"))
        self.assertNotIn("d1", state["play_tile"][play.COMP_PLAYER])
        self.assertEqual(state["discard_tile"][play.COMP_PLAYER], ["d1"])
        self.assertEqual(state["open_tile"], ["d1"])

    def test_invalid_discard_does_not_change_hand(self):
        state = make_state()
        before = state["play_tile"][play.COMP_PLAYER].copy()
        self.assertFalse(play.discard_tile(state, play.COMP_PLAYER, "d2"))
        self.assertEqual(state["play_tile"][play.COMP_PLAYER], before)


class TestAutomaticComputerTurn(unittest.TestCase):
    def test_requested_draw_and_discard_sequence(self):
        state = make_state()
        # Force the example draw so the test does not depend on randomness.
        with patch.object(play, "dist_tile", return_value=["d6"]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                play.comp_process(state)
        text = output.getvalue()
        self.assertIn("COMPUTER_player current at hand tiles: ['d1', 'd5', 'd7', 'd9']", text)
        self.assertIn("The tile to draw: 'd6'", text)
        self.assertIn("COMPUTER_player tiles after draw: ['d1', 'd5', 'd6', 'd7', 'd9']", text)
        self.assertIn("COMPUTER_player automatically discards: d9", text)
        self.assertIn("COMPUTER_player current at hand tiles: ['d1', 'd5', 'd6', 'd7']", text)
        self.assertEqual(play.order_list(state["play_tile"][play.COMP_PLAYER]), ["d1", "d5", "d6", "d7"])
        self.assertEqual(state["discard_tile"][play.COMP_PLAYER], ["d9"])

    def test_explicit_strategy_edge_case_d2(self):
        state = make_state(
            computer_hand=["d2", "d3", "d5", "d8", "d8"],
            human_hand=["d4", "d4", "d6", "d7"],
        )
        # Make every d1 unavailable, matching the previously specified edge case.
        state["DOTS"].pop("d1", None)
        self.assertEqual(play.choose_computer_discard(state), "d2")


class TestHumanTurnDisplay(unittest.TestCase):
    def test_human_turn_shows_hand_before_and_after_draw(self):
        state = make_state()
        state["play_tile"][play.HUMAN_PLAYER] = ["d2", "d3", "d4", "d8"]
        with patch.object(play, "dist_tile", return_value=["d5"]) as draw_mock:
            with patch("builtins.input", side_effect=["D", "d8"]):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    play.human_process(state)
            text = output.getvalue()
            self.assertIn("HUMAN_player current at hand tiles: ['d2', 'd3', 'd4', 'd8']", text)
            self.assertIn("The tile to draw: 'd5'", text)
            self.assertIn("HUMAN_player tiles after draw: ['d2', 'd3', 'd4', 'd5', 'd8']", text)


if __name__ == "__main__":
    unittest.main()
