# Do you want to play a game? — Design

Draft dated September 13, 2026. This proposes a game-selection hub for the existing
Retro-Games collection. Platform order and packaging are proposals for follow-up
coding prompts, not settled requirements or implemented features.

## Purpose and scope

Give players one clear place to discover and enter the available retro games.
The first version offers Retro Eight Ball and Retro Alien Invasion on Java desktop.
Retain the existing standalone launchers. iOS and Android adaptations follow separately;
Android currently has only Eight Ball.

The initial scope is a menu, game details and controls, in-app navigation, and
safe game lifecycle handling. Accounts, downloads, online leaderboards, new game
rules, and additional games are outside this draft's scope.

## Player experience

Open directly to the title **Do you want to play a game?** and subtitle
**Choose your next retro adventure.** Show two game cards:

| Card | Description | Primary action |
| --- | --- | --- |
| Retro Eight Ball | Ask a yes-or-no question. Give the ball a shake. | Play |
| Retro Alien Invasion | Defend Earth. Dodge enemy fire. Chase your high score. | Play |

Each card also offers **How to play**, displaying platform-specific controls.
Play opens the game's existing ready experience; it does not bypass Alien
Invasion's start screen or automatically shake Eight Ball. A visible **Back to
games** action provides the return path.

When leaving an active Alien Invasion run, pause first and show **Leave this game?**
with **Keep playing** and **Leave game**. Explain that leaving ends the current
run. Keep playing resumes that run; leaving saves its best score and disposes the
session. Returning from an already paused run must preserve that paused state
if the player cancels leaving. Eight Ball can return immediately.

Starting a game from the hub creates a fresh session. Do not imply saved-game
resume support. Unavailable platform versions have explanatory text and no Play action.

## Visual direction

Use the existing neon arcade palette: near-black background, cyan headings and
borders, green accents, and off-white body text. Reserve red for destructive or
game-over actions. Use monospaced headings and readable system text for descriptions.
Keep decoration quiet: a static star field or subtle terminal treatment is enough.
No typing animation should delay access to the game list.

```text
+--------------------------------------------------+
| RETRO-GAMES                                      |
| Do you want to play a game?                      |
| Choose your next retro adventure.                |
|                                                  |
| [ Eight Ball ]           [ Alien Invasion ]       |
| Ask a question.          Defend Earth.            |
| [Play] [How to play]     [Play] [How to play]      |
+--------------------------------------------------+
```

Use two columns when space permits and one scrolling column on narrow screens.
Retain Alien Invasion's existing 800 × 600 desktop playfield rather than stretching
its coordinates as part of menu work. The host must fit that playfield plus navigation.

## Input and accessibility

- Use native focusable buttons, with visible focus and a logical Tab order.
- Enter or Space activates a focused button. Escape closes help or opens the
  return flow from a game; it must not silently discard a run.
- Restore focus to the originating game card after returning to the menu.
- Provide accessible names for cards and actions; never encode availability by color alone.
- Allow text growth and scrolling. Mobile actions should have at least 44-point
  iOS or 48-dp Android touch targets.
- Keep the hub static by default and respect reduced-motion preferences for any
  optional animation. Gameplay accessibility improvements are a separate work item.

## Implementation boundaries

Use a small local catalog with stable game ID, title, description, controls, and
platform availability. Keep launch behavior in platform code, separate from display text.
No network catalog or new shared cross-platform engine is needed.

For Java, propose a Swing host with a menu and game container, using CardLayout
or equivalent. Construct and mutate UI on the event dispatch thread. Add game
adapters that create a session, pause it, clear held input, and dispose it.
Avoid calling the current standalone main methods from the hub: those create
independent windows and Alien Invasion uses EXIT_ON_CLOSE.

Alien Invasion currently starts its Swing timer in the panel constructor. Integration
must stop that timer on exit, restart only through an explicit lifecycle path, and
clear movement flags on focus loss. Losing window focus should pause active play.
Persist the best score when a run ends or is deliberately left. Preserve existing
preference keys and Eight Ball's weighted response table.

For a later iOS version, decide whether to add a collection target or integrate
navigation into an existing app before changing projects. The current games are
separate Xcode projects, not routes in one application. Use SwiftUI navigation
around the game views and explicit SpriteKit session teardown. Existing apps'
UserDefaults do not automatically migrate into a new app sandbox.

For Android, expose only Eight Ball as playable until an Alien Invasion port exists.

## Acceptance criteria for the first implementation

1. Both Java games launch from the hub and their standalone commands still work.
2. Help shows the correct controls for the selected game and platform.
3. Leaving and relaunching a game 20 times does not accumulate timers, windows,
   listeners, or stale state; returning to the menu stops gameplay updates.
4. Focus loss pauses Alien Invasion and clears held input. Returning focus does
   not resume automatically or leave the ship moving.
5. Canceling the leave dialog restores the prior play/pause state. Confirming
   saves the best score, returns to the menu, and resets the next run.
6. Keyboard users can reach every hub action, close help, enter a game, and return.
7. Large text and narrow layouts do not hide actions or truncate essential instructions.
8. Eight Ball retains its 24-slot response distribution; Alien Invasion retains
   its established scoring and local high-score storage.
9. Build automation compiles both Java games; lifecycle and navigation checks
   accompany the integration. Any iOS integration receives its own build coverage.
