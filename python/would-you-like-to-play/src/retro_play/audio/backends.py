"""Cancellable synthesis. No waitForFinished, shell, or speech loop on the UI thread."""
import importlib.util
import importlib.metadata
from contextlib import suppress
import os
from pathlib import Path
import shutil
import sys
from ..runtime import worker_command
from PySide6.QtCore import QObject, QProcess, QTimer, Signal


class ProcessSpeechBackend(QObject):
    ready = Signal(int, str)
    failed = Signal(int, str)

    def __init__(self, name, parent=None, executable=None, timeout_ms=15000):
        super().__init__(parent)
        self.name = name
        self.timeout_ms = timeout_ms
        self.job = None
        self.jobs = set()
        self.executable = executable or shutil.which('espeak-ng')
        # Finder-launched apps often do not inherit Homebrew's PATH.
        if not self.executable:
            self.executable = next((p for p in ('/opt/homebrew/bin/espeak-ng', '/usr/local/bin/espeak-ng')
                                    if os.access(p, os.X_OK)), None)
        if name == 'espeak-ng':
            self.available = bool(self.executable)
            path = Path(self.executable) if self.executable else None
            stamp = str(path.stat().st_mtime_ns) if path and path.exists() else 'missing'
            self.identity = 'espeak-ng:%s:%s:en-us:145:32:1' % (self.executable, stamp)
            self.suffix = '.wav'
        else:
            self.available = name == 'pyttsx3' and importlib.util.find_spec('pyttsx3') is not None
            version = importlib.metadata.version('pyttsx3') if self.available else 'missing'
            self.identity = 'pyttsx3:%s:%s:145:1' % (sys.platform, version)
            self.suffix = '.aiff' if sys.platform == 'darwin' else '.wav'

    def start(self, text, output, token):
        self.cancel()
        if not self.available:
            self.failed.emit(token, self.name + ' is unavailable. Install it or select Silent.')
            return
        process = QProcess(self)
        timeout = QTimer(process)
        timeout.setSingleShot(True)
        job = (process, timeout, Path(output), token)
        self.job = job
        self.jobs.add(process)
        process.setStandardOutputFile(QProcess.nullDevice())
        process.setStandardErrorFile(QProcess.nullDevice())
        process.started.connect(lambda: (process.write(text.encode('utf-8')), process.closeWriteChannel()))
        process.finished.connect(lambda code, status: self._complete(job, code == 0))
        process.errorOccurred.connect(lambda error: self._complete(job, False)
                                     if error == QProcess.ProcessError.FailedToStart else None)
        timeout.timeout.connect(lambda: self._timeout(job))
        program, arguments = self.command(output)
        process.start(program, arguments)
        timeout.start(self.timeout_ms)

    def command(self, output):
        if self.name == 'espeak-ng':
            return self.executable, ['-v', 'en-us', '-s', '145', '-p', '32', '-w', str(output), '--stdin']
        return worker_command('speech', output)

    def _timeout(self, job):
        if self.job is job:
            self.cancel()
            self.failed.emit(job[3], 'Speech synthesis timed out; voice is silent until the backend is reselected.')

    def _complete(self, job, success):
        process, timer, output, token = job
        if process not in self.jobs:
            return
        self.jobs.remove(process)
        timer.stop()
        current = self.job is job
        if current:
            self.job = None
        if current and success and output.exists():
            self.ready.emit(token, str(output))
        else:
            with suppress(OSError):
                output.unlink(missing_ok=True)
            if current:
                self.failed.emit(token, 'Speech synthesis failed. Check the selected backend installation.')
        process.deleteLater()

    def cancel(self):
        if self.job is not None:
            process, timer, output, token = self.job
            self.job = None
            timer.stop()
            process.kill()  # Asynchronous; finished cleans the partial file and reaps the child.

    def shutdown(self):
        self.cancel()
        for process in tuple(self.jobs):
            process.kill()
