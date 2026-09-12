package spaceinvaders;

import java.awt.Graphics2D;
import java.awt.Rectangle;

public abstract class GameObject {
    protected double x;
    protected double y;
    protected int width;
    protected int height;
    protected boolean alive = true;

    protected GameObject(double x, double y, int width, int height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    public abstract void tick();

    public abstract void render(Graphics2D graphics);

    public Rectangle getBounds() {
        return new Rectangle((int) x, (int) y, width, height);
    }

    public double getX() { return x; }
    public double getY() { return y; }
    public int getWidth() { return width; }
    public int getHeight() { return height; }
    public boolean isAlive() { return alive; }
    public void destroy() { alive = false; }
}
