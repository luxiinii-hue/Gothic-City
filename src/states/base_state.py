"""Abstract base for all game states."""

from abc import ABC, abstractmethod
import pygame


class BaseState(ABC):
    def __init__(self, game):
        self.game = game

    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass
