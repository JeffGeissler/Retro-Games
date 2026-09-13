from PySide6.QtCore import Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPlainTextEdit,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from ..games.tic_tac_toe import TicTacToe


class TerminalBoard(QWidget):
    move_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setAccessibleName("Terminal Tic Tac Toe board")
        self.text.setMinimumHeight(210)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        families = QFontDatabase.families()
        preferred = ("Menlo", "Consolas", "DejaVu Sans Mono", "Liberation Mono", "Courier New")
        # Some offscreen platforms return the unresolved generic name "monospace".
        fixed_family = next((name for name in preferred if name in families), None)
        if fixed_family is None:
            fixed_family = next((name for name in families if QFontDatabase.isFixedPitch(name)),
                                fixed_font.family())
        self.text.setStyleSheet('font-family: "%s"; font-size: 20px;' % fixed_family)
        layout.addWidget(self.text)
        layout.addWidget(QLabel("Type a cell number below, or choose a cell:"))
        row = QHBoxLayout()
        self.cells = []
        for cell in range(1, 10):
            button = QPushButton(str(cell))
            button.setMinimumWidth(28)
            button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            button.setMinimumHeight(38)
            button.clicked.connect(lambda checked=False, n=cell: self.move_requested.emit(n))
            self.cells.append(button)
            row.addWidget(button)
        layout.addLayout(row)

    def render(self, game: TicTacToe, playable: bool) -> None:
        values = [mark or str(i + 1) for i, mark in enumerate(game.board)]
        rows = ["     " + " | ".join(values[i:i + 3]) for i in (0, 3, 6)]
        self.text.setPlainText("\n" + "\n    ---+---+---\n".join(rows) + "\n")
        for cell, button in enumerate(self.cells, 1):
            button.setEnabled(playable and cell in game.legal_moves)
            button.setAccessibleName("Cell %d, %s" % (cell, game.board[cell - 1] or "empty"))


class ModernBoard(QWidget):
    move_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QGridLayout(self)
        layout.setSpacing(10)
        self.cells = []
        for cell in range(1, 10):
            button = QPushButton(str(cell))
            button.setMinimumSize(80, 64)
            button.setStyleSheet("font-size: 28px; font-weight: bold;")
            button.clicked.connect(lambda checked=False, n=cell: self.move_requested.emit(n))
            self.cells.append(button)
            layout.addWidget(button, (cell - 1) // 3, (cell - 1) % 3)

    def render(self, game: TicTacToe, playable: bool) -> None:
        for cell, button in enumerate(self.cells, 1):
            mark = game.board[cell - 1]
            button.setText(mark or str(cell))
            button.setEnabled(playable and cell in game.legal_moves)
            button.setAccessibleName("Row %d, column %d, %s" % (
                (cell - 1) // 3 + 1, (cell - 1) % 3 + 1, mark or "empty"))
            winning = cell in game.winning_cells
            button.setStyleSheet("font-size: 28px; font-weight: bold;" + (
                "border: 3px solid #13a88a; color: #13a88a;" if winning else ""))
