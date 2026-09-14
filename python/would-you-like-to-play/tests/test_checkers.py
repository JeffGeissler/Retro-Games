import json
from pathlib import Path
import sys
import tempfile
import unittest
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from retro_play.games.checkers import Checkers, parse_path
from retro_play.opponents.checkers import search, Budget, SearchCancelled
from retro_play.opponents.service import SearchService
from retro_play.controller import Controller
from retro_play.storage import Store
from retro_play.ui.window import MainWindow

QUIET = ((1,6),(32,28),(6,1),(30,25),(3,7),(25,30),(7,11),(30,25),
(11,8),(28,32),(8,4),(25,30),(4,8),(32,27),(8,4),(27,31),
(1,5),(30,26),(5,1),(31,27),(4,8),(26,30),(1,6),(30,25),
(8,11),(27,32),(11,15),(32,27),(15,11),(27,31),(6,9),(31,27),
(9,13),(27,32),(13,17),(25,21),(17,14),(32,28),(11,7),(21,25),
(14,10),(28,32),(10,6),(32,27),(6,1),(25,22),(7,3),(27,24),
(3,8),(22,18),(8,3),(18,15),(3,7),(15,18),(1,5),(24,27),
(7,11),(18,14),(5,1),(14,10),(11,8),(27,32),(8,4),(10,15),
(4,8),(15,10),(8,11),(32,27),(11,8),(10,14),(1,5),(27,24),
(8,12),(24,28),(12,8),(14,18),(8,3),(18,14),(3,7),(14,10))

class CheckersRulesTests(unittest.TestCase):
    def test_english_not_international(self):
        game = Checkers()
        self.assertEqual(game._board.variant, 'english')
        self.assertEqual(len(game.pieces), 32)
        self.assertEqual(game.pieces.count('B'), 12)
        self.assertEqual(game.pieces.count('W'), 12)
        self.assertEqual(game.current_player, 'B')
        self.assertEqual(set(Checkers('B:W18:B22').legal_moves), {(22,25),(22,26)})
        self.assertEqual(set(Checkers('B:WK20:BK10').legal_moves),
                         {(10,15),(10,14),(10,7),(10,6)})

    def test_forced_full_capture_and_no_longest_priority(self):
        game = Checkers('B:W18,26:B14')
        for move in ((14,23), (14,17), (14,23,30,21), (True,23)):
            with self.assertRaises(ValueError): game.play(move)
        self.assertEqual(game.history, ())
        self.assertEqual(game.play((14,23,30)).outcome, 'B')
        self.assertEqual(set(Checkers('B:W18,26,10:B14,6').legal_moves),
                         {(14,23,30),(6,15,22,31)})
        self.assertEqual(parse_path('14x23x30'), (14,23,30))
        with self.assertRaises(ValueError): parse_path('33-28')

    def test_crowning_ends_turn_both_colors(self):
        game = Checkers('B:W10,26,27:B22')
        self.assertEqual(game.legal_moves, ((22,31),))
        game = game.play((22,31))
        self.assertEqual(game.pieces[30], 'BK')
        self.assertEqual(game.current_player, 'W')
        game = game.play((10,6))
        self.assertEqual(game.legal_moves, ((31,24),))
        white = Checkers('W:W11:B6,7').play((11,2))
        self.assertEqual(white.pieces[1], 'WK')
        self.assertEqual(white.current_player, 'B')

    def test_blocked_side_loses_and_terminal_rejects(self):
        game = Checkers('B:W5,6,10:B1')
        self.assertEqual(game.outcome, 'W')
        self.assertEqual(game.legal_moves, ())
        with self.assertRaises(ValueError): game.play((1,5))

    def test_save_repetition_and_variant_validation(self):
        cycle = ((1,5),(32,28),(5,1),(28,32))
        game = Checkers('B:WK32:BK1', (cycle * 2)[:-1])
        restored = Checkers.restore(json.loads(json.dumps(game.snapshot())))
        self.assertEqual(restored.fen, game.fen)
        self.assertEqual(restored.play((28,32)).draw_reason, 'Threefold repetition')
        for field, value in [('variant','standard'), ('draw_rules','international'),
                             ('history', [[1,50]]), ('initial_fen','B:W50:B1')]:
            data = game.snapshot(); data[field] = value
            with self.assertRaises(ValueError): Checkers.restore(data)

    def test_40_move_draw_roundtrip_and_man_reset(self):
        game = Checkers('B:W29,K30,K32:B2,K1,K3', QUIET[:-1])
        self.assertIsNone(game.outcome)
        restored = Checkers.restore(game.snapshot())
        self.assertIn('40 moves', restored.play(QUIET[-1]).draw_reason)
        self.assertIsNone(restored.play((29,25)).outcome)

    def test_capture_resets_quiet_draw_clock(self):
        game = Checkers('B:W29,K30,K32:B2,K1,K3', QUIET[:78])
        game = game.play((5,9)).play((14,5))
        self.assertIsNone(game.outcome)

    def test_search_levels_bounds_and_cancellation(self):
        game = Checkers('B:W18,26:B14')
        for level in ('beginner','intermediate','advanced'):
            self.assertEqual(search(game, level)['move'], [14,23,30])
        result = search(Checkers(), 'advanced', budget=Budget(20, 3, 1))
        self.assertLessEqual(result['nodes'], 3)
        self.assertIn(tuple(result['move']), Checkers().legal_moves)
        with self.assertRaises(SearchCancelled):
            search(Checkers(), 'advanced', cancelled=lambda: True)

class CheckersQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.controller = Controller(Store(Path(self.temp.name)))
        self.window = MainWindow(self.controller)
        self.window.show()
        self.window.execute('skip')
        self.window.execute('play checkers')
    def tearDown(self):
        self.window.close()
        QTest.qWait(50)
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()
    def test_full_graphical_chain_and_theme_selection(self):
        self.controller.session.game = Checkers('B:W18,26:B14')
        self.window.render()
        board = self.window.checkers_board
        board.select(14); board.select(23)
        self.assertEqual(self.controller.session.game.history, ())
        self.window.execute('theme modern')
        self.assertEqual(board.path, (14,23))
        self.window.execute('save')
        self.assertEqual(self.controller.store.load_game()['game']['history'], [])
        board.select(30)
        self.assertEqual(self.controller.session.game.history, ((14,23,30),))
        self.assertEqual(self.controller.session.game.outcome, 'B')
    def test_terminal_move_and_cancel_on_catalog_stale_result(self):
        self.window.search.command = lambda: (sys.executable, ['-c','import time; time.sleep(10)'])
        self.window.execute('move 9-13')
        self.assertEqual(self.controller.session.game.history, ((9,13),))
        token = self.window._search_token
        self.window.execute('theme modern')
        self.assertEqual(self.window._search_token, token)
        self.window.execute('pause')
        self.assertFalse(self.window.search.running)
        before = self.controller.session.snapshot()
        self.window._search_ready(token, {'move':[21,17]})
        self.assertEqual(self.controller.session.snapshot(), before)
        self.window.execute('resume')
        self.assertTrue(self.window.search.running)
        self.window.execute('catalog')
        self.assertFalse(self.window.search.running)
        self.assertIsNone(self.controller.session.game)
    def test_save_load_pending_computer_resumes_once(self):
        self.window.execute('move 9-13')
        self.window.execute('catalog')
        self.window.execute('load')
        self.assertFalse(self.window.search.running)
        self.assertEqual(self.controller.session.game.history, ((9,13),))
        self.window.execute('resume')
        for _ in range(150):
            QTest.qWait(20)
            if len(self.controller.session.game.history) == 2: break
        self.assertEqual(len(self.controller.session.game.history), 2)
        QTest.qWait(100)
        self.assertFalse(self.window.search.running)

    def test_real_worker_nonblocking_and_timeout(self):
        service = SearchService(self.window)
        results = []; failures = []; ticks = []
        service.ready.connect(lambda token, data: results.append(data))
        service.failed.connect(lambda token, message: failures.append(message))
        timer = QTimer(self.window); timer.setInterval(10)
        timer.timeout.connect(lambda: ticks.append(1)); timer.start()
        service.start(Checkers().snapshot(), 'beginner')
        for _ in range(100):
            QTest.qWait(20)
            if results or failures: break
        self.assertFalse(failures)
        self.assertTrue(results)
        self.assertIn(tuple(results[0]['move']), Checkers().legal_moves)
        self.assertTrue(ticks)
        service.command = lambda: (sys.executable, ['-c','import time; time.sleep(10)'])
        service.timeout_ms = 50
        service.start(Checkers().snapshot(), 'advanced')
        QTest.qWait(150)
        self.assertFalse(service.running)
        self.assertTrue(failures)
        timer.stop()
