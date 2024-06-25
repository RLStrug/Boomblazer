"""Implements the explosion fire blast in the game

Classes:
    Fire:
        Implements a fire blast resulting from a bomb explosion that will
        dissipate after a fixed amount of time

Type aliases:
    FireDict:
        Result of the conversion from a Fire to a dict

Exception classes:
    FireError: Exception
        A Fire instance may raise this exception when something unexpected
        occurs
"""

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import Optional
from typing import TypedDict
from typing import TYPE_CHECKING
from typing import Union

from boomblazer.config.game import game_config
from boomblazer.environment.position import Position

if TYPE_CHECKING:
    from boomblazer.environment.environment import Environment


class FireError(Exception):
    """Error raised when something goes wrong within a Fire instance
    """


FireDict = TypedDict("FireDict", {"position": Position, "timer": int})


class Fire:
    """Implements a fire blast that will dissipate after a fixed amount of time

    When a fire blast is instanciated, it will automatically disspate after a
    fixed amount of game ticks. It will kill players that cross its path.

    Members:
        _position: Position
            The position at which the fire blast is located
        _timer: int
            The number of game ticks left before the fire blast dissipate

    Class methods:
        from_dict:
            Instanciates a Fire from a dict

    Special methods:
        __init__:
            Initializes a new fire blast

    Methods:
        decrement_timer:
            Decrements the number of ticks left before the fire blast
            dissipates
        to_dict:
            Returns the current instance data in the form of a dict

    Properties:
        position: (Read only)
            The X and Y coordinates of the fire blast
        timer: (Read only)
            The number of game ticks left before the fire blast dissipates
    """

    __slots__ = ("_position", "_timer",)

    def __init__(
            self, position: Sequence[int],
            timer: Optional[int] = None
    ) -> None:
        """Initializes a new fire blast

        Parameters:
            position: Sequence[int] (length = 2)
                The coordinates of the fire blast
        """
        if timer is None:
            timer = game_config.fire_timer_ticks
        self._position = Position(*position)
        self._timer = timer

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, environment: "Environment") -> None:
        """Update fire blast timer and kill players engulfed in flames

        Parameters:
            environment: Environment
                The game environment
        """
        self._timer -= 1
        if self._timer <= 0:
            return

        environment.players = [
            player for player in environment.players
            if player.position != self.position
        ]

    # ---------------------------------------- #
    # GETTERS / SETTERS
    # ---------------------------------------- #

    @property
    def position(self) -> Position:
        """Returns the coordinates of the fire blast

        Return value: Position
            The coordinates of the fire blast
        """
        return self._position

    @property
    def timer(self) -> int:
        """Returns the number of game ticks left before the fire dissipates

        Return value:
            The number of game ticks left before the fire blast dissipates
        """
        return self._timer

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Fire":
        """Instanciates a Fire from a dict

        Parameters:
            data: Mapping[str, Any]
                A mapping that should contain the following keys and values:
                    position: Sequence[int] (length = 2)
                        The X and Y coordinates of the bomb
                    timer: int
                        The number of remaining ticks befaure explosion

        Return value: Fire
            A fire instance initialized from the data in data
        """
        return cls(
            position=Position(*data["position"]),
            timer=int(data["timer"])
        )

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> FireDict:
        """Returns the current instance data in the form of a dict

        Return value: FireDict
            A dictionary containing the position, and the number of ticks
            remaining before the fire is extinguished
        """
        return FireDict({
            "position": self.position,
            "timer": self._timer,
        })
