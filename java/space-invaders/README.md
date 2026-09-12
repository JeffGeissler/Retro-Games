# Retro Alien Invasion

A dependency-free Java Swing arcade game based on my original
`RetroAlienInvasion.java` prototype written back in early 2000s. It is inspired by the old arcade game.

## Requirements

- JDK 17 or newer
- A graphical desktop environment

## Build and run

From the `Retro-Games` directory:

```sh
mkdir -p build/space-invaders
javac -encoding UTF-8 -d build/space-invaders \
  java/RetroAlienInvasion.java \
  $(find java/space-invaders -name '*.java')
java -cp build/space-invaders RetroAlienInvasion
```

## Controls

- Left/right arrows or A/D: move
- Space: fire
- P: pause or resume
- Enter: start or restart

The game stores only the local high score, using Java Preferences.
