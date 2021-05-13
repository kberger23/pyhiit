import tkinter as tk
import tkinter.font as tkFont

import time
from playsound import playsound
from colour import Color

from timer.training import Training


def sound_begin():
    playsound('sound/bell_short_1_trimmed.mp3', False)


def sound_end():
    playsound('sound/bell_long_1_trimmed.mp3', False)


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master, borderwidth=20)

        self._current_time = 0
        self._current_session = -1
        self._clicked_start = False
        self._pause = False
        self._train = Training([Training.PUSH_UPS, Training.WIDE_PUSH_UPS])

        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):

        self.start = tk.Button(self, width=6, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.start["text"] = "Start"
        self.start["command"] = self.start_interval_cycle
        self.start.grid(row=2, column=0, columnspan=1, pady=4, padx=4, sticky="W")

        self.pause = tk.Button(self, width=6, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pause_command
        self.pause.config(width=6)
        self.pause.grid(row=2, column=1, columnspan=1, pady=4, padx=4, sticky="W")

        self.reset = tk.Button(self, width=6, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.reset["text"] = "Reset"
        self.reset["command"] = self.reset_command
        self.reset.grid(row=2, column=3, columnspan=1, pady=4, padx=4, sticky="W")

        self.exercise = tk.Label(self, width=24, height=1, font=tkFont.Font(family="Lucida Grande", size=40))
        self.set_exercise_label("Exercise")
        self.exercise.grid(row=0, column=0, columnspan=20,)

        self.current_timer = tk.Label(self, width=18, height=2, font=tkFont.Font(family="Lucida Grande", size=60))
        self.set_current_time_label()
        self.current_timer.grid(row=1, column=0, columnspan=20)

        self.sessions_label = tk.Label(self, width=18, height=1, font=tkFont.Font(family="Lucida Grande", size=15))
        self.sessions_label["text"] = "Number of sessions"
        self.sessions_label.config(anchor="w")
        self.sessions_label.grid(row=3, column=0, columnspan=1, pady=4, sticky="W")

        sv = tk.StringVar(value=self._train.number_of_rounds)
        sv.trace("w", lambda name, index, mode, sv=sv: self.sessions_entry_command(sv))
        self.sessions_entry = tk.Entry(self, width=4, textvariable=sv, font=tkFont.Font(family="Lucida Grande", size=15))
        self.sessions_entry.grid(row=3, column=1, columnspan=1, pady=4, sticky="W")

        self._exercise_dropdowns = []
        self._exercise_durations = []
        self._new_exercise = None
        for i, exercise in enumerate(self._train.exercises):
            self.create_drop_down_exercise(i, exercise.identifier)

        init_exercise_label = tk.Label(self, width=9, height=1, font=tkFont.Font(family="Lucida Grande", size=15))
        init_exercise_label["text"] = "Init"
        init_exercise_label.config(anchor="e")
        init_exercise_label.grid(row=3, column=2, columnspan=1, pady=4, sticky="W")

        sv = tk.StringVar(value=self._train.init.round_duration)
        sv.trace("w", lambda name, index, mode, sv=sv: self.set_duration_of_exercise(sv, self._train.init))
        self.init_exercise_entry = tk.Entry(self, width=4, textvariable=sv, font=tkFont.Font(family="Lucida Grande", size=15))
        self.init_exercise_entry.grid(row=3, column=3, columnspan=1, pady=4, sticky="W")

        pause_exercise_label = tk.Label(self, width=9, height=1, font=tkFont.Font(family="Lucida Grande", size=15))
        pause_exercise_label["text"] = "Pause"
        pause_exercise_label.config(anchor="e")
        pause_exercise_label.grid(row=4, column=2, columnspan=1, pady=4, sticky="W")

        sv = tk.StringVar(value=self._train.pause.round_duration)
        sv.trace("w", lambda name, index, mode, sv=sv: self.set_duration_of_exercise(sv, self._train.pause))
        self.pause_exercise_entry = tk.Entry(self, width=4, textvariable=sv, font=tkFont.Font(family="Lucida Grande", size=15))
        self.pause_exercise_entry.grid(row=4, column=3, columnspan=1, pady=4, sticky="W")

    def create_drop_down_exercise(self, index, default):

        self.choose_exercise(default, index)
        exercises_string_var = tk.StringVar(value=default)
        self._exercise_dropdowns.append(tk.OptionMenu(self, exercises_string_var, *self._train.AVAILABLE_EXERCISES, command=lambda x: self.choose_exercise(x, index)))
        self._exercise_dropdowns[-1].config(width=24, height=1, anchor="w", font=tkFont.Font(family="Lucida Grande", size=15))
        row = 3 + len(self._exercise_dropdowns)
        self._exercise_dropdowns[-1].grid(row=row, column=0, columnspan=1, pady=4, sticky="W")

        sv = tk.StringVar(value=self._train.exercises[len(self._exercise_dropdowns) - 1].round_duration)
        sv.trace("w", lambda _name, _index, _mode, _sv=sv: self.set_duration_of_exercise_in_list(_sv, index))
        self._exercise_durations.append(tk.Entry(self, width=4, textvariable=sv, font=tkFont.Font(family="Lucida Grande", size=15)))
        self._exercise_durations[-1].grid(row=row, column=1, columnspan=1, pady=4, sticky="W")

        if self._new_exercise:
            self._new_exercise.destroy()
            self._remove_exercise.destroy()
        self._new_exercise = tk.Button(self, text='+', command=lambda: self.create_drop_down_exercise(len(self._exercise_dropdowns), self._train.AVAILABLE_EXERCISES[-1]), bg="gainsboro", bd=1, padx=6, pady=2, font=tkFont.Font(family="Lucida Grande", size=15))
        self._new_exercise.config(width=2)
        self._new_exercise.grid(row=3 + len(self._exercise_dropdowns) + 1, column=0, sticky="W")

        self._remove_exercise = tk.Button(self, text='-', command=self.remove_drop_down_exercise, bg="gainsboro", bd=1, padx=6, pady=2, font=tkFont.Font(family="Lucida Grande", size=15))
        self._remove_exercise.config(width=2)
        self._remove_exercise.grid(row=3 + len(self._exercise_dropdowns) + 1, column=0, sticky="W", padx=60)

    def remove_drop_down_exercise(self):
        self._train.remove_last_exercise()
        self.update()
        self.set_current_time_label()
        self._exercise_dropdowns[-1].destroy()
        del self._exercise_dropdowns[-1]

        self._exercise_durations[-1].destroy()
        del self._exercise_durations[-1]

    def set_duration_of_exercise_in_list(self, sv, _index):
        self.set_duration_of_exercise(sv, self._train.exercises[_index])

    def set_duration_of_exercise(self, sv, exercise):
        try:
            exercise.round_duration = float(sv.get())
        except ValueError:
            pass
        self.update()
        self.set_current_time_label()

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
        if self._clicked_start:
            self.interval_cycle()

    def reset_command(self):
        self._clicked_start = False
        self._set_session_choosable(state="normal")
        self._train.reset_interval()
        self._current_time = 0
        self.set_current_time_label()
        self.resume_command()

    def sessions_entry_command(self, sv):

        if not self._clicked_start:
            number_of_rounds = sv.get()
            try:
                self._train.number_of_rounds = int(number_of_rounds)
            except ValueError:
                pass
            self.update()
            self.set_current_time_label()

    def _set_session_choosable(self, state):
        self.sessions_entry.config(state=state)
        for ex, dur in zip(self._exercise_dropdowns, self._exercise_durations):
            ex.config(state=state)
            dur.config(state=state)

        self._new_exercise.config(state=state)
        self._remove_exercise.config(state=state)

        self.init_exercise_entry.config(state=state)
        self.pause_exercise_entry.config(state=state)

    def choose_exercise(self, selection, index):
        self._train.set_exercise(selection, index)
        self.update()
        self.set_current_time_label()

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
        self._train.reset_interval()
        self._clicked_start = True
        self._set_session_choosable(state="disabled")
        self.resume_command()

    def _is_pause(self, identifier):
        return identifier == self._train.pause.identifier

    def _is_init(self, identifier):
        return identifier == self._train.init.identifier

    def _is_pause_or_init(self, identifier):
        return self._is_pause(identifier) or self._is_init(identifier)

    def interval_cycle(self):

        source_interval = self._train.interval.copy()

        for i, runner in enumerate(source_interval):
            if not self._clicked_start:
                break
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
                self._train.deleteInterval(0)
            else:
                self._train[0].remaining_duration = self._current_time
            if self._pause:
                break

        if not self._pause and self._clicked_start:
            self.set_exercise_label("Done")
            self._current_time = 0
            sound_end()
        self.set_current_time_label()


root = tk.Tk()
root.attributes('-topmost', True)
app = Application(master=root)
app.mainloop()

