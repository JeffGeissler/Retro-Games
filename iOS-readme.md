# Retro Eight Ball for iOS

A native SwiftUI port of Jeff Geissler's Java eight ball, for **iOS/iPadOS 17+**.
It preserves the original weighted answers with a glossy black ball, blue liquid
window, and floating triangular answer face.

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

Each tap gives a short, heavy haptic impact on supported iPhones, shakes the
shell, and lets the triangular answer rise out of the dark liquid into focus.
The face gently bobs and tilts after settling. Repeated taps restart the reveal,
and haptics trigger even when the same answer is chosen twice. Haptic feedback
must be checked on a physical iPhone; the simulator cannot reproduce the feel.

The answer is announced to VoiceOver and repeated below the ball at a readable,
scalable size. The screen scrolls for smaller windows. Reduce Motion disables
all movement and blur transitions, showing the answer immediately; haptics remain
available. Animation updates pause when the app is inactive and otherwise run
at a maximum of 30 frames per second for the gentle floating effect.
The answer remains while the view is active; it resets when the app is relaunched.

No third-party packages, networking, personal data storage, or sensor permissions.

## Distribution and testing

The simulator build is not an installable App Store release. Before distributing,
add your app icon, configure signing and your App Store Connect record, test on
devices, and complete Apple's submission requirements.

Suggested manual checks: repeated taps, every long answer, landscape, iPad split
view, larger text sizes, VoiceOver, Reduce Motion, background/foreground, and
haptics on a physical iPhone.
The updated simulator build passed and its initial screen was visually checked
on an iPhone 17 Pro simulator. The original exhaustive Swift answer test passed;
the response model is unchanged. The animation interaction, accessibility settings,
and physical-device haptic feel still need hands-on testing.

See [README.md](README.md) for probabilities and the [MIT License](LICENSE).
Reduce Motion uses Apple's [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion) setting.
