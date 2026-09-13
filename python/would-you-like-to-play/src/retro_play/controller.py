from dataclasses import replace
from typing import Optional

from .contracts import SilentSpeech, Speech
from .registry import GameRegistry, default_registry
from .session import Phase, Session
from .storage import Preferences, Store


class Controller:
    def __init__(self, store: Store, registry: Optional[GameRegistry] = None,
                 speech: Optional[Speech] = None) -> None:
        self.store = store
        self.registry = registry or default_registry()
        self.speech = speech or SilentSpeech()
        self.notice = ""
        try:
            self.preferences = store.load_preferences()
        except (OSError, ValueError) as error:
            self.preferences = Preferences()
            self.notice = "Preferences could not be loaded; using defaults. " + str(error)
        self.session = Session(self.registry)
        if not self.preferences.simulate_connection:
            self.session.connect()

    def configure(self, **changes) -> None:
        preferences = replace(self.preferences, **changes)
        self.store.save_preferences(preferences)
        self.preferences = preferences

    def start(self, game_id: str = "tic-tac-toe") -> None:
        self.session.start(game_id, self.preferences.difficulty, self.preferences.human)

    def save(self) -> None:
        self.store.save_game(self.session.snapshot())

    def load(self) -> None:
        if self.session.phase not in (Phase.CATALOG, Phase.FINISHED):
            raise ValueError("Return to catalog before loading a saved game.")
        restored = Session.restore(self.registry, self.store.load_game())
        # Resume is always deliberate, even if the file was saved during play.
        if restored.phase == Phase.PLAYING:
            restored.pause()
        self.session = restored

    def catalog(self) -> None:
        # Preserve the current run before leaving; failed saves keep it on screen.
        if self.session.game is not None:
            self.save()
        self.session.catalog()

    def shutdown(self) -> None:
        if self.session.game is not None:
            self.save()
        self.speech.stop()

    @property
    def status(self) -> str:
        session = self.session
        if session.phase == Phase.CONNECTING:
            return "Simulated connection — offline. Skip at any time."
        if session.phase == Phase.CATALOG:
            return "Would you like to play a game?"
        if session.phase == Phase.PAUSED:
            return "Paused. Choose Resume when you are ready."
        if session.phase == Phase.FINISHED:
            result = session.game.outcome
            return "A draw. Shall we play again?" if result == "draw" else (
                "You win! Shall we play again?" if result == session.human
                else "The computer wins. Shall we play again?")
        return "Computer is thinking…" if session.computer_pending else (
            "Your turn (" + session.human + "). Choose an empty cell.")
