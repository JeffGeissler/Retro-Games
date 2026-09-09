package com.jeffgeissler.retroeightball;

import android.animation.ValueAnimator;
import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.Random;

/** Native Android port; no network, sensors, or third-party runtime dependencies. */
public final class MainActivity extends Activity {
    private TextView answer;
    private ValueAnimator animation;
    private final Random random = new Random();

    @Override public void onCreate(Bundle savedState) {
        super.onCreate(savedState);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.BLACK);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER);
        content.setPadding(dp(24), dp(24), dp(24), dp(24));
        scroll.addView(content);
        if (android.os.Build.VERSION.SDK_INT >= 30) {
          scroll.setOnApplyWindowInsetsListener((view, insets) -> {
            android.graphics.Insets bars = insets.getInsets(android.view.WindowInsets.Type.systemBars() | android.view.WindowInsets.Type.displayCutout());
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            return insets;
          });
        } else {
            scroll.setOnApplyWindowInsetsListener((view, insets) -> {
                view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(), insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
                return insets;
            });
        }
        content.addView(label(getString(R.string.title), 24, Color.CYAN));
        content.addView(label(getString(R.string.prompt), 16, Color.WHITE));
        answer = label(savedState == null ? getString(R.string.initial_answer) : savedState.getString("answer", getString(R.string.initial_answer)), 22, Color.GREEN);
        answer.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        answer.setPadding(dp(36), dp(24), dp(36), dp(24));
        GradientDrawable ball = new GradientDrawable();
        ball.setShape(GradientDrawable.OVAL);
        ball.setColor(Color.BLACK);
        ball.setStroke(dp(8), Color.CYAN);
        answer.setBackground(ball);
        int size = Math.min(getResources().getDisplayMetrics().widthPixels - dp(64), dp(360));
        LinearLayout.LayoutParams ballLayout = new LinearLayout.LayoutParams(size, size);
        ballLayout.setMargins(0, dp(28), 0, dp(28));
        content.addView(answer, ballLayout);
        Button shake = new Button(this);
        shake.setText(R.string.shake);
        shake.setTextSize(24);
        shake.setTextColor(Color.CYAN);
        shake.setMinHeight(dp(56));
        shake.setOnClickListener(view -> shake());
        content.addView(shake, new LinearLayout.LayoutParams(-1, -2));
        setContentView(scroll);
        scroll.requestApplyInsets();
    }

    private TextView label(String text, int size, int color) {
        TextView label = new TextView(this);
        label.setText(text);
        label.setTextSize(size);
        label.setTextColor(color);
        label.setGravity(Gravity.CENTER);
        label.setTypeface(Typeface.MONOSPACE, Typeface.BOLD);
        label.setPadding(0, dp(8), 0, dp(8));
        return label;
    }

    private void shake() {
        stopAnimation();
        answer.setText(Responses.choose(random));
        if (!ValueAnimator.areAnimatorsEnabled()) return;
        animation = ValueAnimator.ofFloat(0f, 1f);
        animation.setDuration(1200);
        animation.addUpdateListener(value -> {
            float progress = (float) value.getAnimatedValue();
            answer.setRotation((float) Math.sin(progress * 28.8) * 10 * (1 - progress));
            answer.setAlpha(1f - 0.25f * (float) Math.sin(progress * Math.PI));
        });
        animation.start();
    }

    private void stopAnimation() {
        if (animation != null) { animation.cancel(); animation = null; }
        if (answer != null) { answer.setRotation(0); answer.setAlpha(1); }
    }

    @Override protected void onStop() { stopAnimation(); super.onStop(); }
    @Override protected void onSaveInstanceState(Bundle state) {
        state.putString("answer", answer.getText().toString());
        super.onSaveInstanceState(state);
    }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
}
