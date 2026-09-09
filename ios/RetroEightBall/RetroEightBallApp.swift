import SwiftUI

@main
struct RetroEightBallApp: App {
    var body: some Scene { WindowGroup { ContentView() } }
}

struct ContentView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.scenePhase) private var scenePhase
    @State private var answer = "Ask a question, then SHAKE!"
    @State private var hasAnswer = false
    @State private var started = Date.distantPast
    @State private var shakeCount = 0
    @State private var showingHelp = false

    var body: some View {
        GeometryReader { geometry in
            ScrollView {
                VStack(spacing: 24) {
                    Text("RETRO EIGHT BALL")
                        .font(.system(.title2, design: .monospaced, weight: .bold))
                        .foregroundStyle(.cyan)
                    Text("Think of a yes-or-no question.")
                        .foregroundStyle(.white)
                    TimelineView(.animation(minimumInterval: 1.0 / 30.0,
                                            paused: reduceMotion || scenePhase != .active || showingHelp)) { context in
                        FloatingBall(answer: hasAnswer ? answer : "SHAKE TO ASK",
                                     size: max(160, min(geometry.size.width - 48, 380)),
                                     elapsed: context.date.timeIntervalSince(started),
                                     time: context.date.timeIntervalSinceReferenceDate,
                                     reduceMotion: reduceMotion)
                    }
                    .accessibilityHidden(true)
                    // Keep a full-size answer outside the decorative window for large text and VoiceOver.
                    Text(answer)
                        .font(.system(.title3, design: .monospaced, weight: .semibold))
                        .foregroundStyle(.cyan)
                        .multilineTextAlignment(.center)
                        .frame(minHeight: 56)
                        .accessibilityLabel("Answer: \(answer)")
                    Button(action: shake) {
                        Text("SHAKE!")
                            .font(.system(.title, design: .monospaced, weight: .bold))
                            .frame(maxWidth: .infinity, minHeight: 56)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.cyan)
                    .foregroundStyle(.black)
                    .accessibilityHint("Reveals a randomly weighted answer with a haptic tap")
                    .sensoryFeedback(.impact(weight: .heavy, intensity: 0.9), trigger: shakeCount)
                    Button { showingHelp = true } label: {
                        Label("About & Help", systemImage: "info.circle")
                            .frame(minHeight: 44)
                    }
                    .tint(.cyan)
                    Text("FOR FUN • SINCE THE RETRO DAYS")
                        .font(.system(.caption, design: .monospaced))
                        .foregroundStyle(.gray)
                }
                .padding(24)
                .frame(maxWidth: .infinity)
                .frame(minHeight: geometry.size.height)
            }
        }
        .background(.black)
        .preferredColorScheme(.dark)
        .sheet(isPresented: $showingHelp) { AboutHelpView() }
    }

    private func shake() {
        answer = Responses.choose()
        hasAnswer = true
        started = Date()
        // A separate trigger produces feedback even when the same answer is chosen twice.
        shakeCount += 1
        UIAccessibility.post(notification: .announcement, argument: answer)
    }
}

private struct AboutHelpView: View {
    @Environment(\.dismiss) private var dismiss
    private let privacyURL = URL(string: "https://jeffgeissler.github.io/Retro-Games/privacy/")!
    private let supportURL = URL(string: "https://jeffgeissler.github.io/Retro-Games/support/")!
    private let emailURL = URL(string: "mailto:scale.with.jeff@outlook.com?subject=Retro%20Eight%20Ball%20Support")!

    var body: some View {
        NavigationStack {
            List {
                Section("Retro Eight Ball") {
                    Text("By Jeff Geissler")
                    Text("Version \(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0") (\(Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"))")
                        .foregroundStyle(.secondary)
                }
                Section("Privacy") {
                    Text("The game works offline. It does not collect or transmit personal data, questions, or answers. Opening help pages or sending email uses external services.")
                    Link(destination: privacyURL) { Label("Privacy Policy", systemImage: "hand.raised") }
                }
                Section("Support") {
                    Link(destination: supportURL) { Label("Help & Support", systemImage: "questionmark.circle") }
                    Link(destination: emailURL) { Label("Email Support", systemImage: "envelope") }
                    Text("scale.with.jeff@outlook.com")
                        .textSelection(.enabled)
                        .font(.footnote)
                    Text("If an email app is not configured, copy the address and contact us from your preferred email service.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("About & Help")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
            .tint(.cyan)
        }
        .preferredColorScheme(.dark)
    }
}

/// An inverted triangular die face, seen through the ball's liquid-filled window.
private struct AnswerTriangle: Shape {
    func path(in rect: CGRect) -> Path {
        Path { path in
            path.move(to: CGPoint(x: rect.minX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.midX, y: rect.maxY))
            path.closeSubpath()
        }
    }
}

private struct FloatingBall: View {
    let answer: String
    let size: CGFloat
    let elapsed: TimeInterval
    let time: TimeInterval
    let reduceMotion: Bool

    private var reveal: Double {
        guard !reduceMotion else { return 1 }
        let progress = min(1, max(0, (elapsed - 0.35) / 1.8))
        return progress * progress * (3 - 2 * progress)
    }
    private var shake: Double {
        guard !reduceMotion, elapsed < 1.1 else { return 0 }
        return sin(elapsed * 36) * 9 * pow(max(0, 1 - elapsed / 1.1), 2)
    }
    private var drift: Double { reduceMotion ? 0 : sin(time * 1.25) }

    var body: some View {
        ZStack {
            // Specular highlight and shaded edge give the ball a rounded, solid shell.
            Circle()
                .fill(RadialGradient(colors: [Color(white: 0.25), Color(white: 0.07), .black],
                                     center: .topLeading, startRadius: 0, endRadius: size * 0.9))
                .overlay(Circle().stroke(.white.opacity(0.18), lineWidth: 1))
                .shadow(color: .cyan.opacity(0.15), radius: 18, y: 8)
            Circle()
                .fill(.white.opacity(0.10))
                .frame(width: size * 0.22, height: size * 0.10)
                .blur(radius: 10)
                .offset(x: -size * 0.19, y: -size * 0.34)
            liquidWindow
                .frame(width: size * 0.76, height: size * 0.76)
        }
        .frame(width: size, height: size)
        .rotationEffect(.degrees(shake))
        .offset(x: shake * 0.55)
    }

    private var liquidWindow: some View {
        ZStack {
            Circle().fill(RadialGradient(colors: [Color(red: 0.015, green: 0.07, blue: 0.28),
                                                 Color(red: 0, green: 0.005, blue: 0.035)],
                                         center: .center, startRadius: 0, endRadius: size * 0.4))
            // The die rises from the dark liquid, becoming larger, brighter and sharper.
            triangle
                .scaleEffect(0.65 + 0.35 * reveal)
                .rotation3DEffect(.degrees((1 - reveal) * 48 + drift * 2), axis: (x: 1, y: 0.3, z: 0))
                .rotationEffect(.degrees((1 - reveal) * -18 + drift * 1.5))
                .offset(x: drift * 2, y: (1 - reveal) * size * 0.12 + drift * 3 + size * 0.035)
                .blur(radius: (1 - reveal) * 7)
                .opacity(reveal)
            // Soft glass reflection stays above the floating face.
            Circle().fill(LinearGradient(colors: [.white.opacity(0.10), .clear, .clear],
                                         startPoint: .topLeading, endPoint: .bottomTrailing))
        }
        .clipShape(Circle())
        .overlay(Circle().stroke(Color(white: 0.20), lineWidth: 8))
        .overlay(Circle().stroke(.cyan.opacity(0.30), lineWidth: 1))
    }

    private var triangle: some View {
        ZStack(alignment: .top) {
            AnswerTriangle()
                .fill(LinearGradient(colors: [Color(red: 0.14, green: 0.42, blue: 0.95),
                                             Color(red: 0.025, green: 0.10, blue: 0.40)],
                                     startPoint: .top, endPoint: .bottom))
            AnswerTriangle().stroke(.cyan.opacity(0.75), lineWidth: 1.5)
            Text(answer.uppercased())
                .font(.system(size: size * 0.044, weight: .bold, design: .monospaced))
                .foregroundStyle(Color(red: 0.82, green: 0.96, blue: 1))
                .multilineTextAlignment(.center)
                .lineLimit(3)
                .minimumScaleFactor(0.65)
                .frame(width: size * 0.29, height: size * 0.16)
                .padding(.top, size * 0.035)
        }
        .frame(width: size * 0.55, height: size * 0.47)
        .shadow(color: .blue.opacity(0.65), radius: 12)
    }
}
