# Desktop preview

## Play on Mac — no Terminal or Python required

Open **Would You Like to Play.app** in Finder. The local build is in
`Retro-Games/build/desktop/`. You can drag the app into Applications and keep it
in the Dock. All Python, Qt, game rules, effects, and the computer worker are
inside the app bundle. Saves and preferences live in your user application-data
folder, so replacing the app does not replace them.

Click **Skip connection**, choose **Modern** in Display for point-and-click
boards, and click a game's Play button. Choose the difficulty and your side on
the catalog. Use Pause, Save, Save & catalog, and Load saved game to continue
later. The command field is optional in Modern display.

The locally built preview targets Apple Silicon. Intel Macs require a separate
Intel build. This preview is locally signed, not Developer ID signed or notarized;
public distribution and installer polish remain release work.

## Play on Windows

The **Desktop preview apps** GitHub Actions workflow builds a Windows executable
and runs the standalone gameplay probe. After a successful workflow run, download
**Orbit-Windows-preview**, extract the complete archive, and double-click
**Would You Like to Play.exe**. Keep the adjacent `_internal` directory and
`orbit-worker.exe` together. No Python installation or command prompt is needed
on the player's computer. You can use Windows' Create shortcut / Pin options.

The workflow is checked in locally; a Windows artifact is available only after
these changes are pushed and its Windows job succeeds. Windows has not been
verified on this Mac. The preview executable is not Authenticode-signed.

## Audio

Original effects are bundled. The optional pyttsx3 system-voice adapter is included
when installed on the build host; choose it in the voice control. eSpeak NG is
still an optional external runtime, not bundled: see [AUDIO.md](AUDIO.md).
Missing speech or audio devices never prevent play. Mute all is immediate.

## Developer iteration

Build on the target OS using Python 3.9+ (CI uses 3.12):

```sh
python -m pip install './python/would-you-like-to-play[system-voice]' pyinstaller==6.16.0
python python/would-you-like-to-play/packaging/build.py
```

Output is `build/desktop/`. The macOS `.app` and Windows application folder are
standalone; these build commands are for developers, not players. The windowed
entry point and console-capable helper share bundled dependencies. QProcess
launches the helper without opening a terminal. This avoids assuming that the
frozen app executable can interpret Python `-m` arguments.

The packaging smoke probe clicks both games' widgets, waits for actual computer
replies, and checks save/load in a temporary data directory. The platform workflow
fails if any check fails. Existing unit/widget tests remain the broader regression
suite. Packaging follows [PyInstaller's platform build documentation](https://www.pyinstaller.org/en/stable/usage.html)
and its [windowed-process guidance](https://pyinstaller.org/en/latest/common-issues-and-pitfalls.html).

Still unfinished: signed/notarized public installers, automatic updates, Windows
and Intel Mac native testing, and the remaining games listed in the main README.
