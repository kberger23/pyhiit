import json

from timer.const import EXERCISE_JSON, DEBUG, DEBUG_INTERVAL_TIME


class Exercise:

    def __init__(self, name, exercise_dict):
        self._dict = exercise_dict
        self._name = name

    @property
    def identifier(self):
        return self._name

    @property
    def round_duration(self):
        return self._dict["duration"] if not DEBUG else DEBUG_INTERVAL_TIME


class Runner:

    def __init__(self, session_index: int, remaining_duration: float, exercise: Exercise):
        self.session = session_index
        self.remaining_duration = remaining_duration
        self.exercise = exercise


class Training:

    PAUSE = "Pause"
    INIT = "Init"

    WIDE_PULL_UPS = "Wide pull-ups"
    BACK_ROWS = "Back rows"

    WIDE_PUSH_UPS = "Wide push-ups"
    PUSH_UPS = "Push-ups"

    def __init__(self, exercises: list, number_of_round: int):
        self._exercises = exercises
        self._number_of_round = number_of_round

        with open(EXERCISE_JSON, "r+") as file:
            self._data = json.load(file)

    @property
    def interval(self):
        return [Exercise(ex, self._data[ex]) for _ in range(self._number_of_round) for ex in self._exercises]

    def create_interval(self):

        _interval = list()
        _interval.append(Runner(-1, self.init.round_duration, self.init))
        for j, exer in enumerate(self.interval):
            if not j == 0:
                _interval.append(Runner(j, self.pause.round_duration, self.pause))
            _interval.append(Runner(j, exer.round_duration, exer))
        return _interval

    @property
    def init(self):
        return Exercise(self.INIT, self._data[self.INIT])

    @property
    def pause(self):
        return Exercise(self.PAUSE, self._data[self.PAUSE])