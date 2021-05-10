import time
import numpy as np

from playsound import playsound

import tkinter as tk
import tkinter.font as tkFont

from colour import Color


interval = [5]*2
pause = 2


def sound_begin():
    playsound('sound/bell_short_1.mp3')


def sound_end():
    playsound('sound/bell_long_1.mp3')


class Application(tk.Frame):

    PAUSE = "Pause"
    RUN = "Run"

    def __init__(self, master=None):
        super().__init__(master)

        self._current_time = 0
        self._current_phase = "Init"

        self.master = master
        self.pack()
        self.create_widgets()
        self.create_interval_shit()


    def create_widgets(self):
        self.start = tk.Button(self, width=8, height=2, font=tkFont.Font(family="Lucida Grande", size=20))
        self.start["text"] = "Start timer"
        self.start["command"] = self.interval_cycle
        self.start.pack(side="bottom")

        self.current_timer = tk.Label(self, width=14, height=3, font=tkFont.Font(family="Lucida Grande", size=20))
        self.set_current_time_label()
        self.current_timer.pack(side="top")

        #self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        #self.quit.pack(side="bottom")

    def create_interval_shit(self):
        self._interval = []
        for j, inter in enumerate(interval):
            self._interval.append((self.PAUSE, pause))
            self._interval.append((self.RUN, inter))

    def set_current_time_label(self, color="white"):
        self.current_timer["text"] = f"{self._current_phase:10}{max(self._current_time,0):5.2f}s"
        self.current_timer.config(bg=color)

    def adjust_time(self, phase: str, total_time: float):

        label_refresh_time = 0.01

        if phase == self.PAUSE:
            colors = list(Color("green").range_to(Color("red"), int(total_time / label_refresh_time) + 1))
        elif phase == self.RUN:
            colors = list(Color("red").range_to(Color("green"), int(total_time / label_refresh_time) + 1))
        else:
            KeyError(f"phase {phase} not known.")

        self._current_phase = phase
        self._current_time = total_time
        self.set_current_time_label()
        i = 0
        while self._current_time > -label_refresh_time / 2:
            time.sleep(label_refresh_time)
            self._current_time -= label_refresh_time
            self.set_current_time_label(color=colors[i])
            self.update()
            i += 1

    def interval_cycle(self):

        copy_interval = self._interval.copy()

        for phase, duration in copy_interval:
            self.adjust_time(phase, duration)
            del self._interval[0]

        self._current_phase = "Done"
        self._current_time = 0
        self.set_current_time_label()

root = tk.Tk()
root.attributes('-topmost', True)
app = Application(master=root)
app.mainloop()

