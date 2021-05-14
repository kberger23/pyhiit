from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition


class pyHIIT(App):

    def build(self):

        self.transition = SlideTransition(duration=.1)
        root = ScreenManager(transition=self.transition)
        return root

if __name__ == '__main__':
    pyHIIT().run()
