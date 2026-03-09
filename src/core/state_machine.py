"""GameState enum and transition controller."""

from enum import Enum, auto


class GameState(Enum):
    TITLE = auto()
    TEAM_SELECT = auto()
    MAP = auto()
    COMBAT = auto()
    REWARD = auto()
    RESULT = auto()


class StateMachine:
    def __init__(self):
        self._states: dict[GameState, object] = {}
        self._current_state = None
        self._current_key = None

    def register(self, key: GameState, state):
        self._states[key] = state

    def transition(self, key: GameState, **kwargs):
        if self._current_state is not None:
            self._current_state.exit()
        self._current_key = key
        self._current_state = self._states[key]
        self._current_state.enter(**kwargs)

    @property
    def current(self):
        return self._current_state

    @property
    def current_key(self):
        return self._current_key
