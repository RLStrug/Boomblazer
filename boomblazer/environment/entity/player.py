"""Implements a game player

Enumerations:
    PlayerAction:
        Actions that can be performed by a player

Classes:
    Player:
        Represents a game player

Type aliases:
    PlayerDict:
        Result of the conversion from a Player to a dict

Exception classes:
    CannotDropBombError: Exception
        Error raised when a Player tries to plant a bomb unsuccessfully
"""

import enum
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypedDict

from boomblazer.config.game import game_config
from boomblazer.environment.entity.bomb import Bomb
from boomblazer.environment.map import MapCell
from boomblazer.environment.position import Position

if TYPE_CHECKING:
    from boomblazer.environment.environment import Environment


class PlayerAction(enum.Flag):
    """Actions that can be performed by a player
    """
    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()
    PLANT_BOMB = enum.auto()


class CannotDropBombError(Exception):
    """Error raised when a Player tries to plant a bomb unsuccessfully
    """


PlayerDict = TypedDict(
    "PlayerDict",
    {
        "name": str, "position": Position, "max_bomb_count": int,
        "current_bomb_count": int, "bomb_range": int
    }
)


class Player:
    """Represents a game player

    Members:
        _name: str
            The player's name
        _position: Position
            The position at which the player is located
        _max_bomb_count: int
            The current maximum amount of bombs a player can plant at the same
            time
        _current_bomb_count: int
            The current number of active bombs planted by the player
        _bomb_range: int
            The range in blocks of a bomb explosion blast

    Class methods:
        from_dict:
            Instanciates a Player from a dict

    Special methods:
        __init__:
            Initialize the player data

    Methods:
        create_bomb:
            Tries to plant a bomb at player's position
        increment_bomb_range:
            Makes the player's planted bombs have a larger blast range
        increment_max_bomb_count:
            Allows the player to plant more bombs at the same time
        decrement_max_bomb_count:
            Forces the player to plant less bombs at the same time

    Properties:
        name: (Read only)
            The player's name
        position:
            The X and Y coordinates of the bomb
        max_bomb_count: (Read only)
            The current maximum amount of bombs that can be planted at the same
            time
        current_bomb_count: (Read only)
            The current number of active bombs planted by the player
        bomb_range: (Read only)
            The range in blocks of the explosion blast
    """

    __slots__ = (
        "_name", "_position", "_max_bomb_count", "_current_bomb_count",
        "_bomb_range",
    )

    def __init__(self, name: str, position: Sequence[int] = (0, 0), *,
            max_bomb_count: Optional[int] = None,
            current_bomb_count: int = 0,
            bomb_range: Optional[int] = None
    ) -> None:
        """Initialize the player data

        Parameters:
            name: str
                The player's name
            position: Sequence[int] (length = 2), default=(0,0)
                The player's position

        Keyword only parameters:
            max_bomb_count:
                The current maximum amount of bombs the player can plant at the
                same time
            current_bomb_count: int
                The current number of active bombs planted by the player
            bomb_range: int
                The range in blocks of a bomb explosion blast
        """
        if max_bomb_count is None:
            max_bomb_count = game_config.player_bomb_count
        if bomb_range is None:
            bomb_range = game_config.player_bomb_range
        self._name = name
        self._position = Position(*position)
        self._max_bomb_count = max_bomb_count
        self._current_bomb_count = current_bomb_count
        self._bomb_range = bomb_range

    # ---------------------------------------- #
    # GETTERS / SETTERS
    # ---------------------------------------- #

    @property
    def position(self) -> Position:
        """Returns the player's coordinates

        Return value: Position
            The player's coordinates
        """
        return self._position

    @position.setter
    def position(self, value: Sequence[int]) -> None:
        """Sets the player's coordinates

        Parameters: Sequence[int] (length = 2)
            The player's coordinates
        """
        self._position = Position(*value)

    @property
    def name(self) -> str:
        """Returns the player's name

        Return value: str
            The player's name
        """
        return self._name

    @property
    def max_bomb_count(self) -> int:
        """Returns the current maximum amount of bombs that can be planted at
        the same time

        Return value: int
            The current maximum amount of bombs can plant at the same time
        """
        return self._max_bomb_count

    @property
    def current_bomb_count(self) -> int:
        """Returns the current number of active bombs planted by the player

        Return value: int
            The current number of active bombs planted by the player
        """
        return self._current_bomb_count

    @property
    def bomb_range(self) -> int:
        """Return the range in blocks of the explosion blast

        Return value:
            The range in blocks of the explosion blast
        """
        return self._bomb_range

    # ---------------------------------------- #
    # BOMBS
    # ---------------------------------------- #

    def create_bomb(self) -> Bomb:
        """Tries to plant a bomb at player's position

        Return value:
            The newly plated Bomb instance

        Raises:
            CannotDropBombError:
                When the player has already reached the max number of active
                bombs planted on the map
        """
        if self._current_bomb_count >= self._max_bomb_count:
            raise CannotDropBombError
        self._current_bomb_count += 1
        return Bomb(self._position, self, self._bomb_range)

    def increment_bomb_range(self) -> None:
        """Makes the player's planted bombs have a larger blast range
        """
        self._bomb_range += 1

    def increment_max_bomb_count(self) -> None:
        """Allows the player to plant more bombs at the same time
        """
        self._max_bomb_count += 1

    def decrement_current_bomb_count(self) -> None:
        """Forces the player to plant less bombs at the same time
        """
        self._current_bomb_count -= 1

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, action: PlayerAction, environment: "Environment") -> None:
        """Apply effects of the player's actions on the game environment

        Parameters:
            action: PlayerAction
                The actions performed by the player on this tick
            environment: Environment
                The game environment
        """
        if (
                action & PlayerAction.PLANT_BOMB and
                self._current_bomb_count < self._max_bomb_count
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

        Parameters:
            data: Mapping[str, Any]
                A mapping that should contain the following keys and values:
                    name: str
                        The player's name
                    position: Sequence[int] (length = 2)
                        The player's X and Y coordinates
                    max_bomb_count: int
                        The current maximum amount of bombs the player can
                        plant at the same time
                    current_bomb_count: int
                        The current number of active bombs planted by the
                        player
                    bomb_range: int
                        The range in blocks of a bomb explosion blast

        Return value: Player
            A player instance initialized from the data in data
        """
        return cls(
            name=str(data["name"]),
            position=Position(*data["position"]),
            max_bomb_count=int(data["max_bomb_count"]),
            current_bomb_count=int(data["current_bomb_count"]),
            bomb_range=int(data["bomb_range"])
        )

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> PlayerDict:
        """Returns the current instance data in the form of a dict

        Return value: PlayerDict
            A dictionary containing the position, player's name, position,
            maximum number of bombs that can be planted at the same time, the
            current number of active bombs planted, the player's bomb range
        """
        return PlayerDict({
            "name": self._name,
            "position": self.position,
            "max_bomb_count": self._max_bomb_count,
            "current_bomb_count": self._current_bomb_count,
            "bomb_range": self._bomb_range,
        })
