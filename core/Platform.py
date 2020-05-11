import numpy as np
from Student import Student
import random
from Scorer import Scorer
import pickle
import os
from datetime import datetime
import time
# score(list), question_bank(map: {question_id: list of confidence history), questions:


class Platform:
    def __init__(self, student_name, questions, question_bank, first_time=False):
        """
        :param questions:
        :param question_bank:
        :param date:
        """
        self.student_name = student_name
        self.questions = questions
        self.question_bank = question_bank
        self.first_time = first_time
        self.student = Student(self.student_name, self.question_bank, first_time=self.first_time)
        self.num_questions = 10
        # get current timestamp
        self.ts = datetime.now().timestamp()

    # get current time
    @property
    def date(self):
        return self.ts_to_date(self.ts)

    @staticmethod
    def ts_to_date(ts):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

    @staticmethod
    def date_to_ts(date):
        return time.mktime(datetime.strptime(date, '%Y-%m-%d').timetuple())

    @staticmethod
    def days_to_ts(date):
        return date * 86400

    def get_questions(self):
        """
        :return: question id in this quiz for this student
        """
        # get the questions that are due today
        questions = []
        for key, value in self.student.schedule.items():
            if self.date == value:
                questions.append(key)
        reviews = questions
        print('Reviews: {}'.format(reviews))
        # get the additional number of questions if the questions due today is not enough
        num_new_question = self.num_questions - len(questions)

        # randomly sample additional questions from the available question pool of the student
        if num_new_question > 0:
            _pool = [i for i in self.student.question_bank if i not in questions]
            # if there is not enough questions in the pool, only take what is available
            new_question = random.sample(_pool, min(num_new_question, len(_pool)))
            print('New questions: {}'.format(new_question))
            questions = questions + new_question
            print('Total number of questions: {}'.format(len(questions)))
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
            ans = input('Answer Question ' + str(i) + ': ')
            conf = input('Pick a confidence score ranging 0-2: ')
            s = Scorer(i, self.questions[i], ans, conf)
            evaluation = s.calculate_confidence()
            score = s.calculate_score()
            temp[i] = evaluation
            total_score.append(score)

        dict, student_score, schedule = self.update_student_history(new_confidence=temp, new_score=np.mean(total_score))
        print('for student' + str(self.student_name) + '\n'
              + 'Student Score:' + str(student_score))

        self.print_confidence(dict)
        self.print_schedule(schedule)

        return temp, np.mean(total_score)

    @staticmethod
    def print_confidence(d):
        print('Confidence history for this student')
        for key, value in d.items():
            print('Question ID ' + str(key))
            print(*value)

    @staticmethod
    def print_schedule(d):
        print('Schedule for this student')
        for key, value in d.items():
            print('Question ID ' + str(key) + ' date ' + str(value))

    def update_student_history(self, new_confidence, new_score):
        dict = self.student.question_bank
        for i in new_confidence.keys():
            dict[i].append(new_confidence[i])

        self.student.score.append(new_score)
        schedule = self.student.schedule
        for i in dict.keys():
            if dict[i]:
                interval = self.sm2(dict[i])
                ts = self.days_to_ts(interval) + self.ts
                schedule[i] = self.ts_to_date(ts)

                # Save
        qb_dir = '../data/qb/'
        score_dir = '../data/score/'
        schedule_dir = '../data/schedule/'

        for i in ([qb_dir, score_dir,schedule_dir]):
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
    import pprint
    print('Displaying {question: ans}')

    qb = {str(i): random.randint(0, 4) for i in range(100)}
    pprint.pprint(qb)
    student_bank = {'1', '2', '4'}
    p = Platform('1', qb, student_bank, True)
    p.main()
    student_bank.add(str(random.randint(0, 100)))
    for i in range(100):
        p = Platform('1', qb, student_bank, False)
        p.ts = p.ts + (i+1) * 86400
        print('today is: ' + str(p.date))
        p.main()
        student_bank.add(str(random.randint(0, 100)))


