package spaceinvaders.gfx;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;

public final class Assets {
    private static final int TILE_WIDTH = 20;
    private static final int TILE_HEIGHT = 14;
    private static final SpriteSheet SHEET = buildSheet();

    private Assets() { }

    public static BufferedImage player() { return SHEET.tile(0, 0); }
    public static BufferedImage alien(int frame) { return SHEET.tile(1 + (frame & 1), 0); }

    private static SpriteSheet buildSheet() {
        BufferedImage image = new BufferedImage(TILE_WIDTH * 3, TILE_HEIGHT, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = image.createGraphics();
        drawPixels(g, 0, new Color(55, 255, 105), new String[] {
            ".........##.........", "........####........", ".......######.......",
            "...##############...", "..################..", ".##################.",
            "####################", "####################", "####################"
        });
        drawPixels(g, TILE_WIDTH, new Color(60, 235, 255), new String[] {
            ".....##......##.....", "......##....##......", ".....##########.....",
            "....##..####..##....", "...##############...", "...##.########.##...",
            "...##..........##...", ".....##......##.....", "....##........##...."
        });
        drawPixels(g, TILE_WIDTH * 2, new Color(60, 235, 255), new String[] {
            ".....##......##.....", "...##..##..##..##...", "...##############...",
            "..###..######..###..", "..################..", "....############....",
            ".....##......##.....", "....##........##....", ".....##......##....."
        });
        g.dispose();
        return new SpriteSheet(image, TILE_WIDTH, TILE_HEIGHT);
    }

    private static void drawPixels(Graphics2D g, int offsetX, Color color, String[] rows) {
        g.setColor(color);
        for (int y = 0; y < rows.length; y++) {
            for (int x = 0; x < rows[y].length(); x++) {
                if (rows[y].charAt(x) == '#') g.fillRect(offsetX + x, y + 2, 1, 1);
            }
        }
    }
}
