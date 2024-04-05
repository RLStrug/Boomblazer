"""Implements the explosion fire blast in the game

Classes:
    Fire:
        Implements a fire blast resulting from a bomb explosion that will
        dissipate after a fixed amount of time

Type aliases:
    FireDict:
        Result of the conversion from a Fire to a dict
    FireMapping:
        Mapping that can be used to create a Fire

Exception classes:
    FireError: Exception
        A Fire instance may raise this exception when something unexpected
        occurs
"""

from typing import Dict
from typing import Mapping
from typing import Sequence
from typing import Tuple
from typing import Union

from boomblazer.config import config


class FireError(Exception):
    """Error raised when something goes wrong within a Fire instance
    """


FireDict = Dict[str, Union[Tuple[int, int], int]]
FireMapping = Mapping[str, Union[Sequence[int], int]]


class Fire:
    """Implements a fire blast that will dissipate after a fixed amount of time

    When a fire blast is instanciated, it will automatically disspate after a
    fixed amount of game ticks. It will kill players that cross its path.

    Members:
        _x: int
            The column (horizontal position) at which the fire blast is located
        _y: int
            The row (vertical position) at which the fire blast is located
        _tick: int
            The number of game ticks left before the fire blast dissipate

    Class methods:
        from_dict:
            Instanciates a Fire from a dict

    Special methods:
        __init__:
            Initializes a new fire blast

    Methods:
        decrement_tick:
            Decrements the number of ticks left before the fire blast
            dissipates
        to_dict:
            Returns the current instance data in the form of a dict
    
    Properties:
        position: (Read only)
            The X and Y coordinates of the fire blast
        tick: (Read only)
            The number of game ticks left before the fire blast dissipates
    """

    def __init__(
            self, position: Tuple[int, int],
            tick: int = config.server.fire_timer_ticks
    ) -> None:
        """Initializes a new fire blast

        Parameters:
            position: Sequence[int] (length = 2)
                The first element will determine the X coordinate.
                The second element will determine the Y coordinate
        """
        self._x, self._y = position
        self._tick = tick

    # ---------------------------------------- #
    # FIRE TICK
    # ---------------------------------------- #
    def decrement_tick(self) -> None:
        """Decrements the number of ticks left before the fire blast dissipates

        Raises:
            FireError:
                When the number of game ticks before dissipation is already
                lesser or equal to 0
        """
        if self._tick > 0:
            self._tick -= 1
        else:
            raise FireError(
                "This fire should have been extinguished as his tick is null!"
            )

    # ---------------------------------------- #
    # GETTERS / SETTERS
    # ---------------------------------------- #
    @property
    def position(self) -> Tuple[int, int]:
        """Returns the X and Y coordinates of the fire blast

        Return value: tuple[int, int]
            A tuple containing the X and Y coordinates of the fire blast
        """
        return self._x, self._y

    @property
    def tick(self) -> int:
        """Returns the number of game ticks left before the fire dissipates

        Return value:
            The number of game ticks left before the fire blast dissipates
        """
        return self._tick

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #
    @classmethod
    def from_dict(cls, data: FireMapping) -> "Fire":
        """Instanciates a Fire from a dict

        Parameters:
            data: FireMapping
                A mapping that should contain the following keys and values:
                    position: Sequence[int] (length = 2)
                        The X and Y coordinates of the bomb
                    tick: int
                        The number of remaining ticks befaure explosion

        Return value: Fire
            A fire instance initialized from the data in data
        """
        return cls(data["position"], data["tick"])

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #
    def to_dict(self) -> FireDict:
        """Returns the current instance data in the form of a dict

        Return value: FireDict
            A dictionary containing the position, and the number of ticks
            remaining before the fire is extinguished
        """
        return {
            "position": self.position,
            "tick": self._tick,
        }
