"""Implements the explosion fire blast in the game"""

from __future__ import annotations

import typing

from ...config.game import game_config
from ..position import Position
from ..position import NULL_POSITION

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..environment import Environment


class FireError(Exception):
    """Error raised when something goes wrong within a Fire instance"""


class Fire:
    """Implements a fire blast that will dissipate after a fixed amount of time

    When a fire blast is instanciated, it will automatically disspate after a
    fixed time. It will kill players that cross its path.
    """

    __slots__ = {
        "position": "(Position) Position at which the fire blast is located",
        "timer": "(float) Time mark after which the fire blast will dissipate",
    }

    def __init__(self, position: Position, timer: float) -> None:
        """Initializes a new fire blast

        :param position: Coordinates of the fire blast
        :param timer: Time mark after which the fire blast will dissipate
        """
        self.position = position
        self.timer = timer

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, environment: Environment, time: float) -> None:
        """Update fire blast timer and kill players engulfed in flames

        :param environment: Game environment
        :param time: Current time
        """
        # If fire is extinguished
        if self.timer <= time:
            return
        # If fire is raging
        for player in environment.players.values():
            if player.position == self.position:
                player.position = NULL_POSITION
