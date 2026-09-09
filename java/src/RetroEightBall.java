import com.jeffgeissler.retroeightball.Responses;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import java.awt.BasicStroke;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** Jeff Geissler's neon arcade eight ball, modernized for desktop Java. */
public final class RetroEightBall extends JPanel {
    private String message = "Ask a question, then SHAKE!";
    private final Random random = new Random();
    private final Timer animation;
    private long started;
    private double wobbleAngle;
    private float glowIntensity = 1f;

    public RetroEightBall() {
        setPreferredSize(new Dimension(500, 500));
        setBackground(Color.BLACK);
        getAccessibleContext().setAccessibleName("Magic 8 Ball answer");
        animation = new Timer(30, e -> {
            double seconds = (System.nanoTime() - started) / 1_000_000_000.0;
            if (seconds >= 1.2) {
                ((Timer) e.getSource()).stop();
                wobbleAngle = 0;
                glowIntensity = 1f;
            } else {
                wobbleAngle = Math.sin(seconds * 24) * 10 * (1 - seconds / 1.2);
                glowIntensity = 1f + (float) Math.sin(seconds * 12) * 0.5f;
            }
            repaint();
        });
    }

    private void shake() {
        message = Responses.choose(random);
        getAccessibleContext().setAccessibleDescription(message);
        started = System.nanoTime();
        animation.restart();
        repaint();
    }

    @Override public void removeNotify() {
        animation.stop();
        super.removeNotify();
    }

    @Override protected void paintComponent(Graphics graphics) {
        super.paintComponent(graphics);
        Graphics2D g = (Graphics2D) graphics.create();
        try {
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            int cx = getWidth() / 2, cy = getHeight() / 2;
            int radius = Math.min(getWidth(), getHeight()) / 3;
            g.rotate(Math.toRadians(wobbleAngle), cx, cy);
            int green = Math.min(255, Math.max(0, (int) (255 * glowIntensity)));
            g.setColor(new Color(0, green, 255));
            g.setStroke(new BasicStroke(Math.max(4, radius / 9f)));
            g.drawOval(cx - radius, cy - radius, radius * 2, radius * 2);
            g.setColor(Color.GREEN);
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, Math.max(12, radius / 8)));
            FontMetrics metrics = g.getFontMetrics();
            List<String> lines = new ArrayList<>();
            String line = "";
            for (String word : message.split(" ")) {
                String candidate = line.isEmpty() ? word : line + " " + word;
                if (!line.isEmpty() && metrics.stringWidth(candidate) > radius * 1.5) {
                    lines.add(line);
                    line = word;
                } else line = candidate;
            }
            lines.add(line);
            int y = cy - lines.size() * metrics.getHeight() / 2 + metrics.getAscent();
            for (String text : lines) {
                g.drawString(text, cx - metrics.stringWidth(text) / 2, y);
                y += metrics.getHeight();
            }
        } finally { g.dispose(); }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            RetroEightBall ball = new RetroEightBall();
            JButton button = new JButton("SHAKE!");
            button.setFont(new Font(Font.MONOSPACED, Font.BOLD, 24));
            button.setForeground(Color.CYAN);
            button.setBackground(Color.DARK_GRAY);
            button.addActionListener(e -> ball.shake());
            JFrame frame = new JFrame("Retro Arcade Eight Ball");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.add(ball, BorderLayout.CENTER);
            frame.add(button, BorderLayout.SOUTH);
            frame.getRootPane().setDefaultButton(button);
            frame.setMinimumSize(new Dimension(360, 400));
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }
}
