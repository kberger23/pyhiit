import time
from playsound import playsound

import tkinter as tk

interval = [12]*2
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

        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.start = tk.Button(self)
        self.start["text"] = "Start timer"
        self.start["command"] = self.interval_cycle
        self.start.pack(side="top")

        self.current_timer = tk.Label(self)
        self.set_current_time_label("Init", 0)
        self.current_timer.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom")

    def set_current_time_label(self, phase, time_number):
        self.current_timer["text"] = f"{phase:10}{max(time_number,0):5.2f}s"

    def adjust_time(self, phase: str, total_time: float):

        label_refresh_time = 0.1
        self.set_current_time_label(phase, total_time)
        t = total_time
        while t > -label_refresh_time / 2:
            time.sleep(label_refresh_time)
            t -= label_refresh_time
            self.set_current_time_label(phase, t)
            self.update()

    def interval_cycle(self):

        for j, inter in enumerate(interval):
            self.adjust_time(self.PAUSE, pause)
            #sound_begin()
            self.adjust_time(self.RUN, inter)
            #sound_end()

root = tk.Tk()
app = Application(master=root)
app.mainloop()

