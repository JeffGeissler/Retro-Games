# English / American checkers

Checkers is playable from the catalog in either display. Install the application
as described in [README.md](README.md); `pydraughts==0.6.7` is a required, pinned
dependency. Its Python import is `draughts` (not the separate `py-draughts` package).

## Play

Choose Beginner, Intermediate, or Advanced and Black or White on the checkers card.
Black moves first. Type `play checkers`, then `moves` to list complete legal paths.
Use `move 9-13` for a quiet move or `move 14x23x30` for a capture chain. Squares
1–32 run left to right along the dark squares, starting at the top. Black advances
downward. Terminal men are `b`/`w`, kings `B`/`W`; graphical kings carry a K.

In Modern display, select a piece and each highlighted landing square. Every jump
must be selected before the move commits. Clear selection starts the selection
over. Switching display preserves this selection; saving preserves the last
completed move, not an unfinished selection. Pause, save, catalog, load, and resume
work as for Tic Tac Toe. Loading restores an unfinished game paused. Selecting
White lets the computer start. Difficulty and side changes apply to the next game;
while in checkers, `difficulty advanced` and `mark W` update those preferences.

## Verified rules and library boundary

The adapter explicitly constructs `Board(variant="english", fen=...)` on every
new game and restore. The library's default is international draughts and is
**never used**. Saves identify both `english` and the selected draw policy; other
variants are rejected. The adapter uses `legal_moves()`, complete `Move.steps_move`
paths, `Move.captures`, `push`, `copy`, `fen`, `turn`, and `winner` from the installed
0.6.7 API. Search has no direct library imports.

Verified against the installed implementation and regression fixtures:

- 8×8 board, 32 playable squares, 12 men per side, Black first.
- Men move and capture forward; kings move one diagonal square and jump an
  adjacent enemy, including backward. No flying kings or backward man captures.
- Captures are compulsory and chains must finish. When capture choices differ
  in length, either complete chain is legal: there is no maximum-capture rule.
- Reaching the king row crowns a man and ends its turn immediately, including
  during a jump. A newly crowned king cannot continue backward that turn.
- Having no pieces or no legal move loses. No legal move takes precedence over draw.

These distinctions follow the [WCDF English rules](https://wcdf.net/rules/rules_of_checkers_english.pdf).
Library provenance and API: [pydraughts source](https://github.com/AttackingOrDefending/pydraughts)
and [pinned release](https://pypi.org/project/pydraughts/0.6.7/).

## Selected draw rules

The application uses pydraughts' English automatic adjudication: a third occurrence
of the same position with the same player to move, or 80 consecutive plies
(40 moves by each side) without a capture or a man move. A capture or any man move,
including promotion, resets that clock. Repetition history and the clock survive
save/resume because the full legal history is replayed. The policy identifier is
`english-auto-threefold-80-king-plies-v1`.

This is automatic computer-game adjudication. Tournament referee claims, agreed
draws, and additional tournament procedures are not implemented.

## Computer and cancellation

Separate iterative-deepening negamax with alpha-beta pruning evaluates material,
king value, and man advancement. Limits are whichever is reached first:

| Level | Maximum depth (plies) | Nodes | Search time |
| --- | ---: | ---: | ---: |
| Beginner | 2 | 200 | 0.15 seconds |
| Intermediate | 4 | 1,200 | 0.5 seconds |
| Advanced | 6 | 5,000 | 1.5 seconds |

The last completed iteration supplies the move; a legal deterministic fallback is
available if the first iteration expires. This opponent is bounded, not unbeatable.
Time checks occur between search nodes; an individual rule operation may exceed
the soft search time. A separate QProcess keeps input responsive and has a hard
5-second watchdog including startup. Pause, catalog, and close kill it without
waiting on the UI thread. Results must match the request token and current session
snapshot and pass the rules adapter again. Errors pause the game for retry.
No opening book, endgame database, pondering, or transposition table is included.

## Verification

The local macOS suite covers English/international distinctions, unequal capture
choices, complete chains, both-color crowning, blocked-side defeat, repetition,
40-move draws and reset, save replay, search budgets, cooperative cancellation,
real worker completion, timeout, stale replies, and display changes. Run the full
suite using the README command. Native Windows/Linux validation and playing-strength
benchmarking remain outstanding.
