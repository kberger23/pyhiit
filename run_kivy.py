from datetime import datetime
from itertools import cycle

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from timer.training import get_training, set_training
from timer.frontend import Workout, TimeStuff, History


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

        self._stopped = False

    @property
    def timer(self):
        return self.sm.timer.ids.timer

    @property
    def buttons(self):
        return self.sm.timer.ids.buttons

    @property
    def history(self):
        return self.sm.history

    def press_start(self, instance):
        if self.paused:
            self.paused = False

        self.buttons.start.background_normal = "images/buttons/pause_scaled.png"
        self.timer.clock.start_timer(get_training().interval)

    def press_pause(self, instance):
        if self.paused:
            self.paused = False
            self.buttons.start.background_normal = "images/buttons/pause_scaled.png"
            self.timer.clock.resume()
        else:
            self.buttons.start.background_normal = "images/buttons/play_scaled.png"
            if self.started:
                self.timer.clock.pause()
                self.paused = True

    def press_reset(self, instance):

        self.timer.clock.pause()

        from kivy.uix.popup import Popup
        content = Button(text='Do you really want to stop?')
        self._popup = Popup(title='', content=content, auto_dismiss=True, size_hint=(0.7, 0.13), on_dismiss=self._dismiss)
        content.bind(on_press=self._reset)
        self._popup.open()

    def _reset(self, instance):
        self._stopped = True
        self.timer.clock.reset()
        self.timer.angle = 360
        self.timer.exercise.reset()
        self.timer.round.reset()
        self.paused = False
        self._popup.dismiss()

    def _dismiss(self, instance):
        if not self._stopped and not self.paused:
            self.timer.clock.resume()
        self._stopped = False


class pyHIIT(App):

    def build(self):
        return Overview()


if __name__ == '__main__':
    scale = 0.5
    Window.size = (1080 * scale, 1920 * scale)

    set_training()
    pyHIIT().run()
