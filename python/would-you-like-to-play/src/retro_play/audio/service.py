from collections import deque
from contextlib import suppress
import hashlib
from pathlib import Path
import tempfile
import wave
from PySide6.QtCore import QObject, QTimer, Signal
from .backends import ProcessSpeechBackend
from .playback import QtPlayback

ASSETS = Path(__file__).parent / 'assets'
CONNECTION = ('01_orbit_dial_sequence.wav', '02_carrier_whistle.wav',
              '03_modem_handshake.wav', '04_connection_established.wav')
EFFECTS = {'accept': '06_command_accept.wav', 'error': '07_command_error.wav',
           'save': '10_save_complete.wav', 'move': '11_piece_move.wav',
           'win': '15_player_win.wav', 'loss': '16_orbit_win.wav', 'draw': '17_draw_stalemate.wav'}


class AudioService(QObject):
    """Speech interface plus effects. One active utterance and at most three waiting."""
    notice = Signal(str)
    MAX_QUEUE = 3
    MAX_CACHE_FILES = 64
    MAX_CACHE_BYTES = 32 * 1024 * 1024

    def __init__(self, directory, preferences, parent=None, backend_factory=ProcessSpeechBackend,
                 playback_factory=QtPlayback):
        super().__init__(parent)
        self.cache = Path(directory) / 'speech-cache'
        self.backend_factory = backend_factory
        self.voice = playback_factory(self)
        self.effects = playback_factory(self)
        self.queue = deque(maxlen=self.MAX_QUEUE)
        self.generation = 0
        self.active = None
        self.backend = None
        self.backend_name = None
        self.failed_backend = False
        self.message = ''
        self.preferences = preferences
        self.voice.finished.connect(self._voice_finished)
        self.voice.failed.connect(self._voice_error)
        self.effects.failed.connect(self._report)
        self.voice.availability_changed.connect(self._device_changed)
        self.effects.availability_changed.connect(lambda available: self.effects.stop())
        self.playback_timeout = QTimer(self)
        self.playback_timeout.setSingleShot(True)
        self.playback_timeout.setInterval(30000)
        self.playback_timeout.timeout.connect(lambda: self._voice_error('Voice playback timed out.'))
        self.configure(preferences)
        if not self.voice.available:
            self._report('No audio output device. Silent play remains available.')

    def _report(self, message):
        if self.message == message:
            return
        self.message = message
        self.notice.emit(message)

    def configure(self, preferences):
        changed_backend = preferences.speech_backend != self.backend_name
        if preferences.muted:
            self.stop()
        elif changed_backend or preferences.voice_volume == 0:
            self.cancel_voice()
        if changed_backend:
            if self.backend is not None:
                self.backend.shutdown()
            self.backend_name = preferences.speech_backend
            self.backend = self.backend_factory(self.backend_name, self)
            self.backend.ready.connect(self._ready)
            self.backend.failed.connect(self._synthesis_error)
            self.failed_backend = False
            self.message = ''
            if not self.backend.available and self.backend_name != 'silent':
                self._report(self.backend_name + ' unavailable. Install it or select Silent; effects still work.')
        self.preferences = preferences
        self.voice.set_volume(preferences.voice_volume)
        self.effects.set_volume(preferences.effects_volume)
        if preferences.muted or preferences.effects_volume == 0:
            self.effects.stop()
        # Unmuting never requeues the previous status or connection sounds.

    def speak(self, text):
        p = self.preferences
        if (p.muted or not p.voice_volume or not self.voice.available or
                not self.backend.available or self.failed_backend):
            return
        text = ' '.join(text.split())[:600]
        if not text or text in self.queue or (self.active and text == self.active[0]):
            return
        self.queue.append(text)
        self._pump()

    def _pump(self):
        if self.active or not self.queue:
            return
        text = self.queue.popleft()
        key = hashlib.sha256((self.backend.identity + '\0' + text).encode()).hexdigest()
        target = self.cache / (key + self.backend.suffix)
        self.active = (text, target)
        try:
            self.cache.mkdir(parents=True, exist_ok=True)
            if self._valid_audio(target):
                target.touch()
                self._play(target)
            else:
                target.unlink(missing_ok=True)
                with tempfile.NamedTemporaryFile(dir=self.cache, prefix='pending-',
                                                 suffix=self.backend.suffix, delete=False) as file:
                    pending = Path(file.name)
                self.backend.start(text, pending, self.generation)
        except OSError as error:
            self._voice_error('Speech cache unavailable: ' + str(error))

    @staticmethod
    def _valid_audio(path):
        if not path.exists() or not 44 <= path.stat().st_size <= 4 * 1024 * 1024:
            return False
        with path.open('rb') as source:
            header = source.read(12)
        return ((header[:4] == b'RIFF' and header[8:12] == b'WAVE') or
                (header[:4] == b'FORM' and header[8:12] in (b'AIFF', b'AIFC')))

    def _ready(self, token, path):
        path = Path(path)
        if token != self.generation or self.active is None:
            with suppress(OSError):
                path.unlink(missing_ok=True)
            return
        try:
            if not self._valid_audio(path):
                raise ValueError('Backend did not produce a supported WAV/AIFF file.')
            target = self.active[1]
            path.replace(target)
            self._prune(target)
            self._play(target)
        except (OSError, ValueError) as error:
            with suppress(OSError):
                path.unlink(missing_ok=True)
            self._voice_error(str(error))

    def _prune(self, protected):
        files = sorted((p for p in self.cache.iterdir() if len(p.stem) == 64 and p.suffix in ('.wav', '.aiff')),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        size = 0
        for index, path in enumerate(files):
            size += path.stat().st_size
            if path != protected and (index >= self.MAX_CACHE_FILES or size > self.MAX_CACHE_BYTES):
                path.unlink()

    def _play(self, path):
        self.playback_timeout.start()
        self.voice.play(path)

    def _voice_finished(self):
        self.playback_timeout.stop()
        self.active = None
        self._pump()

    def _synthesis_error(self, token, message):
        if token == self.generation:
            self.failed_backend = True
            self._voice_error(message)

    def _voice_error(self, message):
        self.stop()
        self._report(message)

    def _device_changed(self, available):
        self.stop()
        self._report('Audio device changed. New events use the current output.' if available
                     else 'No audio output device. Silent play remains available.')

    def effect(self, name):
        if not self.preferences.muted and self.preferences.effects_volume and self.effects.available:
            path = ASSETS / EFFECTS.get(name, name)
            if path.name not in (*CONNECTION, *EFFECTS.values()):
                return
            self.effects.stop()
            self.effects.play(path)

    def stop_effects(self):
        self.effects.stop()

    def stop(self):
        self.cancel_voice()
        self.effects.stop()

    def cancel_voice(self):
        self.generation += 1
        self.queue.clear()
        self.active = None
        self.playback_timeout.stop()
        if self.backend is not None:
            self.backend.cancel()
        self.voice.stop()

    def shutdown(self):
        self.stop()
        if self.backend is not None:
            self.backend.shutdown()


def connection_duration(index):
    try:
        with wave.open(str(ASSETS / CONNECTION[index])) as source:
            return int(1000 * source.getnframes() / source.getframerate()) + 100
    except (OSError, wave.Error):
        return 500
