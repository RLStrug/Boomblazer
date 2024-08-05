"""Implements the explosion fire blast in the game"""

from __future__ import annotations

import typing

from ...config.game import game_config
from ..position import Position

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..environment import Environment


class FireError(Exception):
    """Error raised when something goes wrong within a Fire instance"""


class FireDict(typing.TypedDict):
    """Serialization of a Fire"""

    position: Position
    timer: int


class Fire:
    """Implements a fire blast that will dissipate after a fixed amount of time

    When a fire blast is instanciated, it will automatically disspate after a
    fixed amount of game ticks. It will kill players that cross its path.
    """

    __slots__ = {
        "position": "(Position) Position at which the fire blast is located",
        "timer": "(int) Number of game ticks left before the fire blast dissipates",
    }

    def __init__(self, position: Position, timer: int | None = None) -> None:
        """Initializes a new fire blast

        :param position: Coordinates of the fire blast
        :param timer: Number of game ticks left before the fire blast dissipates
        """
        if timer is None:
            timer = game_config.fire_timer_ticks
        self.position = position
        self.timer = timer

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, environment: "Environment") -> None:
        """Update fire blast timer and kill players engulfed in flames

        :param environment: Game environment
        """
        self.timer -= 1
        if self.timer <= 0:
            return

        environment.players = [
            player for player in environment.players if player.position != self.position
        ]

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Fire":
        """Instanciates a Fire from a dict

        :param data: Mapping that should be like FireDict
        :returns: Fire initialized data
        """
        return cls(position=Position(*data["position"]), timer=int(data["timer"]))

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> FireDict:
        """Returns the current instance data serialized

        :returns: Serialized Fire
        """
        return FireDict(
            position=self.position,
            timer=self.timer,
        )
