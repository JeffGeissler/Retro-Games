package spaceinvaders.entities;

import java.awt.Graphics2D;
import spaceinvaders.GameObject;
import spaceinvaders.gfx.Assets;

public final class Alien extends GameObject {
    private double horizontalSpeed;

    public Alien(double x, double y, double horizontalSpeed) {
        super(x, y, 40, 28);
        this.horizontalSpeed = horizontalSpeed;
    }

    @Override
    public void tick() { x += horizontalSpeed; }

    @Override
    public void render(Graphics2D graphics) {
        int frame = ((int) x / 8) & 1;
        graphics.drawImage(Assets.alien(frame), (int) x, (int) y, width, height, null);
    }

    public void reverseAndDescend(int pixels) {
        horizontalSpeed = -horizontalSpeed;
        y += pixels;
    }
}
