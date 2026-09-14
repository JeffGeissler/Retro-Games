import hashlib
import importlib.util
import json
from dataclasses import replace
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
import wave
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from retro_play.audio.backends import ProcessSpeechBackend
from retro_play.audio.playback import QtPlayback
from retro_play.audio.service import ASSETS, CONNECTION, AudioService, connection_duration
from retro_play.controller import Controller
from retro_play.storage import Preferences, Store
from retro_play.ui.window import MainWindow


def wav(path):
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(22050)
        stream.writeframes(b'\0\0' * 2205)


class FakePlayback(QObject):
    finished = Signal()
    failed = Signal(str)
    availability_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.available = True
        self.played = []
        self.stops = 0
        self.volume = 0

    def play(self, path):
        self.played.append(Path(path))

    def set_volume(self, volume):
        self.volume = volume

    def stop(self):
        self.stops += 1


class FakeBackend(QObject):
    ready = Signal(int, str)
    failed = Signal(int, str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.available = name != 'silent'
        self.identity = name + ':test'
        self.suffix = '.wav'
        self.requests = []
        self.cancelled = 0

    def start(self, text, output, token):
        self.requests.append((text, Path(output), token))

    def complete(self, request=None):
        text, path, token = request or self.requests[-1]
        wav(path)
        self.ready.emit(token, str(path))

    def cancel(self):
        self.cancelled += 1

    def shutdown(self):
        self.cancel()


class AudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.service = AudioService(self.directory, Preferences(), backend_factory=FakeBackend,
                                    playback_factory=FakePlayback)

    def tearDown(self):
        self.service.shutdown()
        self.service.deleteLater()
        QTest.qWait(20)
        self.temp.cleanup()

    def test_bounded_queue_cache_hit_and_eviction(self):
        self.service.speak('first')
        for n in range(10):
            self.service.speak('queued ' + str(n))
        self.assertEqual(list(self.service.queue), ['queued 7', 'queued 8', 'queued 9'])
        self.service.backend.complete()
        self.assertEqual(len(self.service.voice.played), 1)
        self.service.stop()
        count = len(self.service.backend.requests)
        self.service.speak('first')
        self.assertEqual(len(self.service.backend.requests), count)
        self.service.voice.finished.emit()
        self.service.MAX_CACHE_FILES = 2
        for text in ('second', 'third'):
            self.service.speak(text)
            self.service.backend.complete()
            self.service.voice.finished.emit()
        files = [p for p in self.service.cache.glob('*.wav') if len(p.stem) == 64]
        self.assertEqual(len(files), 2)

    def test_mute_cancels_immediately_and_late_result_is_discarded(self):
        self.service.speak('old turn')
        old = self.service.backend.requests[-1]
        self.service.speak('queued old turn')
        self.service.effect('accept')
        before = self.service.effects.stops
        self.service.configure(replace(Preferences(), muted=True))
        self.assertGreater(self.service.effects.stops, before)
        self.assertFalse(self.service.queue)
        self.assertIsNone(self.service.active)
        self.service.backend.complete(old)
        self.assertFalse(old[1].exists())
        self.assertEqual(self.service.voice.played, [])
        self.service.configure(Preferences())
        self.assertIsNone(self.service.active)
        self.assertEqual(len(self.service.backend.requests), 1)
        self.service.speak('fresh turn')
        self.service.backend.complete()
        self.assertEqual(len(self.service.voice.played), 1)

    def test_independent_volumes_and_zero_voice_clears_queue(self):
        self.service.speak('hello')
        stops = self.service.effects.stops
        self.service.configure(replace(Preferences(), voice_volume=0, effects_volume=73))
        self.assertEqual(self.service.voice.volume, 0)
        self.assertEqual(self.service.effects.volume, 73)
        self.assertEqual(self.service.effects.stops, stops)
        self.assertIsNone(self.service.active)
        self.service.configure(replace(Preferences(), voice_volume=61, effects_volume=0))
        self.assertEqual(self.service.voice.volume, 61)
        self.service.effect('move')
        self.assertEqual(self.service.effects.played, [])

    def test_backend_failure_device_loss_and_corrupt_cache_remain_silent(self):
        self.service.speak('hello')
        request = self.service.backend.requests[-1]
        request[1].write_text('not audio')
        self.service.backend.ready.emit(request[2], str(request[1]))
        self.assertIsNone(self.service.active)
        self.assertIn('supported', self.service.message)
        self.service.speak('next')
        token = self.service.generation
        self.service.backend.failed.emit(token, 'missing engine')
        self.assertFalse(self.service.queue)
        count = len(self.service.backend.requests)
        self.service.speak('no retry storm')
        self.assertEqual(len(self.service.backend.requests), count)
        self.service.voice.available = False
        self.service.voice.availability_changed.emit(False)
        self.service.configure(replace(Preferences(), speech_backend='silent'))
        self.service.speak('silent')
        self.assertIsNone(self.service.active)

    def test_session_leave_clears_old_narration_but_allows_catalog_prompt(self):
        controller = Controller(Store(self.directory), speech=self.service)
        window = MainWindow(controller, audio=self.service)
        window.execute('skip')
        window.execute('play')
        request = self.service.backend.requests[-1]
        self.service.speak('old queued narration')
        window.execute('catalog')
        self.assertNotIn('old queued narration', self.service.queue)
        self.service.backend.complete(request)
        self.assertEqual(self.service.voice.played, [])
        self.assertIn('ORBIT', self.service.active[0])
        window.close()
        window.deleteLater()

    def test_skip_stops_connection_and_unmute_does_not_replay_it(self):
        controller = Controller(Store(self.directory), speech=self.service)
        window = MainWindow(controller, audio=self.service)
        window._connection_step()
        self.assertEqual(self.service.effects.played[-1].name, CONNECTION[0])
        window.mute.setChecked(True)
        window.execute('skip')
        window.mute.setChecked(False)
        self.assertFalse(window.connection_timer.isActive())
        self.assertEqual(len(self.service.effects.played), 1)
        window.close()
        window.deleteLater()

    def test_preferences_v1_migration_and_v2_roundtrip(self):
        store = Store(self.directory)
        (self.directory / 'preferences.json').write_text(json.dumps({
            'version': 1, 'theme': 'modern', 'difficulty': 'unbeatable',
            'human': 'O', 'simulate_connection': False}))
        old = store.load_preferences()
        self.assertEqual(old.voice_volume, 50)
        new = replace(old, muted=True, effects_volume=17, voice_volume=65, speech_backend='pyttsx3')
        store.save_preferences(new)
        self.assertEqual(store.load_preferences(), new)
        for changes in ({'voice_volume': -1}, {'effects_volume': 101}, {'muted': 1}, {'speech_backend': 'web'}):
            with self.assertRaises(ValueError):
                replace(new, **changes)

    def test_cached_welcome_waits_until_controls_are_visible(self):
        welcome = 'I am ORBIT. Would you like to play a game?'
        self.service.speak(welcome)
        self.service.backend.complete()
        self.service.stop()
        count = len(self.service.voice.played)
        controller = Controller(Store(self.directory), speech=self.service)
        controller.session.connect()
        window = MainWindow(controller, audio=self.service)
        self.assertEqual(len(self.service.voice.played), count)
        window.show()
        QTest.qWait(300)
        self.assertEqual(len(self.service.voice.played), count + 1)
        window.close()
        window.deleteLater()

    def test_supplied_assets_are_byte_identical_and_connection_has_duration(self):
        manifest = json.loads((ASSETS / 'SHA256.json').read_text())
        self.assertEqual(len(manifest), 11)
        for name, digest in manifest.items():
            self.assertEqual(hashlib.sha256((ASSETS / name).read_bytes()).hexdigest(), digest)
        for index in range(4):
            self.assertGreater(connection_duration(index), 100)


class ProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_real_slow_child_does_not_block_ui_and_cancel_reaps_it(self):
        class SlowBackend(ProcessSpeechBackend):
            def command(self, output):
                return sys.executable, ['-c', 'import time; time.sleep(10)']
        with tempfile.TemporaryDirectory() as folder:
            backend = SlowBackend('espeak-ng', executable=sys.executable)
            service = AudioService(Path(folder), Preferences(), backend_factory=lambda name, parent: backend,
                                   playback_factory=FakePlayback)
            controller = Controller(Store(Path(folder)), speech=service)
            window = MainWindow(controller, audio=service)
            window.execute('skip')
            window.execute('play')
            ticks = []
            timer = QTimer()
            timer.setInterval(10)
            timer.timeout.connect(lambda: ticks.append(1))
            timer.start()
            QTest.qWait(120)
            window.execute('1')
            self.assertEqual(controller.session.game.history, (1,))
            self.assertGreater(len(ticks), 3)
            window.execute('catalog')
            service.stop()
            QTest.qWait(150)
            self.assertFalse(backend.jobs)
            timer.stop()
            window.close()
            window.deleteLater()
            service.deleteLater()
            backend.deleteLater()

    def test_timeout_and_missing_executable_fail_without_waiting(self):
        class SlowBackend(ProcessSpeechBackend):
            def command(self, output):
                return sys.executable, ['-c', 'import time; time.sleep(10)']
        with tempfile.TemporaryDirectory() as folder:
            for backend in (SlowBackend('espeak-ng', executable=sys.executable, timeout_ms=40),
                            ProcessSpeechBackend('espeak-ng', executable='/missing/orbit-espeak')):
                failures = []
                backend.failed.connect(lambda token, message: failures.append(message))
                backend.start('test', Path(folder) / 'test.wav', 1)
                QTest.qWait(200)
                self.assertTrue(failures)
                self.assertFalse(backend.jobs)
                backend.deleteLater()

    @unittest.skipUnless(shutil.which('espeak-ng') or Path('/opt/homebrew/bin/espeak-ng').exists(),
                         'Optional eSpeak NG is not installed')
    def test_real_espeak_renders_valid_wav_asynchronously(self):
        with tempfile.TemporaryDirectory() as folder:
            backend = ProcessSpeechBackend('espeak-ng')
            ready, failures = [], []
            backend.ready.connect(lambda token, path: ready.append(path))
            backend.failed.connect(lambda token, message: failures.append(message))
            backend.start('I am ORBIT. Would you like to play a game?', Path(folder) / 'voice.wav', 1)
            for _ in range(100):
                if ready or failures:
                    break
                QTest.qWait(25)
            self.assertFalse(failures)
            self.assertTrue(ready)
            with wave.open(ready[0]) as source:
                self.assertGreater(source.getnframes(), 1000)
            backend.deleteLater()

    def test_qt_multimedia_decodes_pack_without_blocking(self):
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('playback_probe.py'))],
                                timeout=10, capture_output=True, text=True)
        if result.returncode == 77:
            self.skipTest('No physical audio output; silent-device behavior is tested separately')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(importlib.util.find_spec('pyttsx3'), 'Optional pyttsx3 is not installed')
    def test_optional_pyttsx3_renders_file_in_child(self):
        with tempfile.TemporaryDirectory() as folder:
            backend = ProcessSpeechBackend('pyttsx3')
            ready, failures = [], []
            backend.ready.connect(lambda token, path: ready.append(path))
            backend.failed.connect(lambda token, message: failures.append(message))
            backend.start('I am ORBIT.', Path(folder) / ('voice' + backend.suffix), 1)
            for _ in range(600):
                if ready or failures:
                    break
                QTest.qWait(25)
            self.assertFalse(failures)
            self.assertTrue(ready)
            self.assertTrue(AudioService._valid_audio(Path(ready[0])))
            backend.deleteLater()


if __name__ == '__main__':
    unittest.main()
