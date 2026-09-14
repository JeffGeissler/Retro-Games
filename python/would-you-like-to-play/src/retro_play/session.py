"""Application session state machine, independent of presentation and disk I/O."""
from enum import Enum
from typing import Any, Dict, Optional

from .contracts import Game
from .registry import GameRegistry


class Phase(str, Enum):
    CONNECTING = "connecting"
    CATALOG = "catalog"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"


class Session:
    def __init__(self, registry: GameRegistry) -> None:
        self.registry = registry
        self.phase = Phase.CONNECTING
        self.game_id: Optional[str] = None
        self.game: Optional[Game] = None
        self.difficulty = "beginner"
        self.human = "X"

    def connect(self) -> None:
        if self.phase == Phase.CONNECTING:
            self.phase = Phase.CATALOG

    def start(self, game_id: str, difficulty: str, human: str) -> None:
        if self.phase == Phase.CONNECTING:
            raise ValueError("Skip or finish the simulated connection first.")
        if self.phase in (Phase.PLAYING, Phase.PAUSED):
            raise ValueError("Return to catalog before starting another game.")
        definition = self.registry.get(game_id)
        self._validate_options(difficulty, human, definition)
        game = definition.create()
        self.game_id, self.game = game_id, game
        self.difficulty, self.human = difficulty, human
        self.phase = Phase.PLAYING

    @staticmethod
    def _validate_options(difficulty: str, human: str, definition) -> None:
        if difficulty not in definition.difficulties or human not in definition.players:
            raise ValueError("Invalid opponent or player mark.")

    @property
    def computer_pending(self) -> bool:
        return (self.phase == Phase.PLAYING and self.game is not None
                and self.game.current_player != self.human)

    def move(self, cell) -> None:
        if self.phase != Phase.PLAYING or self.game is None:
            raise ValueError("A game must be playing before you can move.")
        if self.computer_pending:
            raise ValueError("Wait for the computer's turn.")
        self.game = self.game.play(cell)
        self._finish_if_needed()

    def computer_step(self) -> None:
        if not self.computer_pending:
            return
        definition = self.registry.get(self.game_id)
        self.apply_computer_move(definition.computer_move(self.game, self.difficulty))

    def apply_computer_move(self, move):
        if not self.computer_pending:
            raise ValueError('There is no pending computer turn.')
        self.game = self.game.play(move)
        self._finish_if_needed()

    def _finish_if_needed(self) -> None:
        if self.game.outcome is not None:
            self.phase = Phase.FINISHED

    def pause(self) -> None:
        if self.phase != Phase.PLAYING:
            raise ValueError("Only an active game can be paused.")
        self.phase = Phase.PAUSED

    def resume(self) -> None:
        if self.phase != Phase.PAUSED:
            raise ValueError("There is no paused game to resume.")
        self.phase = Phase.PLAYING

    def catalog(self) -> None:
        if self.phase == Phase.CONNECTING:
            raise ValueError("Skip or finish the simulated connection first.")
        self.phase, self.game, self.game_id = Phase.CATALOG, None, None

    def snapshot(self) -> Dict[str, Any]:
        if self.game is None:
            raise ValueError("There is no game to save.")
        return {"version": 1, "game_id": self.game_id, "phase": self.phase.value,
                "difficulty": self.difficulty, "human": self.human,
                "game": dict(self.game.snapshot())}

    @classmethod
    def restore(cls, registry: GameRegistry, data: Dict[str, Any]) -> "Session":
        fields = {"version", "game_id", "phase", "difficulty", "human", "game"}
        if not isinstance(data, dict) or set(data) != fields:
            raise ValueError("Invalid save file structure.")
        if type(data["version"]) is not int or data["version"] != 1:
            raise ValueError("Unsupported save version.")
        definition = registry.get(data["game_id"])
        cls._validate_options(data["difficulty"], data["human"], definition)
        game = definition.restore(data["game"])
        try:
            phase = Phase(data["phase"])
        except (ValueError, TypeError):
            raise ValueError("Invalid saved phase.") from None
        if phase not in (Phase.PLAYING, Phase.PAUSED, Phase.FINISHED):
            raise ValueError("Invalid saved phase.")
        if (phase == Phase.FINISHED) != (game.outcome is not None):
            raise ValueError("Saved phase does not match the board.")
        session = cls(registry)
        session.phase, session.game_id, session.game = phase, data["game_id"], game
        session.difficulty, session.human = data["difficulty"], data["human"]
        return session
