"""Implements the position of an entity in the game"""

import typing


class Position(typing.NamedTuple):
    """Represents a position in the game

    Members:
        x: int
            Column (horizontal position) at which the entity is located
        y: int
            Row (vertical position) at which the entity is located
    """

    x: int
    y: int

    def up(self, step: int = 1) -> "Position":
        """Returns a position up from the current position

        Parameters:
            step: int (default = 1)
                How much should the new position should be moved from the current

        Return value: Position
            Upwards position
        """
        return Position(self.x, self.y - step)

    def down(self, step: int = 1) -> "Position":
        """Returns a position down from the current position

        Parameters:
            step: int (default = 1)
                How much should the new position should be moved from the current

        Return value: Position
            Downwards position
        """
        return Position(self.x, self.y + step)

    def left(self, step: int = 1) -> "Position":
        """Returns a position left from the current position

        Parameters:
            step: int (default = 1)
                How much should the new position should be moved from the current

        Return value: Position
            Leftwards position
        """
        return Position(self.x - step, self.y)

    def right(self, step: int = 1) -> "Position":
        """Returns a position right from the current position

        Parameters:
            step: int (default = 1)
                How much should the new position should be moved from the current

        Return value: Position
            Rightwards position
        """
        return Position(self.x + step, self.y)
