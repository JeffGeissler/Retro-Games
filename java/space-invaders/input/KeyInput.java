package spaceinvaders.input;

import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import spaceinvaders.Game;

public final class KeyInput extends KeyAdapter {
    private final Game game;

    public KeyInput(Game game) {
        this.game = game;
    }

    @Override
    public void keyPressed(KeyEvent event) {
        switch (event.getKeyCode()) {
            case KeyEvent.VK_LEFT, KeyEvent.VK_A -> game.setMovingLeft(true);
            case KeyEvent.VK_RIGHT, KeyEvent.VK_D -> game.setMovingRight(true);
            case KeyEvent.VK_SPACE -> game.firePlayerBullet();
            case KeyEvent.VK_P -> game.togglePause();
            case KeyEvent.VK_ENTER -> game.startOrRestart();
            default -> { }
        }
    }

    @Override
    public void keyReleased(KeyEvent event) {
        switch (event.getKeyCode()) {
            case KeyEvent.VK_LEFT, KeyEvent.VK_A -> game.setMovingLeft(false);
            case KeyEvent.VK_RIGHT, KeyEvent.VK_D -> game.setMovingRight(false);
            default -> { }
        }
    }
}
