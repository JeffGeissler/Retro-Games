"""Windowed desktop entry point; background tasks use a separate executable."""
from retro_play.__main__ import main

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == '--desktop-smoke':
        from retro_play.desktop_smoke import run
        raise SystemExit(run(sys.argv[2]))
    raise SystemExit(main())
