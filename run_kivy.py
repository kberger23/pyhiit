import re
from datetime import datetime
from itertools import cycle
from functools import partial

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput

from kivy.graphics import Color, Line, Rectangle
from kivy.properties import NumericProperty

from kivy.clock import Clock

from timer.training import get_training, set_training


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

        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', pos_hint={'x': 0, 'y': 0})
        self.start = Button(text='', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT, background_normal="images/buttons/play_scaled.png")
        self.start.bind(on_press=self.press_start)
        anchor_layout.add_widget(self.start)
        self.add_widget(anchor_layout)

        #reset = Button(text='Reset', font_size=self.BUTTON_FONT_SIZE, pos_hint={'x': 1, 'y': 0}, size=self.BUTTON_SIZE, size_hint=self.BUTTON_SIZE_HINT)
        #reset.bind(on_press=self.press_reset)
        #self.add_widget(reset)

    @property
    def root(self):
        return self.parent.parent.parent.parent

    def press_start(self, instance):
        if not self.root.started:
            self.start.background_normal = "images/buttons/pause_scaled.png"
            self.root.press_start(instance)
        else:
            self.root.press_pause(instance)
            if self.root.paused:
                self.start.background_normal = "images/buttons/play_scaled.png"
            else:
                self.start.background_normal = "images/buttons/pause_scaled.png"

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
        return self.parent.parent.parent.parent.parent

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
            self._timings[0].remaining_duration = self._time
            self.text = f"{max(self._time, 0):.1f}"
            self.clock_event.cancel()

    def resume(self):
        if self.root.started and self._timings:
            self._set_next_exercise()
            self.clock_event = Clock.schedule_interval(self.callback, self.REFRESH_TIME)

    def callback(self, dt):
        self._time = max(0, self._time - dt)
        self.parent.angle = 360 * (self._time / 60 % 1)
        self.text = f"{max(self._time, 0):.1f}"
        if self._time < 1E-6:
            if len(self._timings) == 0:
                self.clock_event.cancel()
                get_training().save_training()
                self.root.history.set_sessions()
            else:
                self._set_next_exercise()

    def start_timer(self, timings):
        if self.clock_event:
            self.clock_event.cancel()
        self._timings = timings.copy()
        self.root.started = True
        self.resume()

    def _set_next_exercise(self):
        self._time = self._timings[0].remaining_duration
        self.parent.exercise.set_label_from_timings(self._timings)
        self.parent.round.set_label_from_timings(self._timings)

        del self._timings[0]


class ExerciseLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initial_text = self.text

    def reset(self):
        self.text = self._initial_text

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
        self._initial_text = self.text

    def reset(self):
        self.text = self._initial_text

    def set_label_from_timings(self, timings: list):
        self.text = f"{timings[0].round_index + 1}/{get_training().number_of_rounds}"


class Timer(FloatLayout):

    angle = NumericProperty(360)

    def __init__(self, **kwargs):

        self.angle = 360
        super(Timer, self).__init__(**kwargs)

        offset = 0.05
        self.round = RoundLabel(text="Round", font_size='50sp', pos_hint={'x': 0, 'y': 0.1 + offset}, size_hint=(1, 1))
        self.add_widget(self.round)

        self.exercise = ExerciseLabel(text="Exercise", font_size='50sp', pos_hint={'x': 0, 'y': 0 + offset}, size_hint=(1, 1))
        self.add_widget(self.exercise)

        self.clock = ClockLabel(text='Time', font_size='100sp', pos_hint={'x': 0, 'y': -0.15 + offset}, size_hint=(1, 1))
        self.add_widget(self.clock)

        self.button = StartPauseResumeReset(text='', pos_hint={'x': 0, 'y': 0}, size=self.size, background_color=(0, 0, 0, 0))
        self.add_widget(self.button)


class ButtonWithDropDown(Button):

    background_color = (0, 0, 0.6, 1)
    background_normal = ""

    def __init__(self, **kwargs):
        self.index = kwargs["index"]
        kwargs.pop("index")
        super().__init__(**kwargs)

        self._dropdown = DropDown()

        for inner_ex in get_training().available_exercises:
            btn = Button(text=inner_ex, size_hint_x=.3, size_hint_y=None, height=40, font_size='15sp', background_normal=self.background_normal, background_color=(0, 0, 0.4, 0.9))
            btn.bind(on_release=lambda btn: self._dropdown.select(btn.text))
            self._dropdown.add_widget(btn)

        self._dropdown.container.spacing = 0
        self._dropdown.container.padding = (0, 0, 0, 0)

        self.bind(on_release=self._dropdown.open)
        self._dropdown.bind(on_select=lambda instance, x: self.change_exercise(x))

    def change_exercise(self, x):
        self.text = x
        get_training().set_exercise(x, self.index)


class SetRounds(TextInput):

    pat = re.compile('[^0-9]')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.text_change, focus=self.on_focus)

    @staticmethod
    def text_change(instance, value):
        try:
            get_training().number_of_rounds = int(value)
        except ValueError:
            pass

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super().insert_text(s, from_undo=from_undo)

    def on_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.select_all())
        else:
            Clock.schedule_once(lambda dt: self.select_text(0, 0))


class ExerciseDuration(TextInput):

    pat = re.compile('[^0-9]')

    def __init__(self, **kwargs):
        self._exercise = kwargs["exercise"]
        kwargs.pop("exercise")
        super().__init__(**kwargs)
        self.bind(text=self.text_change, focus=self.on_focus)

    def text_change(self, instance, value):
        try:
            self._exercise.round_duration = float(value)
            get_training().reset_interval()
        except ValueError:
            pass

    def on_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.select_all())
        else:
            Clock.schedule_once(lambda dt: self.select_text(0, 0))

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super().insert_text(s, from_undo=from_undo)


class ExerciseRemove(Button):

    def __init__(self, **kwargs):
        self.ex_button = kwargs["ex_button"]
        kwargs.pop("ex_button")
        self.dur_button = kwargs["dur_button"]
        kwargs.pop("dur_button")
        super().__init__(**kwargs)
        self.bind(on_press=self.press)

    def press(self, instance):
        get_training().remove_exercise(self.ex_button.index)
        self.parent.remove_widget(self.ex_button)
        self.parent.remove_widget(self.dur_button)
        self.parent.remove_widget(self)


class Exercises(ScrollView):

    COLOR_PLUS_MINUS = (0.1, 0.1, 0.1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._layout = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)

        # Make sure the height is such that there is something to scroll.
        self._layout.bind(minimum_height=self._layout.setter('height'))

        for i, ex in enumerate(get_training().exercises):
            self.add_exercise_widgets(i, ex)

        self.add_plus_to_layout()
        self.add_widget(self._layout)

    def add_plus_to_layout(self):
        plus = Button(text="+", size_hint_x=.05, size_hint_y=None, height=40, font_size='15sp', background_normal="", background_color=self.COLOR_PLUS_MINUS)
        plus.bind(on_press=self.add_exercise_to_layout)
        self._layout.add_widget(plus)

    def add_exercise_widgets(self, index, ex):

        drop_down_button = ButtonWithDropDown(text=ex.identifier, size_hint_x=.7, size_hint_y=None, height=40, font_size='15sp', index=index)
        text_input = ExerciseDuration(text=str(ex.round_duration), size_hint_x=.2, size_hint_y=None, height=40, font_size='15sp', multiline=False, exercise=ex)

        self._layout.add_widget(ExerciseRemove(text="-", size_hint_x=.05, size_hint_y=None, height=40, font_size='15sp', ex_button=drop_down_button, dur_button=text_input, background_normal="", background_color=self.COLOR_PLUS_MINUS))

        self._layout.add_widget(drop_down_button)
        self._layout.add_widget(text_input)

    def add_exercise_to_layout(self, instance):
        self._layout.remove_widget(instance)
        get_training().add_exercise(get_training().available_exercises[-1])
        self.add_exercise_widgets(len(get_training().exercises) - 1, get_training().exercises[-1])
        self.add_plus_to_layout()


class ExercisesInitPause(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = GridLayout(cols=2, spacing=10, padding=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))

        size_dur = 0.4666
        layout.add_widget(Label(text="Rounds", size_hint_x=1-size_dur, size_hint_y=None, height=40, font_size='15sp'))
        layout.add_widget(SetRounds(text=str(get_training().number_of_rounds), size_hint_x=size_dur, size_hint_y=None, height=40, font_size='15sp', multiline=False))

        layout.add_widget(Label(text=get_training().init.identifier, size_hint_x=1-size_dur, size_hint_y=None, height=40, font_size='15sp'))
        layout.add_widget(ExerciseDuration(text=str(get_training().init.round_duration), size_hint_x=size_dur, size_hint_y=None, height=40, font_size='15sp', multiline=False, exercise=get_training().init))
        layout.add_widget(Label(text=get_training().pause.identifier, size_hint_x=1-size_dur, size_hint_y=None, height=40, font_size='15sp'))
        layout.add_widget(ExerciseDuration(text=str(get_training().pause.round_duration), size_hint_x=size_dur, size_hint_y=None, height=40, font_size='15sp', multiline=False, exercise=get_training().pause))

        self.add_widget(layout)


class PastExercisesLabel(Label):
    def __init__(self, **kwargs):
        self._color = kwargs["color"]
        kwargs.pop("color")

        super().__init__(**kwargs)


class PastSessions(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TimeStuff(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Workout(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        boxlayout = BoxLayout(orientation="horizontal", size_hint=(1,1))

        boxlayout.add_widget(Exercises(size_hint_x=.7))
        boxlayout.add_widget(ExercisesInitPause(size_hint_x=.3))
        self.add_widget(boxlayout)


class History(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        self.add_widget(self.scroll_view)
        self._layout = None
        self.set_sessions()

    def set_sessions(self):

        if self._layout is not None:
            self.scroll_view.remove_widget(self._layout)

        history = list(reversed(get_training().history.as_list))

        self._layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self._layout.bind(minimum_height=self._layout.setter('height'))

        colors = cycle([(0.6, 0, 0, 1), (0, 0, 0.6, 1)])
        color = next(colors)

        for i, entry in enumerate(history):
            if not i == 0 and not (datetime.strptime(entry["date"], get_training().DATE_FORMAT).date() == datetime.strptime(history[i - 1]["date"], get_training().DATE_FORMAT).date()):
                color = next(colors)
            text = f"{entry['date']}\nRounds:{entry['rounds']}"
            for ex, dur in entry["exercises"].items():
                text = text + f"\n{ex}: {dur:.0f}s"

            self._layout.add_widget(PastExercisesLabel(text=text, size_hint_y=None, height=100, font_size='11sp', color=color))

        self.scroll_view.add_widget(self._layout)


class ScreenSwitches(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        box = BoxLayout(orientation="horizontal")
        box.add_widget(Button(text="Timer", on_press=self.switch_to_timer))
        box.add_widget(Button(text="Workout", on_press=self.switch_to_workout))
        box.add_widget(Button(text="History", on_press=self.switch_to_history))
        self.add_widget(box)

    @property
    def root(self):
        return self.parent

    def switch_to_timer(self, instance):
        self.parent.sm.switch_to(self.parent.sm.timer, direction='right')

    def switch_to_workout(self, instance):
        direction = 'right' if self.parent.sm.current == "history_screen" else 'left'
        self.parent.sm.switch_to(self.parent.sm.workout, direction=direction)

    def switch_to_history(self, instance):
        self.parent.sm.switch_to(self.parent.sm.history, direction='left')


class Screens(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = TimeStuff(name="time_screen")
        self.add_widget(self.timer)
        self.workout = Workout(name="workout_screen")
        self.add_widget(self.workout)
        self.history = History(name="history_screen")
        self.add_widget(self.history)


class Overview(BoxLayout):

    def __init__(self, **kwargs):
        super(Overview, self).__init__(**kwargs)
        self.add_widget(ScreenSwitches(size_hint=(1, 0.05)))

        self.sm = Screens(size_hint=(1, 0.95))
        self.add_widget(self.sm)

        self.started = False
        self.paused = False
        self.finished = False

    @property
    def timer(self):
        return self.sm.timer.ids.timer

    @property
    def history(self):
        return self.sm.history

    def press_start(self, instance):
        if self.paused:
            self.paused = False
        self.timer.clock.start_timer(get_training().interval)

    def press_pause(self, instance):
        if self.paused:
            self.paused = False
            self.timer.clock.resume()
        else:
            if self.started:
                self.timer.clock.pause()
                self.paused = True

    def press_reset(self, instance):
        self.timer.clock.reset()
        self.timer.angle = 360
        self.timer.exercise.reset()
        self.timer.round.reset()
        self.paused = False


class pyHIIT(App):

    def build(self):
        return Overview()


if __name__ == '__main__':
    scale = 0.5
    Window.size = (1080 * scale, 1920 * scale)

    set_training()
    pyHIIT().run()
