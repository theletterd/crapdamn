# preserve game state, e.g. points, lives, powerups?


class GameState(object):

    def __init__(self, lives=3):
        self._lives = lives
        self._score = 0
        self._message = "CRAP DAMNNNNN"

    def add_score(self, score):
        self._score += score

    @property
    def score(self):
        return self._score

    @property
    def remaining_lives(self):
        return self._lives

    @property
    def message(self):
        return self._message
