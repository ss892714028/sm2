class Scorer:
    def __init__(self, question, ans, response, confidence):
        self.question = question
        self.ans = ans
        self.response = response
        self.confidence = confidence

    @property
    def correctness(self):
        return int(self.ans) == int(self.response)

    def calculate_confidence(self):
        if self.correctness:
            return 2 + int(self.confidence)
        else:
            return 2 - int(self.confidence)

    def calculate_score(self):
        if self.correctness:
            return 1
        else:
            return 0