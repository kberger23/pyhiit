from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty

from kivy.clock import Clock

import numpy as np

import datetime

#interval runner
import time
from timer.training import Training


class IntervalRunner:

    def __init__(self):

        self.current_time = 0
        self.current_session = -1
        self.clicked_start = False
        self.pause = False
        self.train = Training([Training.PUSH_UPS, Training.WIDE_PUSH_UPS])

    def interval_cycle(self, clock_text):

        source_interval = self.train.interval.copy()

        for i, runner in enumerate(source_interval):
            print(runner.exercise.identifier)


class Buttons(BoxLayout):

    BUTTON_SIZE = (100, 100)
    BUTTON_SIZE_HINT = (1./3, None)
    BUTTON_FONT_SIZE = 14

    def __init__(self, **kwargs):
        super(Buttons, self).__init__(**kwargs)

        start = Button(text='Start', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        start.bind(on_press=self.press_start)
        self.add_widget(start)
        pause = Button(text='Pause', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        self.add_widget(pause)
        reset = Button(text='Reset', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        self.add_widget(reset)

    def press_start(self, instance):
        self.parent.ids.timer.clock.start_timer(self.parent.intervalRunner.train.interval)


class ClockLabel(Label):

    REFRESH_TIME = 0.01

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._time = 0
        self._timings = []
        self._clock_event = None

    def callback(self, dt):
        self._time -= dt
        self.text = f"{max(self._time, 0):5.1f}s"
        if self._time < 1E-6:
            if len(self._timings) == 0:
                self._clock_event.cancel()
            else:
                self._set_next_exercise()

    def start_timer(self, timings):
        self._timings = timings.copy()
        self._set_next_exercise()
        self._clock_event = Clock.schedule_interval(self.callback, self.REFRESH_TIME)

    def _set_next_exercise(self):
        self._time = self._timings[0].remaining_duration
        self.parent.exercise.set_label_from_timings(self._timings)
        self.parent.round.set_label_from_timings(self._timings)

        del self._timings[0]


class ExerciseLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_label_from_timings(self, timings: list):
        if timings[0].exercise.identifier.lower() == "pause" or timings[0].exercise.identifier.lower() == "init":
            self.set_label(f"{timings[0].exercise.identifier}: {timings[1].exercise.identifier} next")
        else:
            self.set_label(timings[0].exercise.identifier)

    def set_label(self, label):
        self.text = label


class RoundLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_label_from_timings(self, timings: list):
        print(timings[0].exercise.identifier, timings[0].session)
        self.text = f"Round: {timings[0].round_index + 1}/{self.parent.parent.intervalRunner.train.number_of_rounds}"


class Timer(BoxLayout):

    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)

        self.exercise = ExerciseLabel(text="Exercise", font_size='30sp')
        self.add_widget(self.exercise)

        self.round = RoundLabel(text="Round", font_size='30sp')
        self.add_widget(self.round)

        self.clock = ClockLabel(text='Time', font_size='30sp')
        self.add_widget(self.clock)


class Overview(BoxLayout):
    def __init__(self, **kwargs):
        super(Overview, self).__init__(**kwargs)

        self.intervalRunner = IntervalRunner()



class pyHIIT(App):

    def build(self):
        return Overview()

    # def build(self):
    #     self.myLabel = Label(text ='Waiting for updates...')
    #     Clock.schedule_interval(self.Callback_Clock, 0.1)
    #
    #     return self.myLabel
    #
    # def Callback_Clock(self, dt):
    #     self.count = self.count + 1
    #     self.myLabel.text = "Updated % d...times"% self.count

if __name__ == '__main__':
    pyHIIT().run()
