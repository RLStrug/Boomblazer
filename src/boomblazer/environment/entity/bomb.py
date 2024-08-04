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


class BombDict(typing.TypedDict):
    """Serialization of a Bomb"""

    player: str | None
    position: Position
    range: int
    timer: int


class Bomb:
    """Implements a bomb that will explode after a fixed amount of time

    When a bomb is instanciated, it will automatically explode after a fixed
    amount of game ticks. It will destroy boxes and kill players in its blast.
    """

    __slots__ = {
        "position": "(Position) Position which the bomb is located",
        "player": "(Player | None) Player who planted the bomb.",
        "range": "(int) Range of the explosion blast",
        "timer": "(int) Number of game ticks left before the bomb explodes",
    }

    def __init__(
        self,
        position: Position,
        player: Player | None,
        range_: int,
        timer: int | None = None,
    ) -> None:
        """Initializes a newly planted bomb

        Parameters:
            position: Position
                Coordinates of the bomb
            player: Player
                Player who planted the bomb
            range_: int
                Range of the explosion blast
            timer: int
                Number of game ticks left before the bomb explodes
        """
        if timer is None:
            timer = game_config.bomb_timer_ticks
        self.position = position
        self.player = player
        self.range = range_
        self.timer = timer

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #
    def tick(self, environment: "Environment") -> None:
        """Update bomb timer and apply its explosion effects on the environment

        Parameters:
            environment: Environment
                The game environment
        """
        self.timer -= 1
        if self.timer > 0:
            return

        environment.fires.append(Fire(self.position))

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

                environment.fires.append(Fire(blast_position))

                if blasted_cell is MapCell.BOX:
                    environment.map[blast_position] = MapCell.EMPTY
                    break

        if self.player is not None:
            self.player.current_bomb_count -= 1

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #
    @classmethod
    def from_dict(
        cls, data: Mapping[str, Any], players_list: Iterable["Player"]
    ) -> "Bomb":
        """Instanciates a Bomb from a dict

        Parameters:
            data: Mapping[str, Any]
                Mapping that should be like BombDict
            players_list: Iterable[Player]
                Players present in the game. This is used to find the bomb owner

        Return value: Bomb
            Bomb instance initialized from data
        """
        player: Player | None
        for player in players_list:
            if player.name == data["player"]:
                break
        else:  # If the for loop finished without finding a matching player
            player = None

        return cls(
            position=Position(*data["position"]),
            player=player,
            range_=int(data["range"]),
            timer=int(data["timer"]),
        )

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #
    def to_dict(self) -> BombDict:
        """Returns the current instance data serialized

        Return value: BombDict
            Serialized Bomb
        """
        player_name: str | None
        if self.player is None:
            player_name = None
        else:
            player_name = self.player.name

        return BombDict(
            position=self.position,
            player=player_name,
            range=self.range,
            timer=self.timer,
        )
