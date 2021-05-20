import json
from datetime import datetime
from types import SimpleNamespace

from timer.const import EXERCISE_JSON, DEBUG, DEBUG_INTERVAL_TIME, EXERCISE_HISTORY_JSON

global training


def set_training():
    global training
    training = _Training()


def get_training():
    return training


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

    def __init__(self, session_index: int, remaining_duration: float, exercise: Exercise, round_index: int):
        self.session = session_index
        self._remaining_duration = remaining_duration
        self.exercise = exercise
        self.round_index = round_index

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


class _Training:

    PAUSE = "Pause"
    INIT = "Init"

    DATE_FORMAT = "%d.%m.%Y %H:%M"

    def __init__(self, exercises: list = None, number_of_round: int = 3):
        self._number_of_round = number_of_round
        self._interval = None

        with open(EXERCISE_JSON, "r+") as file:
            self._data = json.load(file)

        if exercises is None:
            exercises = list(self.history.as_list[-1]["exercises"].keys())
        self._exercises = [Exercise(ex, self._data[ex]) for ex in exercises]
        self._init = Exercise(self.INIT, self._data[self.INIT])
        self._pause = Exercise(self.PAUSE, self._data[self.PAUSE])

    @property
    def _data_only_exercises(self):
        exercises = self._data.copy()
        exercises.pop(self.INIT, None)
        exercises.pop(self.PAUSE, None)
        return exercises

    @property
    def available_exercises(self):
        return list(self._data_only_exercises.keys())

    @property
    def exercises_identifier(self):
        ex = SimpleNamespace()
        for key in self._data_only_exercises.keys():
            ex.__dict__[key.replace(" ", "_")] = key
        return ex

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

    def add_exercise(self, exercise):
        self.set_exercise(exercise, len(self._exercises))

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

    def remove_exercise(self, index):
        del self._exercises[index]
        if self._interval is not None:
            self.reset_interval()

    def remove_last_exercise(self):
        self.remove_exercise(-1)

    @property
    def _exercise_loop(self):
        return [ex for _ in range(self._number_of_round) for ex in self._exercises]

    @property
    def number_of_exercise_rounds(self):
        return len(self._exercise_loop)

    def _create_interval(self):

        self._interval = list()
        self._interval.append(Runner(-1, self.init.round_duration, self.init, -1))
        for j, exer in enumerate(self._exercise_loop):
            round_index = int(j / len(self._exercises))
            self._interval.append(Runner(j, exer.round_duration, exer, round_index))
            if not j == len(self._exercise_loop) - 1:
                self._interval.append(Runner(j, self.pause.round_duration, self.pause, round_index))

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

    @property
    def history(self):
        return TrainingHistory()

    def create_history_dict(self):

        history_dict = dict()
        dt_string = datetime.now().strftime(self.DATE_FORMAT)
        history_dict["date"] = dt_string
        history_dict["rounds"] = self.number_of_rounds
        history_dict["exercises"] = dict()
        for ex in self._exercises:
            history_dict["exercises"][ex.identifier] = ex.round_duration
        return history_dict

    def save_training(self):
        self.history.save(self.create_history_dict())

    def __getitem__(self, item):
        return self._interval[item]


class TrainingHistory:

    def __init__(self):
        pass

    @staticmethod
    def read():
        if EXERCISE_HISTORY_JSON.is_file():
            with open(EXERCISE_HISTORY_JSON, "r") as file:
                histories = json.load(file)
            return histories
        else:
            return []

    @property
    def as_list(self):
        return self.read()

    def save(self, history_dict):
        histories = self.as_list
        histories.append(history_dict)
        with open(EXERCISE_HISTORY_JSON, "w") as file:
            json.dump(histories, file, indent=4)

    def maximal_number_of_exercises(self, number_of_entries=8):

        largest_number_of_exercises = 0
        for entry in reversed(self.as_list[-number_of_entries:]):
            largest_number_of_exercises = max(largest_number_of_exercises, len(entry["exercises"]))
        return largest_number_of_exercises