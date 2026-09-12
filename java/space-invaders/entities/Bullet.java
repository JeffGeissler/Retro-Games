package spaceinvaders.entities;

import java.awt.Color;
import java.awt.Graphics2D;
import spaceinvaders.GameObject;

public final class Bullet extends GameObject {
    public Bullet(double x, double y) { super(x, y, 4, 14); }

    @Override
    public void tick() {
        y -= 9;
        if (y + height < 0) destroy();
    }

    @Override
    public void render(Graphics2D graphics) {
        graphics.setColor(Color.WHITE);
        graphics.fillRect((int) x, (int) y, width, height);
    }
}
