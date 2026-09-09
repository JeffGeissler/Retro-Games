# Retro-Games

Games I wrote in the early 2000s, modernized for smartphones (iOS and Android).

## Retro Eight Ball

Jeff Geissler's Java Magic 8 Ball, now an open-source collection of three native
apps. Think of a yes-or-no question and press **SHAKE!** to reveal an answer,
with a neon cyan ball, green lettering, and a short wobble and glow animation.
The Android port uses a fading pulse for its glow effect. The mobile versions
use a button; physically shaking the phone is not required or implemented.

| Version | Source | Instructions |
| --- | --- | --- |
| Java desktop (Swing) | [java/](java/) | Below |
| iPhone and iPad (SwiftUI) | [ios/](ios/) | [iOS-readme.md](iOS-readme.md) |
| Android (Java) | [android/](android/) | [androidOS-readme.md](androidOS-readme.md) |

All three work offline, with no accounts, ads, analytics, or network calls.

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
