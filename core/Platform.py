import numpy as np
import psycopg2
from Student import Student
import random
from Scorer import Scorer
import pickle
import os
from datetime import datetime
import time
import json


class Platform:
    """
    Supports:
    Student individual question bank: Stores the questions that each student can practice on (has taught in class),
    which means that students can have different question banks from each other.

    Quiz question response evaluation: Using the student response answer and self-reported confidence 3 levels, gives a
    evaluation of the response of the question. (if correct: the higher the confident, the lower the evaluation and
    vice versa.) The program saves the evaluation history for each student/question combination.

    Automatic scheduling: Using the history of question response evaluation, Automatically calculates the next date that
    a question appears again for a student (SM2 algorithm).

    Automatic quiz generation: For each student, using the schedule, number of questions in the quiz, and the current date,
    automatically generate a quiz for the student. If the number of questions that are due is lower than the number of
    questions that is passed in, we add new (unseen) questions for the student. This is done by sampling new questions
    from that student's own question bank, excluding the questions already in the schedule.

    Question Mastery: If the student gets a question correct for 5 consecutive times, the question is considered mastered
    and will not appear again in the future.
    """

    def __init__(self, student_name, questions, question_bank, first_time=False):
        """
        :param questions: All questions available in this platform
        :param question_bank: Student individual question bank
        :param date: current date
        """
        self.student_name = student_name
        self.questions = questions
        self.question_bank = question_bank
        self.first_time = first_time
        self.student = Student(self.student_name, self.question_bank, first_time=self.first_time)
        self.num_questions = 20
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

    @staticmethod
    def create_database():
        connection = psycopg2.connect(user="postgres",
                                      password="star0731",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="sm2")
        cursor = connection.cursor()
        create_table_query = '''
        -- Table: public.student
        DROP TABLE IF EXISTS student; 
        -- DROP TABLE public.student;

        CREATE TABLE public.student
        (
            STUDENT_ID SERIAL PRIMARY KEY,
            STUDENT_NAME VARCHAR(50) UNIQUE NOT NULL,
            QUESTION_BANK TEXT,
            SCORE TEXT,
            SCHEDULE TEXT,
            MASTERED TEXT
        )

        WITH (
            OIDS = FALSE
        )
        TABLESPACE pg_default;

        ALTER TABLE public.student
            OWNER to postgres;
        '''
        cursor.execute(create_table_query)
        connection.commit()
        connection.close()

    def get_questions(self):
        """
        :return: question id in this quiz for this student
        """
        # get the questions that are due today
        questions = []
        for key, value in self.student.schedule.items():
            if self.date == value and key not in self.student.mastered:
                questions.append(key)
        reviews = questions
        print('Reviews: {}'.format(reviews))
        # get the additional number of questions if the questions due today is not enough
        num_new_question = self.num_questions - len(questions)

        # randomly sample additional questions from the available question pool of the student that
        # are not in the schedule AND are yet mastered
        if num_new_question > 0:
            _pool = [i for i in self.student.question_bank if i not in set(questions)
                     and i not in self.student.schedule.keys() and i not in self.student.mastered]
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
            # for manual input ans
            # ans = input('Answer Question ' + str(i) + ': ')
            # conf = input('Pick a self reported confidence score ranging [0, 2]: ')

            # to use answer_question method from Student class
            ans = self.student.answer_question(self.questions[i])
            print('Answer Question ' + str(i) + ': ' + str(ans))
            # randomly pick a confidence score for experimentation purposes
            conf = random.randint(0, 2)
            print('Pick a self reported confidence score ranging [0, 2]: ' + str(conf))

            # calculate the score using Scorder class
            s = Scorer(i, self.questions[i], ans, conf)
            evaluation = s.calculate_confidence()
            score = s.calculate_score()
            temp[i] = evaluation
            total_score.append(score)

        dict, student_score, schedule = self.update_student_history(new_evaluation=temp, new_score=np.mean(total_score))
        print('for student' + str(self.student_name) + '\n'
              + 'Student Score:' + str(student_score))

        # update student question_bank and mastered questions
        self.student.question_bank = dict
        self.student.update_mastered()

        # print for visualization
        self.print_evaluation(dict)
        self.print_schedule(schedule)

        # Save
        connection = psycopg2.connect(user="postgres",
                                      password="star0731",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="sm2")
        cursor = connection.cursor()

        str_dict, str_score, str_schedule, str_mastered = \
            json.dumps(dict), json.dumps(self.student.score), json.dumps(schedule), json.dumps(list(self.student.mastered))

        insert_table_query = f'''
        INSERT INTO PUBLIC.STUDENT (STUDENT_NAME, QUESTION_BANK, SCORE, SCHEDULE, MASTERED)
        VALUES
        ('{self.student.student_name}','{str_dict}', '{str_score}', '{str_schedule}', '{str_mastered}')
        ON CONFLICT (STUDENT_NAME) DO UPDATE SET 
        QUESTION_BANK = '{str_dict}',
        SCORE = '{str_score}',
        SCHEDULE = '{str_schedule}',
        MASTERED = '{str_mastered}';
        '''
        cursor.execute(insert_table_query)
        connection.commit()
        connection.close()
        return temp, np.mean(total_score)

    @staticmethod
    def print_evaluation(d):
        print('Evaluation history for this student')
        for key, value in d.items():
            print('Question ID ' + str(key))
            print(*value)

    @staticmethod
    def print_schedule(d):
        print('Schedule for this student')
        for key, value in d.items():
            print('Question ID ' + str(key) + ' date ' + str(value))

    def update_student_history(self, new_evaluation, new_score):
        # add today's data to history
        dict = self.student.question_bank
        for i in new_evaluation.keys():
            dict[i].append(new_evaluation[i])
        # add score
        self.student.score.append(new_score)
        schedule = self.student.schedule
        for i in dict.keys():
            # if history not empty AND asked today AND yet to be mastered
            if dict[i] and i in new_evaluation.keys() and i not in self.student.mastered:
                interval = self.sm2(dict[i])
                ts = self.days_to_ts(interval) + self.ts
                schedule[i] = self.ts_to_date(ts)

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
        print(self.student.mastered)


if __name__ == '__main__':
    import pprint
    import random
    print('Displaying {question: ans}')

    qb = {str(i): random.randint(0, 1) for i in range(1000)}
    # pprint.pprint(qb)
    student_bank = {'1', '2', '4'}
    p = Platform('SIDA', qb, student_bank, True)
    p.create_database()
    p.main()
    student_bank.add(str(random.randint(0, 999)))
    for i in range(10):
        print('----------------------------------------NewDay---------------------------------------------')

        p = Platform('SIDA', qb, student_bank, False)
        p.ts = p.ts + (i+1) * 86400
        print('Today is: ' + str(p.date))
        p.main()

        rnd = random.randint(0, 100)
        if rnd > 70:
            student_bank.add(str(random.randint(0, 999)))
    print(p.student.question_bank)

