"""Packaged-app integration probe, invoked only by release verification."""
import json
from pathlib import Path
import tempfile
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from .controller import Controller
from .storage import Store
from .ui.window import MainWindow


def run(report):
    app = QApplication([])
    temp = tempfile.TemporaryDirectory()
    controller = Controller(Store(Path(temp.name)))
    window = MainWindow(controller)
    window.show()
    result = {'ok': False}
    stage = [0]

    def tick():
        try:
            if stage[0] == 0:
                window.skip.click()
                window.theme.setCurrentText('Modern')
                window.play_buttons[0].click()
                window.modern_board.cells[0].click()
                assert controller.session.game.history == (1,)
                stage[0] = 1
            elif stage[0] == 1 and len(controller.session.game.history) == 2:
                controller.catalog()
                window.render()
                window.play_buttons[1].click()
                window.checkers_board.squares[9].click()
                window.checkers_board.squares[13].click()
                assert controller.session.game.history == ((9,13),)
                stage[0] = 2
            elif stage[0] == 2 and len(controller.session.game.history) == 2:
                controller.save()
                before = controller.session.game.snapshot()
                controller.catalog(); controller.load()
                assert controller.session.game.snapshot() == before
                result.update(ok=True, checks=['desktop widgets', 'tic tac toe reply',
                    'packaged checkers worker', 'save/load', 'modern board clicks'])
                finish()
        except Exception as error:
            result['error'] = repr(error)
            finish()

    def finish():
        timer.stop()
        window.close()
        Path(report).write_text(json.dumps(result, indent=2))
        app.quit()

    timer = QTimer(); timer.timeout.connect(tick); timer.start(50)
    QTimer.singleShot(15000, finish)
    app.exec()
    temp.cleanup()
    return 0 if result['ok'] else 1
