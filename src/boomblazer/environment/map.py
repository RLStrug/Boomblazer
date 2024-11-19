"""Implements a game map

Constants:
    NULL_MAP: Map
        Uninitialized Map
"""

from __future__ import annotations

import enum
import typing

from .position import Position

if typing.TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Mapping
    from importlib.resources.abc import Traversable
    from typing import Any
    from typing import IO


class MapError(Exception):
    """Error raised when a Map intialization data is invalid

    This can happen if the map version number is missing, the map environment
    is too high or too large, the environment contains invalid cells, too many
    players are registered
    """


class MapCell(enum.Enum):
    """Represents a cell content on the map"""

    WALL = "#"  # not destructible wall
    BOX = "+"  # destructible
    EMPTY = " "
    SPAWN = "S"


class Map:
    """Represents a game map current state"""

    __slots__ = {
        "version": "(int) Map version number",
        "_data": "(list[list[MapCell]]) Map cells",
    }

    def __init__(self, version: int, data: list[list[MapCell]]) -> None:
        """Initializes a game Map

        :param version: Map version number.
        :param data: Map cells data
        """
        self.version = version
        self._data = data

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_io_data(cls, map_io: IO[str]) -> "Map":
        """Instanciates a Map from IO data

        :param map_io: IO object containing the initial map data
        :returns: Map instance initialized from the IO data
        """
        # Get version number
        magic_string = "Boomblazer map version alpha "

        version_tag = map_io.readline()
        if not version_tag.startswith(magic_string):
            raise MapError(f"Map file must start with {magic_string}<N>")

        try:
            version_number = int(version_tag.removeprefix(magic_string))
        except ValueError as exc:
            raise MapError("Version number should be a number... >:(") from exc

        try:
            data = [[MapCell(cell) for cell in line.rstrip("\r\n")] for line in map_io]
        except ValueError as exc:
            raise MapError("Unknown map cell value") from exc

        map_ = cls(version_number, data)
        return map_

    @classmethod
    def from_file(cls, map_filepath: Traversable) -> "Map":
        """Instanciates a Map from a file

        :param map_filepath: Path to the file containing the initial map data
        :returns: A Map instance initialized from the file
        """
        try:
            with map_filepath.open("r", encoding="utf8") as map_file:
                return cls.from_io_data(map_file)
        except OSError as exc:
            raise MapError(f"Cannot open {str(map_filepath)!r}") from exc

    # ---------------------------------------- #
    # CELL GET/SET
    # ---------------------------------------- #

    def __getitem__(self, position: Position) -> MapCell:
        """Gets a cell from the map

        :param position: Coordinates of the cell to fetch
        """
        return self._data[position.y][position.x]

    def __setitem__(self, position: Position, value: MapCell) -> None:
        """Sets a cell from the map

        :param position: Coordinates of the cell to update
        :param value: New value of the selected cell
        """
        self._data[position.y][position.x] = MapCell(value)

    # ---------------------------------------- #
    # SPECIAL FUNCTIONS
    # ---------------------------------------- #

    def __iter__(self) -> Iterator[list[MapCell]]:
        """Iterates over map rows

        :returns: Iterator that yields the map rows
        """
        return iter(self._data)

    def __str__(self) -> str:
        """Returns a printable representation of the map

        :returns: Printable representation of the map
        """
        return "\n".join("".join(cell.value for cell in row) for row in self._data)


NULL_MAP = Map(0, [])
