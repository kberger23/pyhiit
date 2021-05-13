import json
from datetime import datetime

from timer.const import EXERCISE_JSON, DEBUG, DEBUG_INTERVAL_TIME, EXERCISE_HISTORY_JSON


class Exercise:

    def __init__(self, name, exercise_dict):
        self._dict = exercise_dict
        self._name = name
        self._updated = False

    @property
    def identifier(self):
        return self._name

    @property
    def round_duration(self):
        return self._dict["duration"] if not DEBUG or self._updated else DEBUG_INTERVAL_TIME

    @round_duration.setter
    def round_duration(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(f"{value} has to be type float or int, but is {type(value)}")
        if value < 0:
            raise ValueError(f"{value} has to be greater equal zero.")
        self._dict["duration"] = value
        print(f"New duration is {self._dict['duration']}")
        self._updated = True

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

    AVAILABLE_EXERCISES = [WIDE_PULL_UPS, BACK_ROWS, WIDE_PUSH_UPS, PUSH_UPS]

    def __init__(self, exercises: list, number_of_round: int = 3):
        self._number_of_round = number_of_round
        self._interval = None

        with open(EXERCISE_JSON, "r+") as file:
            self._data = json.load(file)

        self._exercises = [Exercise(ex, self._data[ex]) for ex in exercises]
        self._init = Exercise(self.INIT, self._data[self.INIT])
        self._pause = Exercise(self.PAUSE, self._data[self.PAUSE])

    @property
    def number_of_rounds(self):
        return self._number_of_round

    @number_of_rounds.setter
    def number_of_rounds(self, value):
        if not isinstance(value, int):
            raise TypeError("Integer are required")
        self._number_of_round = value
        if self._interval is not None:
            self.reset_interval()

    @property
    def exercises(self):
        return self._exercises

    def set_exercise(self, value, index):
        if not isinstance(value, str):
            raise TypeError("String are required")

        exercise = Exercise(value, self._data[value])
        # Todo check for validity
        if index < len(self._exercises):
            self._exercises[index] = exercise
        elif index == len(self._exercises):
            self._exercises.append(exercise)
        else:
            raise KeyError(f"{index} is not valid for array of size {len(self._exercises)}")
        if self._interval is not None:
            self.reset_interval()

    def remove_last_exercise(self):
        del self._exercises[-1]
        if self._interval is not None:
            self.reset_interval()

    @property
    def _exercise_loop(self):
        return [ex for _ in range(self._number_of_round) for ex in self._exercises]

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
        return self._init

    @property
    def pause(self):
        return self._pause

    def create_history_dict(self):

        history_dict = dict()
        dt_string = datetime.now().strftime("%d.%m.%Y %H:%M")
        history_dict["date"] = dt_string
        history_dict["rounds"] = self.number_of_rounds
        history_dict["exercises"] = dict()
        for ex in self._exercises:
            history_dict["exercises"][ex.identifier] = ex.round_duration
        return history_dict

    def save(self):
        histories = self.read_history()
        histories.append(self.create_history_dict())
        with open(EXERCISE_HISTORY_JSON, "w") as file:
            json.dump(histories, file, indent=4)

    @staticmethod
    def read_history():
        if EXERCISE_HISTORY_JSON.is_file():
            with open(EXERCISE_HISTORY_JSON, "r") as file:
                histories = json.load(file)
            return histories
        else:
            return []

    def get_maximal_number_of_exercises_in_history(self):

        largest_number_of_exercises = 0
        for entry in self.read_history():
            largest_number_of_exercises = max(largest_number_of_exercises, len(entry["exercises"]))
        return largest_number_of_exercises

    def __getitem__(self, item):
        return self._interval[item]

