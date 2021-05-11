from abc import ABC, abstractmethod

from .const import DEBUG, DEBUG_INTERVAL_TIME


class Exercise(ABC):

    def __init__(self):
        pass

    @property
    @abstractmethod
    def identifier(self):
        pass

    @property
    @abstractmethod
    def round_duration(self):
        pass


class Pause(Exercise):

    def __init__(self):
        super().__init__()

    @property
    def identifier(self):
        return "pause"

    @property
    def round_duration(self):
        return 7 if not DEBUG else DEBUG_INTERVAL_TIME


class Init(Exercise):

    def __init__(self):
        super().__init__()

    @property
    def identifier(self):
        return "init"

    @property
    def round_duration(self):
        return 10 if not DEBUG else DEBUG_INTERVAL_TIME


class PullUps(Exercise):

    def __init__(self):
        super().__init__()

    @property
    def identifier(self):
        return "Pull-ups"

    @property
    def round_duration(self):
        return 30 if not DEBUG else DEBUG_INTERVAL_TIME


class PullUpsWide(Exercise):

    def __init__(self):
        super().__init__()

    @property
    def identifier(self):
        return "Wide pull-ups"

    @property
    def round_duration(self):
        return 30 if not DEBUG else DEBUG_INTERVAL_TIME
