from dataclasses import dataclass
from typing import Callable, Dict, Mapping, Any, Tuple

from .contracts import Game
from .games.tic_tac_toe import TicTacToe, choose_move
from .games.checkers import Checkers, parse_path


def checkers_computer_move(game, difficulty):
    from .opponents.checkers import search
    return tuple(search(game, difficulty)['move'])


@dataclass(frozen=True)
class GameDefinition:
    id: str
    title: str
    description: str
    instructions: str
    create: Callable[[], Game]
    restore: Callable[[Mapping[str, Any]], Game]
    computer_move: Callable[[Game, str], Any]
    parse_move: Callable[[str], Any] = int
    players: Tuple[str, ...] = ("X", "O")
    difficulties: Tuple[str, ...] = ("beginner", "unbeatable")


class GameRegistry:
    def __init__(self) -> None:
        self._games: Dict[str, GameDefinition] = {}

    def register(self, definition: GameDefinition) -> None:
        if definition.id in self._games:
            raise ValueError("Duplicate game ID: " + definition.id)
        self._games[definition.id] = definition

    def get(self, game_id: str) -> GameDefinition:
        try:
            return self._games[game_id]
        except (KeyError, TypeError):
            raise ValueError("Unknown game. Use catalog to see available games.") from None

    def catalog(self) -> Tuple[GameDefinition, ...]:
        return tuple(self._games.values())


def default_registry() -> GameRegistry:
    registry = GameRegistry()
    registry.register(GameDefinition(
        "tic-tac-toe", "Tic Tac Toe", "Three in a row. A worthy first challenge.",
        "X goes first. Choose cells 1–9, left to right, top to bottom. "
        "Make three in a row, column, or diagonal to win. A full board is a draw.",
        TicTacToe, TicTacToe.restore, choose_move,
    ))
    registry.register(GameDefinition(
        'checkers', 'English / American Checkers', 'Compulsory jumps. Short kings. Every move matters.',
        'Black moves first on the 32 numbered dark squares. Men move and capture forward; kings move one '
        'diagonal square in either direction. Captures are compulsory. Choose any complete jump chain; '
        'the longest chain is not required. Reaching the crown row ends the turn. '
        'Type move 9-13 or a full capture path such as move 14x23x30. '
        'Automatic draws: threefold repetition or 40 moves per side without a capture or man move.',
        Checkers, Checkers.restore, checkers_computer_move, parse_path,
        ('B', 'W'), ('beginner', 'intermediate', 'advanced'),
    ))
    return registry
