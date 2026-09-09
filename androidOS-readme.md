# Retro Eight Ball for Android

A native Java Android app with the original eight weighted answers, cyan ring,
green text, and wobble/fade pulse. Requires **Android 8.0 (API 26) or newer**.

## Open and run

1. Clone the **entire repository**; Android shares the answer model in `shared/java`.
2. Open the `android` folder in Android Studio with support for Android Gradle
   Plugin 8.9.2. Select JDK 17 for Gradle and install Android SDK Platform 35.
3. Let Gradle sync. The included wrapper downloads Gradle 8.11.1 and verifies
   the distribution checksum; an internet connection is needed for the first build.
4. Select an emulator or connected device and run the **app** configuration.
5. Tap **SHAKE!** to reveal an answer. Physical device shaking is not implemented.

## Command-line build

Set `ANDROID_HOME` to your Android SDK location, or let Android Studio create
`android/local.properties`. From the `android` directory:

```sh
./gradlew assembleDebug lintDebug
```

On Windows use `gradlew.bat assembleDebug lintDebug`.
The debug APK is produced at `app/build/outputs/apk/debug/app-debug.apk`.
With an emulator or USB-debugging device connected, use `./gradlew installDebug`.
Debug signing is handled automatically by the Android build tools.

Versions are pinned to AGP 8.9.2, Gradle 8.11.1, JDK 17, and SDK 35, matching
[Google's compatibility table](https://developer.android.com/build/releases/agp-8-9-0-release-notes).

## Behavior and accessibility

The app works offline and declares no permissions. Answers are exposed as a
polite accessibility live region. It respects disabled system animations,
cancels animations when backgrounded, and saves the answer across activity
recreation such as rotation. Content scrolls on short displays and respects
system bars and display cutouts.

Suggested manual checks: rapid taps, long answers, rotation, large fonts,
TalkBack, disabled animations, background/resume, and devices running API 26
and API 35. GitHub Actions builds the APK and runs Android lint; device UI testing
is a separate check. This Mac does not have an Android SDK installed.

## Release builds

The debug APK is for development. For distribution, add a launcher icon,
choose your final application ID, create a private signing key, and use Android
Studio's Generate Signed App Bundle / APK flow. Never commit the key or passwords.
Check the store's current submission requirements before publishing.

See [README.md](README.md) for the Java model's exhaustive probability test
and [LICENSE](LICENSE) for the MIT license. The Gradle wrapper has a separate
[Apache 2.0 license](android/gradle/LICENSE).
