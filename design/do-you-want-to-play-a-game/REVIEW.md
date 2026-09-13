# Latest updates — review

Reviewed September 13, 2026: commit `14240fd` (Java and iPhone Alien Invasion),
plus local Eight Ball Xcode project and scheme changes. This is a source review;
gameplay was not exercised. No application code was changed during this review.

## Findings

### P2 — iOS can award points more than once for the same alien in one frame

In [GameScene.swift](../../ios/RetroAlienInvasion/GameScene.swift),
`resolveCollisions()` lines 209–215, aliens marked in `hitAliens` remain eligible
for later bullets until the loop finishes. If two bullets overlap the same alien
in that frame, both add points and both are consumed, although only one alien
is removed. Exclude already-hit identities before awarding points. Verify with
two bullets intersecting a single alien in one update: award exactly one kill.

### P2 — desktop focus loss can leave movement held and gameplay running

[KeyInput.java](../../java/space-invaders/input/KeyInput.java) clears movement only
on key-release events, and [Game.java](../../java/space-invaders/Game.java) installs
no focus-loss handler. Hold a movement key, switch windows, and release outside
the game: the release may never reach the listener, leaving movement active.
Clear input and pause on focus loss. Verify both movement directions and resume.

### P2 — the new game is absent from build automation

[The workflow](../../.github/workflows/build.yml) compiles only Eight Ball Java
sources and builds only its iOS project. Alien Invasion compilation failures can
therefore pass the existing CI. Add both new build targets and focused gameplay
checks in follow-up coding work.

## Integration considerations

- The desktop Alien Invasion timer starts in its constructor and has no disposal
  hook. Its standalone window uses EXIT_ON_CLOSE. A hub must adapt those lifecycle
  choices before embedding or opening it from a shared application.
- The main README does not yet catalog Alien Invasion. This documentation update
  adds links to its existing platform instructions.
- Local Eight Ball edits rename the target/product to RetroMagicEightBall and
  update scheme references consistently. The scheme filename remains
  RetroEightBall.xcscheme, so existing scheme-name instructions still match.
  Signing-team and orientation changes were observed but not device-validated.

## Verification limits

Attempted compilation of both Java games and execution of ResponsesTest. The
environment's Java launcher reported **Unable to locate a Java Runtime**, so
neither compilation nor tests ran. No JDK was installed for this documentation
task. iOS builds and simulator/device gameplay were not run. Findings above
are based on source inspection, not reproduced runtime tests.
