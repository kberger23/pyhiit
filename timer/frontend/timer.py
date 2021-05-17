from functools import partial

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.graphics import Color, Line, Rectangle
from kivy.properties import NumericProperty

from kivy.clock import Clock

from timer.training import get_training


class StartPauseResumeReset(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self.press, on_release=self.release)
        self._clock_event = None
        self._long_press = False

    @property
    def root(self):
        return self.parent.parent.parent.parent.parent

    def update(self, instance, dt):
        if self.state == "down":
            self._long_press = True
            self.root.press_reset(instance)
        else:
            self._long_press = False
        self._clock_event.cancel()

    def press(self, instance):
        self._clock_event = Clock.schedule_once(partial(self.update, instance), 3)

    def release(self, instance):
        if self._long_press:
            self._long_press = False
        else:
            if not self.root.started:
                self.root.press_start(instance)
            else:
                return self.root.press_pause(instance)


class Buttons(FloatLayout):

    BUTTON_SIZE = (f'{100}dp', f'{110}dp')
    BUTTON_SIZE_HINT = (None, None)
    BUTTON_FONT_SIZE = 14

    def __init__(self, **kwargs):
        super(Buttons, self).__init__(**kwargs)

        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', pos_hint={'x': -0.1, 'y': 0})
        self.start = Button(text='', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT, background_normal="images/buttons/play_scaled.png")
        self.start.bind(on_press=self.press_start)
        anchor_layout.add_widget(self.start)
        self.add_widget(anchor_layout)

        anchor_layout2 = AnchorLayout(anchor_x='center', anchor_y='bottom', pos_hint={'x': 0.1, 'y': 0})
        reset = Button(text='Stop', font_size=self.BUTTON_FONT_SIZE, pos_hint={'x': 1, 'y': 0}, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        reset.bind(on_press=self.press_reset)
        anchor_layout2.add_widget(reset)
        self.add_widget(anchor_layout2)

    @property
    def root(self):
        return self.parent.parent.parent.parent

    def press_start(self, instance):
        if not self.root.started:
            self.root.press_start(instance)
        else:
            self.root.press_pause(instance)

    def press_reset(self, instance):
        self.root.press_reset(instance)


class ClockLabel(Label):

    angle = NumericProperty(360)
    REFRESH_TIME = 1./60.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initial_text = self.text
        self.clock_event = None
        self.reset(init=True)

    @property
    def root(self):
        return App.get_running_app().root

    def reset(self, init=False):
        self._time = 0
        self._timings = []
        if self.clock_event:
            self.clock_event.cancel()
        if not init:
            self.root.started = False
        with self.canvas:
            self._line = Line(width=5, color=Color(0, 0, 1))
        self.text = self._initial_text

    def pause(self):
        if self.root.started and self._timings:
            self.text = f"{max(self._time, 0):.1f}"
            self.clock_event.cancel()

    def resume(self):
        if self.root.started and self._timings:
            self.clock_event = Clock.schedule_interval(self.callback, self.REFRESH_TIME)

    def callback(self, dt):

        self._time = max(0, self._time - dt)
        self.parent.angle = 360 * (self._time / self._current_timing.exercise.round_duration)
        self.text = f"{max(self._time, 0):.1f}"

        if self._time < 1E-6:
            if len(self._timings) == 0:
                self.clock_event.cancel()
                get_training().save_training()
                self.root.history.set_sessions()
            else:
                self._set_next_exercise()

    def start_timer(self, timings):

        self._timings = timings.copy()
        self.root.started = True
        self._set_next_exercise()

    def _set_next_exercise(self):
        if self.clock_event:
            self.clock_event.cancel()
        self._current_timing = self._timings[0]
        del self._timings[0]

        self._time = self._current_timing.remaining_duration
        self.parent.exercise.set_label_from_timings(self._current_timing, self._timings[0] if self._timings else None)
        self.parent.round.set_label_from_timings(self._current_timing)

        self.parent.parent.parent.ids.upcomming.create_widgets([self._current_timing] + self._timings)
        self.resume()


class ExerciseLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initial_text = self.text

    def reset(self):
        self.text = self._initial_text

    def set_label_from_timings(self, current_timing, next_timing):
        if current_timing.exercise.identifier.lower() == "pause" or current_timing.exercise.identifier.lower() == "init":
            self.set_label(f"Next: {next_timing.exercise.identifier}")
        else:
            self.set_label(current_timing.exercise.identifier)

    def set_label(self, label):
        self.text = label


class RoundLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initial_text = self.text

    def reset(self):
        self.text = self._initial_text

    def set_label_from_timings(self, current_timing):
        self.text = f"{current_timing.round_index + 1}/{get_training().number_of_rounds}"


class ExerciseLabelInBar(Label):

    def __init__(self, **kwargs):
        self._color = kwargs["background_color"]
        kwargs.pop("background_color")
        super().__init__(**kwargs)


class UpcommingExercises(AnchorLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.anchor_y = "bottom"

        self._layout = None
        self._widgets = []
        self.create_widgets(get_training().interval)

    def create_widgets(self, interval):
        if self._layout is not None:
            for widget in self._widgets:
                self._layout.remove_widget(widget)
            self.remove_widget(self._layout)

        self._widgets = []
        self._layout = FloatLayout(size_hint_y=0.9)

        n_to_show = 4
        interval_to_show = interval[:n_to_show]

        for i, entry in enumerate(reversed(interval_to_show)):

            real_index = i + 1 + max(0, n_to_show - len(interval_to_show))
            scaling = (real_index/n_to_show)**1
            opacity = (0.7 - 0.01) * scaling + 0.01
            opacity_font = (1 - 0.2) * scaling + 0.2
            font_size = (40 - 15) * scaling + 15

            dx = 0.2
            size_hint_y = 1/(n_to_show + 1)

            pos_y = (0 - 1) * scaling + 1

            lbl = ExerciseLabelInBar(text=f"{entry.exercise.identifier}", pos_hint={'x': 0, 'y': pos_y}, size_hint_y=size_hint_y, font_size=f'{font_size}sp', color=(1, 1, 1, opacity_font), background_color=(0, 0, 1, opacity))
            self._widgets.append(lbl)
            self._layout.add_widget(self._widgets[-1])
        self.add_widget(self._layout)

    def reset(self):
        self.create_widgets(get_training().interval)


class Timer(FloatLayout):

    angle = NumericProperty(360)

    def __init__(self, **kwargs):

        self.angle = 360
        super(Timer, self).__init__(**kwargs)

        offset = 0.05
        self.round = RoundLabel(text="Round", font_size='60sp', pos_hint={'x': 0, 'y': 0.1 + offset}, size_hint=(1, 1))
        self.add_widget(self.round)

        self.exercise = ExerciseLabel(text="Exercise", font_size='50sp', pos_hint={'x': 0, 'y': 0 + offset}, size_hint=(1, 1))
        #self.add_widget(self.exercise)

        self.clock = ClockLabel(text='Time', font_size='150sp', pos_hint={'x': 0, 'y': -0.15 + offset}, size_hint=(1, 1))
        self.add_widget(self.clock)

        self.button = StartPauseResumeReset(text='', pos_hint={'x': 0, 'y': 0}, size=self.size, background_color=(0, 0, 0, 0))
        self.add_widget(self.button)


class TimeStuff(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)