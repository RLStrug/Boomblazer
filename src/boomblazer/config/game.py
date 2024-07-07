"""Game environment configuration variables

Global variables:
    game_config: _GameConfig
        Singleton of _GameConfig dataclass

Classes:
    _GameConfig:
        Dataclass containing the game configuration values
"""

import dataclasses
from typing import ClassVar

from .base_config import BaseConfig


@dataclasses.dataclass(slots=True)
class _GameConfig(BaseConfig):
    """Dataclass containing the game configuration values

    Class constants:
        _DEFAULT_TICKS_PER_SECOND: int
            The default value for number of ticks per second
        _DEFAULT_BOMB_TIMER_SECONDS: float
            The default value for number of seconds before a bomb explodes
        _DEFAULT_FIRE_TIMER_SECONDS: float
            The default value for number of seconds before fire dissipates
        _DEFAULT_PLAYER_BOMB_COUNT: int
            The default number of bombs a player can drop at the same time
        _DEFAULT_PLAYER_BOMB_COUNT: int
            The default range of a bomb explosion blast

    Members:
        ticks_per_second: int
            The number of ticks per second
        bomb_timer_seconds: float
            The number of seconds before a bomb explodes
        fire_timer_seconds: float
            The number of seconds before a fire blast dissipates
        player_bomb_count: int
            The number of bombs a player can drop at the same time
        player_bomb_range: int
            The range of a bomb explosion blast

    Properties:
        tick_frequency (read-only):
            The number of seconds between 2 ticks
        bomb_timer_ticks (read-only):
            The number of ticks before a bomb explodes
        fire_timer_ticks (read-only):
            The number of ticks before a fire blast dissipates
    """

    _DEFAULT_TICKS_PER_SECOND: ClassVar[int] = 60
    _DEFAULT_BOMB_TIMER_SECONDS: ClassVar[float] = 3.0
    _DEFAULT_FIRE_TIMER_SECONDS: ClassVar[float] = 1.0
    _DEFAULT_PLAYER_BOMB_COUNT: ClassVar[int] = 1
    _DEFAULT_PLAYER_BOMB_RANGE: ClassVar[int] = 2

    ticks_per_second: int = _DEFAULT_TICKS_PER_SECOND
    bomb_timer_seconds: float = _DEFAULT_BOMB_TIMER_SECONDS
    fire_timer_seconds: float = _DEFAULT_FIRE_TIMER_SECONDS
    player_bomb_count: int = _DEFAULT_PLAYER_BOMB_COUNT
    player_bomb_range: int = _DEFAULT_PLAYER_BOMB_RANGE

    @property
    def tick_frequency(self) -> float:
        """Returns the number of seconds between 2 ticks

        Return value: float
            The number of seconds between 2 ticks
        """
        return 1 / self.ticks_per_second

    @property
    def bomb_timer_ticks(self) -> int:
        """Returns the number of ticks before a bomb explodes

        Return value: int
            The number of ticks before a bomb explodes
        """
        return round(self.bomb_timer_seconds * self.ticks_per_second)

    @property
    def fire_timer_ticks(self) -> int:
        """Returns the number of ticks before a fire blast dissipates

        Return value: int
            The number of ticks before a fire blast dissipates
        """
        return round(self.fire_timer_seconds * self.ticks_per_second)


game_config=_GameConfig()
