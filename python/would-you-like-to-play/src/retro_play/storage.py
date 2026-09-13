"""Versioned JSON persistence; atomic replacement keeps the prior file on failure."""
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict


@dataclass(frozen=True)
class Preferences:
    theme: str = "terminal"
    difficulty: str = "beginner"
    human: str = "X"
    simulate_connection: bool = True

    def __post_init__(self) -> None:
        if self.theme not in ("terminal", "modern"):
            raise ValueError("Theme must be terminal or modern.")
        if self.difficulty not in ("beginner", "unbeatable"):
            raise ValueError("Difficulty must be beginner or unbeatable.")
        if self.human not in ("X", "O"):
            raise ValueError("Player mark must be X or O.")
        if type(self.simulate_connection) is not bool:
            raise ValueError("Invalid connection preference.")


class Store:
    def __init__(self, directory: Path) -> None:
        self.directory = Path(directory)

    def _read(self, name: str) -> Dict[str, Any]:
        path = self.directory / name
        if path.stat().st_size > 65536:
            raise ValueError("The data file is too large.")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeError) as error:
            raise ValueError("The data file is not valid JSON.") from error
        if not isinstance(data, dict):
            raise ValueError("The data file must contain an object.")
        return data

    def _write(self, name: str, data: Dict[str, Any]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                             dir=self.directory, delete=False) as output:
                temporary = output.name
                json.dump(data, output, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.directory / name)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)

    def load_preferences(self) -> Preferences:
        try:
            data = self._read("preferences.json")
        except FileNotFoundError:
            return Preferences()
        expected = {"version", "theme", "difficulty", "human", "simulate_connection"}
        if set(data) != expected or type(data["version"]) is not int or data["version"] != 1:
            raise ValueError("Unsupported preferences file.")
        return Preferences(**{key: value for key, value in data.items() if key != "version"})

    def save_preferences(self, preferences: Preferences) -> None:
        self._write("preferences.json", {"version": 1, **asdict(preferences)})

    def save_game(self, snapshot: Dict[str, Any]) -> None:
        self._write("session.json", snapshot)

    def load_game(self) -> Dict[str, Any]:
        try:
            return self._read("session.json")
        except FileNotFoundError:
            raise ValueError("No saved game yet. Start a game, then choose Save.") from None
