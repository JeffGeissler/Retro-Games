package spaceinvaders.util;

import java.util.prefs.Preferences;

public final class HighScoreManager {
    private static final String HIGH_SCORE = "highScore";
    private final Preferences preferences = Preferences.userNodeForPackage(HighScoreManager.class);

    public int load() { return preferences.getInt(HIGH_SCORE, 0); }

    public int record(int score) {
        int highScore = Math.max(load(), score);
        preferences.putInt(HIGH_SCORE, highScore);
        return highScore;
    }
}
