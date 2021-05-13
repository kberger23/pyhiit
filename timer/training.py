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
        self._remaining_duration = remaining_duration
        self.exercise = exercise

    @property
    def remaining_duration(self):
        return self._remaining_duration

    @remaining_duration.setter
    def remaining_duration(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(f"{value} has to be type float or int, but is {type(value)}")
        if value < 0:
            raise ValueError(f"{value} has to be greater equal zero.")
        self._remaining_duration = value


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
        self._interval = None

        with open(EXERCISE_JSON, "r+") as file:
            self._data = json.load(file)

    @property
    def _exercise_loop(self):
        return [Exercise(ex, self._data[ex]) for _ in range(self._number_of_round) for ex in self._exercises]

    @property
    def number_of_exercise_rounds(self):
        return len(self._exercise_loop)

    def _create_interval(self):

        self._interval = list()
        self._interval.append(Runner(-1, self.init.round_duration, self.init))
        for j, exer in enumerate(self._exercise_loop):
            if not j == 0:
                self._interval.append(Runner(j, self.pause.round_duration, self.pause))
            self._interval.append(Runner(j, exer.round_duration, exer))

    @property
    def interval(self):
        if self._interval is None:
            self._create_interval()
        return self._interval

    def reset_interval(self):
        self._create_interval()

    def deleteInterval(self, index):
        del self._interval[index]

    @property
    def init(self):
        return Exercise(self.INIT, self._data[self.INIT])

    @property
    def pause(self):
        return Exercise(self.PAUSE, self._data[self.PAUSE])

    def __getitem__(self, item):
        return self._interval[item]
