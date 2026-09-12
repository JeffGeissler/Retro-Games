package spaceinvaders.entities;

import java.awt.Color;
import java.awt.Graphics2D;
import spaceinvaders.GameObject;

public final class AlienBullet extends GameObject {
    private final int worldHeight;

    public AlienBullet(double x, double y, int worldHeight) {
        super(x, y, 5, 14);
        this.worldHeight = worldHeight;
    }

    @Override
    public void tick() {
        y += 5.5;
        if (y > worldHeight) destroy();
    }

    @Override
    public void render(Graphics2D graphics) {
        graphics.setColor(new Color(255, 80, 110));
        graphics.fillRect((int) x, (int) y, width, height);
    }
}
