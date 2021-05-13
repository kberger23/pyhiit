import tkinter as tk
import tkinter.font as tkFont

import time
from playsound import playsound
from colour import Color

from timer.training import Training, Runner


def sound_begin():
    playsound('sound/bell_short_1_trimmed.mp3', False)


def sound_end():
    playsound('sound/bell_long_1_trimmed.mp3', False)


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master, borderwidth=20)

        self._current_time = 0
        self._current_session = -1
        self._pause = False
        self._train = None

        self.master = master
        self.pack()
        self.init_interval()
        self.create_widgets()

    def create_widgets(self):

        self.start = tk.Button(self, width=6, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.start["text"] = "Start"
        self.start["command"] = self.start_interval_cycle
        self.start.grid(row=2, column=0, columnspan=1, pady=4, padx=4)

        self.pause = tk.Button(self, width=6, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pause_command
        self.pause.grid(row=2, column=1, columnspan=1, pady=4, padx=4)

        self.exercise = tk.Label(self, width=18, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.set_exercise_label("Exercise")
        self.exercise.grid(row=0, column=0, columnspan=20,)

        self.current_timer = tk.Label(self, width=18, height=2, font=tkFont.Font(family="Lucida Grande", size=60))
        self.set_current_time_label()
        self.current_timer.grid(row=1, column=0, columnspan=20,)

        self.sessions_label = tk.Label(self, width=18, height=1, font=tkFont.Font(family="Lucida Grande", size=15))
        self.sessions_label["text"] = "Number of sessions"
        self.sessions_label.grid(row=3, column=0, columnspan=1, pady=4)

        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.sessions_entry_command(sv))
        self.sessions_entry = tk.Entry(self, width=18, textvariable=sv, font=tkFont.Font(family="Lucida Grande", size=15))
        self.sessions_entry.grid(row=3, column=1, columnspan=1, pady=4)

    def init_interval(self):

        self._pause = False
        self._train = Training([Training.PUSH_UPS, Training.WIDE_PUSH_UPS], 3)

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

    def sessions_entry_command(self, sv):
        print("session entry changed")
        print(sv.get())

    def set_exercise_label(self, exe: str):
        self.exercise["text"] = exe
        self.update()

    def set_current_time_label(self, color="white"):
        self.current_timer["text"] = f"[{self._current_session + 1}/{self._train.number_of_exercise_rounds}]{max(self._current_time, 0):5.2f}s"
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

    def _is_pause(self, identifier):
        return identifier == self._train.pause.identifier

    def _is_init(self, identifier):
        return identifier == self._train.init.identifier

    def _is_pause_or_init(self, identifier):
        return self._is_pause(identifier) or self._is_init(identifier)

    def interval_cycle(self):

        source_interval = self._train.interval

        for i, runner in enumerate(source_interval):
            if self._is_pause_or_init(runner.exercise.identifier):
                self.set_exercise_label(f"{runner.exercise.identifier}: {source_interval[i + 1].exercise.identifier} next")
            else:
                self.set_exercise_label(runner.exercise.identifier)

            self._current_session = runner.session
            self.adjust_time(runner.exercise.identifier, runner.remaining_duration, runner.exercise.round_duration)
            if self._current_time < 1E-6:
                if self._is_pause_or_init(runner.exercise.identifier):
                    sound_begin()
                else:
                    sound_end()
                time.sleep(0.2)
                del self._train.interval[0]
            else:
                self._train.interval[0] = Runner(runner.session, self._current_time, runner.exercise)
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

