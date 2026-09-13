from dataclasses import dataclass
from typing import Callable, Dict, Mapping, Any, Tuple

from .contracts import Game
from .games.tic_tac_toe import TicTacToe, choose_move


@dataclass(frozen=True)
class GameDefinition:
    id: str
    title: str
    description: str
    instructions: str
    create: Callable[[], Game]
    restore: Callable[[Mapping[str, Any]], Game]
    computer_move: Callable[[Game, str], int]


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
    return registry
