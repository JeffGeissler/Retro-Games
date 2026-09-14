from pathlib import Path
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaDevices, QMediaPlayer


class QtPlayback(QObject):
    finished = Signal()
    failed = Signal(str)
    availability_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = QMediaDevices(self)
        self.output = QAudioOutput(self)
        self.player = None
        self.devices.audioOutputsChanged.connect(self._devices_changed)
        self.available = not QMediaDevices.defaultAudioOutput().isNull()

    def _devices_changed(self):
        self.stop()
        device = QMediaDevices.defaultAudioOutput()
        self.available = not device.isNull()
        if self.available:
            self.output.setDevice(device)
        self.availability_changed.emit(self.available)

    def _status(self, player, status):
        if player is self.player and status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.finished.emit()

    def play(self, path):
        if not self.available:
            self.failed.emit('No audio output device. Silent play remains available.')
            return
        self.stop()
        player = QMediaPlayer(self)
        self.player = player
        player.setAudioOutput(self.output)
        player.mediaStatusChanged.connect(lambda status: self._status(player, status))
        player.errorOccurred.connect(lambda error, text: self.failed.emit('Audio playback unavailable: ' + text)
                                    if player is self.player else None)
        player.setSource(QUrl.fromLocalFile(str(Path(path).resolve())))
        player.play()

    def set_volume(self, volume):
        self.output.setVolume(volume / 100)

    def stop(self):
        player, self.player = self.player, None
        if player is not None:
            player.stop()
            player.setAudioOutput(None)
            player.deleteLater()
