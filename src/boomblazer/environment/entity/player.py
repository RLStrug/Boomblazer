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


class PlayerAction(enum.Flag):
    """Actions that can be performed by a player"""

    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()
    PLANT_BOMB = enum.auto()


class CannotDropBombError(Exception):
    """Error raised when a Player tries to plant a bomb unsuccessfully"""


class PlayerDict(typing.TypedDict):
    """Serialization of a Player"""

    name: str
    position: Position
    max_bomb_count: int
    current_bomb_count: int
    bomb_range: int


class Player:
    """Represents a game player"""

    __slots__ = {
        "name": "(str) Player's name",
        "position": "(Position) Position at which the player is located",
        "max_bomb_count": "(int) Maximum amount of bombs that can be planted",
        "current_bomb_count": "(int) Number of bombs planted",
        "bomb_range": "(int) Range of a bomb explosion blast",
    }

    def __init__(
        self,
        name: str,
        position: Position = Position(0, 0),
        *,
        max_bomb_count: int | None = None,
        current_bomb_count: int = 0,
        bomb_range: int | None = None,
    ) -> None:
        """Initialize player data

        :param name: Player's name
        :param position: Player's position
        :param max_bomb_count: Maximum amount of bombs that can be planted
        :param current_bomb_count: Number of active bombs planted
        :param bomb_range: Range of a bomb explosion blast
        """
        if max_bomb_count is None:
            max_bomb_count = game_config.player_bomb_count
        if bomb_range is None:
            bomb_range = game_config.player_bomb_range
        self.name = name
        self.position = position
        self.max_bomb_count = max_bomb_count
        self.current_bomb_count = current_bomb_count
        self.bomb_range = bomb_range

    # ---------------------------------------- #
    # BOMBS
    # ---------------------------------------- #

    def create_bomb(self) -> Bomb:
        """Tries to plant a bomb at player's position

        :returns: The newly planted Bomb
        :raises CannotDropBombError: If max number of planted bombs is reached
        """
        if self.current_bomb_count >= self.max_bomb_count:
            raise CannotDropBombError
        self.current_bomb_count += 1
        return Bomb(self.position, self, self.bomb_range)

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, action: PlayerAction, environment: "Environment") -> None:
        """Apply effects of the player's actions on the game environment

        :param action: Actions performed by the player on this tick
        :param environment: Game environment
        """
        if (
            action & PlayerAction.PLANT_BOMB
            and self.current_bomb_count < self.max_bomb_count
            # # Is it truly useful to forbid planting a bomb on top of
            # # another? To prevent planting multiple bombs by accident?
            # not self.environment.bomb_here(player.position) and
            # # Is it possible for the player to be standing on a cell that
            # # is unsuitable for planting a bomb?
            # self.environment.map[player.position] == MapCell.EMPTY
        ):
            new_bomb = self.create_bomb()
            environment.bombs.append(new_bomb)

        new_position = self.position
        if action & PlayerAction.MOVE_UP:
            new_position = new_position.up()
        if action & PlayerAction.MOVE_DOWN:
            new_position = new_position.down()
        if action & PlayerAction.MOVE_RIGHT:
            new_position = new_position.right()
        if action & PlayerAction.MOVE_LEFT:
            new_position = new_position.left()

        if environment.map[new_position] == MapCell.EMPTY:
            self.position = new_position

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Player":
        """Instanciates a Player from a dict

        :param data: A mapping that be like PlayerDict
        :returns: Player instance initialized from data
        """
        return cls(
            name=str(data["name"]),
            position=Position(*data["position"]),
            max_bomb_count=int(data["max_bomb_count"]),
            current_bomb_count=int(data["current_bomb_count"]),
            bomb_range=int(data["bomb_range"]),
        )

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> PlayerDict:
        """Returns the current instance data serialized

        :returns: Serialized Player
        """
        return PlayerDict(
            name=self.name,
            position=self.position,
            max_bomb_count=self.max_bomb_count,
            current_bomb_count=self.current_bomb_count,
            bomb_range=self.bomb_range,
        )
