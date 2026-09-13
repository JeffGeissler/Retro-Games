"""One command boundary used by both typed commands and UI actions."""
from dataclasses import dataclass
import shlex

from .controller import Controller

HELP = ("Commands: help · skip · catalog · play tic-tac-toe · move 1–9 (or 1–9) · "
        "pause · resume · save · load · theme terminal|modern · "
        "difficulty beginner|unbeatable · mark X|O. "
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
                    cell = int(args[0])
                except ValueError:
                    raise ValueError("Choose a cell from 1 to 9.") from None
                c.session.move(cell)
                message = c.status
            elif command == "pause" and not args:
                c.session.pause()
                message = c.status
            elif command == "resume" and not args:
                c.session.resume()
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
                c.configure(**{key: value})
                message = "Theme changed." if command == "theme" else "Preference saved for your next game."
            else:
                raise ValueError("Unknown command or arguments. Type help for commands.")
            return CommandResult(True, message)
        except (ValueError, OSError) as error:
            return CommandResult(False, str(error))
