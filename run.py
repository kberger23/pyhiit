import time
from playsound import playsound

import tkinter as tk

interval = [1]*2
pause = 5

def sound_begin():
    playsound('sound/bell_short_1.mp3')

def sound_end():
    playsound('sound/bell_long_1.mp3')



class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self._timer = None

        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.start = tk.Button(self)
        self.start["text"] = "Start timer"
        self.start["command"] = self.countdown
        self.start.pack(side="top")

        self.current_timer = tk.Label(self)
        self.current_timer["text"] = 0
        self.current_timer.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom")

    def update_timer(self):

        label_refresh_time = 0.1
        self._timer -= label_refresh_time
        self.current_timer["text"] = f"{self._timer:.2f}s"
        if self._timer > label_refresh_time:
            self.after(int(label_refresh_time * 1000), self.update_timer)

    def adjust_time(self, total_time: float):

        self._timer = total_time
        print(f"total_time = {total_time}")
        self.update_timer()



    def countdown(self):

        self.adjust_time(pause)

        # for i, _int in enumerate(interval):
        #
        #     interval_counter = i + 1
        #     print(f"Starting interval {interval_counter}")
        #     sound_begin()
        #     time.sleep(_int)
        #     sound_end()
        #     print(f"Finished interval {interval_counter}")
        #     self.current_timer["text"] = self.current_timer["text"] + 1

root = tk.Tk()
app = Application(master=root)
app.mainloop()
exit(0)

for i, _int in enumerate(interval):
    time.sleep(pause)
    interval_counter = i + 1
    print(f"Starting interval {interval_counter}")
    sound_begin()
    time.sleep(_int)
    sound_end()
    print(f"Finished interval {interval_counter}")

print("Finished session")
sound_end()
