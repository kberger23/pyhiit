import re

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput

from kivy.clock import Clock

from timer.training import get_training

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


class Workout(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        boxlayout = BoxLayout(orientation="horizontal", size_hint=(1,1))

        boxlayout.add_widget(Exercises(size_hint_x=.7))
        boxlayout.add_widget(ExercisesInitPause(size_hint_x=.3))
        self.add_widget(boxlayout)