"""Bounded iterative-deepening alpha-beta. Depends only on the rules adapter."""
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class Budget:
    depth: int
    nodes: int
    seconds: float


BUDGETS = {'beginner': Budget(2, 200, .15), 'intermediate': Budget(4, 1200, .5),
           'advanced': Budget(6, 5000, 1.5)}


class SearchCancelled(Exception):
    pass


class BudgetReached(Exception):
    pass


def evaluate(game):
    score = 0
    for cell, piece in enumerate(game.pieces, 1):
        if not piece:
            continue
        side, king = piece[0], piece.endswith('K')
        row = (cell - 1) // 4
        value = 175 if king else 100 + (row if side == 'B' else 7 - row) * 5
        score += value if side == game.current_player else -value
    return score


def search(game, difficulty, cancelled=lambda: False, budget=None):
    if difficulty not in BUDGETS:
        raise ValueError('Choose beginner, intermediate, or advanced for checkers.')
    budget = budget or BUDGETS[difficulty]
    if not game.legal_moves:
        raise ValueError('There is no legal computer move.')
    started = time.monotonic()
    nodes = 0
    completed = 0
    best = sorted(game.legal_moves)[0]  # Legal deterministic fallback if the budget expires early.

    def check_budget():
        if cancelled():
            raise SearchCancelled()
        if nodes >= budget.nodes or time.monotonic() - started >= budget.seconds:
            raise BudgetReached()

    def ordered(position):
        return sorted(position.legal_moves, key=lambda move: (-len(position.captures(move)), move))

    def negamax(position, depth, alpha, beta):
        nonlocal nodes
        check_budget()
        nodes += 1
        if position.outcome is not None:
            return 0 if position.outcome == 'draw' else (
                100000 + depth if position.outcome == position.current_player else -100000 - depth)
        if depth == 0:
            return evaluate(position)
        value = -1000000
        for move in ordered(position):
            child = position.play(move)
            score = -negamax(child, depth - 1, -beta, -alpha)
            value = max(value, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return value

    try:
        for depth in range(1, budget.depth + 1):
            value = -1000000
            candidate = best
            for move in ordered(game):
                check_budget()
                score = -negamax(game.play(move), depth - 1, -1000000, -value)
                if score > value:
                    value, candidate = score, move
            best, completed = candidate, depth
    except BudgetReached:
        pass
    return {'move': list(best), 'nodes': nodes, 'depth': completed,
            'elapsed': time.monotonic() - started}
