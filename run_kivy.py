from datetime import datetime
from itertools import cycle

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button


from timer.training import get_training, set_training
from timer.frontend import Workout, Timer


class PastExercisesLabel(Label):
    def __init__(self, **kwargs):
        self._color = kwargs["color"]
        kwargs.pop("color")

        super().__init__(**kwargs)


class TimeStuff(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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
