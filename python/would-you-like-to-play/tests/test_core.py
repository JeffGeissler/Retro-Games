import copy
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from retro_play.commands import CommandRouter
from retro_play.controller import Controller
from retro_play.games.tic_tac_toe import IllegalMove, TicTacToe, choose_move
from retro_play.registry import default_registry
from retro_play.session import Phase, Session
from retro_play.storage import Preferences, Store


class RulesTests(unittest.TestCase):
    def test_illegal_moves_leave_position_unchanged(self):
        game = TicTacToe().play(5)
        for move in (0, 10, -1, 5, True, 1.0, "1", None):
            with self.subTest(move=move), self.assertRaises(IllegalMove):
                game.play(move)
        self.assertEqual(game.history, (5,))

    def test_win_draw_and_terminal_move_rejection(self):
        win = TicTacToe((1, 4, 2, 5, 3))
        self.assertEqual(win.outcome, "X")
        self.assertEqual(win.winning_cells, (1, 2, 3))
        self.assertEqual(win.legal_moves, ())
        with self.assertRaises(IllegalMove):
            win.play(9)
        draw = TicTacToe((1, 2, 3, 5, 4, 6, 8, 7, 9))
        self.assertEqual(draw.outcome, "draw")
        self.assertEqual(draw.legal_moves, ())

    def test_beginner_uses_only_legal_moves_and_can_vary(self):
        game = TicTacToe((5, 1, 9))
        rng = random.Random(128)
        choices = {choose_move(game, "beginner", rng) for _ in range(100)}
        self.assertEqual(choices, set(game.legal_moves))
        with self.assertRaises(ValueError):
            choose_move(game, "invalid")

    def test_unbeatable_against_every_human_continuation_as_either_mark(self):
        terminal_counts = {}
        for computer in ("X", "O"):
            leaves = 0

            def visit(game):
                nonlocal leaves
                if game.outcome:
                    leaves += 1
                    self.assertIn(game.outcome, (computer, "draw"), game.history)
                    return
                if game.current_player == computer:
                    visit(game.play(choose_move(game, "unbeatable")))
                else:
                    for move in game.legal_moves:
                        visit(game.play(move))

            visit(TicTacToe())
            self.assertGreater(leaves, 50)
            terminal_counts[computer] = leaves
        print("\nUnbeatable exhaustive terminal branches:", terminal_counts)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.registry = default_registry()
        self.session = Session(self.registry)

    def test_registry_and_state_transitions(self):
        self.assertEqual([g.id for g in self.registry.catalog()], ["tic-tac-toe"])
        with self.assertRaises(ValueError):
            self.registry.register(self.registry.get("tic-tac-toe"))
        with self.assertRaises(ValueError):
            self.session.start("tic-tac-toe", "beginner", "X")
        self.session.connect()
        self.session.start("tic-tac-toe", "beginner", "X")
        self.session.move(1)
        with self.assertRaises(ValueError):
            self.session.move(2)
        self.session.pause()
        before = self.session.game
        self.session.computer_step()
        self.assertIs(self.session.game, before)
        with self.assertRaises(ValueError):
            self.session.move(2)
        self.session.resume()
        self.session.computer_step()
        self.assertEqual(len(self.session.game.history), 2)
        self.session.catalog()
        self.assertIsNone(self.session.game)

    def test_computer_starts_when_human_is_o(self):
        self.session.connect()
        self.session.start("tic-tac-toe", "unbeatable", "O")
        self.assertTrue(self.session.computer_pending)
        self.session.computer_step()
        self.assertEqual(self.session.game.history, (5,))
        self.assertFalse(self.session.computer_pending)

    def test_save_round_trip_for_every_phase_and_pending_turn(self):
        for history, phase, human in (
            ((), Phase.PLAYING, "O"),
            ((1,), Phase.PLAYING, "X"),
            ((1, 5), Phase.PAUSED, "X"),
            ((1, 4, 2, 5, 3), Phase.FINISHED, "X"),
            ((1, 2, 3, 5, 4, 6, 8, 7, 9), Phase.FINISHED, "O"),
        ):
            with self.subTest(history=history, phase=phase):
                session = Session(self.registry)
                session.connect()
                session.start("tic-tac-toe", "unbeatable", human)
                session.game, session.phase = TicTacToe(history), phase
                encoded = json.loads(json.dumps(session.snapshot()))
                restored = Session.restore(self.registry, encoded)
                self.assertEqual(restored.snapshot(), session.snapshot())
                self.assertEqual(restored.computer_pending, session.computer_pending)

    def test_rejects_impossible_or_unknown_saves(self):
        self.session.connect()
        self.session.start("tic-tac-toe", "beginner", "X")
        valid = self.session.snapshot()
        for key, value in (("version", 2), ("version", True), ("game_id", "missing"),
                           ("phase", "finished"), ("phase", "catalog"),
                           ("human", "Z"), ("difficulty", "hard"),
                           ("game", {"history": [1, 1]}),
                           ("game", {"history": [True]}),
                           ("game", {"history": [1, 4, 2, 5, 3, 6]})):
            invalid = copy.deepcopy(valid)
            invalid[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                Session.restore(self.registry, invalid)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name))
        self.controller = Controller(self.store)
        self.router = CommandRouter(self.controller)
        self.router.execute("skip")

    def command(self, command):
        result = self.router.execute(command)
        self.assertTrue(result.ok, result.message)
        return result

    def test_command_round_trip_and_preferences(self):
        self.command("difficulty unbeatable")
        self.command("mark O")
        self.command("play tic-tac-toe")
        self.controller.session.computer_step()
        self.command("1")
        self.command("save")
        before = self.controller.session.snapshot()
        self.command("theme modern")
        self.assertEqual(self.controller.session.snapshot(), before)
        self.command("catalog")
        self.command("load")
        self.assertEqual(self.controller.session.phase, Phase.PAUSED)
        self.assertEqual(self.controller.session.game.history, tuple(before["game"]["history"]))
        self.command("resume")
        self.assertEqual(self.controller.session.snapshot(), before)
        second = Controller(self.store)
        self.assertEqual(second.preferences, Preferences("modern", "unbeatable", "O", True))

    def test_bad_commands_and_loads_do_not_mutate_game(self):
        self.command("play")
        before = self.controller.session.snapshot()
        for command in ("move zero", "move 10", "play", "load", "resume", "theme purple",
                        "mark Z", "help extra", "\"unterminated", "move 1 2"):
            self.assertFalse(self.router.execute(command).ok, command)
            self.assertEqual(self.controller.session.snapshot(), before)
        self.command("catalog")
        self.store.save_game({"version": 99})
        original = self.controller.session
        self.assertFalse(self.router.execute("load").ok)
        self.assertIs(self.controller.session, original)

    def test_persistence_failure_retains_previous_save_and_session(self):
        self.command("play")
        self.command("save")
        prior = self.store.load_game()
        self.command("1")
        with patch("retro_play.storage.os.replace", side_effect=OSError("disk full")):
            self.assertFalse(self.router.execute("catalog").ok)
            self.assertEqual(self.controller.session.phase, Phase.PLAYING)
            self.assertFalse(self.router.execute("theme modern").ok)
            self.assertEqual(self.controller.preferences.theme, "terminal")
        self.assertEqual(self.store.load_game(), prior)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [Path(self.temp.name) / "session.json"])

    def test_corrupt_preferences_and_missing_save_report_errors(self):
        self.assertFalse(self.router.execute("load").ok)
        (Path(self.temp.name) / "preferences.json").write_text("not JSON")
        controller = Controller(self.store)
        self.assertEqual(controller.preferences, Preferences())
        self.assertIn("using defaults", controller.notice)

    def test_shutdown_saves_and_speech_is_replaceable(self):
        class RecordingSpeech:
            def __init__(self):
                self.stopped = False

            def speak(self, text):
                pass

            def stop(self):
                self.stopped = True

        speech = RecordingSpeech()
        c = Controller(self.store, speech=speech)
        c.session.connect()
        c.start()
        c.shutdown()
        self.assertTrue(speech.stopped)
        self.assertEqual(self.store.load_game(), c.session.snapshot())


if __name__ == "__main__":
    unittest.main()
