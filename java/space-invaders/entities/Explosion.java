package spaceinvaders.entities;

import java.awt.Color;
import java.awt.Graphics2D;
import spaceinvaders.GameObject;

public final class Explosion extends GameObject {
    private int life = 18;

    public Explosion(double centerX, double centerY) {
        super(centerX - 18, centerY - 18, 36, 36);
    }

    @Override
    public void tick() {
        if (--life <= 0) destroy();
    }

    @Override
    public void render(Graphics2D graphics) {
        int radius = 4 + (18 - life);
        int alpha = Math.max(0, Math.min(255, life * 14));
        graphics.setColor(new Color(255, 220, 70, alpha));
        graphics.drawOval((int) (x + width / 2.0 - radius), (int) (y + height / 2.0 - radius), radius * 2, radius * 2);
        graphics.drawLine((int) x, (int) (y + height / 2.0), (int) (x + width), (int) (y + height / 2.0));
        graphics.drawLine((int) (x + width / 2.0), (int) y, (int) (x + width / 2.0), (int) (y + height));
    }
}
