"""Implements a game player

Classes:
    Player:
        Represents a game player

Type aliases:
    PlayerDict:
        Result of the conversion from a Player to a dict
    PlayerMapping:
        Mapping that can be used to create a Player

Exception classes:
    CannotDropBombError: Exception
        Error raised when a Player tries to plant a bomb unsuccessfully
"""

from typing import Dict
from typing import Mapping
from typing import Sequence
from typing import Tuple
from typing import Union

from boomblazer.config import config
from boomblazer.entity.bomb import Bomb


class CannotDropBombError(Exception):
    """Error raised when a Player tries to plant a bomb unsuccessfully
    """


PlayerDict = Dict[str, Union[str, Tuple[int, int], int]]
PlayerMapping = Mapping[str, Union[str, Sequence[int], int]]


class Player:
    """Represents a game player

    Members:
        _name: str
            The player's name
        _x: int
            The column (horizontal position) at which the player is located
        _y: int
            The row (vertical position) at which the player is located
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
        "_name", "_x", "_y", "_max_bomb_count", "_current_bomb_count",
        "_bomb_range",
    )

    def __init__(self, name: str, position: Tuple[int, int] = (0, 0), *,
            max_bomb_count: int = config.server.player_bomb_count,
            current_bomb_count: int = 0,
            bomb_range: int = config.server.player_bomb_range
    ) -> None:
        """Initialize the player data

        Parameters:
            name: str
                The player's name
            position: tuple[int, int], default=(0,0)
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
        self._name = name
        self._x, self._y = position
        self._max_bomb_count = max_bomb_count
        self._current_bomb_count = current_bomb_count
        self._bomb_range = bomb_range

    # ---------------------------------------- #
    # GETTERS / SETTERS
    # ---------------------------------------- #
    @property
    def position(self) -> Tuple[int, int]:
        """Returns The X and Y coordinates of the bomb

        Return value: Tuple[int, int]
            The X and Y coordinates of the bomb
        """
        return self._x, self._y

    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        """Sets The X and Y coordinates of the bomb

        Return value: Tuple[int, int]
            The X and Y coordinates of the bomb
        """
        if len(value) != 2 \
                or not isinstance(value[0], int) \
                or not isinstance(value[1], int):
            raise ValueError("A position is of type (int, int)!")
        self._x = value[0]
        self._y = value[1]

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
        return Bomb(self.position, self, self._bomb_range)

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
    # IMPORT
    # ---------------------------------------- #
    @classmethod
    def from_dict(cls, data: PlayerMapping) -> "Player":
        """Instanciates a Player from a dict

        Parameters:
            data: PlayerMapping
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
            name=data["name"], position=data["position"],
            max_bomb_count=data["max_bomb_count"],
            current_bomb_count=data["current_bomb_count"],
            bomb_range=data["bomb_range"]
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
        return {
            "name": self._name,
            "position": self.position,
            "max_bomb_count": self._max_bomb_count,
            "current_bomb_count": self._current_bomb_count,
            "bomb_range": self._bomb_range,
        }
