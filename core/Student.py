import json
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import random


class Student:
    def __init__(self, student_name, question_bank, accuracy, laziness=10, first_time=False):
        """
        :param question_bank: Questions that the student is available to practice on.
        :param confident: track the self reported confidence score for each question.
        :param score: a list that contains all score of that student
        """
        self.student_name = student_name
        self.accuracy = accuracy
        self.laziness = laziness
        if first_time:
            self.question_bank, self.schedule, self.intervals, self.easiness = self.initialize(question_bank)
            self.score = []
            self.mastered = set()
        else:
            self.question_bank = question_bank
            self.student_id, self.student_name, self.question_bank, \
                self.score, self.schedule, self.mastered, self.intervals, self.easiness = self.load()

    @property
    def average_score(self):
        return np.array(self.score).mean()

    @property
    def average_score_attempted(self):
        return np.array([i for i in self.score if str(i) != 'nan']).mean()

    def update_mastered(self):
        for key, value in self.question_bank.items():
            if len(value) >= 5:
                if np.array([i > 2 for i in value[-5:]]).all():
                    self.mastered.add(key)

    @staticmethod
    def initialize(question_bank):
        qb = {}
        for i in question_bank:
            qb[i] = []
        schedule = {}
        intervals = {}
        easiness = {}
        for i in question_bank:
            intervals[i] = []
            easiness[i] = 2.5
        return qb, schedule, intervals, easiness

    def load(self):
        connection = psycopg2.connect(user="postgres",
                                      password="star0731",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="sm2")
        cursor = connection.cursor()
        cursor.execute("SELECT STUDENT_ID, STUDENT_NAME, QUESTION_BANK, SCORE, "
                       "SCHEDULE, MASTERED, INTERVALS, EASINESS FROM PUBLIC.STUDENT "
                       f"WHERE STUDENT.STUDENT_name='{self.student_name}'")
        row = cursor.fetchone()
        student_id, student_name, evaluations, score, schedule, mastered, intervals, easiness = \
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
        connection.close()
        evaluations, score, schedule, mastered, intervals, easiness =\
            json.loads(evaluations), json.loads(score), json.loads(schedule), set(json.loads(mastered)),\
            json.loads(intervals), json.loads(easiness)

        evaluations = self.update(self.question_bank, evaluations)
        intervals = self.update(self.question_bank, intervals)
        print(easiness)
        easiness = self.update(self.question_bank, easiness, easiness=True)
        return student_id, student_name, evaluations, score, schedule, mastered, intervals, easiness

    @staticmethod
    def update(qb, new, easiness=False):
        """
        Because the student may learn new knowledges and eligible to practice on more questions,
        we need to update the keys (question ids) for evaluation and interval event tracking.
        :param qb:
        :param new:
        :param easiness
        :return:
        """
        for i in qb:
            if i not in new.keys():
                if easiness:
                    new[i] = 2.5
                else:
                    new[i] = []
        return new

    def answer_question(self, ans):
        rnd = random.randint(0, 100)
        wrong_ans = np.array([i for i in range(4) if i != ans])
        # there is a chance that the student does not submit an answer, in this case, we return nan
        if rnd < self.laziness:
            return np.nan
        if rnd > self.accuracy:
            return random.choice(wrong_ans)
        else:
            return ans

    def plot_score(self):
        p = plt.plot(self.score)
        p.show()
