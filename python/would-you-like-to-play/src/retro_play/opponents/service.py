"""Nonblocking search process with bounded output, deadline, and stale-result rejection."""
import json
from ..runtime import worker_command
from PySide6.QtCore import QObject, QProcess, QTimer, Signal


class SearchService(QObject):
    ready = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, parent=None, timeout_ms=5000):
        super().__init__(parent)
        self.token = 0
        self.job = None
        self.jobs = set()
        self.timeout_ms = timeout_ms

    @property
    def running(self):
        return self.job is not None

    def command(self):
        return worker_command('search')

    def start(self, snapshot, difficulty):
        self.cancel()
        token = self.token
        process = QProcess(self)
        timer = QTimer(process)
        timer.setSingleShot(True)
        output = bytearray()
        job = (process, timer, token, output)
        self.job = job
        self.jobs.add(process)
        request = json.dumps({'game': snapshot, 'difficulty': difficulty}).encode()
        process.setStandardErrorFile(QProcess.nullDevice())
        process.started.connect(lambda: (process.write(request), process.closeWriteChannel()))
        process.readyReadStandardOutput.connect(lambda: self._read(job))
        process.finished.connect(lambda code, status: self._finish(job, code))
        process.errorOccurred.connect(lambda error: self._finish(job, -1)
                                     if error == QProcess.ProcessError.FailedToStart else None)
        timer.timeout.connect(lambda: self._fail(job, 'Computer search timed out. Resume to retry.'))
        program, arguments = self.command()
        process.start(program, arguments)
        timer.start(self.timeout_ms)
        return token

    def _read(self, job):
        process, timer, token, output = job
        output.extend(bytes(process.readAllStandardOutput()))
        if len(output) > 8192:
            self._fail(job, 'Computer response exceeded its size limit.')

    def _fail(self, job, message):
        if self.job is job:
            self.cancel()
            self.failed.emit(job[2], message)

    def _finish(self, job, code):
        process, timer, token, output = job
        if process not in self.jobs:
            return
        self._read(job)
        self.jobs.remove(process)
        timer.stop()
        current = self.job is job
        if current:
            self.job = None
            try:
                if code != 0:
                    raise ValueError('Computer process failed. Resume to retry.')
                data = json.loads(output)
                move = data['move']
                if (type(move) is not list or not 2 <= len(move) <= 13 or
                        any(type(cell) is not int or not 1 <= cell <= 32 for cell in move)):
                    raise ValueError('Invalid computer move response.')
                self.ready.emit(token, data)
            except (ValueError, KeyError, TypeError) as error:
                self.failed.emit(token, str(error))
        process.deleteLater()

    def cancel(self):
        self.token += 1
        if self.job is not None:
            process, timer, token, output = self.job
            self.job = None
            timer.stop()
            process.kill()
