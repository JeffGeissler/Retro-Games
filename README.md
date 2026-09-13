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

Possible expansions include **Four in Orbit** (Connect Four style), **Signal Breaker** (code deduction), **Asteroid Nim**, **Orbital Reversi**, and **Solitaire: Lost Transmission**. Solitaire is solo play with optional computer hints; a same-deal computer challenge is a later option.

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
