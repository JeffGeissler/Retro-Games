# Would you like to play a game?

An offline PySide6 desktop game terminal with a complete single-player Tic Tac Toe
experience and English/American checkers. Switch between a green terminal board and a modern board without
losing your position. Choose a beginner computer or an unbeatable opponent,
play as X or O, and save a game to continue later. Original modem effects and offline
ORBIT narration now use Qt Multimedia, with eSpeak NG and optional pyttsx3 adapters.
See [AUDIO.md](AUDIO.md) for setup, controls, runtime checks, and asset provenance.

This implements the September 13, 2026 coding request. The earlier
[Java hub proposal](../../design/do-you-want-to-play-a-game/DESIGN.md) is a separate
draft. The [shared ORBIT roadmap](../../architecture.md) was retrieved from GitHub
when integrating this increment for publication; the implementation had been built
from the coding request before that roadmap was available locally.

## Open the desktop app

For testing without Python commands, open **Would You Like to Play.app** from
`Retro-Games/build/desktop/` in Finder. Choose **Modern** for mouse-driven boards.
See [DESKTOP.md](DESKTOP.md) for Mac launch instructions, Windows preview builds,
and current packaging limits.

## Run from source (developers)

Requires Python 3.9+ and a desktop supported by PySide6 6.8.3. This dependency
version was exercised with Python 3.9 on macOS; Python 3.11 or 3.12 is also a
suitable choice for a new environment. Installation downloads dependencies;
running the app does not use the network.

From the **Retro-Games repository root** on macOS or Linux:

```sh
python3 -m venv .venv-play-game
source .venv-play-game/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./python/would-you-like-to-play
retro-play
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv-play-game
.\.venv-play-game\Scripts\python.exe -m pip install --upgrade pip
.\.venv-play-game\Scripts\python.exe -m pip install -e .\python\would-you-like-to-play
.\.venv-play-game\Scripts\retro-play.exe
```

With the environment active, `python -m retro_play` is an equivalent entry point.
Skip the connection for one launch or choose a separate data directory:

```sh
retro-play --skip-connection
retro-play --data-dir ./build/play-game-data
```

## Play

1. Watch the approximately four-second **simulated** connection, or select **Skip connection**.
2. Choose the computer difficulty and your mark in the catalog. X always starts.
3. Select **Play Tic Tac Toe**. Click a cell or type its number and press Enter.
4. Form a row, column, or diagonal of three marks. A full board without a winner is a draw.
5. Use **Pause**, **Resume**, or change **Display** at any time. **Play again** starts
   a new game after a win, loss, or draw.

The beginner chooses random legal moves. The unbeatable computer searches all
remaining positions using minimax; it can draw against perfect play. Choosing
O lets the computer make the opening move.

Both displays use the same board numbering:

```text
1 | 2 | 3
--+---+--
4 | 5 | 6
--+---+--
7 | 8 | 9
```

Native buttons support keyboard focus and activation. The modern board exposes
row, column, and occupancy labels; the terminal offers an ASCII board and numbered
cell buttons. **How to play** shows the rules and commands. Controls scroll when
the window is small.

## Checkers

Select **Play English / American Checkers** in the catalog, or type `play checkers`. Choose
your side and difficulty on its card. Type `moves` for legal paths, then `move 9-13`
or a full capture path such as `move 14x23x30`. In Modern display, click the piece
and every landing square. See [CHECKERS.md](CHECKERS.md) for rules, draw policy,
verified pydraughts API, search limits, and save behavior.

## Commands

| Command | Effect |
| --- | --- |
| `help` | Rules and command reference |
| `skip` | Finish the simulated connection immediately |
| `catalog` | Save the current game, then return to the catalog |
| `play` or `play tic-tac-toe` | Start a new game from the catalog or a finished game |
| `move 5` or `5` | Play the center cell |
| `pause` / `resume` | Suspend / continue the current game |
| `save` | Save the current position |
| `load` | Load the save from the catalog or a finished game |
| `theme terminal` / `theme modern` | Change display immediately and persist the preference |
| `difficulty beginner` / `difficulty unbeatable` | Select the opponent for the next game |
| `mark X` / `mark O` | Select your mark for the next game |

Commands are parsed locally; they do not execute shell commands. Invalid moves,
occupied cells, moves during computer turns, and invalid state transitions report
an error without changing the board.

## Preferences and save/resume

Theme, next-game difficulty, next-game mark, and whether to simulate the next
connection persist in `preferences.json`. One save slot, `session.json`, contains
the game ID, schema version, move history, phase, difficulty, and player mark.

**Save**, **Save & catalog**, and normal window closure write the current game.
A later save replaces the single slot. Starting a new game does not immediately
overwrite it. There is no per-move autosave or crash recovery of unsaved moves.

Select **Load saved game**, then **Resume**. An unfinished loaded game is always
paused, including saves made during the computer's turn. Finished saves show the
result. Loading a game does not change your current display preference. A pending
computer move executes once after resume.

By default files live in Qt's application data directory for `RetroGames` /
`WouldYouLikeToPlay`; its exact location depends on the OS. Use `--data-dir` to
choose an explicit location for backups or portable testing. The application uses
[Qt's QStandardPaths API](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QStandardPaths.html)
to select the default location.

Writes use a temporary file and atomic replacement. Loading replays every move
and checks the phase, version, and settings before replacing the session. Corrupt
preferences fall back to defaults with a visible notice. A failed save when
returning to the catalog leaves the game open; a failed save on close offers
Cancel or Close without saving. Use one running instance per data directory.

## Verify

With the virtual environment activated, from the repository root:

```sh
python -m unittest discover -s python/would-you-like-to-play/tests -v
```

For a headless runner on macOS/Linux:

```sh
QT_QPA_PLATFORM=offscreen python -m unittest discover -s python/would-you-like-to-play/tests -v
```

Core-only verification does not import Qt:

```sh
python -m unittest discover -s python/would-you-like-to-play/tests -p test_core.py -v
```

The combined local suite passed 45 tests, including actual Qt widgets and checkers workers. The audio increment
adds subprocess, queue, cancellation, cache, asset, and physical-output checks
described in [AUDIO.md](AUDIO.md). Coverage
includes illegal and post-game moves; wins and draws; all human continuations
against the unbeatable strategy as either mark (152 terminal branches as X and
635 as O); valid and invalid save round trips; failed-write preservation;
preferences; keyboard moves; connection skipping; pause/resume; replay; and
mid-game display changes with a pending computer move, and narrow-window layouts.
The GitHub Actions workflow now runs this suite on Linux; that remote job has not
been executed as part of this local implementation.

## Package structure

```text
src/retro_play/
  __main__.py          CLI and QApplication entry point
  audio/               Synthesis adapters, narration/cache service, Qt playback, assets
  contracts.py         Game protocol and replaceable Speech interface
  registry.py          Game metadata, engine factories, restore and opponent hooks
  games/checkers.py     English-only pydraughts rules and validated replay
  opponents/            Bounded checkers search and cancellable process transport
  ui/checkers_board.py  ASCII and graphical full-chain selection
  games/tic_tac_toe.py  Immutable rules, replay validation, beginner and minimax AI
  session.py           Session state machine and versioned snapshots
  storage.py           Preferences and atomic JSON persistence
  controller.py        Application operations and storage coordination
  commands.py          Shared command router for UI and typed input
  ui/boards.py         Terminal and modern board widgets
  ui/window.py         Connection, catalog, game shell and cancellable Qt timers
tests/
  test_core.py          Rules, strategy, state and persistence tests
  test_ui.py            Real Qt interaction tests
  test_audio.py         Audio lifecycle, synthesis, cache and asset tests
  playback_probe.py     Isolated zero-volume physical-device smoke test
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for contracts, state transitions, and extension boundaries.

## Deliberately unfinished

- Broader roadmap items still pending include off-UI-thread Tic Tac Toe search, reproducible
  beginner RNG continuation across saves, self-play study mode, enhanced-retro
  presentation, text-scaling/reduced-motion preferences, and a broader ORBIT dialogue system.
  Current Tic Tac Toe search runs synchronously over its small finite tree;
  beginner saves preserve the position but not future random choices.

- Offline narration is implemented; speech recognition, microphone access, voice
  command input, and a system voice picker remain unimplemented.
- Tic Tac Toe and English checkers are integrated. Chess and the planetary game remain unfinished. Eight Ball and Alien Invasion retain
  their existing separate Java/mobile entry points. There is no Python adapter for them.
- No real connection, networking, multiplayer, cloud saves, multiple save slots,
  scores across games, signed installers, automatic updates, or mobile Python builds. Standalone desktop preview packaging is implemented.
- Automated Qt tests and rendered previews do not constitute a full native-device,
  screen-reader, or cross-platform accessibility audit. Windows and Linux have not
  been exercised locally.

The original repository license applies to this source. PySide6 and Qt retain
their own licenses; see the repository's third-party notices.
