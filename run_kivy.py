from kivy.app import App
from kivy.core.window import Window

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label

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
        return App.get_running_app().root

    def switch_to_timer(self, instance):
        if self.root.workout_changed:
            self.root.reset(instance)

        self.root.sm.switch_to(self.root.sm.timer, direction='right')
        self.root.workout_changed = False

    def switch_to_workout(self, instance):
        direction = 'right' if self.root.sm.current == "history_screen" else 'left'
        self.root.sm.switch_to(self.root.sm.workout, direction=direction)

    def switch_to_history(self, instance):
        self.root.sm.switch_to(self.root.sm.history, direction='left')


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

        self._popup = None

        self.started = False
        self.paused = False
        self.finished = False

        self._stopped = False

        self.workout_changed = False

    @property
    def timer(self):
        return self.sm.timer.ids.timer

    @property
    def buttons(self):
        return self.sm.timer.ids.buttons

    @property
    def upcomming_exercises(self):
        return self.sm.timer.ids.upcomming

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

        if self.started:
            self.timer.clock.pause()

            boxlayout = BoxLayout(orientation="vertical")

            anch = AnchorLayout(size_hint_y=0.7)
            lbl = Label(text='Do you really want to stop?')
            anch.add_widget(lbl)
            boxlayout.add_widget(anch)

            grid = GridLayout(rows=1, size_hint_y=0.3, spacing=20)
            yes = Button(text='yes')
            yes.bind(on_press=self.reset)
            grid.add_widget(yes)

            no = Button(text='no')
            no.bind(on_press=lambda *args: self._popup.dismiss())
            grid.add_widget(no)
            boxlayout.add_widget(grid)

            self._popup = Popup(title='', content=boxlayout, auto_dismiss=True, size_hint=(0.7, 0.2), on_dismiss=self._dismiss)
            self._popup.open()

    def reset(self, instance):
        self._stopped = True
        self.timer.clock.reset()
        self.timer.angle = 360
        self.timer.exercise.reset()
        self.timer.round.reset()
        self.upcomming_exercises.reset()
        self.paused = False
        self.buttons.start.background_normal = "images/buttons/play_scaled.png"

        if self._popup:
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
