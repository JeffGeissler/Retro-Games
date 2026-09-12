import SpriteKit
import SwiftUI

struct ContentView: View {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var model: GameViewModel
    @State private var scene: GameScene

    init() {
        let model = GameViewModel()
        _model = StateObject(wrappedValue: model)
        _scene = State(initialValue: GameScene(model: model))
    }

    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Color.black.ignoresSafeArea()
                VStack(spacing: 8) {
                    hud
                    SpriteView(scene: scene, options: [.ignoresSiblingOrder])
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                        .overlay(RoundedRectangle(cornerRadius: 8).stroke(.cyan.opacity(0.35)))
                        .gesture(DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                let fraction = value.location.x / max(1, geometry.size.width)
                                scene.movePlayer(to: fraction * scene.size.width)
                            })
                        .accessibilityLabel("Alien invasion game field")
                        .accessibilityValue("Score \(model.score), wave \(model.wave), \(model.lives) lives")
                    controls
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)

                if model.phase != .playing { overlay }
            }
        }
        .preferredColorScheme(.dark)
        .onChange(of: scenePhase) { _, phase in
            if phase != .active, model.phase == .playing { scene.togglePause() }
        }
    }

    private var hud: some View {
        HStack {
            metric("SCORE", value: String(format: "%06d", model.score))
            Spacer()
            metric("HIGH", value: String(format: "%06d", model.highScore))
            Spacer()
            metric("WAVE", value: "\(model.wave)")
            Spacer()
            metric("LIVES", value: "\(model.lives)")
        }
        .foregroundStyle(.white)
        .accessibilityElement(children: .combine)
    }

    private func metric(_ title: String, value: String) -> some View {
        VStack(spacing: 1) {
            Text(title).font(.system(size: 10, weight: .bold, design: .monospaced)).foregroundStyle(.gray)
            Text(value).font(.system(size: 15, weight: .bold, design: .monospaced))
        }
    }

    private var controls: some View {
        HStack(spacing: 14) {
            movementButton(symbol: "arrow.left", direction: -1, label: "Move left")
            movementButton(symbol: "arrow.right", direction: 1, label: "Move right")
            Button { scene.fire() } label: {
                Label("FIRE", systemImage: "scope")
                    .font(.system(.headline, design: .monospaced, weight: .bold))
                    .frame(maxWidth: .infinity, minHeight: 48)
            }
            .buttonStyle(.borderedProminent)
            .tint(.red)
            .disabled(model.phase != .playing)
            Button { scene.togglePause() } label: {
                Image(systemName: model.phase == .paused ? "play.fill" : "pause.fill")
                    .frame(width: 34)
                    .frame(minHeight: 48)
            }
            .buttonStyle(.bordered)
            .tint(.cyan)
            .disabled(model.phase == .ready || model.phase == .gameOver)
            .accessibilityLabel(model.phase == .paused ? "Resume" : "Pause")
        }
    }

    private func movementButton(symbol: String, direction: CGFloat, label: String) -> some View {
        Image(systemName: symbol)
            .font(.title2.bold())
            .frame(width: 58, height: 48)
            .background(.cyan.opacity(model.phase == .playing ? 0.25 : 0.08), in: RoundedRectangle(cornerRadius: 9))
            .foregroundStyle(.cyan)
            .contentShape(Rectangle())
            .gesture(DragGesture(minimumDistance: 0)
                .onChanged { _ in scene.setMovement(direction) }
                .onEnded { _ in scene.setMovement(0) })
            .accessibilityElement()
            .accessibilityLabel(label)
            .accessibilityAddTraits(.isButton)
            .accessibilityAction { scene.nudgePlayer(direction) }
    }

    private var overlay: some View {
        VStack(spacing: 18) {
            Text(overlayTitle)
                .font(.system(.title, design: .monospaced, weight: .black))
                .foregroundStyle(.cyan)
                .multilineTextAlignment(.center)
            if model.phase == .gameOver {
                Text("SCORE \(model.score)")
                    .font(.system(.title3, design: .monospaced, weight: .bold))
            }
            Button(model.phase == .paused ? "RESUME" : model.phase == .gameOver ? "PLAY AGAIN" : "START GAME") {
                if model.phase == .paused { scene.togglePause() } else { scene.startOrRestart() }
            }
            .font(.system(.headline, design: .monospaced, weight: .bold))
            .buttonStyle(.borderedProminent)
            .tint(.cyan)
            .foregroundStyle(.black)
            .controlSize(.large)
            if model.phase == .ready {
                Text("DRAG THE SHIP OR USE THE ARROWS\nTAP FIRE TO SHOOT")
                    .font(.system(.caption, design: .monospaced, weight: .semibold))
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(28)
        .background(.black.opacity(0.9), in: RoundedRectangle(cornerRadius: 16))
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(.cyan.opacity(0.5)))
        .padding(28)
    }

    private var overlayTitle: String {
        switch model.phase {
        case .ready: "RETRO ALIEN\nINVASION"
        case .paused: "PAUSED"
        case .gameOver: "GAME OVER"
        case .playing: ""
        }
    }
}
