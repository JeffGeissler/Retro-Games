import argparse
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Would you like to play a game?")
    parser.add_argument("--data-dir", type=Path, help="Override local preferences/save directory")
    parser.add_argument("--skip-connection", action="store_true", help="Skip simulated connection this launch")
    parser.add_argument("--mute", action="store_true", help="Start muted for this launch")
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
    audio = None
    try:
        from dataclasses import replace
        from .audio.service import AudioService
        if args.mute:
            controller.preferences = replace(controller.preferences, muted=True)
        audio = AudioService(directory, controller.preferences, app)
        controller.speech = audio
    except (ImportError, OSError) as error:
        controller.notice = "Audio unavailable; continuing silently. " + str(error)
    if args.skip_connection:
        controller.session.connect()
    window = MainWindow(controller, audio=audio)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
