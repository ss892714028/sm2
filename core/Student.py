import numpy as np
from Sm2p import sm2
import pickle


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
        else:
            self.question_bank = question_bank
            self.question_bank, self.score, self.schedule = self.load()

    @property
    def average_score(self):
        return np.array(self.score).mean()

    @staticmethod
    def number_of_days(history):
        return sm2(history)

    @staticmethod
    def initialize(question_bank):
        qb = {}
        for i in question_bank:
            qb[i] = []

        schedule = {}
        for i in question_bank:
            schedule[i] = None
        return qb, schedule

    def load(self):

        qb_dir = '../data/qb/'+str(self.student_name)+'.p'
        score_dir = '../data/score/'+str(self.student_name)+'.p'
        schedule_dir = '../data/schedule/'+str(self.student_name)+'.p'
        with open(qb_dir, 'rb') as fp:
            qb = pickle.load(fp)

        for i in self.question_bank:
            if i not in qb.keys():
                qb[i] = []

        with open(score_dir, 'rb') as c:
            score = pickle.load(c)

        with open(schedule_dir, 'rb') as c:
            schedule = pickle.load(c)

        return qb, score, schedule

