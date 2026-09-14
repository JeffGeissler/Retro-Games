from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFontDatabase, QPainter, QPen
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPlainTextEdit,
                               QPushButton, QStackedWidget, QVBoxLayout, QWidget)


def square_at(row, column):
    return row * 4 + column // 2 + 1 if (row + column) % 2 else None


class Square(QPushButton):
    def __init__(self, number):
        super().__init__()
        self.number = number
        self.piece = ''
        self.selected = False
        self.hint = False
        self.setMinimumSize(38, 42)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.fillRect(rect, QColor('#75513b' if self.number else '#ebd5b1'))
        if self.number:
            font = painter.font()
            font.setPixelSize(11)
            painter.setFont(font)
            painter.setPen(QColor('#ffffff'))
            painter.drawText(rect.adjusted(3, 1, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, str(self.number))
        if self.piece:
            diameter = min(rect.width(), rect.height()) - 15
            center = rect.center()
            from PySide6.QtCore import QRectF
            circle = QRectF(center.x() - diameter / 2, center.y() - diameter / 2 + 2, diameter, diameter)
            black = self.piece[0] == 'B'
            painter.setBrush(QColor('#182234' if black else '#fff5dd'))
            painter.setPen(QPen(QColor('#bdcbe5' if black else '#382312'), 2))
            painter.drawEllipse(circle)
            if self.piece.endswith('K'):
                font.setPixelSize(max(12, int(diameter * .55)))
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(QColor('#ffffff' if black else '#182234'))
                painter.drawText(circle, Qt.AlignmentFlag.AlignCenter, 'K')
        if self.selected or self.hint or self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor('#67ffbc' if self.selected else '#ffdf57'), 3))
            painter.drawRect(rect.adjusted(2, 2, -2, -2))


class CheckersBoard(QWidget):
    move_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.game = None
        self.path = ()
        self.key = None
        self.playable = False
        layout = QVBoxLayout(self)
        self.views = QStackedWidget()
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(240)
        self.terminal.setAccessibleName('Numbered English checkers board')
        families = QFontDatabase.families()
        family = next((f for f in ('Menlo', 'Consolas', 'DejaVu Sans Mono', 'Courier New') if f in families), 'monospace')
        self.terminal.setStyleSheet('font-family: "%s"; font-size: 15px;' % family)
        self.views.addWidget(self.terminal)
        graphical = QWidget()
        grid = QGridLayout(graphical)
        grid.setSpacing(0)
        self.squares = {}
        for row in range(8):
            for col in range(8):
                number = square_at(row, col)
                button = Square(number)
                if number:
                    button.clicked.connect(lambda checked=False, n=number: self.select(n))
                    self.squares[number] = button
                else:
                    button.setEnabled(False)
                grid.addWidget(button, row, col)
        self.views.addWidget(graphical)
        layout.addWidget(self.views)
        legend = QLabel('Black moves down from 1–12; White moves up from 21–32. K marks a king.\n'
                        'Terminal: b/w = man, B/W = king. Type moves to list complete legal paths.')
        legend.setWordWrap(True)
        layout.addWidget(legend)
        self.selection = QLabel()
        self.selection.setWordWrap(True)
        self.selection.setAccessibleName('Checkers move selection')
        layout.addWidget(self.selection)
        self.clear = QPushButton('Clear selection')
        self.clear.clicked.connect(self.reset_selection)
        layout.addWidget(self.clear)

    def reset_selection(self):
        self.path = ()
        self._selection()

    def render(self, game, playable, theme):
        key = (game.fen, game.history)
        if key != self.key:
            self.path = ()
            self.key = key
        self.game, self.playable = game, playable
        rows = []
        for row in range(8):
            cells = []
            for col in range(8):
                square = square_at(row, col)
                value = ''
                if square:
                    piece = game.pieces[square - 1]
                    mark = (piece[0] if piece.endswith('K') else piece.lower()) if piece else '.'
                    value = mark + str(square).zfill(2)
                cells.append(value.center(5))
            rows.append(''.join(cells))
        text = '\n'.join(rows)
        if self.terminal.toPlainText() != text:
            self.terminal.setPlainText(text)
        self.views.setCurrentIndex(0 if theme == 'terminal' else 1)
        self._selection()

    def _selection(self):
        if self.game is None:
            return
        candidates = [move for move in self.game.legal_moves if move[:len(self.path)] == self.path]
        next_cells = {move[len(self.path)] for move in candidates if len(move) > len(self.path)}
        starts = {move[0] for move in self.game.legal_moves}
        for square, button in self.squares.items():
            piece = self.game.pieces[square - 1]
            button.piece = piece
            button.selected = square in self.path
            button.hint = self.playable and square in next_cells
            button.setEnabled(self.playable and square in (next_cells | starts))
            name = ('Black' if piece.startswith('B') else 'White') + (' king' if piece.endswith('K') else ' man') if piece else 'empty'
            button.setAccessibleName('Square %d, %s' % (square, name))
            button.update()
        self.clear.setEnabled(bool(self.path))
        if self.path:
            self.selection.setText('Selected path: ' + ' → '.join(map(str, self.path)) +
                                   '. Next landing: ' + ', '.join(map(str, sorted(next_cells))) +
                                   '. The board changes only after the full move is selected.')
        else:
            self.selection.setText('Capture required. Choose a capturing piece.' if self.game.capture_required
                                   else 'Choose a piece, then its destination. Or enter a full move below.')

    def select(self, square):
        if not self.playable:
            return
        prefix = self.path + (square,)
        candidates = [move for move in self.game.legal_moves if move[:len(prefix)] == prefix]
        if not candidates:
            prefix = (square,)
            candidates = [move for move in self.game.legal_moves if move[0] == square]
        if not candidates:
            return
        self.path = prefix
        if prefix in self.game.legal_moves:
            notation = self.game.notation(prefix)
            self.path = ()
            self.move_requested.emit(notation)
        self._selection()
