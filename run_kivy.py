from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

import datetime


class Buttons(BoxLayout):

    BUTTON_SIZE = (100, 100)
    BUTTON_FONT_SIZE = 14

    def __init__(self, **kwargs):
        super(Buttons, self).__init__(**kwargs)

        start = Button(text='Start', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=(1./3, None))
        self.add_widget(start)
        self._pause = Button(text='Pause', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=(1./3, None))
        self.add_widget(self._pause)
        reset = Button(text='Reset', font_size=self.BUTTON_FONT_SIZE, size=self.BUTTON_SIZE, size_hint=(1./3, None))
        self.add_widget(reset)


class Timer(BoxLayout):
    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)

        self._remaining_time = Label(text="30s", font_size='30sp')
        self.add_widget(self._remaining_time)


class Overview(BoxLayout):
    def __init__(self, **kwargs):
        super(Overview, self).__init__(**kwargs)


class pyHIIT(App):

    def build(self):

        return Overview()


if __name__ == '__main__':
    pyHIIT().run()
