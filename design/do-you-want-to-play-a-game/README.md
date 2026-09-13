# Do you want to play a game?

**Follow-up implementation:** [Would you like to play a game?](../../python/would-you-like-to-play/README.md)
is now a separate PySide6 application with Tic Tac Toe. The proposal below records
the earlier Java/mobile hub assumption and is not its implementation brief.

Proposed home screen for the Retro-Games collection. Choose a game, read its
controls, and start playing through a simple retro arcade menu.

**Status: design draft; implementation has not started.** The working assumption
is that this title describes a game-selection hub. No existing source design was
provided. Follow-up coding prompts can revise the concept and choose the first platform.

## Documents

- [Design and acceptance criteria](DESIGN.md)
- [Review of the latest repository updates](REVIEW.md)
- [Repository README](../../README.md)

## Existing games

| Game | Java desktop | iOS | Android |
| --- | --- | --- | --- |
| Retro Eight Ball | Implemented | Implemented | Implemented |
| Retro Alien Invasion | Implemented | Implemented | Not implemented |

These are source availability statements, not verification of device builds.
The games currently have separate entry points; a shared launcher does not exist.

## Run the existing games

- Eight Ball: [desktop instructions](../../README.md#run-the-desktop-app),
  [iOS instructions](../../iOS-readme.md), [Android instructions](../../androidOS-readme.md).
- Alien Invasion: [desktop instructions](../../java/space-invaders/README.md),
  [iPhone instructions](../../ios/RetroAlienInvasion/README.md).

There is no build or run command for the proposed hub yet.

## Suggested coding sequence

1. Confirm the hub concept and first platform; Java is the proposed starting point.
2. Address the gameplay and lifecycle findings in the review.
3. Implement the menu, local game catalog, and navigation on that platform.
4. Integrate both games with explicit enter, pause, return, and disposal behavior.
5. Verify repeat launches, focus changes, accessibility, and existing standalone entry points.
6. Adapt the design to mobile once packaging and navigation are decided.

Keep the first implementation offline and preserve existing game rules and local scores.
