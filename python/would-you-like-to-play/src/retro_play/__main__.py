import argparse
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Would you like to play a game?")
    parser.add_argument("--data-dir", type=Path, help="Override local preferences/save directory")
    parser.add_argument("--skip-connection", action="store_true", help="Skip simulated connection this launch")
    args = parser.parse_args()
    from PySide6.QtCore import QStandardPaths
    from PySide6.QtWidgets import QApplication
    from .controller import Controller
    from .storage import Store
    from .ui.window import MainWindow

    app = QApplication(sys.argv[:1])
    app.setOrganizationName("RetroGames")
    app.setApplicationName("WouldYouLikeToPlay")
    directory = args.data_dir or Path(QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation))
    controller = Controller(Store(directory))
    if args.skip_connection:
        controller.session.connect()
    window = MainWindow(controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
