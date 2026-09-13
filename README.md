# Retro-Games

Games I wrote in the early 2000s, modernized for smartphones (iOS and Android).

## Would you like to play a game — planned Python desktop arcade

**Status: design only.** The Python application described here has not been implemented. Its proposed features are separate from the existing games documented below. See [architecture.md](architecture.md) for module boundaries, dependencies, verification criteria, and sequential implementation prompts.

Inspired by the atmosphere of *WarGames* with Matthew Broderick, this original offline arcade opens with a simulated modem connection and a mechanical computer voice asking, “Would you like to play a game?” The host is **ORBIT — Opponent Reasoning and Board Intelligence Terminal**: curious, dryly funny, and interested in how people play.

### Experience

- Default simulated command line: black background, green or amber text, ASCII boards, blinking cursor, and optional scanlines.
- Short, skippable connection sequence with original dialing tones, carrier whistles, and handshake sounds. The connection is theatrical and local.
- Original offline synthetic narration, on by default at moderate volume; immediate mute and independent voice/effects controls.
- Enhanced retro and modern graphical themes, switchable during a match without changing state, difficulty, or history.
- Keyboard navigation, clickable modern boards, readable text scaling, reduced motion, and persistent preferences.
- Application commands such as `games`, `play chess`, `help`, `hint`, `save`, `resume`, `theme modern`, and `voice off`. Commands never execute an operating-system shell.
- No account, server, online language model, or gameplay network connection required.

| Mode | Appearance | Interaction |
| --- | --- | --- |
| Terminal (default) | Phosphor text and ASCII boards | Commands, arrows, shortcuts |
| Enhanced retro | Pixel pieces, restrained glow, transcript | Keyboard and mouse |
| Modern | Clean typography, graphical boards, accessible contrast | Clickable moves and command palette |

### Planned games

| Game | Opponent / mechanics | Signature feature |
| --- | --- | --- |
| Tic tac toe | Random beginner and minimax expert | ORBIT self-play study mode demonstrates optimal draws |
| Checkers | English/American rules and bounded search | Forced captures and complete jump sequences |
| Chess | python-chess rules with Stockfish opponent | Adjustable strength, hints, history, optional analysis |
| Galatic Thermal Nuclear War | Fictional planets with simultaneous actions | Shared instability and cooperative or competitive outcomes |

The requested spelling **Galatic Thermal Nuclear War** is retained intentionally. This is an imaginary planet-versus-planet arcade board game, with invented worlds and abstract points. It must not depict real nations, Earth geography, real weapons data, or realistic military operations.

### Expanded creative catalog

The arcade is ORBIT's collection of experiments: familiar games, strange competitions, and mysteries about how people think. All entries below are planned designs, not implemented features. Movie atmosphere is a starting point; the mechanics and stories are original.

| Game | Player experience | ORBIT's role |
| --- | --- | --- |
| Falken's Labyrinth | Shifting ASCII maze with doors, teleporters, and unreliable maps | Rival explorer or maze architect |
| Ghost in the Modem | Investigate an abandoned fictional bulletin-board system through messages, puzzles, and corrupted files | Guide occasionally surprised by discoveries |
| Dead Letter Office | Decode transmissions through substitution ciphers, patterns, and logic | Rival cryptanalyst or cryptic correspondent |
| Starship Captain | Explore a generated galaxy, manage a peculiar crew, and negotiate first contact | Rival captain with a persistent personality |
| The Last Colony | Sustain an outpost through equipment failures, alien weather, and resource shortages | Competing colony leader or cooperative partner |
| First Contact | Discover an alien language through symbols, responses, and experiments | Alien intelligence with learnable rules |
| Paradox Engine | Send a limited number of messages to previous turns to solve temporal puzzles | Rival using the same time-travel rules |
| Black Box | Infer a machine's hidden rules by experimenting with inputs and outputs | Puzzle designer; swap roles and let ORBIT solve yours |
| Orbital Salvage | Bid for derelict spacecraft, assemble unusual equipment, and explore wrecks | Rival who remembers public bidding habits |
| The Impossible Auction | Bid on objects with secret values, strange powers, and consequences | Several bidders with distinct bluffing styles |
| Dungeon on Drive B: | Short text adventures with ASCII maps, equipment, monsters, and exploration | Narrator and tactical monster controller |
| Paperclip Republic | Absurd economic competition over office supplies, automation, and fictional corporate espionage | Rival executive with ridiculous ambitions |
| Memory Leak | Play on a board whose previously visible regions disappear and must be remembered | Opponent with an explicit, enforced memory limit |
| Protocol Zero | Secretly program several robot moves, then watch both plans collide | Rival planner under equal information constraints |
| The Unwinnable Game | Apparently impossible challenges where discovering the actual objective is part of play | Learner accompanying the player's discoveries |

**Classic games with personality:** Midnight Blackjack uses fictional chips in an orbital casino; Chess Against Yesterday uses a disclosed local profile of previous matches; Solitaire: Lost Transmission reveals optional story fragments. Additional card-game candidates are Gin Rummy against ORBIT, Hearts against three personalities, Bridge with computer partners/opponents, and Poker with fictional chips. Starfighter Duel is a stylized spaceship arcade candidate.

Retain the earlier expansion ideas: Four in Orbit, Signal Breaker, Asteroid Nim, and Orbital Reversi. Solitaire remains solo with optional hints, with a same-deal computer challenge as a later mode. Falken's Labyrinth is a proposed original maze design, not a reconstruction of the movie's unspecified game mechanics.

### The mystery connecting the arcade

Every implemented base game is immediately available. Optional discoveries reveal ORBIT's history: an unfinished tournament, a missing opponent, and a message dated tomorrow. Discoveries unlock extra scenarios and dialogue, never access to ordinary play. Players can disable the story layer and replay clues in a journal.

An ASCII star map can become a graphical galaxy when the theme changes; state, clues, and mechanics remain identical. ORBIT's tone evolves through authored discoveries rather than requiring online AI.

> “I have added three new games. One of them may be a conversation.”

**First creative expansion:** Ghost in the Modem, Protocol Zero, and First Contact. These add mystery, tactical competition, and discovery after the foundational release. The rest remain a staged catalog, not a requirement to implement everything at once.

### Proposed implementation

Python with **PySide6 Qt Widgets** for the desktop interface and **Qt Multimedia** for playback. Evaluate **eSpeak NG** for the mechanical voice, with **pyttsx3** as an optional adapter. Reuse **python-chess / Stockfish** and **pydraughts** behind isolated adapters. These are proposed dependencies, not installed or integrated features.

Build a complete tic tac toe experience first, then add audio, chess, checkers, and the planetary game. Save/resume, theme switching, cancellation, and silent operation belong in the foundation.

There are no Python installation or launch commands yet. Use the [implementation prompts](architecture.md#implementation-prompts) when starting development.

The repository's existing [MIT license](LICENSE) remains unchanged. Future dependencies and bundled engines retain their own licenses; review distribution compatibility and update [third-party notices](THIRD_PARTY_NOTICES.md) when integrating them. In particular, python-chess and Stockfish use GPL licenses.

---

## Retro Eight Ball

Jeff Geissler's Java Magic 8 Ball, now an open-source collection of three native
apps. Think of a yes-or-no question and press **SHAKE!** to reveal an answer,
with a neon cyan ball, green lettering, and a short wobble and glow animation.
The iOS version adds a glossy shell, a floating triangular answer in blue liquid,
and a haptic tap on SHAKE. The Android port uses a fading pulse for its glow effect. The mobile versions
use a button; physically shaking the phone is not required or implemented.

| Version | Source | Instructions |
| --- | --- | --- |
| Java desktop (Swing) | [java/](java/) | Below |
| iPhone and iPad (SwiftUI) | [ios/](ios/) | [iOS-readme.md](iOS-readme.md) |
| Android (Java) | [android/](android/) | [androidOS-readme.md](androidOS-readme.md) |

All three games work offline, with no accounts, ads, analytics, or gameplay network calls.
The iOS About & Help screen opens external privacy/support pages and an email link.

## Run the desktop app

Install a JDK 17 or newer, then run these commands from the repository root:

```sh
mkdir -p build/java
javac -encoding UTF-8 -d build/java shared/java/com/jeffgeissler/retroeightball/Responses.java java/src/RetroEightBall.java
java -cp build/java RetroEightBall
```

On Windows, use `mkdir build\java` if the folder does not exist; the `javac`
and `java` commands above are otherwise the same. A graphical desktop is required.
Click **SHAKE!**, or press Enter, to ask again. Consecutive answers can repeat.

To produce a runnable JAR after compiling:

```sh
jar --create --file build/RetroEightBall.jar --main-class RetroEightBall -C build/java .
java -jar build/RetroEightBall.jar
```

## Original answer probabilities

The original eight responses and weights are preserved in all versions.
Each shake independently chooses one of 24 equally likely weighted slots.

| Answer | Weight (out of 24) |
| --- | ---: |
| It is certain. | 3 |
| Ask again later. | 2 |
| My reply is no. | 3 |
| Outlook good. | 4 |
| Better not tell you now. | 1 |
| Yes — definitely. | 5 |
| Very doubtful. | 2 |
| Signs point to yes. | 4 |

Desktop and Android share [Responses.java](shared/java/com/jeffgeissler/retroeightball/Responses.java).
iOS mirrors the same table in [Responses.swift](ios/RetroEightBall/Responses.swift).

## Review and modernization

- Replaced wildcard imports that made `Timer` ambiguous between Swing and Java utilities.
- Wrapped long responses to fit the desktop ball.
- Copied and disposed the graphics context so rotation does not leak into other painting.
- Consolidated desktop animation timing, reset its final state before repainting,
  and stopped animation when the panel is removed.
- Separated window construction from the panel and retained Swing's event dispatch thread.
- Added mobile accessibility labels/announcements, reduced-motion support on iOS,
  Android's system animation setting, and Android answer restoration on rotation.

## Verification

```sh
javac -encoding UTF-8 -d build/java shared/java/com/jeffgeissler/retroeightball/Responses.java tests/java/ResponsesTest.java
java -cp build/java ResponsesTest
```

This exhaustively checks all 24 slots and invalid roll boundaries. The Swift
equivalent is described in the iOS README. [GitHub Actions](../../actions)
compiles Java, builds the iOS simulator app, builds/lints Android, and checks
both answer tables. Successful runs provide desktop JAR and Android debug APK
artifacts. Build checks do not replace hands-on device and accessibility testing.

## Contributing and license

Issues and pull requests are welcome. Keep each game's source in its platform
folder and include build/test instructions with changes. If changing response
weights, update both implementations and their tests.

Original app by **Jeff Geissler**. Released under the [MIT License](LICENSE).
Gradle wrapper licensing is listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
