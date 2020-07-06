import matplotlib.pyplot as plt
import psycopg2
import json
import math

def plot_interval(question_id, student_id):
    connection = psycopg2.connect(user="postgres",
                                  password="star0731",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="sm2")
    cursor = connection.cursor()

    query = \
        f"SELECT INTERVALS, QUESTION_BANK, STUDENT_NAME FROM PUBLIC.STUDENT WHERE STUDENT_ID = {student_id}"
    cursor.execute(query)
    row = cursor.fetchone()
    connection.close()
    interval = row[0]
    evaluation = row[1]
    student_name = row[2]
    interval = load(interval, question_id)
    evaluation = load(evaluation, question_id)

    fig, ax1 = plt.subplots()
    t = range(len(interval))
    color = 'tab:red'
    ax1.set_xlabel('No. Occurrence')
    ax1.set_ylabel('Interval in days', color=color)
    ax1.scatter(t, interval, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Evaluation History', color=color)  # we already handled the x-label with ax1
    ax2.plot(t, evaluation, color=color, linestyle='--', marker='o')
    ax2.tick_params(axis='y', labelcolor=color)
    # fig.tight_layout()  # otherwise the right y-label is slightly clipped

    # xint = range(0, math.ceil(len(interval)) + 1)
    # plt.xticks(xint)
    plt.title(f'Student: {student_name}')
    plt.savefig(f'../data/test/{student_id}/{question_id}.png')
    plt.close()


def load(string, question_id):
    m = json.loads(string)
    m = m[question_id]
    m = [float(i) for i in m]
    return m


def main(student_id):
    connection = psycopg2.connect(user="postgres",
                                  password="star0731",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="sm2")
    cursor = connection.cursor()

    query = \
        f"SELECT QUESTION_BANK FROM PUBLIC.STUDENT WHERE STUDENT_ID = {student_id}"
    cursor.execute(query)
    row = cursor.fetchone()
    connection.close()
    QB = row[0]
    QB = json.loads(QB)
    questions = QB.keys()
    for i in questions:
        plot_interval(question_id=i, student_id=student_id)


if __name__ == '__main__':
    main(102)
    main(1)