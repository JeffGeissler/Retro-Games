"""Real Qt widget tests; run with QT_QPA_PLATFORM=offscreen in headless environments."""
from pathlib import Path
import tempfile
import unittest

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from retro_play.controller import Controller
from retro_play.session import Phase
from retro_play.storage import Store
from retro_play.ui.window import MainWindow


class WidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.controller = Controller(Store(Path(self.temp.name)))
        self.window = MainWindow(self.controller)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_skip_and_automatic_connection_do_not_reenter_catalog(self):
        self.assertTrue(self.window.connection_timer.isActive())
        QTest.mouseClick(self.window.skip, Qt.MouseButton.LeftButton)
        self.assertEqual(self.controller.session.phase, Phase.CATALOG)
        self.assertFalse(self.window.connection_timer.isActive())
        self.window.execute("play")
        self.window._connection_step()
        self.assertEqual(self.controller.session.phase, Phase.PLAYING)

    def test_connection_completes_and_preference_can_skip_next_launch(self):
        for _ in range(4):
            self.window._connection_step()
        self.assertEqual(self.controller.session.phase, Phase.CATALOG)
        self.window.simulation.setChecked(False)
        self.assertEqual(Controller(self.controller.store).session.phase, Phase.CATALOG)

    def test_catalog_and_boards_fit_width_and_scroll_vertically(self):
        self.window.execute("skip")
        metrics = QFontMetrics(self.window.terminal_board.text.font())
        self.assertEqual(metrics.horizontalAdvance("i"), metrics.horizontalAdvance("W"))
        for size in ((820, 860), (560, 540)):
            self.window.resize(*size)
            for command in ("catalog", "play", "theme modern", "theme terminal"):
                self.window.execute(command)
                self.app.processEvents()
                self.app.processEvents()
                self.assertEqual(self.window.centralWidget().horizontalScrollBar().maximum(), 0,
                                 (size, command))
            self.window.execute("catalog")

    def test_midgame_theme_switch_preserves_pending_turn_and_save(self):
        self.window.execute("skip")
        self.window.execute("difficulty unbeatable")
        self.window.execute("play")
        QTest.mouseClick(self.window.terminal_board.cells[0], Qt.MouseButton.LeftButton)
        self.assertEqual(self.controller.session.game.history, (1,))
        before = self.controller.session.snapshot()
        self.window.theme.setCurrentText("Modern")
        self.assertEqual(self.controller.session.snapshot(), before)
        self.assertEqual(self.window.boards.currentIndex(), 1)
        self.assertEqual(self.window.modern_board.cells[0].text(), "X")
        self.assertFalse(self.window.modern_board.cells[1].isEnabled())
        self.window.execute("save")
        self.assertEqual(self.controller.store.load_game(), before)
        QTest.qWait(420)
        self.assertEqual(len(self.controller.session.game.history), 2)
        after = self.controller.session.snapshot()
        self.window.theme.setCurrentText("Terminal")
        self.assertEqual(self.controller.session.snapshot(), after)
        QTest.qWait(420)
        self.assertEqual(self.controller.session.snapshot(), after)

    def test_pause_catalog_load_cancel_pending_ai_and_resume_once(self):
        for command in ("skip", "mark O", "play", "pause"):
            self.window.execute(command)
        self.assertFalse(self.window.ai_timer.isActive())
        QTest.qWait(400)
        self.assertEqual(self.controller.session.game.history, ())
        self.window.execute("catalog")
        self.window.execute("load")
        self.assertEqual(self.controller.session.phase, Phase.PAUSED)
        self.window.execute("theme modern")
        self.assertFalse(self.window.ai_timer.isActive())
        self.window.execute("resume")
        QTest.qWait(420)
        self.assertEqual(len(self.controller.session.game.history), 1)
        self.assertFalse(self.window.ai_timer.isActive())

    def test_keyboard_move_and_finished_game_replay(self):
        self.window.execute("skip")
        self.window.execute("play")
        self.window.command.setFocus()
        QTest.keyClicks(self.window.command, "1")
        QTest.keyClick(self.window.command, Qt.Key.Key_Return)
        self.assertEqual(self.controller.session.game.history, (1,))
        # Deterministic opponent replies permit a complete player win through UI commands.
        self.window.ai_timer.stop()
        for computer, human in ((4, 2), (5, 3)):
            self.controller.session.game = self.controller.session.game.play(computer)
            self.window.render()
            self.window.execute(str(human))
            self.window.ai_timer.stop()
        self.assertEqual(self.controller.session.phase, Phase.FINISHED)
        self.assertIn("You win", self.window.status.text())
        self.assertFalse(self.window.pause_button.isEnabled())
        self.assertTrue(self.window.again.isVisible())
        QTest.mouseClick(self.window.again, Qt.MouseButton.LeftButton)
        self.assertEqual(self.controller.session.phase, Phase.PLAYING)
        self.assertEqual(self.controller.session.game.history, ())


if __name__ == "__main__":
    unittest.main()
