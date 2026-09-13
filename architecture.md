# Architecture: Would you like to play a game

> Proposed design, not an implemented Python application. This document covers the new desktop arcade, not the existing Java, iOS, or Android games. See [README.md](README.md) for the product overview and existing project instructions.

## Goals and scope

Build an offline Python desktop arcade inspired by the retro-computing atmosphere of WarGames. Default to a simulated command line, with an original modem handshake and mechanical speech. Allow players to switch to enhanced retro or modern graphical presentation without losing a match.

The initial catalog comprises tic tac toe, English/American checkers, chess, and **Galatic Thermal Nuclear War**. Retain that requested spelling. The planetary game is an explicitly imaginary arcade board game with invented planets and abstract resources; exclude real-world geography, factions, weapons specifications, and operational military modeling.

Use original dialogue, sounds, and art. The original host, **ORBIT**, delivers concise event-driven observations. An online language model is unnecessary.

This documentation change introduces no application code, dependencies, assets, or packaging. Existing platform applications and their build instructions remain separate.

## User experience

Startup proceeds through a skippable connection sequence, welcome, and game catalog. Provide Mute and Skip before playback starts. The theatrical connection needs no network access.

| Presentation | Layout | Input |
| --- | --- | --- |
| Terminal (default) | Green/amber text, ASCII board, transcript, prompt | Commands and keyboard |
| Enhanced retro | Pixel board and terminal transcript | Keyboard and mouse |
| Modern | Graphical board, clear controls, accessible contrast | Clickable moves and command palette |

Themes are views over the same session. Voice and effects preferences are independent. Persist theme, font size, text speed, reduced motion, voice selection, and separate volume settings.

Decorative typing must not delay access to complete text for assistive technology. All essential information remains visible with sound disabled. Provide original short lines such as “I have calculated several possibilities. You may still surprise me.”

Parse a fixed application command language. Never pass entered text to a shell, evaluate it as Python, or use it to construct executable commands.

## Technology decisions

| Area | Proposed choice | Integration boundary |
| --- | --- | --- |
| Desktop UI | PySide6 / Qt Widgets | Presentation adapters |
| Audio playback | Qt Multimedia | Audio controller |
| Mechanical speech | eSpeak NG | Managed subprocess speech adapter |
| Optional system speech | pyttsx3 | Alternative speech adapter |
| Chess rules | python-chess | Chess rules adapter |
| Chess opponent | Stockfish executable, UCI | Opponent adapter |
| Checkers rules | pydraughts, English/American variant | Checkers rules adapter |
| Checkers opponent | Bounded alpha-beta search | Worker process |
| Storage | Standard-library sqlite3 and JSON | Repository |
| Domain models | Standard-library dataclasses and enums | Core |
| Tests | Standard-library unittest initially | Rules and service boundaries |

Verify compatible releases, platform support, APIs, and packaging at implementation time; this design intentionally does not pin speculative versions.

PySide6 supports both visual styles inside one desktop application. Avoid mixing multiple GUI event loops. Textual is a possible later frontend for an actual terminal, sharing the domain and application layers.

pydraughts supplies rules and engine communication, not a guaranteed ready-made opponent for this application. Start with bounded search over legal actions, and evaluate an external engine only after checking variant and license compatibility.

### Primary references

- [Qt Widgets](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html)
- [Qt Multimedia](https://doc.qt.io/qtforpython-6/overviews/qtmultimedia-multimediaoverview.html)
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
- [python-chess documentation](https://python-chess.readthedocs.io/en/stable/)
- [Stockfish](https://github.com/official-stockfish/Stockfish)
- [pydraughts](https://github.com/AttackingOrDefending/pydraughts)
- [Textual](https://textual.textualize.io/)

The repository currently uses MIT. That does not relicense dependencies. python-chess and Stockfish use GPL licenses; pydraughts identifies MIT licensing and includes additional notices. Evaluate the complete dependency and distribution arrangement before shipping, including Qt and speech backends. Update THIRD_PARTY_NOTICES.md when actual dependencies or assets are added. This design does not change LICENSE or assume a final distribution model.

## Architecture

Use a modular monolith: one application with explicit internal boundaries and no required backend.

```mermaid
flowchart TD
    Views[Terminal and graphical views] --> Controller[Command router and session controller]
    Controller --> Registry[Game registry]
    Registry --> Rules[Game rules and state]
    Controller --> Opponents[Opponent adapters]
    Opponents --> Rules
    Controller --> Storage[Save and settings repository]
    Controller --> Events[Presentation events]
    Events --> Views
    Events --> Dialogue[Dialogue director]
    Dialogue --> Audio[Audio controller]
```

| Component | Owns | Must not own |
| --- | --- | --- |
| Application shell | Startup, catalog, navigation, settings | Game rules |
| Session controller | Turn lifecycle, validation, scheduling, cancellation | Board-specific rendering |
| Game module | Initial state, legal actions, transitions, outcomes | UI, speech, storage |
| Opponent adapter | Action selection and difficulty/time budget | Authoritative state mutation |
| Presentation adapter | Text/board view models | Rules enforcement |
| Dialogue director | Original lines selected from events | Move decisions |
| Audio controller | Synthesis, queue, caching, playback, mute | Match progress |
| Repository | Versioned saves and preferences | Executable object loading |

### Patterns

- **Strategy:** exchange opponents and difficulty policies.
- **Adapter:** isolate third-party rules, engines, and speech.
- **State machine:** make session transitions explicit.
- **Observer/events:** distribute accepted changes to views, history, and dialogue.
- **Repository:** keep storage separate from domain logic.
- **Registry:** explicitly register games without growing central game-specific conditionals.

Do not add a dependency-injection framework or network service without a concrete need. Constructor-provided adapters are sufficient initially.

### Proposed package organization

The following paths are a future layout, not files created by this design:

| Future path | Purpose |
| --- | --- |
| python/would_you_like_to_play/ | Isolated Python application root |
| .../application/ | Session controller, commands, registry |
| .../domain/ | Shared contracts, actions, outcomes, events |
| .../games/ | Registered foundation and expansion game modules |
| .../narrative/ | Optional story director, clue graph, journal, content validation |
| .../opponents/ | Search and external-engine adapters |
| .../presentation/ | Qt shell and theme-specific views |
| .../audio/ | Speech adapters, mixer/controller, cache |
| .../persistence/ | Save and preference repository |
| .../assets/ | Original dialogue, sounds, fonts/art with provenance |
| python/tests/ | Domain, adapter, persistence, and lifecycle checks |

Preserve existing java/, ios/, android/, shared/, and tests/ content. A future Python project can have its own dependency metadata and packaging within python/.

## Game contracts and state

Each registered game declares:

- Stable game ID, display name, rules version, and state schema version.
- Initial state from settings and an optional seed.
- Legal actions for a player and validation without mutation.
- Application of an action or resolution of a simultaneous round.
- Outcome: ongoing, win/loss, draw, shared victory, or shared loss where supported.
- Validated serialization and deserialization.
- Player-specific presentation data independent of Qt; hidden information stays in authoritative state.
- Capabilities such as hints, undo, analysis, player count, observations, and alternating, simultaneous, narrative, or fixed-tick sessions.

Prefer immutable snapshots or controlled copies at boundaries. An accepted action or declared simulation tick is the only path to a game-state transition. Reject invalid actions without partial mutation.

Alternating games use player-turn and computer-turn states. The planetary game uses commit, reveal, and resolve states; do not force it through alternating moves. UI themes consume the same snapshot.

### Lifecycle

Application: connecting → catalog → active session → catalog/exit.

Alternating session: player turn → computer thinking → player turn, with pause and finished transitions.

Simultaneous session: collect commitments → reveal both → resolve once → next round or finished.

Each asynchronous job carries a session ID and state revision. Apply its result only if both still match and the action remains valid.

Hints are optional capabilities and should disclose whether they affect challenge scoring. Define undo behavior per game; do not silently rewind only half a player/computer turn.

## Opponents

| Game | Initial strategy | Difficulty |
| --- | --- | --- |
| Tic tac toe | Random beginner; minimax expert | Randomness / optimal play |
| Checkers | Alpha-beta over library legal moves | Search budget and evaluation |
| Chess | Stockfish through UCI | Supported strength controls and bounded time |
| Planetary | Public-state policies | Cautious, Competitive, Reciprocal, Erratic |

Heavy Python search runs in a worker process. External engines run as managed subprocesses. Keep Qt updates on the UI thread. Enforce deadlines, cancel on session changes, and shut down owned workers on exit. A late answer must never enter a new game.

Use fixed executable paths/configuration and argument arrays for external engines, not shell interpolation. Missing engines produce an actionable message; other catalog games remain available.

## Audio design

Use separate logical channels for effects, narration, and optional ambience. Voice is initially enabled at moderate volume, with mute available before startup audio.

The speech adapter produces an audio asset or reports unavailability. Evaluate eSpeak NG for a deliberately mechanical voice, optionally with restrained filtering. pyttsx3 may provide a platform-dependent alternative. Prototype voice quality, cancellation, and packaging on each target OS.

Cache generated speech by text, backend/version, voice, speed, and effect parameters. Bound the cache and queue. Announce selections, moves, and outcomes instead of reading ASCII characters. Prioritize important outcomes over disposable chatter.

Mute immediately stops playback and clears queued speech. Skip intro cancels its audio and timers. Leaving a game cancels its narration and search. Failures or missing audio devices result in fully playable silent operation. Do not play obsolete narration when audio is re-enabled.

## Persistence

Use a local SQLite repository with validated JSON match payloads. Store preferences separately from match state. Saves include:

- Game ID, rules version, state schema version, and save format version.
- Current state, turn/round phase, move history, and difficulty settings.
- Random seed and generator state needed for reproducible continuation.
- Relevant opponent policy state, such as prior public rounds.
- Creation/update timestamps.

Initially save simultaneous games at completed round boundaries to avoid exposing hidden commitments. State that limitation in the UI. Never use pickle or executable object deserialization for saves.

Use atomic transactions. Validate identifiers, payload shape, bounds, and supported versions before loading. Preserve an incompatible save and explain the issue instead of silently resetting it. Define migrations only when versions actually change.

## Galatic Thermal Nuclear War: provisional design

Subtitle: **An imaginary planet-versus-planet arcade game.**

Use geometric invented worlds such as Vela-9 and Orison, exaggerated moons, fictional technology, and abstract points. The mechanics should make cooperative survival a discoverable outcome.

### Starting balance targets

- Each planet: 10 energy, 5 shield, 10 stability.
- Round income: 3 energy, capped at 15.
- Actions: Charge, Shield, Pulse, Repair, Offer Accord.
- Pulse consumes energy, removes shield before stability, and raises shared rift instability.
- Mutual accord lowers instability and advances a shared peace objective.
- Three consecutive mutual accords produce a shared victory.
- Zero stability produces defeat; simultaneous zero produces mutual collapse.
- Maximum rift instability produces shared loss.
- A round cap ends remaining unresolved matches as draws.

These are provisional targets. Before coding, define action costs/effects, shield/stability caps, instability threshold, round limit, initial income timing, failed-action handling, and precedence when several endings coincide.

### Simultaneous resolution requirements

1. Grant income at the documented round boundary.
2. Give each policy the same permitted public snapshot and its own private state.
3. Validate and commit actions against that snapshot.
4. Reveal only after both commitments exist.
5. Compute effects from both actions and apply a documented resolution table.
6. Evaluate terminal conditions once, using explicit precedence.
7. Record the resolved round and emit presentation events.

No policy may inspect the player's current hidden action. Resolution must not depend on whether the player or computer is processed first. Test symmetry under swapping the planets.

An optional Explore Outcomes mode runs seeded computer-versus-computer matches and reports survival, shared wins, and collapse. Report observed results without claiming a strategy is proven optimal. Balance work should check for endless defense and dominant single-action strategies.

## Expanded catalog and game design

The [expanded catalog in README.md](README.md#expanded-creative-catalog) is part of the planned product scope. Preserve all proposed games while delivering them in stages. The first creative expansion is Ghost in the Modem, Protocol Zero, and First Contact; the original four-game foundation remains the first release.

Each game must have a small rules/design sheet before coding: core loop, allowed information, actions, outcome or completion condition, difficulty, save boundary, and terminal/modern presentation. The following are initial design directions, not complete balanced rules.

| Game | Core loop and completion | Algorithm / design direction |
| --- | --- | --- |
| Falken's Labyrinth | Explore, collect keys, navigate shifts, reach an exit or beat a rival | Seeded graph generation; BFS/A* on the opponent's known map; validate solvability after shifts |
| Ghost in the Modem | Read fictional BBS messages, connect clues, unlock local archives, resolve a case | Authored narrative graph, inventory, prerequisites, graded hints; virtual files only |
| Dead Letter Office | Inspect, hypothesize, decode, submit a message | Seeded cipher puzzles and constraint-based hints; verify intended solutions |
| Starship Captain | Choose a destination, allocate crew, negotiate encounters, finish an expedition | Turn-based graph exploration, seeded events, utility-based rival captain |
| The Last Colony | Allocate resources, resolve a day, react to hazards, survive a scenario | Bounded resource simulation and utility policies; competitive or cooperative scenarios |
| First Contact | Send a symbol sequence, observe a response, infer meaning, complete communication tasks | Seeded finite grammar/lexicon and authored semantic rules; hints resolve ambiguity |
| Paradox Engine | Act, send a limited message to an earlier checkpoint, replay, satisfy an objective | Versioned timeline branches and deterministic replay; explicitly define causal rules |
| Black Box | Submit probes, compare outputs, predict results or identify a rule | Finite rule grammar and bounded hypothesis search; user-created rules use a safe editor |
| Orbital Salvage | Bid, equip a craft, explore a wreck, bank recoveries | Seeded loot/events and utility bidders; define bankruptcy and expedition limits |
| The Impossible Auction | Receive private values, bid, resolve item effects, compare final utility | Hidden-information agents, budgets, declared auction rules, seeded effects |
| Dungeon on Drive B: | Explore, equip, fight, recover an objective, escape | Turn-based map generation, validated routes, finite-state monster tactics |
| Paperclip Republic | Choose production/investments, resolve a market cycle, meet an absurd objective | Bounded economic model, scripted events, competing utility policies |
| Memory Leak | Observe, choose a board action, lose visibility, complete a scenario | Separate observation history and bounded-memory policy; define board rules before coding |
| Protocol Zero | Commit short robot programs, reveal, resolve steps, reach or control objectives | Simultaneous programming, bounded search/rollouts, explicit collision and tie rules |
| The Unwinnable Game | Experiment, find evidence, reinterpret a goal, complete a discoverable alternate objective | Authored scenario state machines; stable hidden rules, graded hints, no arbitrary rule changes |

### Classic variants and remaining candidates

| Game / variant | Initial design direction |
| --- | --- |
| Midnight Blackjack | Standard blackjack with a published house ruleset and fictional chips; ORBIT is dealer |
| Chess Against Yesterday | Chess variant mode using disclosed local style statistics to bias legal engine choices; opt-in profile, inspect/reset controls; no claim of exact personal imitation |
| Solitaire: Lost Transmission | Specify a solitaire variant, legal deals and hints; optional narrative fragments and later same-deal challenge |
| Gin Rummy | Published ruleset, hand evaluation, observation-limited opponent |
| Hearts | Four seats, three distinct policies, explicit passing/scoring rules |
| Bridge | Four seats with computer partner/opponents; select a bidding convention and scoring format before implementation |
| Poker | Choose one variant, betting limits and showdown rules; fictional chips and private-hand isolation |
| Starfighter Duel | Stylized space arena with fixed simulation ticks, pause/resume, textual tactical display and graphical view |
| Four in Orbit | Connect Four style grid with bounded search and terminal/graphical boards |
| Signal Breaker | Code-setting and deduction roles, finite candidate elimination |
| Asteroid Nim | Specify normal or misère rules; mathematical opponent and optional explanation |
| Orbital Reversi | Legal flipping/capture rules and positional search |

These designs may reuse suitable libraries after API, rule, maintenance, and license checks. Small original mechanics can use standard-library collections, heapq, random, and explicit state machines. Do not adopt an unverified package just to avoid implementing a small rule system.

## Architecture extensions for the creative catalog

### Session models and observations

Extend game capabilities to declare alternating, simultaneous, narrative, or fixed-tick play; player count; solo/cooperative/competitive roles; hidden information; and save boundaries. Avoid imposing a two-player alternating-board contract on the entire catalog.

The authoritative rules layer owns complete state. Views, narration, hints, and opponent policies receive player-specific observations. Hidden cards, unseen maze cells, alien meanings, and unrevealed programs must not leak through logs, captions, hints, or modern UI tooltips. An opponent may have scenario-defined knowledge only when the rules disclose it. Memory Leak additionally restricts retained opponent observations rather than merely hiding data at rendering time.

Narrative games consume validated choices or application commands. ORBIT may be a guide, dealer, environment, collaborator, or multiple opponents; a computer adversary is not compulsory for every game.

Starfighter Duel is a later fixed-tick capability: advance simulation through controlled tick transitions, render independently, suspend ticks on pause, and save only at safe paused checkpoints. Keyboard controls and an accessible textual tactical mode need explicit prototyping; graphical fidelity alone does not satisfy terminal-mode support.

### Optional story director

Add a story director alongside the dialogue director. It consumes semantic, spoiler-safe events such as scenario_completed or clue_discovered and maintains a versioned local narrative profile. It does not modify a game's legal moves, opponent information, or base availability.

Store authored story content as validated data with stable clue IDs, prerequisites, optional dialogue, and explicit effects. Evaluate prerequisites deterministically and grant each discovery idempotently. Verify that clue graphs are reachable and do not require playing every game.

Story premise: an unfinished tournament, a missing opponent, and a message dated tomorrow gradually reveal ORBIT's history. All implemented base games remain selectable. Unlock only optional scenarios and dialogue. Provide story-off, spoiler-aware journal, replay clue, and separate story reset controls. Story reset must not delete match saves; resetting a match must not erase story progress.

The story director uses authored templates/state machines and works offline. Fictional BBS messages, “corrupted files,” transmissions, and espionage are in-game data; Ghost in the Modem never browses actual personal files or contacts remote systems.

### Persistence and reproducibility extensions

Persist campaign flags, discovered clue IDs, content version, generated world seeds, opponent persona state, and timeline branch data where relevant. Separate local profile history from individual matches. Chess Against Yesterday profiling is opt-in, local, disclosed, and resettable.

Define save checkpoints per game: completed turns, completed simultaneous rounds, narrative choices, or paused simulation snapshots. Narrative and procedural games must reproduce their world and clue state after loading. Different themes receive equivalent observations and cannot reveal extra clues.

### Delivery stages

1. Foundation: original four games, audio, persistence, themes, and cancellation.
2. Creative identity: Ghost in the Modem, Protocol Zero, First Contact, and the optional story director.
3. Puzzle and classic depth: Falken's Labyrinth, Dead Letter Office, Black Box, Memory Leak, card/board additions and variants.
4. Larger scenarios: Starship Captain, The Last Colony, Orbital Salvage, The Impossible Auction, Dungeon on Drive B:, Paperclip Republic, Paradox Engine, The Unwinnable Game, and Starfighter Duel.

Stages 3–4 are planning groups, not a mandatory internal order. Scope one working game per implementation task; preserve the complete catalog without presenting unimplemented games as playable.

### Additional verification

- Generated mazes and narrative prerequisite graphs have reachable objectives.
- Hidden information is filtered consistently for policies, views, hints, dialogue, and logs.
- Opponent memory limits are enforced in policy state.
- Simultaneous robot programs resolve collisions and ties independently of player processing order.
- Alien-language tasks provide sufficient evidence for their intended solutions; equivalent valid interpretations are handled explicitly.
- Time-travel replay and seeded worlds reproduce after save/load.
- Duplicate events do not duplicate story rewards; story-off keeps ordinary games fully playable.
- Profiles can be inspected/reset without deleting unrelated matches.
- Theme changes reveal no extra information and preserve campaign progress.
- Fixed-tick games pause without advancing timers or physics.

## Verification and delivery

### First playable slice

Connection → catalog → tic tac toe → computer response → result → save/resume → theme switch. Establish cancellation and silent operation here. Add complete audio, chess, checkers, then the planetary game.

### Acceptance criteria

- Illegal moves never mutate state.
- Expert tic tac toe cannot lose across reachable legal play.
- Checkers enforces the selected variant, mandatory captures, multi-jumps, promotion, and documented draws.
- Chess handles promotion, castling, en passant, checkmate, draw claims, and automatic draws.
- Theme changes preserve the exact session state.
- Mute interrupts playback and clears pending narration.
- Restart/exit cancels work; stale results cannot mutate sessions.
- Saves round-trip and reproduce continuation where randomness applies.
- Simultaneous resolution is symmetric and keeps hidden actions private.
- Missing engines, speech backends, or audio devices fail gracefully.
- Keyboard-only use, scaling, focus, and reduced motion work in both main themes.

Use focused domain and lifecycle tests, mocked external failures, and manual desktop/audio checks. Package and smoke-test the current OS first; report other platforms as unverified until tested. Do not claim existing repository CI validates the planned Python application.

## Implementation prompts

Use the shared brief with each prompt, then execute the numbered increments in order. These prompts authorize future implementation when explicitly submitted; this document itself is design-only.

### Shared brief

> Build an offline Python desktop application named “Would you like to play a game” in an isolated python/ area of Retro-Games. Preserve existing applications and documents. Follow architecture.md. Use PySide6 Qt Widgets and Qt Multimedia, a default simulated terminal, a skippable original modem sequence, original mechanical speech, persistent independent audio controls, and a modern theme switchable during a match. The original host ORBIT uses concise event-driven dialogue. Separate game rules, sessions, opponents, presentation, audio, and persistence. Use validated local versioned saves. Keep search and speech generation off the UI thread, cancel on session changes, and reject stale results. Never execute user commands as shell input. Required games are tic tac toe, English/American checkers, chess, and the explicitly fictional planet-versus-planet Galatic Thermal Nuclear War. Verify dependency APIs, versions, licenses, and platform support before integration. Deliver working increments with focused tests and accurate run instructions.

### 1. Foundation and tic tac toe

> Implement the shared brief through a complete tic tac toe experience. Create package boundaries, game contracts, registry, session state machine, command router, Qt shell, skippable connection presentation, catalog, terminal and modern boards, random beginner and unbeatable minimax opponents, preferences, and save/resume. Keep speech behind a replaceable interface. Verify illegal moves, unbeatable play, save round trips, mid-game theme switching, and stale-response rejection. Provide actual run instructions and clearly identify unfinished features.

### 2. Retro speech and modem audio

> Add original modem effects and offline mechanical narration. Evaluate eSpeak NG on the target platform and implement a speech adapter; make pyttsx3 an optional alternative. Use Qt Multimedia playback, bounded caching/queues, separate effects/voice volume, immediate mute, skip, and cancellation. Keep input responsive and silent operation playable. Verify session changes clear narration and re-enabling audio does not play obsolete lines. Document runtime dependencies, platform checks, and asset provenance.

### 3. Chess

> Add chess through python-chess and a managed Stockfish UCI subprocess. Implement typed and graphical moves, promotion selection, legal-move feedback, difficulty, hints, history, outcomes, and save/resume. Bound thinking time and reject stale results. Handle missing/failed engines with an actionable message. Verify special moves, checkmate, draw claims, automatic draws, cancellation, and shutdown. Document acquisition and distribution requirements without changing the repository license implicitly.

### 4. Checkers

> Add English/American checkers using pydraughts after verifying its rules and API. Implement both views, forced captures, full multi-jump selection, promotion, outcomes, saves, and a bounded alpha-beta opponent with adjustable difficulty. Separate search from the rules adapter. Document draw rules and verify that international draughts rules are not selected accidentally. Test capture chains, promotion, no-legal-move outcomes, and cancellation.

### 5. Fictional planetary game

> Implement Galatic Thermal Nuclear War as an original abstract science-fiction arcade game. First complete the provisional rules in architecture.md with explicit costs, caps, timing, resolution table, ending precedence, and round limit. Implement simultaneous commit/reveal/resolve turns with validation against the round snapshot and processing-order-independent results. Opponents may use public state and previous rounds but cannot inspect current hidden player actions. Add Cautious, Competitive, Reciprocal, and Erratic policies, seeded randomness, both visual themes, original narration, round-boundary saves, and optional outcome exploration. Test resource bounds, ending precedence, hidden-action isolation, symmetry, reproducibility, and representative balance scenarios.

### 6. Release readiness and extension

> Finish the application against the acceptance criteria. Verify keyboard use, scaling, reduced motion, immediate mute, startup skipping, save handling, missing engines, audio recovery, and process shutdown. Package and smoke-test the current OS and state which platforms remain unverified. Add appropriate dependency/asset notices. Demonstrate extension boundaries by adding Signal Breaker with computer code-setting and code-solving roles, without game-specific branches in the shell. Keep catalog expansions beyond this scope as future work.

### 7. Creative catalog contracts and optional mystery

> Extend the foundation according to Architecture extensions for the creative catalog. Add observation filtering, explicit session capabilities, and the optional story director with authored local content, stable clue IDs, a spoiler-aware journal, idempotent discoveries, and independent profile reset. Keep all implemented base games available and story-off fully playable. Test hidden-information filtering across every output channel, duplicate events, reset isolation, clue reachability, and save/theme continuity. Keep remaining catalog entries clearly marked as planned.

### 8. Ghost in the Modem

> Build one complete original fictional BBS mystery with messages, virtual archives, an inventory, evidence-linked choices, graded hints, and a satisfying resolution. Use authored narrative data and deterministic prerequisites, not actual filesystem exploration or networking. Give ORBIT a guide role and connect optional discoveries to the story director. Implement terminal and modern presentations, save/resume, story-off behavior, and tests for reachable completion and spoiler-safe hints.

### 9. Protocol Zero

> Write and implement a bounded robot-programming game with short secret programs, simultaneous commitment, step-by-step reveal/resolution, and explicit movement, collision, objective, and tie rules. ORBIT uses only its permitted observations. Provide replay, both themes, legal-program validation, difficulty budgets, and round-boundary saves. Test symmetry, collisions, hidden-program isolation, deterministic replay, and stale-work cancellation.

### 10. First Contact

> Build an offline language-discovery game with a finite seeded alien lexicon/grammar, observable responses, and authored communication objectives. Design enough evidence to infer solutions, accept explicitly equivalent valid interpretations, and provide graded hints. ORBIT plays the alien intelligence using fixed scenario rules. Include a notebook in both themes, saves, optional story discoveries, and tests for consistency, solvability, hidden-answer isolation, and reproducibility.

### 11. One additional catalog game

> Implement one explicitly selected game from the expanded catalog in architecture.md. Before coding, complete its rules sheet: loop, observations, actions, outcomes, difficulty, save boundary, and both presentations. Follow that game's listed design direction and reuse existing contracts. For card games specify the exact variant; for time travel specify causal rules; for Memory Leak enforce policy memory limits; for Starfighter Duel establish fixed-tick and accessible terminal behavior. Deliver only the selected game's playable increment, tests, original content, and accurate instructions. Keep the other catalog entries planned.

### 12. Creative expansion release review

> Verify the expanded application against foundation and creative-catalog acceptance criteria. Check story-off, journal spoilers, hidden-information isolation, profile resets, save migrations, procedural reproducibility, theme parity, and cancellation. Confirm no base game is locked by narrative progress and no planned entry appears playable. Run relevant automated checks and manual desktop/audio checks, update actual build instructions and dependency notices, and state remaining platform limitations.
