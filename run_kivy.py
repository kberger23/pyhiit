from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty

from kivy.clock import Clock

from timer.training import Training

global train


class Buttons(BoxLayout):

    BUTTON_SIZE = (100, 100)
    BUTTON_SIZE_HINT = (1./3, None)
    BUTTON_FONT_SIZE = 14

    def __init__(self, **kwargs):
        super(Buttons, self).__init__(**kwargs)

        self._paused = False

        start = Button(text='Start', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        start.bind(on_press=self.press_start)
        self.add_widget(start)
        self.pause = Button(text='Pause', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        self.pause.bind(on_press=self.press_pause)
        self.add_widget(self.pause)
        reset = Button(text='Reset', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        reset.bind(on_press=self.press_reset)
        self.add_widget(reset)

    def press_start(self, instance):
        self.parent.ids.timer.clock.start_timer(train.interval)

    def press_pause(self, instance):
        if self._paused:
            self.pause.text = "Pause"
            self._paused = False
            self.parent.ids.timer.clock.resume()
        else:
            if self.parent.ids.timer.clock.started:
                self.pause.text = "Resume"
                self.parent.ids.timer.clock.pause()
                self._paused = True

    def press_reset(self, instance):
        print("reset")


class ClockLabel(Label):

    angle = NumericProperty(360)
    REFRESH_TIME = 1./60.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._time = 0
        self._timings = []
        self.clock_event = None
        self.started = False
        with self.canvas:
            self._line = Line(width=5, color=Color(0, 0, 1))

    def pause(self):
        if self.started:
            self._timings[0].remaining_duration = self._time
            self.text = f"{max(self._time, 0):5.1f}"
            self.clock_event.cancel()

    def callback(self, dt):
        self._time = max(0, self._time - dt)
        self.parent.angle = 360 * (self._time / 60 % 1)
        self.text = f"{max(self._time, 0):5.1f}"
        if self._time < 1E-6:
            if len(self._timings) == 0:
                self.clock_event.cancel()
            else:
                self._set_next_exercise()

    def start_timer(self, timings):
        if self.clock_event:
            self.clock_event.cancel()
        self._timings = timings.copy()
        self.started = True
        self.resume()

    def resume(self):
        if self.started:
            self._set_next_exercise()
            self.clock_event = Clock.schedule_interval(self.callback, self.REFRESH_TIME)

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
            self.set_label(f"Next: {timings[1].exercise.identifier}")
        else:
            self.set_label(timings[0].exercise.identifier)

    def set_label(self, label):
        self.text = label


class RoundLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_label_from_timings(self, timings: list):
        self.text = f"Round: {timings[0].round_index + 1}/{train.number_of_rounds}"


class Timer(FloatLayout):

    angle = NumericProperty(360)

    def __init__(self, **kwargs):

        self.angle = 360
        super(Timer, self).__init__(**kwargs)

        self.round = RoundLabel(text="Round", font_size='30sp', pos_hint={'x': 0, 'y': 0.1}, size_hint=(1, 1))
        self.add_widget(self.round)

        self.exercise = ExerciseLabel(text="Exercise", font_size='30sp', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))
        self.add_widget(self.exercise)

        self.clock = ClockLabel(text='Time', font_size='60sp', pos_hint={'x': 0, 'y': -0.15}, size_hint=(1, 1))
        self.add_widget(self.clock)


class MyDropDown(DropDown):
    def __init__(self, **kwargs):
        self._index = kwargs["index"]
        kwargs.pop("index")
        super().__init__(**kwargs)
        self._button = None

    def add_button(self, button):
        self._button = button

    def change_text(self, text):
        print(f"index = {self._index}")
        self._button.text = text


class ButtonWithDropDown(Button):

    def __init__(self, **kwargs):
        self._index = kwargs["index"]
        kwargs.pop("index")
        super().__init__(**kwargs)

        self._dropdown = DropDown()
        for inner_ex in train.available_exercises:
            btn = Button(text=inner_ex, size_hint_x=.3, size_hint_y=None, height=40, font_size='15sp')
            btn.bind(on_release=lambda btn: self._dropdown.select(btn.text))
            self._dropdown.add_widget(btn)

        self.bind(on_release=self._dropdown.open)
        self._dropdown.bind(on_select=lambda instance, x: self.change_exercise(x))

    def change_exercise(self, x):
        self.text = x
        train.set_exercise(x, self._index)


class Exercises(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)

        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))

        for i, ex in enumerate(train.exercises):

            drop_down_button = ButtonWithDropDown(text=ex.identifier, size_hint_x=.3, size_hint_y=None, height=40, font_size='15sp', index=i)
            layout.add_widget(drop_down_button)

        self.add_widget(layout)


class ExercisesInitPaus(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        btn = Button(text=train.init.identifier, size_hint_x=.3, size_hint_y=None, height=40, font_size='15sp')
        layout.add_widget(btn)
        btn = Button(text=train.pause.identifier, size_hint_x=.3, size_hint_y=None, height=40, font_size='15sp')
        layout.add_widget(btn)

        self.add_widget(layout)


class ExercisesPlus(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Exercises(size_hint_x=.7))
        self.add_widget(ExercisesInitPaus(size_hint_x=.3))


class Overview(BoxLayout):
    def __init__(self, **kwargs):
        super(Overview, self).__init__(**kwargs)


class pyHIIT(App):

    def build(self):
        return Overview()


if __name__ == '__main__':
    train = Training()
    pyHIIT().run()
