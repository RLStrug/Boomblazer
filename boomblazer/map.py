"""Implements a game map

Enumerations:
    MapCell:
        Represents a cell content on the map

Classes:
    Map:
        The game map data

Type aliases:
    MapDict:
        Result of the conversion from a Map to a dict

Exception classes:
    MapError: Exception
        Error raised when a Map intialization data is invalid
"""

import enum
import pathlib
from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any
from typing import Optional
from typing import TextIO
from typing import TypedDict

from boomblazer.entity.position import Position


class MapError(Exception):
    """Error raised when a Map intialization data is invalid

    This can happen if the map version number is missing, the map environment
    is too high or too large, the environment contains invalid cells, too many
    players are registered
    """


class MapCell(enum.Enum):
    """Represents a cell content on the map
    """
    WALL = "#"  # not destructible wall
    BOX = "+"  # destructible
    EMPTY = " "
    SPAWN = "S"


MapDict = TypedDict(
    "MapDict",
    {
        "version": int,
        "data": list[str],
    }
)


class Map:
    """Represents a game map current state

    Members:
        version: int
            The map version number. This ensures compatibility between server,
            clients, and map file
        _data: list[list[MapCell]]
            The map cells data

    Class methods:
        from_io_data:
            Instanciates a Map from IO data
        from_file:
            Instanciates a Map from a file
        from_dict:
            Instanciates a Map from a dict

    Special methods:
        __init__:
            Initializes a game Map
        __iter__:
            Iterates over map rows
        __getitem__:
            Gets a cell from the map
        __setitem__:
            Sets a cell from the map
        __str__:
            Returns a printable representation of the map

    Methods:
        to_dict:
            Returns the current instance data in the form of a dict
    """

    __slots__ = ("version", "_data",)

    def __init__(
            self, version: int = 0,
            data: Optional[list[list[MapCell]]] = None,
    ) -> None:
        """Initializes a game Map

        Parameters:
            version: int (default = 0)
                The map version number. This ensures compatibility between
                server, clients, and map file
            data: list[list[MapCell]] (default = [[]])
                The map cells data
        """
        self.version = version
        self._data = data or [[]]

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_io_data(cls, map_io: TextIO) -> "Map":
        """Instanciates a Map from IO data

        Parameters:
            map_io: TextIO
                IO object containing the initial map data

        Return value: Map
            A Map instance initialized from the IO data
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
            data = [
                [MapCell(cell) for cell in line.rstrip("\r\n")]
                for line in map_io
            ]
        except ValueError as exc:
            raise MapError("Unknown map cell value") from exc

        map_ = cls(version_number, data)
        return map_

    @classmethod
    def from_file(cls, map_filepath: pathlib.Path) -> "Map":
        """Instanciates a Map from a file

        Used by the server when starting a new game

        Parameters:
            map_filepath: pathlib.Path
                Path to the file containing the initial map data

        Return value: Map
            A Map instance initialized from the file
        """
        try:
            with open(map_filepath, "r", encoding="utf8") as map_file:
                return cls.from_io_data(map_file)
        except OSError as exc:
            raise MapError(f"Cannot open {str(map_filepath)!r}") from exc

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Map":
        """Instanciates a Map from a dict

        Used as intermediate constructor from JSON data

        Parameters:
            data: Mapping[str, Any]
                A mapping that should contain the following keys and values:
                    version: int
                        The map version number
                    data: Sequence[Sequence[str]]
                        The map current environment state

        Return value: Map
            A Map instance initialized from data
        """
        map_data = [
            [MapCell(cell) for cell in row]
            for row in data["data"]
        ]
        return cls(
            version=int(data["version"]),
            data=map_data,
        )

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> MapDict:
        """Returns the current instance data in the form of a dict

        Return value: MapDict
            A dictionary containing the map version number, and the cells data
        """
        return MapDict({
            "version": self.version,
            "data": [
                "".join(cell.value for cell in row) for row in self._data
            ],
        })

    # ---------------------------------------- #
    # CELL GET/SET
    # ---------------------------------------- #

    def __getitem__(self, position: Position) -> MapCell:
        """Gets a cell from the map

        Parameters:
            position: Position
                The coordinates of the cell to fetch
        """
        return self._data[position.y][position.x]

    def __setitem__(self, position: Position, value: MapCell) -> None:
        """Sets a cell from the map

        Parameters:
            position: Position
                The coordinates of the cell to update
            value: MapCell
                The new value of the selected cell
        """
        self._data[position.y][position.x] = MapCell(value)

    # ---------------------------------------- #
    # SPECIAL FUNCTIONS
    # ---------------------------------------- #

    def __iter__(self) -> Iterator[list[MapCell]]:
        """Iterates over map rows

        Return value: Iterator[list[MapCell]]
            An Iterator that yields the map rows
        """
        return iter(self._data)

    def __str__(self) -> str:
        """Returns a printable representation of the map

        Return value:
            A printable representation of the map
        """
        return "\n".join(
            "".join(cell.value for cell in row)
            for row in self._data
        )
