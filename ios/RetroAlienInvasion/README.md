# Retro Alien Invasion for iPhone

A native SwiftUI and SpriteKit version of the Java game. It targets iOS 17 or
newer, runs entirely offline, and stores only the high score in `UserDefaults`.

## Run

Open `ios/RetroAlienInvasion.xcodeproj`, select the **RetroAlienInvasion**
scheme and an iPhone simulator, then choose Product → Run.

Command-line simulator build from the repository root:

```sh
xcodebuild -project ios/RetroAlienInvasion.xcodeproj \
  -scheme RetroAlienInvasion \
  -sdk iphonesimulator \
  -configuration Debug \
  -derivedDataPath build/retro-alien-ios \
  CODE_SIGNING_ALLOWED=NO build
```

## Controls

- Drag anywhere on the game field to position the ship.
- Hold the left and right buttons for precise movement.
- Tap **Fire** to shoot.
- Use the pause button to suspend or resume the game.

The game automatically pauses when sent to the background.
