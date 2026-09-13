"""Small, Qt-independent contracts for games and replaceable speech providers."""
from typing import Any, Mapping, Optional, Protocol, Tuple


class Game(Protocol):
    @property
    def current_player(self) -> str: ...

    @property
    def outcome(self) -> Optional[str]: ...

    @property
    def legal_moves(self) -> Tuple[int, ...]: ...

    def play(self, move: int) -> "Game": ...

    def snapshot(self) -> Mapping[str, Any]: ...


class Speech(Protocol):
    def speak(self, text: str) -> None: ...

    def stop(self) -> None: ...


class SilentSpeech:
    """Default adapter. No speech engine, microphone, or network is used."""

    def speak(self, text: str) -> None:
        pass

    def stop(self) -> None:
        pass
