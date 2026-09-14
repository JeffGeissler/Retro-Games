"""Console-capable helper, launched without a terminal by QProcess."""
import sys

kind = sys.argv.pop(1)
if kind == 'search':
    from retro_play.opponents.worker import main
elif kind == 'speech':
    from retro_play.audio.pyttsx_worker import main
else:
    raise SystemExit('Unknown worker')
main()
