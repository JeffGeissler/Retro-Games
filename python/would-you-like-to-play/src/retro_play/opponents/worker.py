"""One JSON request, one JSON response; no GUI imports or shell execution."""
import json
import sys
from retro_play.games.checkers import Checkers
from .checkers import search


def main():
    raw = sys.stdin.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError('Search request too large')
    data = json.loads(raw)
    game = Checkers.restore(data['game'])
    print(json.dumps(search(game, data['difficulty'])))


if __name__ == '__main__':
    main()
