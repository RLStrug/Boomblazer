"""Implements a game player"""

from __future__ import annotations

import enum
import typing

from ...config.game import game_config
from ..map import MapCell
from ..position import Position
from .bomb import Bomb

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..environment import Environment


class PlayerAction(enum.IntFlag):
    """Actions that can be performed by a player"""

    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()
    PLANT_BOMB = enum.auto()
    DIE = enum.auto()


class CannotDropBombError(Exception):
    """Error raised when a Player tries to plant a bomb unsuccessfully"""


class Player:
    """Represents a game player"""

    __slots__ = {
        "position": "(Position) Position at which the player is located",
        "current_bomb_count": "(int) Number of bombs planted",
        "bomb_range": "(int) Range of a bomb explosion blast",
        "max_bomb_count": "(int) Maximum amount of bombs that can be planted",
    }

    def __init__(
        self, position: Position, bomb_range: int, max_bomb_count: int
    ) -> None:
        """Initialize player data

        :param position: Player's position
        :param max_bomb_count: Maximum amount of bombs that can be planted
        :param current_bomb_count: Number of active bombs planted
        :param bomb_range: Range of a bomb explosion blast
        """
        if max_bomb_count is None:
            max_bomb_count = game_config.player_bomb_count
        if bomb_range is None:
            bomb_range = game_config.player_bomb_range
        self.position = position
        self.current_bomb_count = 0
        self.bomb_range = bomb_range
        self.max_bomb_count = max_bomb_count

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, action: PlayerAction, environment: Environment, time: float) -> None:
        """Apply effects of the player's actions on the game environment

        :param action: Actions performed by the player on this tick
        :param environment: Game environment
        :param time: Current time
        """
        if (
            action & PlayerAction.PLANT_BOMB
            and self.current_bomb_count < self.max_bomb_count
            and not any(bomb.position == self.position for bomb in environment.bombs)
            # # Is it possible for the player to be standing on a cell that
            # # is unsuitable for planting a bomb?
            # self.environment.map[player.position] == MapCell.EMPTY
        ):
            environment.plant_bomb(self.position, self, self.bomb_range, time)
            self.current_bomb_count += 1

        new_position = self.position
        if action & PlayerAction.MOVE_UP:
            new_position = new_position.up()
        if action & PlayerAction.MOVE_DOWN:
            new_position = new_position.down()
        if action & PlayerAction.MOVE_RIGHT:
            new_position = new_position.right()
        if action & PlayerAction.MOVE_LEFT:
            new_position = new_position.left()

        if environment.map[new_position] in (MapCell.EMPTY, MapCell.SPAWN):
            self.position = new_position
