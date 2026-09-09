# Retro Eight Ball for iOS

A native SwiftUI port of Jeff Geissler's Java eight ball, for **iOS/iPadOS 17+**.
It preserves the original weighted answers, neon colors, and wobble/glow effect.

## Open and run

1. Clone the entire repository and open `ios/RetroEightBall.xcodeproj` in Xcode 15+
   with an installed iOS SDK (locally compiled with Xcode 26.6).
2. Select the **RetroEightBall** scheme and an iPhone or iPad simulator.
3. Choose Product → Run. No signing account is needed for a simulator.
4. Think of a question and tap **SHAKE!**. This version uses the button rather
   than motion sensors. A new tap replaces the current animation.

For a physical device, select your own team in Signing & Capabilities, use a
unique bundle identifier if needed, connect your device, and run from Xcode.
No signing credentials are included in this repository.

## Command-line build

From the repository root:

```sh
xcodebuild -project ios/RetroEightBall.xcodeproj -scheme RetroEightBall -sdk iphonesimulator -configuration Debug -derivedDataPath build/ios CODE_SIGNING_ALLOWED=NO build
```

Verify every weighted answer without launching the UI:

```sh
swiftc ios/RetroEightBall/Responses.swift tests/ios/main.swift -o /tmp/retro-responses-test
/tmp/retro-responses-test
```

## Behavior and accessibility

The answer is announced to VoiceOver. Text scales and the screen scrolls for
smaller windows. Reduce Motion disables the wobble/glow animation. Animation
updates pause when the app is inactive and stop after the effect finishes.
The answer remains while the view is active; it resets when the app is relaunched.

No third-party packages, networking, personal data storage, or sensor permissions.

## Distribution and testing

The simulator build is not an installable App Store release. Before distributing,
add your app icon, configure signing and your App Store Connect record, test on
devices, and complete Apple's submission requirements.

Suggested manual checks: repeated taps, every long answer, landscape, iPad split
view, larger text sizes, VoiceOver, Reduce Motion, and background/foreground.
The initial simulator build and exhaustive Swift answer test passed locally;
hands-on simulator/device interaction has not yet been verified.

See [README.md](README.md) for probabilities and the [MIT License](LICENSE).
Reduce Motion uses Apple's [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion) setting.
