# Third-party notices

The Gradle wrapper scripts and `android/gradle/wrapper/gradle-wrapper.jar` are
from Gradle 8.11.1 and licensed under Apache License 2.0, rather than this
repository's MIT license. The scripts retain their original copyright headers.

Source: https://github.com/gradle/gradle/tree/v8.11.1

License: [Apache License 2.0](android/gradle/LICENSE)

Build tools and platform SDKs are separately licensed by their respective owners.

## Python desktop app

The optional `python/would-you-like-to-play` app depends on PySide6 6.8.3,
including its Qt and Shiboken runtime dependencies, installed through pip.
These dependencies retain their upstream licenses and notices. Consult
<https://doc.qt.io/qtforpython-6/licenses.html> and the installed distributions'
license files when redistributing a packaged application. They are not covered
by this repository's MIT license.

## Offline audio increment

The user-supplied ORBIT Arcade Sound Pack contributes eleven unmodified WAV
files. Its README describes them as original synthesized effects without reproduced
film/game audio. The supplied README and SHA-256 manifest are bundled with the
assets; no separate license declaration was supplied and this change does not
assign a new license to them. See [audio provenance](python/would-you-like-to-play/AUDIO.md#asset-provenance).

eSpeak NG is an optional external executable, not bundled in this repository. Its
[upstream COPYING](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING)
contains GPLv3 terms. The optional [pyttsx3 2.99](https://pypi.org/project/pyttsx3/2.99/)
distribution declares MPL-2.0; its platform bridges and OS voices retain their
own terms. Qt Multimedia and the codecs shipped with the PySide6 distribution
also retain their upstream notices. Installing a runtime is separate from bundling
it in a distributable app; no app installer or speech-engine binary is added here.

## Python checkers

The application depends on [pydraughts 0.6.7](https://github.com/AttackingOrDefending/pydraughts),
licensed under MIT, with upstream attribution in its LICENSE and other_licenses
directory. Its transitive dependency msl-loadlib retains its own MIT license.
These packages are installed as dependencies, not vendored; preserve their license
files when distributing a bundled application. No external engine binaries or
opening/endgame databases are included. See the application CHECKERS.md for API
verification and selected English draw rules.
