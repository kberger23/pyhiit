from abc import ABC, abstractmethod


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


class PullUps(Exercise):

    def __init__(self):
        super().__init__()

    @property
    def identifier(self):
        return "pull-ups"

    @property
    def round_duration(self):
        return 2


class PullUpsWide(Exercise):

    def __init__(self):
        super().__init__()

    @property
    def identifier(self):
        return "Wide pull-ups"

    @property
    def round_duration(self):
        return 2