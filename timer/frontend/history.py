from datetime import datetime
from itertools import cycle

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label


from timer.training import get_training


class PastExercisesLabel(Label):
    def __init__(self, **kwargs):
        self._color = kwargs["color"]
        kwargs.pop("color")

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