package spaceinvaders.entities;

import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import spaceinvaders.GameObject;
import spaceinvaders.gfx.Assets;

public final class Player extends GameObject {
    private final int worldWidth;
    private boolean movingLeft;
    private boolean movingRight;

    public Player(double x, double y, int worldWidth) {
        super(x, y, 50, 24);
        this.worldWidth = worldWidth;
    }

    @Override
    public void tick() {
        if (movingLeft != movingRight) x += movingLeft ? -5.0 : 5.0;
        x = Math.max(8, Math.min(worldWidth - width - 8, x));
    }

    @Override
    public void render(Graphics2D graphics) {
        BufferedImage sprite = Assets.player();
        graphics.drawImage(sprite, (int) x, (int) y, width, height, null);
    }

    public void setMovingLeft(boolean movingLeft) { this.movingLeft = movingLeft; }
    public void setMovingRight(boolean movingRight) { this.movingRight = movingRight; }
}
