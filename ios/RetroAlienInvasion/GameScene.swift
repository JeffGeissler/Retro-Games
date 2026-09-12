import SpriteKit
import UIKit

@MainActor
final class GameScene: SKScene {
    private let model: GameViewModel
    private let player = SKShapeNode()
    private var aliens: [SKShapeNode] = []
    private var playerBullets: [SKShapeNode] = []
    private var alienBullets: [SKShapeNode] = []
    private var lastUpdate: TimeInterval = 0
    private var alienDirection: CGFloat = 1
    private var movement: CGFloat = 0
    private var playerFireCooldown: TimeInterval = 0
    private var alienFireCooldown: TimeInterval = 0.8
    private var hitCooldown: TimeInterval = 0
    private var generator = SystemRandomNumberGenerator()

    init(model: GameViewModel) {
        self.model = model
        super.init(size: CGSize(width: 390, height: 700))
        scaleMode = .resizeFill
        backgroundColor = UIColor(red: 0.01, green: 0.02, blue: 0.055, alpha: 1)
        anchorPoint = .zero
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func didMove(to view: SKView) {
        view.preferredFramesPerSecond = 60
        view.ignoresSiblingOrder = true
        buildStars()
        resetGame()
    }

    override func didChangeSize(_ oldSize: CGSize) {
        guard oldSize != .zero else { return }
        player.position.y = playerY
        player.position.x = min(max(player.position.x, 28), size.width - 28)
    }

    func startOrRestart() {
        switch model.phase {
        case .ready:
            model.phase = .playing
        case .gameOver:
            resetGame()
            model.phase = .playing
        case .playing, .paused:
            break
        }
    }

    func togglePause() {
        if model.phase == .playing {
            model.phase = .paused
            movement = 0
        } else if model.phase == .paused {
            model.phase = .playing
            lastUpdate = 0
        }
    }

    func setMovement(_ direction: CGFloat) {
        movement = model.phase == .playing ? min(1, max(-1, direction)) : 0
    }

    func movePlayer(to x: CGFloat) {
        guard model.phase == .playing else { return }
        player.position.x = min(max(x, 28), size.width - 28)
    }

    func nudgePlayer(_ direction: CGFloat) {
        guard model.phase == .playing else { return }
        movePlayer(to: player.position.x + min(1, max(-1, direction)) * 34)
    }

    func fire() {
        guard model.phase == .playing, playerFireCooldown <= 0, playerBullets.count < 3 else { return }
        let bullet = makeRect(size: CGSize(width: 4, height: 15), color: .white)
        bullet.name = "playerBullet"
        bullet.position = CGPoint(x: player.position.x, y: player.position.y + 20)
        bullet.zPosition = 3
        addChild(bullet)
        playerBullets.append(bullet)
        playerFireCooldown = 0.2
        UIImpactFeedbackGenerator(style: .light).impactOccurred(intensity: 0.55)
    }

    override func update(_ currentTime: TimeInterval) {
        guard model.phase == .playing else {
            lastUpdate = currentTime
            return
        }
        let delta = lastUpdate == 0 ? 1.0 / 60.0 : min(currentTime - lastUpdate, 1.0 / 20.0)
        lastUpdate = currentTime
        playerFireCooldown -= delta
        alienFireCooldown -= delta
        hitCooldown -= delta

        updatePlayer(delta: delta)
        updateAliens(delta: delta)
        updateBullets(delta: delta)
        resolveCollisions()
        fireAlienBulletIfNeeded()

        if aliens.isEmpty {
            model.wave += 1
            spawnAliens()
        } else if aliens.contains(where: { $0.frame.minY <= player.position.y + 24 }) {
            finishGame()
        }
    }

    private var playerY: CGFloat { max(58, size.height * 0.09) }

    private func resetGame() {
        aliens.forEach { $0.removeFromParent() }
        playerBullets.forEach { $0.removeFromParent() }
        alienBullets.forEach { $0.removeFromParent() }
        aliens.removeAll()
        playerBullets.removeAll()
        alienBullets.removeAll()
        movement = 0
        alienDirection = 1
        model.score = 0
        model.lives = 3
        model.wave = 1

        if player.parent == nil {
            player.path = playerPath()
            player.fillColor = UIColor(red: 0.22, green: 1, blue: 0.42, alpha: 1)
            player.strokeColor = .clear
            player.zPosition = 2
            addChild(player)
        }
        player.position = CGPoint(x: size.width / 2, y: playerY)
        player.alpha = 1
        spawnAliens()
    }

    private func spawnAliens() {
        alienDirection = 1
        let columns = 8
        let spacing = min(CGFloat(43), (size.width - 42) / CGFloat(columns))
        let startX = (size.width - spacing * CGFloat(columns - 1)) / 2
        let startY = size.height - 86

        for row in 0..<4 {
            for column in 0..<columns {
                let alien = SKShapeNode(path: alienPath())
                alien.fillColor = UIColor(red: 0.22, green: 0.92, blue: 1, alpha: 1)
                alien.strokeColor = .clear
                alien.name = "alien"
                alien.position = CGPoint(x: startX + CGFloat(column) * spacing,
                                         y: startY - CGFloat(row) * 39)
                alien.zPosition = 2
                addChild(alien)
                aliens.append(alien)
            }
        }
        alienFireCooldown = 0.9
    }

    private func updatePlayer(delta: TimeInterval) {
        player.position.x += movement * 230 * delta
        player.position.x = min(max(player.position.x, 28), size.width - 28)
    }

    private func updateAliens(delta: TimeInterval) {
        let speed = CGFloat(27 + (model.wave - 1) * 5)
        let dx = alienDirection * speed * delta
        let wouldHitEdge = aliens.contains { alien in
            let nextX = alien.position.x + dx
            return nextX - 17 <= 7 || nextX + 17 >= size.width - 7
        }
        if wouldHitEdge {
            alienDirection *= -1
            aliens.forEach { $0.position.y -= 13 }
        } else {
            aliens.forEach { $0.position.x += dx }
        }
    }

    private func updateBullets(delta: TimeInterval) {
        playerBullets.forEach { $0.position.y += 480 * delta }
        alienBullets.forEach { $0.position.y -= 285 * delta }
        playerBullets.removeAll { bullet in
            if bullet.position.y > size.height + 20 {
                bullet.removeFromParent()
                return true
            }
            return false
        }
        alienBullets.removeAll { bullet in
            if bullet.position.y < -20 {
                bullet.removeFromParent()
                return true
            }
            return false
        }
    }

    private func resolveCollisions() {
        var hitAliens = Set<ObjectIdentifier>()
        var spentBullets = Set<ObjectIdentifier>()
        for bullet in playerBullets {
            for alien in aliens where bullet.frame.intersects(alien.frame) {
                spentBullets.insert(ObjectIdentifier(bullet))
                hitAliens.insert(ObjectIdentifier(alien))
                explode(at: alien.position, color: alien.fillColor)
                model.addScore(10 * model.wave)
                break
            }
        }
        playerBullets.removeAll { bullet in
            guard spentBullets.contains(ObjectIdentifier(bullet)) else { return false }
            bullet.removeFromParent()
            return true
        }
        aliens.removeAll { alien in
            guard hitAliens.contains(ObjectIdentifier(alien)) else { return false }
            alien.removeFromParent()
            return true
        }

        guard hitCooldown <= 0,
              let bullet = alienBullets.first(where: { $0.frame.intersects(player.frame) }) else { return }
        bullet.removeFromParent()
        alienBullets.removeAll { $0 === bullet }
        model.lives -= 1
        hitCooldown = 1.0
        explode(at: player.position, color: player.fillColor)
        player.run(.sequence([.fadeAlpha(to: 0.2, duration: 0.08),
                              .fadeAlpha(to: 1, duration: 0.08)]), withKey: "hit")
        UINotificationFeedbackGenerator().notificationOccurred(.warning)
        if model.lives <= 0 { finishGame() }
    }

    private func fireAlienBulletIfNeeded() {
        guard alienFireCooldown <= 0, !aliens.isEmpty else { return }
        let columns = Dictionary(grouping: aliens) { Int($0.position.x / 35) }
        let frontLine = columns.values.compactMap { $0.min(by: { $0.position.y < $1.position.y }) }
        guard let shooter = frontLine.randomElement(using: &generator) else { return }
        let bullet = makeRect(size: CGSize(width: 5, height: 14),
                              color: UIColor(red: 1, green: 0.3, blue: 0.44, alpha: 1))
        bullet.name = "alienBullet"
        bullet.position = CGPoint(x: shooter.position.x, y: shooter.position.y - 20)
        bullet.zPosition = 3
        addChild(bullet)
        alienBullets.append(bullet)
        alienFireCooldown = max(0.35, 1.05 - Double(model.wave) * 0.055) + Double.random(in: 0...0.35)
    }

    private func finishGame() {
        guard model.phase == .playing else { return }
        movement = 0
        model.saveHighScore()
        model.phase = .gameOver
        UINotificationFeedbackGenerator().notificationOccurred(.error)
        UIAccessibility.post(notification: .announcement,
                             argument: "Game over. Score \(model.score). High score \(model.highScore).")
    }

    private func explode(at point: CGPoint, color: UIColor) {
        let burst = SKShapeNode(circleOfRadius: 7)
        burst.position = point
        burst.strokeColor = color
        burst.fillColor = .clear
        burst.lineWidth = 3
        burst.zPosition = 5
        addChild(burst)
        burst.run(.sequence([.group([.scale(to: 3.2, duration: 0.22),
                                      .fadeOut(withDuration: 0.22)]), .removeFromParent()]))
    }

    private func buildStars() {
        guard childNode(withName: "stars") == nil else { return }
        let field = SKNode()
        field.name = "stars"
        field.zPosition = -5
        for index in 0..<75 {
            let star = SKShapeNode(circleOfRadius: index.isMultiple(of: 11) ? 1.1 : 0.55)
            star.fillColor = UIColor(white: 0.55, alpha: 0.65)
            star.strokeColor = .clear
            star.position = CGPoint(x: CGFloat((index * 137 + 43) % 997) / 997 * size.width,
                                    y: CGFloat((index * 71 + 29) % 991) / 991 * size.height)
            field.addChild(star)
        }
        addChild(field)
    }

    private func makeRect(size: CGSize, color: UIColor) -> SKShapeNode {
        let node = SKShapeNode(rectOf: size, cornerRadius: 1)
        node.fillColor = color
        node.strokeColor = .clear
        return node
    }

    private func playerPath() -> CGPath {
        let path = CGMutablePath()
        path.move(to: CGPoint(x: -25, y: -10))
        path.addLine(to: CGPoint(x: 25, y: -10))
        path.addLine(to: CGPoint(x: 25, y: 5))
        path.addLine(to: CGPoint(x: 8, y: 5))
        path.addLine(to: CGPoint(x: 8, y: 12))
        path.addLine(to: CGPoint(x: -8, y: 12))
        path.addLine(to: CGPoint(x: -8, y: 5))
        path.addLine(to: CGPoint(x: -25, y: 5))
        path.closeSubpath()
        return path
    }

    private func alienPath() -> CGPath {
        let path = CGMutablePath()
        path.move(to: CGPoint(x: -17, y: -8))
        path.addLine(to: CGPoint(x: -13, y: 8))
        path.addLine(to: CGPoint(x: -7, y: 8))
        path.addLine(to: CGPoint(x: -4, y: 14))
        path.addLine(to: CGPoint(x: 4, y: 14))
        path.addLine(to: CGPoint(x: 7, y: 8))
        path.addLine(to: CGPoint(x: 13, y: 8))
        path.addLine(to: CGPoint(x: 17, y: -8))
        path.addLine(to: CGPoint(x: 9, y: -8))
        path.addLine(to: CGPoint(x: 6, y: -2))
        path.addLine(to: CGPoint(x: -6, y: -2))
        path.addLine(to: CGPoint(x: -9, y: -8))
        path.closeSubpath()
        return path
    }
}
