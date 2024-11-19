"""Implements the bombs in the game"""

from __future__ import annotations

import typing

from ...config.game import game_config
from ..map import MapCell
from ..position import Position
from .fire import Fire

if typing.TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Mapping
    from typing import Any

    from ..environment import Environment
    from .player import Player


class BombError(Exception):
    """Error raised when something goes wrong within a Bomb instance"""


class Bomb:
    """Implements a bomb that will explode after a fixed amount of time

    When a bomb is instanciated, it will automatically explode after a fixed
    amount of game ticks. It will destroy boxes and kill players in its blast.
    """

    __slots__ = {
        "position": "(Position) Position which the bomb is located",
        "player": "(Player | None) Player who planted the bomb.",
        "range": "(int) Range of the explosion blast",
        "timer": "(float) Time mark after which the bomb will explode",
    }

    def __init__(
        self, position: Position, player: Player, range_: int, timer: float
    ) -> None:
        """Initializes a newly planted bomb

        :param position: Coordinates of the bomb
        :param player: Player who planted the bomb
        :param range_: Range of the explosion blast
        :param timer: Time mark after which the bomb will explode
        """
        self.position = position
        self.player = player
        self.range = range_
        self.timer = timer

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #
    def tick(self, environment: Environment, time: float) -> None:
        """Update bomb timer and apply its explosion effects on the environment

        :param environment: The game environment
        :param time: The current time
        """
        # If bomb is still ticking
        if self.timer > time:
            return

        # If bomb is exploding
        environment.blast_fire(self.position, self.timer)

        directions = (
            self.position.up,
            self.position.down,
            self.position.left,
            self.position.right,
        )

        for move in directions:
            for distance in range(1, self.range + 1):
                blast_position = move(distance)
                blasted_cell = environment.map[blast_position]
                if blasted_cell is MapCell.WALL:
                    break

                environment.blast_fire(blast_position, self.timer)

                if blasted_cell is MapCell.BOX:
                    environment.map[blast_position] = MapCell.EMPTY
                    break

        if self.player is not None:
            self.player.current_bomb_count -= 1
