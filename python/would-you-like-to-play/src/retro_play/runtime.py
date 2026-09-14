"""Locate background helpers in source installs and standalone desktop bundles."""
from pathlib import Path
import sys


def worker_command(kind, *arguments):
    if getattr(sys, 'frozen', False):
        suffix = '.exe' if sys.platform == 'win32' else ''
        return str(Path(sys.executable).with_name('orbit-worker' + suffix)), [kind, *map(str, arguments)]
    module = {'search': 'retro_play.opponents.worker', 'speech': 'retro_play.audio.pyttsx_worker'}[kind]
    return sys.executable, ['-B', '-m', module, *map(str, arguments)]
