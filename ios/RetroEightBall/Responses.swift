enum Responses {
    static let answers: [(text: String, weight: Int)] = [
        ("It is certain.", 3), ("Ask again later.", 2), ("My reply is no.", 3),
        ("Outlook good.", 4), ("Better not tell you now.", 1), ("Yes — definitely.", 5),
        ("Very doubtful.", 2), ("Signs point to yes.", 4)
    ]
    static let totalWeight = answers.reduce(0) { $0 + $1.weight }
    static func answer(for roll: Int) -> String {
        precondition((0..<totalWeight).contains(roll))
        var remainder = roll
        for answer in answers {
            if remainder < answer.weight { return answer.text }
            remainder -= answer.weight
        }
        preconditionFailure("Invalid response weights")
    }
    static func choose() -> String { answer(for: Int.random(in: 0..<totalWeight)) }
}
