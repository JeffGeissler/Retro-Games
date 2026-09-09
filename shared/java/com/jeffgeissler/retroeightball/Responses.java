package com.jeffgeissler.retroeightball;

import java.util.Random;

/** Original answer order and weights, shared by desktop and Android. */
public final class Responses {
    private static final String[] ANSWERS = {
        "It is certain.", "Ask again later.", "My reply is no.", "Outlook good.",
        "Better not tell you now.", "Yes — definitely.", "Very doubtful.", "Signs point to yes."
    };
    private static final int[] WEIGHTS = {3, 2, 3, 4, 1, 5, 2, 4};
    public static final int TOTAL_WEIGHT = 24;
    private Responses() {}

    public static String choose(Random random) { return forRoll(random.nextInt(TOTAL_WEIGHT)); }

    /** Maps a zero-based roll to an answer; useful for deterministic verification. */
    public static String forRoll(int roll) {
        if (roll < 0 || roll >= TOTAL_WEIGHT) throw new IllegalArgumentException("Roll must be 0–23");
        for (int i = 0; i < WEIGHTS.length; i++) {
            if (roll < WEIGHTS[i]) return ANSWERS[i];
            roll -= WEIGHTS[i];
        }
        throw new AssertionError("Invalid response weights");
    }
}
