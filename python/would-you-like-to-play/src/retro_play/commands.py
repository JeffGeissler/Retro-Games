"""One command boundary used by both typed commands and UI actions."""
from dataclasses import dataclass
import shlex

from .controller import Controller

HELP = ("Commands: help · skip · catalog · play tic-tac-toe|checkers · moves · "
        "move 1–9 (Tic Tac Toe) or move 9-13 / move 14x23x30 (checkers) · "
        "pause · resume · save · load · theme terminal|modern · "
        "difficulty beginner|unbeatable (Tic Tac Toe), beginner|intermediate|advanced (checkers) · mark X|O or B|W. "
        "Difficulty and mark apply to the next game. Catalog saves the current game.")


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    message: str


class CommandRouter:
    def __init__(self, controller: Controller) -> None:
        self.controller = controller

    def execute(self, text: str) -> CommandResult:
        try:
            words = shlex.split(text.strip().lower())
            if not words:
                return CommandResult(True, "")
            if len(words) == 1 and words[0].isdigit():
                words = ["move", words[0]]
            command, args = words[0], words[1:]
            c = self.controller
            if command == "help" and not args:
                message = HELP
            elif command == "skip" and not args:
                c.speech.stop()
                c.session.connect()
                message = "Local terminal ready. No network connection was made."
            elif command == "catalog" and not args:
                c.catalog()
                message = "Available: " + ", ".join(game.id for game in c.registry.catalog())
            elif command == "play" and len(args) <= 1:
                c.start(args[0] if args else "tic-tac-toe")
                message = c.status
            elif command == "move" and len(args) == 1:
                try:
                    definition = c.registry.get(c.session.game_id)
                    cell = definition.parse_move(args[0])
                except ValueError:
                    if c.session.game_id == 'checkers':
                        raise
                    raise ValueError("Choose a cell from 1 to 9 in an active Tic Tac Toe game.") from None
                c.session.move(cell)
                message = c.status
            elif command == 'moves' and not args:
                if c.session.game is None:
                    raise ValueError('Start a game first.')
                game = c.session.game
                message = 'Legal moves: ' + ', '.join(
                    game.notation(move) if c.session.game_id == 'checkers' else str(move)
                    for move in game.legal_moves)
            elif command == "pause" and not args:
                c.session.pause()
                c.speech.stop()
                message = c.status
            elif command == "resume" and not args:
                c.session.resume()
                c.speech.stop()
                message = c.status
            elif command == "save" and not args:
                c.save()
                message = "Game saved on this device."
            elif command == "load" and not args:
                c.load()
                message = "Saved game loaded. " + c.status
            elif command in ("theme", "difficulty", "mark") and len(args) == 1:
                key = "human" if command == "mark" else command
                value = args[0].upper() if command == "mark" else args[0]
                if c.session.game_id == 'checkers' and command in ('difficulty', 'mark'):
                    key = 'checkers_' + key
                c.configure(**{key: value})
                message = "Theme changed." if command == "theme" else "Preference saved for your next game."
            else:
                raise ValueError("Unknown command or arguments. Type help for commands.")
            return CommandResult(True, message)
        except (ValueError, OSError) as error:
            return CommandResult(False, str(error))
