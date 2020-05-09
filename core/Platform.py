import numpy as np
from Student import Student
import random
from Scorer import Scorer
import pickle
import os
import math
# score(list), question_bank(map: {question_id: list of confidence history), questions:


class Platform:
    def __init__(self, student_name, questions, question_bank, date, first_time=False):
        """
        :param questions:
        :param question_bank:
        :param date:
        """
        self.student_name = student_name
        self.questions = questions
        self.student = Student(student_name, question_bank, first_time=first_time)
        self.date = date
        self.num_questions = np.random.randint(5, 20)

    def get_questions(self):
        """
        :return: question id in this quiz for this student
        """
        # get the questions that are due today
        questions = []
        for key, value in self.student.schedule.items():
            if self.date == value:
                questions.append(key)
        # get the additional number of questions if the questions due today is not enough
        num_new_question = self.num_questions - len(questions)

        # randomly sample additional questions from the question pool of the student

        if num_new_question > 0:
            _pool = [i for i in self.student.schedule.keys() if i not in questions]
            questions = questions + random.sample(_pool, min(num_new_question, len(_pool)))
        return questions

    def give_quiz(self, questions):
        """
        Give the quiz to the student, update the question_back and score for that student
        :param questions: questions that are going to be given.
        :return: new question_bank, new score
        """
        temp = {}
        total_score = []
        for i in questions:
            ans = input(str(i))
            conf = input('confidence 0-2')
            s = Scorer(i, self.questions[i], ans, conf)
            confidence = s.calculate_confidence()
            score = s.calculate_score()
            temp[i] = confidence
            total_score.append(score)

        print(self.update_student_history(new_confidence=temp, new_score=np.mean(total_score)))

        return temp, np.mean(total_score)

    def update_student_history(self, new_confidence, new_score):
        dict = self.student.question_bank
        print(new_confidence)
        for i in new_confidence.keys():
            dict[i].append(new_confidence[i])

        self.student.score.append(new_score)
        schedule = self.student.schedule
        for i in dict.keys():
            if dict[i]:
                print(dict[i])
                interval = self.sm2(dict[i])
                schedule[i] = interval

        # self.student.question_bank = dict
        # self.student.schedule = schedule
        # Save
        qb_dir = '../data/qb/'
        score_dir = '../data/score/'
        schedule_dir = '../data/schedule/'

        for i in ([qb_dir,score_dir,schedule_dir]):
            if not os.path.exists(i):
                os.makedirs(i)
        pickle.dump(dict, open(qb_dir+str(self.student_name) + '.p', "wb"))
        pickle.dump(self.student.score, open(score_dir + str(self.student_name) + '.p', "wb"))
        pickle.dump(schedule, open(schedule_dir + str(self.student_name) + '.p', "wb"))

        return dict, self.student.score, schedule

    @staticmethod
    def sm2(x: [int], a=6.0, b=-0.8, c=0.28, d=0.02, theta=0.2) -> float:
        """
        Returns the number of days to delay the next review of an item by, fractionally, based on the history of answers x to
        a given question, where
        x == 0: Incorrect, Hardest
        x == 1: Incorrect, Hard
        x == 2: Incorrect, Medium
        x == 3: Correct, Medium
        x == 4: Correct, Easy
        x == 5: Correct, Easiest
        @param x The history of answers in the above scoring.
        @param theta When larger, the delays for correct answers will increase.
        """

        assert all(0 <= x_i <= 5 for x_i in x)
        correct_x = [x_i >= 3 for x_i in x]
        # If you got the last question incorrect, just return 1
        if not correct_x[-1]:
            return 1.0

        # Calculate the latest consecutive answer streak
        num_consecutively_correct = 0
        for correct in reversed(correct_x):
            if correct:
                num_consecutively_correct += 1
            else:
                break

        return a * (max(1.3, 2.5 + sum(b + c * x_i + d * x_i * x_i for x_i in x))) ** (
                    theta * num_consecutively_correct)

    def main(self):
        questions = self.get_questions()
        new_confidence, new_score = self.give_quiz(questions)


if __name__ == '__main__':
    p = Platform('110', {i: random.randint(0,3) for i in range(10)}, [1, 2, 3, 4, 5, 6],'1', True)
    p.main()

