"""Game environment configuration variables

Global variables:
    game_config: _GameConfig
        Singleton of _GameConfig dataclass
"""

from __future__ import annotations

import dataclasses
import typing

from .base_config import BaseConfig


@dataclasses.dataclass
class _GameConfig(BaseConfig):
    """Dataclass containing game configuration values

    Class constants:
        _DEFAULT_TICKS_PER_SECOND: int
            Default value for number of ticks per second
        _DEFAULT_BOMB_TIMER_SECONDS: float
            Default time before a bomb explodes
        _DEFAULT_FIRE_TIMER_SECONDS: float
            Default time before fire dissipates
        _DEFAULT_PLAYER_BOMB_COUNT: int
            Default number of bombs a player can drop at the same time
        _DEFAULT_PLAYER_BOMB_COUNT: int
            Default range of a bomb explosion blast

    Members:
        ticks_per_second: int
            Number of ticks per second
        bomb_timer_seconds: float
            Time before a bomb explodes
        fire_timer_seconds: float
            Time before a fire blast dissipates
        player_bomb_count: int
            Number of bombs a player can drop at the same time
        player_bomb_range: int
            Range of a bomb explosion blast
    """

    _DEFAULT_TICKS_PER_SECOND: typing.ClassVar[int] = 60
    _DEFAULT_BOMB_TIMER_SECONDS: typing.ClassVar[float] = 3.0
    _DEFAULT_FIRE_TIMER_SECONDS: typing.ClassVar[float] = 1.0
    _DEFAULT_PLAYER_BOMB_COUNT: typing.ClassVar[int] = 1
    _DEFAULT_PLAYER_BOMB_RANGE: typing.ClassVar[int] = 2

    ticks_per_second: int = _DEFAULT_TICKS_PER_SECOND
    bomb_timer_seconds: float = _DEFAULT_BOMB_TIMER_SECONDS
    fire_timer_seconds: float = _DEFAULT_FIRE_TIMER_SECONDS
    player_bomb_count: int = _DEFAULT_PLAYER_BOMB_COUNT
    player_bomb_range: int = _DEFAULT_PLAYER_BOMB_RANGE

    @property
    def tick_frequency(self) -> float:
        """Time between 2 ticks"""
        return 1 / self.ticks_per_second


game_config = _GameConfig()
