"""Implements the bombs in the game

Classes:
    Bomb:
        Implements a bomb that will explode after a fixed amount of time

Type aliases:
    BombDict:
        Result of the conversion from a Bomb to a dict

Exception classes:
    BombError: Exception
        A Bomb instance may raise this exception when something unexpected
        occurs
"""

import typing
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import Optional

from boomblazer.config.game import game_config
from boomblazer.environment.entity.fire import Fire
from boomblazer.environment.map import MapCell
from boomblazer.environment.position import Position

if typing.TYPE_CHECKING:
    from boomblazer.environment.entity.player import Player
    from boomblazer.environment.environment import Environment


class BombError(Exception):
    """Error raised when something goes wrong within a Bomb instance
    """


BombDict = typing.TypedDict(
    "BombDict",
    {"player": str, "position": Position, "range": int, "timer": int}
)


class Bomb:
    """Implements a bomb that will explode after a fixed amount of time

    When a bomb is instanciated, it will automatically explode after a fixed
    amount of game ticks. It will destroy boxes and kill players in its blast.

    Members:
        position: Position
            The position which the bomb is located
        player: Player
            The player who planted the bomb.
            This information is needed because each player can only plant so
            many bombs at a time.
            When the bomb explodes, the player will be notified that another
            bomb can be planted.
        range: int
            The range in blocks of the explosion blast
        timer: int
            The number of game ticks left before the bomb explodes

    Class methods:
        from_dict:
            Instanciates a Bomb from a dict

    Special methods:
        __init__:
            Initializes a newly planted bomb

    Methods:
        decrement_timer:
            Decrements the number of ticks left before the explosion
        to_dict:
            Returns the current instance data in the form of a dict
    """

    __slots__ = ("position", "player", "range", "timer",)

    def __init__(
            self, position: Position, player: "Player",
            range_: int, timer: Optional[int] = None
    ) -> None:
        """Initializes a newly planted bomb

        Parameters:
            position: Position
                The coordinates of the bomb
            player: Player
                The player who planted the bomb
            range_: int
                The range of the explosion blast
            timer: int
                The number of game ticks left before the bomb explodes
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
            self.position.up, self.position.down, self.position.left,
            self.position.right
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
            self.player.decrement_current_bomb_count()
        # # Treat all exploded boxes after because multiple explosions break
        # # only one box
        # self._treat_exploded_boxes(exploded_boxes)

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #
    @classmethod
    def from_dict(
            cls, data: Mapping[str, Any],
            players_list: Iterable["Player"]
    ) -> "Bomb":
        """Instanciates a Bomb from a dict

        Parameters:
            data: Mapping[str, Any]
                A mapping that should contain the following keys and values:
                    position: Sequence[int] (length = 2)
                        The X and Y coordinates of the bomb
                    player: str
                        The name of the player who planted the bomb
                    range: int
                        The range of the bomb blast
                    timer: int
                        The number of remaining ticks befaure explosion
            players_list: Iterable[Player]
                The players present in the game. This is used to find the owner
                of the bomb from the player's name

        Return value: Bomb
            A bomb instance initialized from the data in data

        Raises:
            BombError:
                When the player name in the dict cannot be associated to a
                player in `players_list`
        """
        for player in players_list:
            if player.name == data["player"]:
                break
        else:  # If the for loop finished without finding a matching player
            raise BombError(f"Cannot find owner of bomb ({data['player']})")

        return cls(
            position=Position(*data["position"]),
            player=player,
            range_=int(data["range"]),
            timer=int(data["timer"])
        )

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #
    def to_dict(self) -> BombDict:
        """Returns the current instance data in the form of a dict

        Return value: BombDict
            A dictionary containing the position, planter's name, range of
            the explosion blast of the bomb, and the number of ticks remaining
            before the explosion
        """
        return BombDict({
            "position": self.position,
            "player": self.player.name,
            "range": self.range,
            "timer": self.timer,
        })
