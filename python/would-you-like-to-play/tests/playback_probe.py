"""Isolated device smoke test using the real QApplication event loop, at zero volume."""
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from retro_play.audio.playback import QtPlayback
from retro_play.audio.service import ASSETS, CONNECTION

app = QApplication([])
player = QtPlayback()
if not player.available:
    print('No physical audio output device')
    raise SystemExit(77)
player.set_volume(0)
result = [1]

def finished():
    result[0] = 0
    app.quit()

def failed(message):
    print(message)
    app.quit()

player.finished.connect(finished)
player.failed.connect(failed)
QTimer.singleShot(5000, app.quit)
QTimer.singleShot(0, lambda: player.play(sys.argv[1] if len(sys.argv) > 1 else ASSETS / CONNECTION[3]))
app.exec()
player.stop()
print('Qt playback completed' if result[0] == 0 else 'Qt playback did not complete')
raise SystemExit(result[0])
