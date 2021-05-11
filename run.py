import tkinter as tk
import tkinter.font as tkFont

import time
from playsound import playsound
from colour import Color

from timer import exercise

init = 1
pause = 2


class Training:

    def __init__(self, exercises: list, number_of_round: int):
        self._exercises = exercises
        self._number_of_round = number_of_round

    @property
    def interval(self):
        return [ex() for ex in self._exercises for _ in range(self._number_of_round)]


train = Training([exercise.PullUps, exercise.PullUpsWide], 3)


def sound_begin():
    playsound('sound/bell_short_1_trimmed.mp3', False)


def sound_end():
    playsound('sound/bell_long_1_trimmed.mp3', False)


class Application(tk.Frame):

    READY = "Start in"
    PAUSE = "Pause"
    RUN = "Run"

    def __init__(self, master=None):
        super().__init__(master)

        self._interval = []
        self._current_time = 0
        self._current_phase = ""
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

        self.current_timer = tk.Label(self, width=18, height=2, font=tkFont.Font(family="Lucida Grande", size=60))
        self.set_current_time_label()
        self.current_timer.pack(side="top")

        #self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        #self.quit.pack(side="bottom")

    def init_interval(self):

        self._pause = False
        self._interval = []

        self._interval.append((self.READY, -1, init, init))
        for j, exercise in enumerate(train.interval):
            if not j == 0:
                self._interval.append((self.PAUSE, j, pause, pause))
            self._interval.append((self.RUN, j, exercise.round_duration, exercise.round_duration))

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

    def set_current_time_label(self, color="white"):
        self.current_timer["text"] = f"[{self._current_session + 1}/{len(train.interval)}]{self._current_phase:10}{max(self._current_time,0):5.2f}s"
        self.current_timer.config(bg=color)

    def adjust_time(self, phase: str, remaining_duration: float, total_time: float):

        label_refresh_time = 0.01

        if phase == self.PAUSE:
            colors = list(Color("green").range_to(Color("red"), int(total_time / label_refresh_time) + 1))
        elif phase == self.RUN:
            colors = list(Color("red").range_to(Color("green"), int(total_time / label_refresh_time) + 1))
        elif phase == self.READY:
            colors = list(Color("white").range_to(Color("green"), int(total_time / label_refresh_time) + 1))
        else:
            raise KeyError(f"phase {phase} not known.")

        self._current_phase = phase
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

    def interval_cycle(self):

        copy_interval = self._interval.copy()

        for phase, session, remaining_duration, total_duration in copy_interval:
            self._current_session = session
            self.adjust_time(phase, remaining_duration, total_duration)
            if self._current_time < 1E-6:
                del self._interval[0]
                if phase == self.RUN:
                    sound_end()
                if phase == self.PAUSE or phase == self.READY:
                    sound_begin()
                time.sleep(0.5)
            else:
                self._interval[0] = (phase, session, self._current_time, total_duration)
            if self._pause:
                break

        if not self._pause:
            self._current_phase = ""
            self._current_time = 0
            sound_end()
        self.set_current_time_label()


root = tk.Tk()
root.attributes('-topmost', True)
app = Application(master=root)
app.mainloop()

