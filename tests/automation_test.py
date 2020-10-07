import json
from app.automation import Automation, determinate, minimize


def general_test(id_: int, func):
    with open(f'tests/fa_{id_}.json', 'r') as input_file:
        fa = json.load(input_file, object_hook=lambda d: Automation(**d))
    with open(f'tests/dfa_ans_{id_}.json', 'r') as answer_file:
        assert func(fa) == json.load(answer_file, object_hook=lambda d: Automation(**d))


def test_determinate():
    general_test(1, determinate)


def test_minimize():
    general_test(3, minimize)


def test_determinate_then_minimize():
    def determinate_than_minimize(fa: Automation):
        return minimize(determinate(fa))
    general_test(2, determinate_than_minimize)
