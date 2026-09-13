# Tic Tac Toe increment architecture

The September 13, 2026 user request is the implementation brief for this increment:
a PySide6 app, skippable simulated connection, catalog, terminal and modern boards,
beginner and unbeatable computers, persistent preferences, save/resume, replaceable
speech, and verified rules and persistence. It supersedes the earlier Java-first
hub assumption for this Python application. The earlier proposal remains historical.
The [full ORBIT roadmap](../../architecture.md) was fetched from GitHub during
publication. It includes further requirements beyond this implementation, including
worker-based search and reproducible random continuation; those remain unfinished
and are listed in the application README.

## Boundaries

The engine is immutable and independent of Qt. Its move history is authoritative:
the board, next player, legal moves, winning cells, and outcome are derived from it.
Construction rejects out-of-range, repeated, and post-result moves. Both board
widgets render the same session engine, so changing a theme cannot rebuild a game.

`Game` describes the behavior the session needs: current player, outcome, legal
moves, immutable `play`, and a snapshot. `GameDefinition` supplies catalog metadata,
creation, restoration, and computer strategy. `GameRegistry` rejects duplicate IDs
and unknown games. It is an explicit local registry, not dynamic code loading.

`Session` owns game ID, engine, phase, human mark, and difficulty. `Controller`
coordinates session actions, preferences, and storage. `CommandRouter` is the
common action boundary for UI controls and typed commands. It uses `shlex` only
for tokenization, never to execute commands. UI code owns timers and rendering;
it does not choose computer moves or validate game rules.

## Session transitions

| Current phase | Action | Next phase |
| --- | --- | --- |
| Connecting | Timed completion or skip | Catalog |
| Catalog | Play | Playing |
| Playing | Legal human/computer move | Playing or Finished |
| Playing | Pause | Paused |
| Paused | Resume | Playing |
| Playing / Paused / Finished | Save & catalog | Catalog, after successful save |
| Catalog / Finished | Load | Paused for an unfinished save; Finished otherwise |
| Finished | Play again | Playing with a fresh board |

Save and theme changes preserve phase and engine. Changing difficulty or mark
preferences affects the next game, not the current session. Starting over during
an active/paused game requires returning to the catalog first, which saves it.
Normal close pauses an active game and saves; canceling a failed close restores
the prior active state. Loading validates into a new Session before assignment.

The computer timer is single-shot. Rendering starts it only when a computer turn
is pending and no timer is already active. Pausing, leaving, and closing stop it.
The timer callback rechecks the session before moving, preventing stale moves.
Connection simulation is a separate four-step timer; skip stops it immediately.
No sleeps block the UI thread.

## Persistence

The two JSON files have independent version-1 schemas. Saves store the engine's
move history rather than accepting an arbitrary board with impossible counts or
multiple winners. The loader rejects unknown games/versions and mismatched
terminal phases. JSON reads are size-limited. Writes flush a temporary file and
replace the target atomically; failures preserve the previous target.

There is a single save slot. The app does not coordinate concurrent instances or
provide autosave after every move. Resume preserves the current theme preference
and pauses any unfinished loaded session before allowing play to continue.

## Opponents

Beginner samples uniformly from legal moves. Unbeatable uses cached negamax over
the full remaining game tree with scores win=1, draw=0, loss=-1 from the player
to move's perspective. Center/corner ordering breaks ties. The exhaustive test
branches over every human move while using the production computer strategy for
each computer turn, checking both player assignments for any computer loss.

## Speech and later games

Inject a `Speech` implementation into `Controller`; it has `speak(text)` and
`stop()` methods. The default `SilentSpeech` has no side effects. The UI sends
changed status text and reports adapter failures without stopping gameplay.
A real adapter should enqueue work without blocking the UI; recognition and voice
commands are not part of this increment.

Adding another game requires an engine implementing `Game`, a registered
`GameDefinition`, tests, and a suitable view. The current board widgets and game
page are explicitly Tic Tac Toe-specific; this is not yet a generic board-rendering
plugin system. Native Java/iOS games are not loaded into the Python process.
