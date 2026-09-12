package spaceinvaders;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import spaceinvaders.entities.Alien;
import spaceinvaders.entities.AlienBullet;
import spaceinvaders.entities.Bullet;
import spaceinvaders.entities.Explosion;
import spaceinvaders.entities.Player;
import spaceinvaders.input.KeyInput;
import spaceinvaders.util.HighScoreManager;

public final class Game extends JPanel {
    public static final int WIDTH = 800;
    public static final int HEIGHT = 600;
    private static final int PLAYER_Y = HEIGHT - 72;

    private enum State { READY, PLAYING, PAUSED, GAME_OVER }

    private final Handler handler = new Handler();
    private final HighScoreManager highScores = new HighScoreManager();
    private final Random random = new Random();
    private final Timer timer = new Timer(16, event -> gameLoop());
    private Player player;
    private State state = State.READY;
    private int score;
    private int highScore;
    private int lives;
    private int wave;
    private int fireCooldown;
    private int alienFireCooldown;
    private boolean formationAtEdge;

    public Game() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setBackground(new Color(3, 5, 14));
        setFocusable(true);
        highScore = highScores.load();
        resetWorld();
        addKeyListener(new KeyInput(this));
        timer.start();
    }

    private void resetWorld() {
        handler.clear();
        player = new Player(WIDTH / 2.0 - 25, PLAYER_Y, WIDTH);
        handler.add(player);
        score = 0;
        lives = 3;
        wave = 1;
        fireCooldown = 0;
        formationAtEdge = false;
        createAliens();
    }

    private void createAliens() {
        double speed = 0.65 + (wave - 1) * 0.12;
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 10; col++) {
                handler.add(new Alien(80 + col * 62, 68 + row * 48, speed));
            }
        }
        alienFireCooldown = 55;
    }

    private void gameLoop() {
        if (state == State.PLAYING) updateGame();
        repaint();
    }

    private void updateGame() {
        if (fireCooldown > 0) fireCooldown--;
        if (alienFireCooldown > 0) alienFireCooldown--;
        moveAlienFormation();
        handler.tick();
        resolveCollisions();
        fireAlienBullet();

        List<Alien> aliens = handler.find(Alien.class);
        if (aliens.isEmpty()) {
            wave++;
            createAliens();
        } else if (aliens.stream().anyMatch(alien -> alien.getY() + alien.getHeight() >= PLAYER_Y)) {
            endGame();
        }
    }

    private void moveAlienFormation() {
        List<Alien> aliens = handler.find(Alien.class);
        boolean atEdge = aliens.stream().anyMatch(alien ->
            alien.getX() <= 12 || alien.getX() + alien.getWidth() >= WIDTH - 12);
        if (atEdge && !formationAtEdge) aliens.forEach(alien -> alien.reverseAndDescend(16));
        formationAtEdge = atEdge;
    }

    private void resolveCollisions() {
        for (Bullet bullet : handler.find(Bullet.class)) {
            for (Alien alien : handler.find(Alien.class)) {
                if (bullet.isAlive() && bullet.getBounds().intersects(alien.getBounds())) {
                    bullet.destroy();
                    alien.destroy();
                    handler.add(new Explosion(alien.getX() + alien.getWidth() / 2.0,
                        alien.getY() + alien.getHeight() / 2.0));
                    score += 10 * wave;
                    highScore = Math.max(highScore, score);
                }
            }
        }

        for (AlienBullet bullet : handler.find(AlienBullet.class)) {
            if (bullet.getBounds().intersects(player.getBounds())) {
                bullet.destroy();
                lives--;
                handler.add(new Explosion(player.getX() + player.getWidth() / 2.0,
                    player.getY() + player.getHeight() / 2.0));
                if (lives <= 0) endGame();
            }
        }
    }

    private void fireAlienBullet() {
        if (alienFireCooldown > 0) return;
        List<Alien> aliens = handler.find(Alien.class);
        if (aliens.isEmpty()) return;

        Alien shooter = aliens.stream()
            .sorted(Comparator.comparingDouble(Alien::getY).reversed())
            .limit(Math.min(10, aliens.size()))
            .skip(random.nextInt(Math.min(10, aliens.size())))
            .findFirst().orElse(aliens.get(0));
        handler.add(new AlienBullet(shooter.getX() + shooter.getWidth() / 2.0,
            shooter.getY() + shooter.getHeight(), HEIGHT));
        alienFireCooldown = Math.max(25, 75 - wave * 4) + random.nextInt(35);
    }

    public void firePlayerBullet() {
        if (state != State.PLAYING || fireCooldown > 0) return;
        if (handler.find(Bullet.class).size() >= 3) return;
        handler.add(new Bullet(player.getX() + player.getWidth() / 2.0 - 2, player.getY() - 14));
        fireCooldown = 12;
    }

    public void setMovingLeft(boolean moving) { player.setMovingLeft(moving); }
    public void setMovingRight(boolean moving) { player.setMovingRight(moving); }

    public void togglePause() {
        if (state == State.PLAYING) state = State.PAUSED;
        else if (state == State.PAUSED) state = State.PLAYING;
    }

    public void startOrRestart() {
        if (state == State.READY) state = State.PLAYING;
        else if (state == State.GAME_OVER) {
            resetWorld();
            state = State.PLAYING;
        }
    }

    private void endGame() {
        highScore = highScores.record(score);
        state = State.GAME_OVER;
    }

    @Override
    protected void paintComponent(Graphics graphics) {
        super.paintComponent(graphics);
        Graphics2D g = (Graphics2D) graphics.create();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_OFF);
        drawStars(g);
        handler.render(g);
        drawHud(g);
        if (state != State.PLAYING) drawOverlay(g);
        g.dispose();
    }

    private void drawStars(Graphics2D g) {
        g.setColor(new Color(60, 75, 105));
        for (int i = 0; i < 70; i++) {
            int x = (i * 137 + 43) % WIDTH;
            int y = (i * 71 + 29) % HEIGHT;
            g.fillRect(x, y, (i % 9 == 0) ? 2 : 1, 1);
        }
    }

    private void drawHud(Graphics2D g) {
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 20));
        g.setColor(Color.WHITE);
        g.drawString(String.format("SCORE %06d", score), 16, 28);
        g.drawString(String.format("HIGH %06d", highScore), 315, 28);
        g.drawString("WAVE " + wave, 655, 28);
        g.setColor(new Color(55, 255, 105));
        g.drawString("LIVES " + lives, 16, HEIGHT - 18);
        g.setStroke(new BasicStroke(2));
        g.drawLine(0, HEIGHT - 45, WIDTH, HEIGHT - 45);
    }

    private void drawOverlay(Graphics2D g) {
        g.setColor(new Color(0, 0, 0, 190));
        g.fillRect(0, 0, WIDTH, HEIGHT);
        String title = switch (state) {
            case READY -> "RETRO ALIEN INVASION";
            case PAUSED -> "PAUSED";
            case GAME_OVER -> "GAME OVER";
            default -> "";
        };
        drawCentered(g, title, HEIGHT / 2 - 34, 36, new Color(60, 235, 255));
        String prompt = state == State.PAUSED ? "PRESS P TO CONTINUE" : "PRESS ENTER TO START";
        drawCentered(g, prompt, HEIGHT / 2 + 22, 18, Color.WHITE);
        if (state == State.READY) drawCentered(g, "ARROWS/A-D MOVE   SPACE FIRES   P PAUSES", HEIGHT / 2 + 62, 15, Color.LIGHT_GRAY);
    }

    private void drawCentered(Graphics2D g, String text, int y, int size, Color color) {
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, size));
        g.setColor(color);
        int x = (WIDTH - g.getFontMetrics().stringWidth(text)) / 2;
        g.drawString(text, x, y);
    }

    private static void launch() {
        Game game = new Game();
        JFrame frame = new JFrame("Retro Alien Invasion");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setResizable(false);
        frame.add(game);
        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
        game.requestFocusInWindow();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(Game::launch);
    }
}
