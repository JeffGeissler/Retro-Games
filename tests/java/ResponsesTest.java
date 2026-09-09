import com.jeffgeissler.retroeightball.Responses;
import java.util.LinkedHashMap;
import java.util.Map;

public final class ResponsesTest {
    public static void main(String[] args) {
        Map<String, Integer> actual = new LinkedHashMap<>();
        for (int roll = 0; roll < 24; roll++) actual.merge(Responses.forRoll(roll), 1, Integer::sum);
        Map<String, Integer> expected = Map.of(
            "It is certain.", 3, "Ask again later.", 2, "My reply is no.", 3, "Outlook good.", 4,
            "Better not tell you now.", 1, "Yes — definitely.", 5, "Very doubtful.", 2, "Signs point to yes.", 4);
        if (!actual.equals(expected)) throw new AssertionError(actual);
        for (int invalid : new int[]{-1, 24}) {
            try { Responses.forRoll(invalid); throw new AssertionError("Accepted invalid roll"); }
            catch (IllegalArgumentException expectedException) { /* Expected. */ }
        }
        System.out.println("All 24 weighted outcomes and invalid boundaries passed.");
    }
}
