import Foundation

@MainActor
final class GameViewModel: ObservableObject {
    enum Phase {
        case ready
        case playing
        case paused
        case gameOver
    }

    @Published var score = 0
    @Published var highScore: Int
    @Published var lives = 3
    @Published var wave = 1
    @Published var phase: Phase = .ready

    private static let highScoreKey = "retroAlienInvasion.highScore"

    init(defaults: UserDefaults = .standard) {
        highScore = defaults.integer(forKey: Self.highScoreKey)
    }

    func addScore(_ points: Int) {
        score += points
        highScore = max(highScore, score)
    }

    func saveHighScore(defaults: UserDefaults = .standard) {
        defaults.set(highScore, forKey: Self.highScoreKey)
    }
}
