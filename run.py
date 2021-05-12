import tkinter as tk
import tkinter.font as tkFont

import time
from playsound import playsound
from colour import Color
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
        _interval.append((-1, self.init.round_duration, self.init))
        for j, exer in enumerate(self.interval):
            if not j == 0:
                _interval.append((j, self.pause.round_duration, self.pause))
            _interval.append((j, exer.round_duration, exer))
        return _interval

    @property
    def init(self):
        return Exercise(self.INIT, self._data[self.INIT])

    @property
    def pause(self):
        return Exercise(self.PAUSE, self._data[self.PAUSE])


train = Training([Training.PUSH_UPS, Training.WIDE_PUSH_UPS], 3)


def sound_begin():
    playsound('sound/bell_short_1_trimmed.mp3', False)


def sound_end():
    playsound('sound/bell_long_1_trimmed.mp3', False)


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self._interval = []
        self._current_time = 0
        self._current_session = -1
        self._pause = False

        self.master = master
        self.pack()
        self.create_widgets()
        self.init_interval()

    def create_widgets(self):

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

        self.start = tk.Button(self, width=8, height=2, font=tkFont.Font(family="Lucida Grande", size=40))
        self.start["text"] = "Start"
        self.start["command"] = self.start_interval_cycle
        self.start.pack(in_=self.bottom_frame, side="left")

        self.pause = tk.Button(self, width=8, height=2, font=tkFont.Font(family="Lucida Grande", size=40))
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pause_command
        self.pause.pack(in_=self.bottom_frame, side="right")

        self.exercise = tk.Label(self, width=24, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.set_exercise_label("Exercise")
        self.exercise.pack(side="top")

        self.current_timer = tk.Label(self, width=18, height=2, font=tkFont.Font(family="Lucida Grande", size=60))
        self.set_current_time_label()
        self.current_timer.pack(side="top")

    def init_interval(self):

        self._pause = False
        self._interval = train.create_interval()

    def pause_command(self):
        self._pause = True
        self.pause["text"] = "Resume"
        self.pause["command"] = self.resume_command
        self.update()

    def resume_command(self):
        self._pause = False
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pause_command
        self.update()
        self.interval_cycle()

    def set_exercise_label(self, exe: str):
        self.exercise["text"] = exe
        self.update()

    def set_current_time_label(self, color="white"):
        self.current_timer["text"] = f"[{self._current_session + 1}/{len(train.interval)}]{max(self._current_time,0):5.2f}s"
        self.current_timer.config(bg=color)

    def adjust_time(self, phase: str, remaining_duration: float, total_time: float):

        label_refresh_time = 0.01

        if self._is_pause(phase):
            colors = list(Color("green").range_to(Color("red"), int(total_time / label_refresh_time) + 1))
        elif self._is_init(phase):
            colors = list(Color("white").range_to(Color("red"), int(total_time / label_refresh_time) + 1))
        else:
            colors = list(Color("red").range_to(Color("green"), int(total_time / label_refresh_time) + 1))

        self._current_time = remaining_duration
        self.set_current_time_label()
        i = 0
        while self._current_time > 1E-6 and not self._pause:
            time.sleep(label_refresh_time)
            self._current_time -= label_refresh_time
            self.set_current_time_label(color=colors[i])
            self.update()
            i += 1

    def start_interval_cycle(self):
        self.init_interval()
        self.interval_cycle()

    @staticmethod
    def _is_pause(identifier):
        return identifier == train.pause.identifier

    @staticmethod
    def _is_init(identifier):
        return identifier == train.init.identifier

    def _is_pause_or_init(self, identifier):
        return self._is_pause(identifier) or self._is_init(identifier)

    def interval_cycle(self):

        source_interval = self._interval.copy()

        for i, ( session, remaining_duration, _exercise) in enumerate(source_interval):
            if self._is_pause_or_init(_exercise.identifier):
                self.set_exercise_label(f"{_exercise.identifier}: {source_interval[i + 1][-1].identifier} next")
            else:
                self.set_exercise_label(_exercise.identifier)

            self._current_session = session
            self.adjust_time(_exercise.identifier, remaining_duration, _exercise.round_duration)
            if self._current_time < 1E-6:
                if self._is_pause_or_init(_exercise.identifier):
                    sound_begin()
                else:
                    sound_end()
                time.sleep(0.5)
                del self._interval[0]
            else:
                self._interval[0] = (session, self._current_time, _exercise)
            if self._pause:
                break

        if not self._pause:
            self.set_exercise_label("Done")
            self._current_time = 0
            sound_end()
        self.set_current_time_label()


root = tk.Tk()
root.attributes('-topmost', True)
app = Application(master=root)
app.mainloop()

