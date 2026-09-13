from dataclasses import dataclass
from functools import lru_cache
import random
from typing import Any, Mapping, Optional, Tuple

LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
         (2, 5, 8), (0, 4, 8), (2, 4, 6))


class IllegalMove(ValueError):
    pass


@dataclass(frozen=True)
class TicTacToe:
    """Immutable, replay-validated position. Public moves use cells 1–9."""

    history: Tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if type(self.history) is not tuple:
            raise ValueError("Move history must be a tuple.")
        board = [""] * 9
        for turn, move in enumerate(self.history):
            if self._outcome(board) is not None:
                raise IllegalMove("The game has already ended.")
            if type(move) is not int or not 1 <= move <= 9:
                raise IllegalMove("Choose a cell from 1 to 9.")
            if board[move - 1]:
                raise IllegalMove("That cell is occupied.")
            board[move - 1] = "X" if turn % 2 == 0 else "O"

    @property
    def board(self) -> Tuple[str, ...]:
        board = [""] * 9
        for turn, move in enumerate(self.history):
            board[move - 1] = "X" if turn % 2 == 0 else "O"
        return tuple(board)

    @staticmethod
    def _outcome(board) -> Optional[str]:
        for a, b, c in LINES:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return "draw" if all(board) else None

    @property
    def current_player(self) -> str:
        return "X" if len(self.history) % 2 == 0 else "O"

    @property
    def outcome(self) -> Optional[str]:
        return self._outcome(self.board)

    @property
    def winning_cells(self) -> Tuple[int, ...]:
        board = self.board
        for line in LINES:
            if board[line[0]] and len({board[i] for i in line}) == 1:
                return tuple(i + 1 for i in line)
        return ()

    @property
    def legal_moves(self) -> Tuple[int, ...]:
        if self.outcome is not None:
            return ()
        return tuple(i + 1 for i, mark in enumerate(self.board) if not mark)

    def play(self, move: int) -> "TicTacToe":
        return TicTacToe(self.history + (move,))

    def snapshot(self) -> Mapping[str, Any]:
        return {"history": list(self.history)}

    @classmethod
    def restore(cls, data: Mapping[str, Any]) -> "TicTacToe":
        if not isinstance(data, dict) or set(data) != {"history"}:
            raise ValueError("Invalid Tic Tac Toe snapshot.")
        history = data["history"]
        if type(history) is not list or len(history) > 9:
            raise ValueError("Invalid move history.")
        return cls(tuple(history))


@lru_cache(maxsize=6000)
def _value(board: Tuple[str, ...], player: str) -> int:
    """Negamax score from the next player's perspective."""
    outcome = TicTacToe._outcome(board)
    if outcome:
        return 0 if outcome == "draw" else (1 if outcome == player else -1)
    other = "O" if player == "X" else "X"
    return max(-_value(board[:i] + (player,) + board[i + 1:], other)
               for i, mark in enumerate(board) if not mark)


def choose_move(game: TicTacToe, difficulty: str,
                rng: Optional[random.Random] = None) -> int:
    if not game.legal_moves:
        raise IllegalMove("There are no legal moves.")
    if difficulty == "beginner":
        return (rng or random).choice(game.legal_moves)
    if difficulty != "unbeatable":
        raise ValueError("Unknown opponent difficulty.")
    # Prefer center and corners among equally strong moves.
    order = (5, 1, 3, 7, 9, 2, 4, 6, 8)
    other = "O" if game.current_player == "X" else "X"
    return max((move for move in order if move in game.legal_moves),
               key=lambda move: -_value(game.play(move).board, other))
