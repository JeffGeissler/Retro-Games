var counts: [String: Int] = [:]
for roll in 0..<24 { counts[Responses.answer(for: roll), default: 0] += 1 }
let expected = ["It is certain.": 3, "Ask again later.": 2, "My reply is no.": 3,
                "Outlook good.": 4, "Better not tell you now.": 1, "Yes — definitely.": 5,
                "Very doubtful.": 2, "Signs point to yes.": 4]
precondition(Responses.totalWeight == 24)
precondition(counts == expected, "Response distribution differs from the original")
print("All 24 Swift weighted outcomes passed.")
