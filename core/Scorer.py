class Scorer:
    """
    This scorer class takes the correct answer, the student's response, student's self-reported confidence score and
    returns a evaluation of student's response

    """
    def __init__(self, question, ans, response, confidence):
        self.question = question
        self.ans = ans
        self.response = response
        self.confidence = confidence

    @property
    def correctness(self):
        return int(self.ans) == int(self.response)

    def calculate_confidence(self):
        """
        if the response is correct, evaluation ranges from [3,5]; if the response is incorrect, evaluation ranges from [0,2]
        if the question is correct, the higher the self-reported confidence score, the higher the evaluation and vice versa
        :return: evaluation score
        """
        if self.correctness:
            return 2 + int(self.confidence)
        else:
            return 2 - int(self.confidence)

    def calculate_score(self):
        if self.correctness:
            print('correct')
            return 1
        else:
            print('incorrect')
            return 0