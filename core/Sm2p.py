

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

    return a * (max(1.3, 2.5 + sum(b + c * x_i + d * x_i * x_i for x_i in x))) ** (theta * num_consecutively_correct)