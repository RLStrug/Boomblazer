"""Implements the explosion fire in the game

Classes:
    Fire:
        The implementation of fire blast resulting from a Bomb explosion

Exception classes:
    FireError: Exception
        A Fire instance may raise this exception when something unexpected
        occurs
"""

from typing import Tuple


class FireError(Exception):
    """Error raised when something goes wrong within a Fire instance
    """


class Fire:
    """Implements a fire blast that will dissipate after a fixed amount of time

    When a fire blast is instanciated, it will automatically disspate after a
    fixed amount of game ticks. It will kill players that cross its path.

    Class constants:
        FIRE_TICKS_DELAY: int
            The amount of ticks after which the fire blast dissipates

    Members:
        _x: int
            The column (horizontal position) at which the fire blast is located
        _y: int
            The row (vertical position) at which the fire blast is located
        _tick: int
            The number of game ticks left before the fire blast dissipate

    Special methods:
        __init__:
            Initializes a new fire blast

    Methods:
        decrement_tick:
            Decrements the number of ticks left before the fire blast
            dissipates
    
    Properties:
        position: (Read only)
            The X and Y coordinates of the fire blast
        tick: (Read only)
            The number of game ticks left before the fire blast dissipates
    """

    FIRE_TICKS_DELAY: int = 5

    def __init__(self, position: tuple) -> None:
        """Initializes a new fire blast

        Parameters:
            position: Sequence[int] (length = 2)
                The first element will determine the X coordinate.
                The second element will determine the Y coordinate
        """
        self._x: int = position[0]
        self._y: int = position[1]
        self._tick: int = self.FIRE_TICKS_DELAY

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
