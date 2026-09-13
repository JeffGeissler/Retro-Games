from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit,
                               QProgressBar, QPushButton, QScrollArea, QStackedWidget,
                               QVBoxLayout, QWidget)

from ..commands import CommandRouter, HELP
from ..controller import Controller
from ..session import Phase
from .boards import ModernBoard, TerminalBoard

THEMES = {
    "terminal": """
        QWidget { background: #081110; color: #b5f5d1; font-size: 14px; }
        QLabel#title { color: #64ffb0; font-size: 25px; font-weight: bold; }
        QLabel#eyebrow { color: #53cdd1; font-size: 12px; }
        QPushButton, QComboBox, QLineEdit { background: #112722; border: 1px solid #3d7868;
            border-radius: 5px; padding: 8px; }
        QPushButton:hover { background: #1c4135; }
        QPushButton:focus, QLineEdit:focus, QComboBox:focus { border: 2px solid #72ffbb; }
        QPushButton:disabled { color: #789b8a; background: #0c1915; border-color: #294c3d; }
        QPlainTextEdit { background: #060e0c; border: 1px solid #294c3d; padding: 8px; }
        QFrame#card { border: 1px solid #3d7868; border-radius: 8px; }
        QProgressBar { border: 1px solid #3d7868; text-align: center; }
        QProgressBar::chunk { background: #228c63; }
    """,
    "modern": """
        QWidget { background: #f1f4fa; color: #17243b; font-size: 14px; }
        QLabel#title { color: #253f81; font-size: 25px; font-weight: bold; }
        QLabel#eyebrow { color: #52627b; font-size: 12px; }
        QPushButton, QComboBox, QLineEdit { background: #ffffff; border: 1px solid #b5c3dc;
            border-radius: 9px; padding: 8px; }
        QPushButton:hover { background: #dfe8ff; }
        QPushButton:focus, QLineEdit:focus, QComboBox:focus { border: 2px solid #365cce; }
        QPushButton:disabled { color: #546580; background: #e5eaf3; border-color: #c9d2e3; }
        QPlainTextEdit { background: #ffffff; border: 1px solid #c9d2e3; padding: 8px; }
        QFrame#card { border: 1px solid #b5c3dc; border-radius: 10px; }
        QProgressBar { border: 1px solid #b5c3dc; text-align: center; }
        QProgressBar::chunk { background: #839ee9; }
    """,
}


def label(text: str, name: str = "") -> QLabel:
    widget = QLabel(text)
    widget.setWordWrap(True)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    if name:
        widget.setObjectName(name)
    return widget


class MainWindow(QMainWindow):
    def __init__(self, controller: Controller) -> None:
        super().__init__()
        self.controller = controller
        self.router = CommandRouter(controller)
        self.setWindowTitle("Would you like to play a game?")
        self.resize(820, 860)
        self.setMinimumSize(560, 540)
        self._theme = None
        self._spoken_status = None
        self._last_phase = None

        self.ai_timer = QTimer(self)
        self.ai_timer.setSingleShot(True)
        self.ai_timer.setInterval(350)
        self.ai_timer.timeout.connect(self._computer_turn)
        self.connection_timer = QTimer(self)
        self.connection_timer.setInterval(450)
        self.connection_timer.timeout.connect(self._connection_step)
        self.connection_step = 0

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(label("RETRO-GAMES  /  LOCAL PLAY  /  01", "eyebrow"))
        layout.addWidget(label("Would you like to play a game?", "title"))
        toolbar = QHBoxLayout()
        toolbar.addWidget(label("Display"))
        self.theme = QComboBox()
        self.theme.addItems(["Terminal", "Modern"])
        self.theme.setAccessibleName("Board display theme")
        self.theme.currentTextChanged.connect(lambda text: self.execute("theme " + text.lower()))
        toolbar.addWidget(self.theme)
        toolbar.addStretch()
        self.help_button = self._button("How to play", "help")
        toolbar.addWidget(self.help_button)
        layout.addLayout(toolbar)
        self.status = label("")
        self.status.setAccessibleName("Session status")
        layout.addWidget(self.status)

        self.pages = QStackedWidget()
        layout.addWidget(self.pages)
        self._build_connection()
        self._build_catalog()
        self._build_game()

        self.transcript = QPlainTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setMaximumBlockCount(150)
        self.transcript.setFixedHeight(120)
        self.transcript.setAccessibleName("Command responses")
        layout.addWidget(self.transcript)
        command_row = QHBoxLayout()
        self.command = QLineEdit()
        self.command.setPlaceholderText("Enter a command or cell 1–9. Type help for commands.")
        self.command.setAccessibleName("Game command")
        self.command.returnPressed.connect(self._submit)
        command_row.addWidget(self.command)
        send = QPushButton("Enter")
        send.clicked.connect(self._submit)
        command_row.addWidget(send)
        layout.addLayout(command_row)
        layout.addWidget(label("OFFLINE • Single-player • Progress saved on this device", "eyebrow"))
        scroll.setWidget(root)
        self.setCentralWidget(scroll)
        self._append(controller.notice or "Welcome. Select Tic Tac Toe or type help.")
        self.render()
        if controller.session.phase == Phase.CONNECTING:
            self.connection_timer.start()

    def _button(self, text: str, command: str) -> QPushButton:
        button = QPushButton(text.replace("&", "&&"))
        button.setMinimumHeight(38)
        button.clicked.connect(lambda checked=False: self.execute(command))
        return button

    def _build_connection(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(label("ESTABLISHING A LITTLE NOSTALGIA", "eyebrow"))
        self.connection_text = label("Initializing local terminal…")
        layout.addWidget(self.connection_text)
        layout.addWidget(label("This connection is simulated. No modem, server, or network is used."))
        self.progress = QProgressBar()
        self.progress.setRange(0, 4)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.skip = self._button("Skip connection", "skip")
        layout.addWidget(self.skip)
        self.pages.addWidget(page)

    def _build_catalog(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(label("GAME CATALOG", "eyebrow"))
        options = QHBoxLayout()
        options.addWidget(label("Computer"))
        self.difficulty = QComboBox()
        self.difficulty.addItems(["Beginner", "Unbeatable"])
        self.difficulty.setAccessibleName("Computer difficulty for next game")
        self.difficulty.currentTextChanged.connect(lambda text: self.execute("difficulty " + text.lower()))
        options.addWidget(self.difficulty)
        options.addWidget(label("Your mark"))
        self.mark = QComboBox()
        self.mark.addItems(["X", "O"])
        self.mark.setAccessibleName("Your mark for next game")
        self.mark.currentTextChanged.connect(lambda text: self.execute("mark " + text))
        options.addWidget(self.mark)
        layout.addLayout(options)
        layout.addWidget(label("X moves first. Beginner plays random legal moves; Unbeatable plays optimally."))
        self.play_buttons = []
        for definition in self.controller.registry.catalog():
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(label(definition.title, "title"))
            card_layout.addWidget(label(definition.description))
            card_layout.addWidget(label(definition.instructions))
            play = self._button("Play " + definition.title, "play " + definition.id)
            self.play_buttons.append(play)
            card_layout.addWidget(play)
            layout.addWidget(card)
        layout.addWidget(self._button("Load saved game", "load"))
        self.simulation = QCheckBox("Show simulated connection on next launch")
        self.simulation.toggled.connect(self._simulation_changed)
        layout.addWidget(self.simulation)
        layout.addWidget(label("Eight Ball and Alien Invasion remain separate apps in this repository; "
                               "they are not integrated into this Python catalog."))
        self.pages.addWidget(page)

    def _build_game(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.game_heading = label("")
        layout.addWidget(self.game_heading)
        self.boards = QStackedWidget()
        self.terminal_board = TerminalBoard()
        self.modern_board = ModernBoard()
        for board in (self.terminal_board, self.modern_board):
            board.move_requested.connect(lambda cell: self.execute("move " + str(cell)))
            self.boards.addWidget(board)
        layout.addWidget(self.boards)
        actions = QHBoxLayout()
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(lambda: self.execute(
            "resume" if self.controller.session.phase == Phase.PAUSED else "pause"))
        actions.addWidget(self.pause_button)
        actions.addWidget(self._button("Save", "save"))
        actions.addWidget(self._button("Save & catalog", "catalog"))
        self.again = self._button("Play again", "play tic-tac-toe")
        actions.addWidget(self.again)
        layout.addLayout(actions)
        layout.addWidget(label("Three in a row wins. Cells are numbered 1–9, left to right, top to bottom. "
                               "Save & catalog and closing the window save your current game."))
        self.pages.addWidget(page)

    def _append(self, text: str) -> None:
        if text:
            self.transcript.appendPlainText(text)

    def _submit(self) -> None:
        text = self.command.text()
        self.command.clear()
        self.execute(text)
        self.command.setFocus()

    def execute(self, text: str) -> None:
        result = self.router.execute(text)
        if text.strip():
            self._append("> " + text)
        self._append(("Error: " if not result.ok else "") + result.message)
        if text.strip().lower() == "help":
            QMessageBox.information(self, "How to play", self.controller.registry.get(
                "tic-tac-toe").instructions + "\n\n" + HELP)
        self.render()

    def _simulation_changed(self, enabled: bool) -> None:
        try:
            self.controller.configure(simulate_connection=enabled)
        except (OSError, ValueError) as error:
            self._append("Error: " + str(error))
        self.render()

    def _connection_step(self) -> None:
        if self.controller.session.phase != Phase.CONNECTING:
            self.connection_timer.stop()
            return
        self.connection_step += 1
        self.progress.setValue(self.connection_step)
        messages = ("", "Checking local game library…", "Preparing the board…",
                    "Local terminal ready.", "Welcome.")
        self.connection_text.setText(messages[self.connection_step])
        if self.connection_step == 4:
            self.execute("skip")

    def _computer_turn(self) -> None:
        self.controller.session.computer_step()
        self._append(self.controller.status)
        self.render()

    @staticmethod
    def _select(combo: QComboBox, text: str) -> None:
        combo.blockSignals(True)
        combo.setCurrentText(text)
        combo.blockSignals(False)

    def render(self) -> None:
        c, session = self.controller, self.controller.session
        if self._theme != c.preferences.theme:
            self._theme = c.preferences.theme
            self.setStyleSheet(THEMES[self._theme])
        self._select(self.theme, c.preferences.theme.title())
        self._select(self.difficulty, c.preferences.difficulty.title())
        self._select(self.mark, c.preferences.human)
        self.simulation.blockSignals(True)
        self.simulation.setChecked(c.preferences.simulate_connection)
        self.simulation.blockSignals(False)
        self.status.setText(c.status)
        if c.status != self._spoken_status:
            self._spoken_status = c.status
            try:
                c.speech.speak(c.status)
            except Exception as error:
                self._append("Speech adapter unavailable: " + str(error))
        if session.phase != Phase.CONNECTING:
            self.connection_timer.stop()
        if session.phase == Phase.CONNECTING:
            self.pages.setCurrentIndex(0)
        elif session.phase == Phase.CATALOG:
            self.pages.setCurrentIndex(1)
            if self._last_phase != Phase.CATALOG and self.play_buttons:
                self.play_buttons[0].setFocus()
        else:
            self.pages.setCurrentIndex(2)
            self.game_heading.setText("TIC TAC TOE  •  You: %s  •  Computer: %s  •  %s" % (
                session.human, "O" if session.human == "X" else "X", session.difficulty.title()))
            playable = session.phase == Phase.PLAYING and not session.computer_pending
            self.terminal_board.render(session.game, playable)
            self.modern_board.render(session.game, playable)
            self.boards.setCurrentIndex(0 if self._theme == "terminal" else 1)
            self.pause_button.setText("Resume" if session.phase == Phase.PAUSED else "Pause")
            self.pause_button.setEnabled(session.phase in (Phase.PAUSED, Phase.PLAYING))
            self.again.setVisible(session.phase == Phase.FINISHED)
        if session.computer_pending:
            if not self.ai_timer.isActive():
                self.ai_timer.start()
        else:
            self.ai_timer.stop()
        self._last_phase = session.phase

    def closeEvent(self, event) -> None:
        was_playing = self.controller.session.phase == Phase.PLAYING
        if was_playing:
            self.controller.session.pause()
        self.ai_timer.stop()
        self.connection_timer.stop()
        try:
            self.controller.shutdown()
        except (OSError, ValueError) as error:
            answer = QMessageBox.question(self, "Unable to save", str(error) +
                "\nClose without saving?", QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
            if answer != QMessageBox.StandardButton.Discard:
                if was_playing:
                    self.controller.session.resume()
                if self.controller.session.phase == Phase.CONNECTING:
                    self.connection_timer.start()
                self.render()
                event.ignore()
                return
        event.accept()
