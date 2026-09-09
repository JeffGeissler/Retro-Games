import SwiftUI

@main
struct RetroEightBallApp: App {
    var body: some Scene { WindowGroup { ContentView() } }
}

struct ContentView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.scenePhase) private var scenePhase
    @State private var answer = "Ask a question, then SHAKE!"
    @State private var started = Date.distantPast

    var body: some View {
        GeometryReader { geometry in
            ScrollView {
                VStack(spacing: 28) {
                    Text("RETRO EIGHT BALL")
                        .font(.system(.title2, design: .monospaced, weight: .bold))
                        .foregroundStyle(.cyan)
                    Text("Think of a yes-or-no question.")
                        .foregroundStyle(.white)
                    TimelineView(.animation(paused: reduceMotion || scenePhase != .active || started == .distantPast)) { context in
                        let elapsed = context.date.timeIntervalSince(started)
                        let active = elapsed >= 0 && elapsed < 1.2 && !reduceMotion
                        let angle = active ? sin(elapsed * 24) * 10 * (1 - elapsed / 1.2) : 0
                        let glow = active ? 14 + 8 * sin(elapsed * 12) : 14
                        ZStack {
                            Circle().fill(.black)
                            Circle().stroke(.cyan, lineWidth: 12)
                                .shadow(color: .cyan.opacity(0.7), radius: glow)
                            Text(answer)
                                .font(.system(.title2, design: .monospaced, weight: .bold))
                                .foregroundStyle(.green)
                                .multilineTextAlignment(.center)
                                .minimumScaleFactor(0.5)
                                .padding(44)
                        }
                        .frame(width: min(geometry.size.width - 64, 360), height: min(geometry.size.width - 64, 360))
                        .rotationEffect(.degrees(angle))
                    }
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel("Answer")
                    .accessibilityValue(answer)
                    Button(action: shake) {
                        Text("SHAKE!")
                            .font(.system(.title, design: .monospaced, weight: .bold))
                            .frame(maxWidth: .infinity, minHeight: 56)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.cyan)
                    .foregroundStyle(.black)
                    .accessibilityHint("Reveals a randomly weighted answer")
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
        .task(id: started) {
            guard started != .distantPast else { return }
            do {
                try await Task.sleep(for: .milliseconds(1250))
                started = .distantPast
            } catch { /* A new shake replaces the pending reset. */ }
        }
    }

    private func shake() {
        answer = Responses.choose()
        started = reduceMotion ? .distantPast : Date()
        UIAccessibility.post(notification: .announcement, argument: answer)
    }
}
