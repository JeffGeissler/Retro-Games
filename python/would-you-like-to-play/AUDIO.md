# ORBIT audio and offline narration

This increment adds original supplied connection effects and offline narration to
the existing Tic Tac Toe application. Game rules and saves remain independent of
audio. The speech interface still accepts `speak(text)` and `stop()`; the concrete
`AudioService` coordinates adapters and Qt Multimedia playback.

## Run and controls

From the Retro-Games repository root, with the existing virtual environment:

```sh
source .venv-play-game/bin/activate
python -m pip install -e ./python/would-you-like-to-play
brew install espeak-ng
retro-play
```

Homebrew is the installation route evaluated on this Mac, not a runtime dependency
of the app. Linux distributions can install eSpeak NG using their package manager
(for example, `sudo apt-get install espeak-ng` on Debian/Ubuntu). On Windows use the
[eSpeak NG project installation instructions](https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md)
and make `espeak-ng` available on PATH. Windows/Linux operation remains unverified
locally; CI includes Linux synthesis tests.

The app searches PATH and the two usual macOS Homebrew locations. It invokes the
executable directly with an argument list and sends text through stdin. No shell,
cloud service, speech recognition, microphone, or downloaded voice model is used.

Always-visible controls are available before connection playback begins:

- **Mute all** stops both playback channels, cancels synthesis, and clears narration.
- **Effects** adjusts modem and game effects independently, from 0–100.
- **Voice** adjusts narration independently, from 0–100. Zero also clears narration.
- **espeak-ng / pyttsx3 / silent** selects the speech adapter. Silent leaves effects
  available; Mute all silences both channels.
- **Skip connection** stops the modem clips and enters the catalog immediately.
  When voice is enabled, the catalog can then deliver its new welcome line.
- `retro-play --mute` starts muted for that launch. `--skip-connection` remains available.

The defaults are effects 40%, voice 50%, eSpeak NG, and unmuted. Controls persist
in version-2 preferences. Version-1 preferences retain existing game/display
settings and receive these audio defaults. Audio changes apply immediately even
if saving preferences fails; the app reports that they apply only to this launch.
Unmuting or raising voice volume never replays discarded speech or elapsed modem
stages. Only subsequent events produce sound.

## Optional system voice

```sh
python -m pip install -e './python/would-you-like-to-play[system-voice]'
```

Select **pyttsx3** in the app. The extra pins pyttsx3 2.99; its platform dependencies
include PyObjC on macOS and the appropriate OS speech driver. It uses the default
installed system voice at 145 words/minute. That voice is an alternative to the
more mechanical eSpeak NG delivery, not an imitation of a film performer.

pyttsx3's `save_to_file` and blocking `runAndWait` execute only in a separate
Python process. On the tested Mac its system driver writes AIFC; the app caches it
with an `.aiff` extension and uses Qt for playback. Other platforms use `.wav`.
Drivers that cannot produce a supported file produce a notice and silent play.
There is no automatic fallback that silently selects a different voice. To retry
a failed speech backend, select **silent**, then select the desired backend again.

## Runtime evaluation

Evaluated on macOS 26.6.2, Apple Silicon, Python 3.9.6, PySide6 6.8.3:

| Component | Result |
| --- | --- |
| eSpeak NG 1.52.0 (Homebrew) | Installed and exercised through both CLI and asynchronous adapter; produced valid mono 22,050 Hz WAV. The welcome line rendered to 3.28 seconds. |
| Mechanical settings | English US, 145 words/minute, pitch 32; synthesized file volume is full scale, with playback volume controlled independently by Qt. |
| pyttsx3 2.99 / PyObjC 11.1 | Installed as an optional extra; offline child-process file rendering produced valid AIFC on this Mac. |
| Qt Multimedia / FFmpeg 7.1 | Physical-output decoding/playback smoke-tested at zero volume using the normal QApplication event loop. This verifies completion without an audible quality assessment. |
| Qt native macOS backend diagnostic | Did not complete loading under the offscreen diagnostic; it is not selected by the application. |

An initial physical-device test using QTest waits in a shared QApplication stalled.
The device smoke test now uses a fresh process with the normal Qt event loop,
a five-second watchdog, and a ten-second parent timeout. The normal-event-loop
FFmpeg probe completed. This distinction is recorded rather than treating the
stalled harness as a passing device test. Headless runners with no audio output
skip only that physical-device test; fake-device failure and silent-play tests run.

## Cancellation and bounds

- Speech is rendered by asynchronous `QProcess`. The GUI never calls
  `waitForFinished`, `subprocess.run`, or a speech engine's blocking loop.
- Each channel uses Qt `QMediaPlayer` and `QAudioOutput`. Playback decoding runs in
  Qt's multimedia backend. Replacing/stopping a player invalidates its callbacks.
- One narration is active, with at most **three waiting lines**. Duplicate pending
  text is coalesced. When full, the oldest waiting line is discarded. Each line is
  limited to 600 characters. Only authored status text is narrated, not raw commands.
- Synthesis is limited to **15 seconds** per request; playback has a **30-second**
  watchdog. Failure clears the queue and reports a notice. A synthesis failure
  disables that adapter until it is reselected, avoiding a retry storm.
- Every cancellation advances a generation counter. Results from an earlier
  generation are discarded and their temporary files removed. Pending subprocesses
  are killed asynchronously and reaped on completion; the UI does not wait for them.
- Starting, loading, leaving, pausing, resuming, finishing, skipping, muting, switching
  backend, and closing cancel outdated narration. A transition may then enqueue a
  new context-appropriate line, such as the catalog welcome.
- Effects use a separate channel with no backlog. A new effect replaces the previous
  one. The connection progresses through four timed clips even when silent; skipped
  and elapsed stages are never replayed.
- Losing the audio device stops playback and clears narration. Reconnection only
  permits future events. Missing backend, cache errors, malformed output, and Qt
  playback errors leave board controls, commands, and visible status available.

## Speech cache

`speech-cache/` lives under the app data directory (or `--data-dir`). Keys hash the
adapter identity, settings, and text. eSpeak identity includes executable path and
modification time; pyttsx3 identity includes platform and installed package version.
Cached files are WAV or AIFF/AIFC. They are local and excluded from the repository.

Synthesis writes a unique temporary file. The app checks type/header and a 4 MiB
per-file limit, then atomically replaces the cache target. Qt performs final media
decoding. Successful new renders prune the least recently used completed entries
to **64 files / 32 MiB**. Cache hits update access recency. Ordinary cancellation
removes partial files; an abrupt process crash can leave a `pending-*` file, which
can be removed along with the rest of the cache while the app is closed.

The cache can be deleted while the app is closed without affecting preferences or
match saves. Concurrent application instances sharing one data directory remain
unsupported. The cache does not include volume because volume is applied at playback.

## Asset provenance

The user supplied the **ORBIT Arcade Sound Pack** from Downloads. Its README states
that it contains original synthesized effects, mono 44.1 kHz 16-bit PCM, with no
reproduced film/game audio. That statement is source-provided provenance, not an
independent authorship audit. The supplied README is preserved verbatim as
[`SOURCE_README.txt`](src/retro_play/audio/assets/SOURCE_README.txt).

Eleven WAVs are bundled byte-for-byte; their SHA-256 values are recorded in
[`SHA256.json`](src/retro_play/audio/assets/SHA256.json) and verified by tests.
No trimming, mixing, pitch processing, or resampling was applied to these assets.

| Supplied files | Use |
| --- | --- |
| 01 orbit dial sequence; 02 carrier whistle; 03 modem handshake; 04 connection established | Sequential simulated connection, roughly 4.4 seconds including stage gaps |
| 06 command accept; 07 command error | Command feedback |
| 10 save complete | Explicit successful Save |
| 11 piece move | Computer move |
| 15 player win; 16 ORBIT win; 17 draw/stalemate | Round result |

The other twelve supplied effects are not bundled or presented as implemented
features. Speech audio is generated locally from original app dialogue by the
selected engine; no speech recording or film sample is bundled. The supplied pack
has no separate license declaration. This change records its user-supplied origin
without assigning it a new license. Engine/library licenses remain separate from
the repository license; see [third-party notices](../../THIRD_PARTY_NOTICES.md).

## Verification and remaining limits

Run all tests with the environment active, from this directory:

```sh
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

The suite covers game regressions, real slow-child responsiveness, timeout/reaping,
missing executable, eSpeak rendering, optional pyttsx3 rendering, late-result
rejection, session-exit clearing, immediate mute, independent volumes, cache bounds,
asset integrity, v1 preference migration, and a separately time-limited Qt device
probe. Optional-engine tests are marked skipped when their runtime is absent.

Local verification passed **33 tests**, including both installed speech adapters
and the real Qt output probe. A wheel was built and checked to contain all eleven
WAVs plus the supplied README and checksum manifest. Documentation links and
`git diff --check` also passed. The updated Linux CI job has not yet run remotely.

Sound quality at audible volume, hot-plug behavior on physical devices, and
Windows/Linux device behavior still need hands-on validation. There is no voice
picker, ambient loop, audio installer bundle, cloud narration, microphone input,
or speech recognition. The existing broader game roadmap remains planned.

Implementation references: [QProcess](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QProcess.html),
[Qt audio overview](https://doc.qt.io/qtforpython-6/overviews/qtmultimedia-audiooverview.html),
[eSpeak NG guide](https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md),
[pyttsx3 2.99](https://pypi.org/project/pyttsx3/2.99/), and
[pyttsx3 engine API](https://pyttsx3.readthedocs.io/en/latest/engine.html).
