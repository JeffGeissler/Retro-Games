package spaceinvaders.gfx;

import java.awt.image.BufferedImage;

public final class SpriteSheet {
    private final BufferedImage sheet;
    private final int tileWidth;
    private final int tileHeight;

    public SpriteSheet(BufferedImage sheet, int tileWidth, int tileHeight) {
        this.sheet = sheet;
        this.tileWidth = tileWidth;
        this.tileHeight = tileHeight;
    }

    public BufferedImage tile(int column, int row) {
        return sheet.getSubimage(column * tileWidth, row * tileHeight, tileWidth, tileHeight);
    }
}
