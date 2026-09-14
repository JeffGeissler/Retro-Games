"""English/American rules adapter. All library access is confined to this module."""
from dataclasses import dataclass, field
from functools import cached_property
import re
from typing import Tuple
from draughts import Board, BLACK, WHITE

VARIANT = 'english'
DRAW_RULES = 'english-auto-threefold-80-king-plies-v1'
MAX_HISTORY = 16384


def parse_path(text):
    if not isinstance(text, str) or not re.fullmatch(r'\d{1,2}(?:[-x]\d{1,2}){1,12}', text):
        raise ValueError('Use a full path, for example move 9-13 or move 14x23x30.')
    result = tuple(int(part) for part in re.split('[-x]', text))
    if any(not 1 <= cell <= 32 for cell in result):
        raise ValueError('English checkers uses squares 1–32.')
    return result


def parse_fen(fen):
    """Validate our numeric English FEN subset before passing any save data upstream."""
    if not isinstance(fen, str) or len(fen) > 160 or not re.fullmatch(
            r'[BW]:W(?:K?\d{1,2}(?:,K?\d{1,2})*)?:B(?:K?\d{1,2}(?:,K?\d{1,2})*)?', fen):
        raise ValueError('Invalid English checkers starting position.')
    pieces = {}
    for section in fen.split(':')[1:]:
        side = section[0]
        entries = section[1:].split(',') if section[1:] else []
        if len(entries) > 12:
            raise ValueError('English checkers has at most 12 pieces per side.')
        for entry in entries:
            king = entry.startswith('K')
            square = int(entry[1:] if king else entry)
            if not 1 <= square <= 32 or square in pieces:
                raise ValueError('Invalid or duplicated English checkers square.')
            if not king and ((side == 'B' and square >= 29) or (side == 'W' and square <= 4)):
                raise ValueError('A piece on its promotion row must be a king.')
            pieces[square] = side + ('K' if king else '')
    return pieces


@dataclass(frozen=True)
class Checkers:
    initial_fen: str = 'startpos'
    history: Tuple[Tuple[int, ...], ...] = ()
    _board: Board = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        if self.initial_fen != 'startpos':
            parse_fen(self.initial_fen)
        if type(self.history) is not tuple or len(self.history) > MAX_HISTORY:
            raise ValueError('Invalid checkers move history.')
        board = Board(variant=VARIANT, fen=self.initial_fen)
        if board.variant != VARIANT:
            raise ValueError('English checkers rules are required.')
        for path in self.history:
            self._validate_path(path)
            if board.winner() is not None:
                raise ValueError('Moves after the game has ended are not allowed.')
            self._push(board, path)
        object.__setattr__(self, '_board', board)

    @staticmethod
    def _validate_path(path):
        if (type(path) is not tuple or not 2 <= len(path) <= 13 or
                any(type(cell) is not int or not 1 <= cell <= 32 for cell in path)):
            raise ValueError('Provide every landing square of a complete legal move.')

    @staticmethod
    def _push(board, path):
        move = next((m for m in board.legal_moves() if tuple(m.steps_move) == path), None)
        if move is None:
            raise ValueError('Illegal or incomplete move. Captures are mandatory; finish every jump.')
        board.push(move)

    @cached_property
    def _moves(self):
        return tuple(self._board.legal_moves()) if self.outcome is None else ()

    @property
    def legal_moves(self):
        return tuple(tuple(move.steps_move) for move in self._moves)

    @property
    def current_player(self):
        return 'B' if self._board.turn == BLACK else 'W'

    @cached_property
    def outcome(self):
        return {BLACK: 'B', WHITE: 'W', 0: 'draw', None: None}[self._board.winner()]

    @property
    def draw_reason(self):
        if self.outcome != 'draw':
            return ''
        return ('Threefold repetition' if self._board.fens.count(self._board.fen) >= 3
                else '40 moves per side without a capture or man move')

    @cached_property
    def pieces(self):
        # Return an immutable board representation; no upstream internal piece API is exposed.
        pieces = parse_fen(self._board.fen)
        return tuple(pieces.get(cell, '') for cell in range(1, 33))

    @property
    def fen(self):
        return self._board.fen

    def captures(self, path):
        move = next((m for m in self._moves if tuple(m.steps_move) == path), None)
        return tuple(move.captures) if move else ()

    @property
    def capture_required(self):
        return bool(self._moves and self._moves[0].captures)

    def notation(self, path):
        return ('x' if self.captures(path) else '-').join(map(str, path))

    def play(self, path):
        self._validate_path(path)
        if self.outcome is not None:
            raise ValueError('The game has ended.')
        if path not in self.legal_moves:
            raise ValueError('Illegal or incomplete move. Captures are mandatory; finish every jump.')
        board = self._board.copy()  # Copies repetition and draw counters as well as pieces.
        self._push(board, path)
        result = object.__new__(Checkers)
        object.__setattr__(result, 'initial_fen', self.initial_fen)
        object.__setattr__(result, 'history', self.history + (path,))
        object.__setattr__(result, '_board', board)
        return result

    def snapshot(self):
        return {'variant': VARIANT, 'draw_rules': DRAW_RULES,
                'initial_fen': self.initial_fen, 'history': [list(path) for path in self.history]}

    @classmethod
    def restore(cls, data):
        if (not isinstance(data, dict) or set(data) != {'variant', 'draw_rules', 'initial_fen', 'history'} or
                data['variant'] != VARIANT or data['draw_rules'] != DRAW_RULES):
            raise ValueError('Unsupported checkers variant or draw rules. English rules are required.')
        history = data['history']
        if type(history) is not list or len(history) > MAX_HISTORY or any(type(path) is not list for path in history):
            raise ValueError('Invalid checkers move history.')
        return cls(data['initial_fen'], tuple(tuple(path) for path in history))
