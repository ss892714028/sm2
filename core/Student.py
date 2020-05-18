import json
import numpy as np
from Sm2p import sm2
import matplotlib.pyplot as plt
import psycopg2
import random


class Student:
    def __init__(self, student_name, question_bank, first_time=False):
        """
        :param question_bank: Questions that the student is available to practice on.
        :param confident: track the self reported confidence score for each question.
        :param score: a list that contains all score of that student
        """
        self.student_name = student_name
        if first_time:
            self.question_bank, self.schedule = self.initialize(question_bank)
            self.score = []
            self.mastered = set()
        else:
            self.question_bank = question_bank
            self.student_id, self.student_name, self.question_bank, \
                self.score, self.schedule, self.mastered = self.load()

    @property
    def average_score(self):
        return np.array(self.score).mean()

    def update_mastered(self):
        for key, value in self.question_bank.items():
            if len(value) >= 5:
                if np.array([i > 2 for i in value[-5:]]).all():
                    self.mastered.add(key)

    @staticmethod
    def number_of_days(history):
        return sm2(history)

    @staticmethod
    def initialize(question_bank):
        qb = {}
        for i in question_bank:
            qb[i] = []

        schedule = {}

        return qb, schedule

    def load(self):
        connection = psycopg2.connect(user="postgres",
                                      password="star0731",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="sm2")
        cursor = connection.cursor()
        cursor.execute("SELECT STUDENT_ID, STUDENT_NAME, QUESTION_BANK, SCORE, SCHEDULE, MASTERED FROM PUBLIC.STUDENT "
                       f"WHERE STUDENT.STUDENT_name='{self.student_name}'")
        row = cursor.fetchone()
        student_id, student_name, qb, score, schedule, mastered = row[0], row[1], row[2], row[3], row[4], row[5]
        connection.close()
        qb, score, schedule, mastered = json.loads(qb), json.loads(score), json.loads(schedule), set(json.loads(mastered))
        for i in self.question_bank:
            if i not in qb.keys():
                qb[i] = []
        return student_id, student_name, qb, score, schedule, mastered

    @staticmethod
    def answer_question(ans):
        rnd = random.randint(0, 100)
        wrong_ans = np.array([i for i in range(4) if i != ans])
        if rnd > 90:
            return random.choice(wrong_ans)
        else:
            return ans

    def plot_score(self):
        p = plt.plot(self.score)
        p.show()