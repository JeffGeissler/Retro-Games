package spaceinvaders;

import java.awt.Graphics2D;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public final class Handler {
    private final List<GameObject> objects = new ArrayList<>();

    public void tick() {
        for (GameObject object : new ArrayList<>(objects)) {
            if (object.isAlive()) object.tick();
        }
        objects.removeIf(object -> !object.isAlive());
    }

    public void render(Graphics2D graphics) {
        for (GameObject object : new ArrayList<>(objects)) object.render(graphics);
    }

    public void add(GameObject object) { objects.add(object); }
    public void clear() { objects.clear(); }

    public List<GameObject> objects() {
        return Collections.unmodifiableList(objects);
    }

    public <T extends GameObject> List<T> find(Class<T> type) {
        List<T> matches = new ArrayList<>();
        for (GameObject object : objects) {
            if (type.isInstance(object) && object.isAlive()) matches.add(type.cast(object));
        }
        return matches;
    }
}
