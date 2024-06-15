"""Implements a game map environment

Enumerations:
    MapCellEnum:
        Represents a cell content on the map

Classes:
    MapEnvironment:
        The current game map environment state

Type aliases:
    MapEnvironmentDict:
        Result of the conversion from a MapEnvironment to a dict

Exception classes:
    MapEnvironmentError: Exception
        Error raised when a MapEnvironment intialization data is invalid
"""

import enum
import json
import pathlib
import string
from collections.abc import Collection
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import TextIO
from typing import TypedDict
from typing import Union

from boomblazer.entity.bomb import Bomb
from boomblazer.entity.bomb import BombDict
from boomblazer.entity.fire import Fire
from boomblazer.entity.fire import FireDict
from boomblazer.entity.player import Player
from boomblazer.entity.player import PlayerDict
from boomblazer.entity.position import Position


class MapEnvironmentError(Exception):
    """Error raised when a MapEnvironment intialization data is invalid

    This can happen if the map version number is missing, the map environment
    is too high or too large, the environment contains invalid cells, too many
    players are registered
    """


class MapCellEnum(enum.Enum):
    """Represents a cell content on the map
    """
    WALL = "X"  # not destructible wall
    BOX = "+"  # destructible
    EMPTY = " "
    # fire = "*"  # fire created by an explosion


MapEnvironmentDict = TypedDict(
    "MapEnvironmentDict",
    {
        "version": int, "state": list[str], "players": list[PlayerDict],
        "bombs": list[BombDict], "fires": list[FireDict]
    }
)


class MapEnvironment:
    """Represents a game map environment current state

    An instance of this class contains data about everything on the map.
    This includes players, bombs, fire blasts and the map environment.

    Class constants:
        MAX_WIDTH: int
            The maximum width allowed for a map environment
        MAX_HEIGHT: int
            The maximum height allowed for a map environment
        MAX_NUMBER_OF_PLAYERS: int
            The maximum number of players that can play on one map
        __SPAWN_CHARS: list[str]
            The characters that represent players spaww points on map init data
        __ALLOWED_CHARS: list[str]
            All the allowed characters on map init data

    Members:
        _version: int
            The map version number. This ensures compatibility between server,
            clients, and map file
        _state: list[list[MapCellEnum]]
            The current map environment state
        _bombs: list[Bomb]
            The bombs currently planted on the map
        _players: list[Player]
            The currently living players
        _fires: list[Fire]
            The currently active fire blasts

    Class methods:
        from_file:
            Instanciates a MapEnvironment from a file
        from_dict:
            Instanciates a MapEnvironment from a dict
        from_json:
            Instanciates a MapEnvironment from json data

    Special methods:
        __init__:
            Initializes a game MapEnvironment
        __getitem__Environment:
            Gets a cell from the current map environment state
        __setitem__:
            Sets a cell from the current map environment state
        __str__:
            Returns a printable representation of the map environment state

    Methods:
        _init_v0:
            Initializes a list of players without environment data
        _init_v1:
            Initializes a game MapEnvironment version 1
        to_dict:
            Returns the current instance data in the form of a dict
        to_json:
            Returns the current instance data in the form of json data
        bomb_here:
            Tells if there is a bomb at given position
        fire_here:
            Tells if there is a fire blast at given position
        _init_players_position:
            Move players to their respective spawn points

    Properties:
        version (read-only:
            The map version number
        state:
            The current map environment state
        bombs:
            The bombs currently planted on the map
        players:
            The currently living players
        fires:
            The currently active fire blasts
    """

    __slots__ = ("_version", "_state", "_bombs", "_players", "_fires")

    # PARAMETERS
    MAX_WIDTH = 50
    MAX_HEIGHT = 20
    MAX_NUMBER_OF_PLAYERS = 6

    __SPAWN_CHARS = list(string.ascii_uppercase[:MAX_NUMBER_OF_PLAYERS])
    __ALLOWED_CHARS = [e.value for e in MapCellEnum] + __SPAWN_CHARS

    def __init__(
            self, version: int,
            state: Sequence[Sequence[MapCellEnum]] = ((),),
            players: Iterable[Player] = (),
            bombs: Iterable[Bomb] = (),
            fires: Iterable[Fire] = ()
    ) -> None:
        """Initializes a game MapEnvironment

        Parameters:
            version: int
                The map version number. This ensures compatibility between
                server, clients, and map file
            state: Sequence[Sequence[MapCellEnum]] (default = ((),) )
                The current map environment state
            players: Iterable[Player] (default = () )
                The currently living players
            bombs: Iterable[Bomb] (default = () )
                The bombs currently planted on the map
            fires: Iterable[Fire] (default = () )
                The fire blasts currently raging on the map
        """
        self._version = version
        self._state = [list(row) for row in state]
        self._players = list(players)
        self._bombs = list(bombs)
        self._fires = list(fires)

        # TODO Remove _init_vX? Check empty state?
        # check version
        if self._version == 0:
            # Only contains the players list
            self._init_v0(players)
        elif self._version == 1:
            self._init_v1(state, players, bombs, fires)
        else:
            raise NotImplementedError(
                f"Map version {version} is not implemented yet"
            )

    def _init_v0(self, players: Iterable[Player]) -> None:
        """Initializes a list of players without environment data

        Parameters:
            players: Iterable[Player]
                The currently living players
        """
        self._players = list(players)

    def _init_v1(
            self, state: Sequence[Sequence[MapCellEnum]],
            players: Iterable[Player], bombs: Iterable[Bomb],
            fires: Iterable[Fire]
    ) -> None:
        """Initializes a MapEnvironment version 1

        Parameters:
            state: Sequence[Sequence[MapCellEnum]]
                The current map environment state
            players: Iterable[Player]
                The currently living players
            bombs: Iterable[Bomb]
                The bombs currently planted on the map
            fires: Iterable[Fire]
                The fire blasts currently raging on the map
        """
        self._state = [list(row) for row in state]
        self._players = list(players)
        if bombs is None:
            bombs = []
        self._bombs = list(bombs)
        if fires is None:
            fires = []
        self._fires = list(fires)

        # check size
        if len(self._state) > self.MAX_HEIGHT:
            raise MapEnvironmentError("Map high as fuck")
        if any(len(i) > self.MAX_WIDTH for i in self._state):
            raise MapEnvironmentError("Map wide as your mama")


    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_io_data(
            cls, map_io: TextIO, players: Collection[Player]
    ) -> "MapEnvironment":
        """Instanciates a MapEnvironment from IO data

        Used by the server when starting a new game

        Parameters:
            map_io: TextIO
                IO object containing the initial map data
            players: Collection[Player]
                Players that joined the game

        Return value: MapEnvironment
            A MapEnvironment instance initialized from the file
        """
        # get version number
        version_tag = map_io.readline()
        if not version_tag.startswith("#V"):
            raise MapEnvironmentError(
                "Map file must start with version number (e.g. '#V1')"
            )
        try:
            version_number = int(version_tag[2:])
        except ValueError as exc:
            raise MapEnvironmentError(
                "Version number should be a number... >:("
            ) from exc

        # XXX Find better way
        data = map_io.read().splitlines()

        # check content
        if any(
                cell not in cls.__ALLOWED_CHARS
                for row in data for cell in row
        ):
            raise MapEnvironmentError("Bad characters in map")

        # create state
        state: list[list[MapCellEnum]] = [
            [
                MapCellEnum.EMPTY if cell in cls.__SPAWN_CHARS
                else MapCellEnum(cell)
                for cell in row
            ]
            for row in data
        ]

        # create players
        if len(players) > len(cls.__SPAWN_CHARS):
            raise MapEnvironmentError("Too many players")

        map_environment = cls(version_number, state, players)
        map_environment._init_players_position(data)

        return map_environment

    @classmethod
    def from_file(
            cls, map_filename: pathlib.Path, players: Collection[Player]
    ) -> "MapEnvironment":
        """Instanciates a MapEnvironment from a file

        Used by the server when starting a new game

        Parameters:
            map_filename: pathlib.Path
                Path to the file containing the initial map data
            players: Iterable[Player]
                Players that joined the game

        Return value: MapEnvironment
            A MapEnvironment instance initialized from the file
        """
        with open(map_filename, "r", encoding="utf8") as map_file:
            return cls.from_io_data(map_file, players)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MapEnvironment":
        """Instanciates a MapEnvironment from a dict

        Used as intermediate constructor from JSON data

        Parameters:
            data: Mapping[str, Any]
                A mapping that should contain the following keys and values:
                    version: int
                        The map version number
                    state: Sequence[Sequence[str]]
                        The map current environment state
                    players: Iterable[Mapping[str, Any]]
                        The currently living players
                    bombs: Iterable[Mapping[str, Any]]
                        The bombs currently planted
                    fires: Iterable[Mapping[str, Any]]
                        The fire blasts currently raging

        Return value: MapEnvironment
            A MapEnvironment instance initialized from data
        """
        state = [
            [
                MapCellEnum.EMPTY
                if cell in cls.__SPAWN_CHARS else MapCellEnum(cell)
                for cell in row
            ]
            for row in data["state"]
        ]
        players = [
            Player.from_dict(player) for player in data["players"]
        ]
        bombs = [
            Bomb.from_dict(bomb, players) for bomb in data["bombs"]
        ]
        fires =  [
            Fire.from_dict(fire) for fire in data["fires"]
        ]
        return cls(
            version=int(data["version"]),
            state=state,
            players=players,
            bombs=bombs,
            fires=fires
        )

    @classmethod
    def from_json(
            cls, json_str: Union[str, bytes, bytearray], *args, **kwargs
    ) -> "MapEnvironment":
        """Instanciates a MapEnvironment from json data

        Used when a client recieves an update from the server

        Parameters:
            json_str: str | bytes | bytearray
                JSON data representing the map current environment state
            *args:
                positional arguments to pass to json.loads
            **kwargs:
                keyword arguments to pass to json.loads

        Return value: MapEnvironment
            A MapEnvironment instance initialized from the JSON data
        """
        json_data = json.loads(json_str, *args, **kwargs)
        return cls.from_dict(json_data)

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> MapEnvironmentDict:
        """Returns the current instance data in the form of a dict

        Return value: MapEnvironmentDict
            A dictionary containing the map version number, the environment
            state, the living players, and the planted bombs
        """
        return MapEnvironmentDict({
            "version": self._version,
            "state": [
                "".join(cell.value for cell in row) for row in self._state
            ],
            "players": [player.to_dict() for player in self._players],
            "bombs": [bomb.to_dict() for bomb in self._bombs],
            "fires": [fire.to_dict() for fire in self._fires],
        })

    def to_json(self, *args, **kwargs) -> str:
        """Returns the current instance data in the form of json data

        Parameters:
            *args:
                positional arguments to pass to json.loads
            **kwargs:
                keyword arguments to pass to json.loads

        Return value: str
            Serialized MapEnvironment data as a JSON object
        """
        return json.dumps(self.to_dict(), *args, **kwargs)

    # ---------------------------------------- #
    # CELL GET/SET
    # ---------------------------------------- #

    def __getitem__(self, position: Position) -> MapCellEnum:
        """Gets a cell from the current map environment state

        Parameters:
            position: Position
                The coordinates of the cell to fetch
        """
        return self._state[position.y][position.x]

    def __setitem__(
            self, position: Position, value: MapCellEnum
    ) -> None:
        """Sets a cell from the current map environment state

        Parameters:
            position: tuple[int, int]
                The coordinates of the cell to update
            value: MapCellEnum
                The new value of the selected cell
        """
        self._state[position.y][position.x] = value

    # ---------------------------------------- #
    # VERSION
    # ---------------------------------------- #
    @property
    def version(self) -> int:
        """Returns the map version number

        Return value: int
            The map version number
        """
        return self._version

    # ---------------------------------------- #
    # BOMBS
    # ---------------------------------------- #
    @property
    def bombs(self) -> list[Bomb]:
        """Returns the bombs currently planted on the map

        Return value: list[Bomb]
            The bombs currently planted on the map
        """
        return self._bombs

    @bombs.setter
    def bombs(self, value: list[Bomb]) -> None:
        """Sets the bombs currently planted on the map

        Parameters:
            value: list[Bomb]
                The bombs currently planted on the map
        """
        self._bombs = value

    def bomb_here(self, position: tuple[int, int]) -> bool:
        """Tells if there is a bomb at given position

        Parameters:
            position: tuple[int, int]
                The position to check

        Return value: bool
            True if a bomb is planted a position, False otherwise
        """
        return any(b.position == position for b in self._bombs)

    # ---------------------------------------- #
    # PLAYERS
    # ---------------------------------------- #
    @property
    def players(self) -> list[Player]:
        """Returns the currently living players

        Return value: list[Player]
            The currently living players
        """
        return self._players

    @players.setter
    def players(self, value: list[Player]):
        """Sets the currently living players

        Parameters:
            value: list[Player]
                The currently living players
        """
        self._players = value

    # ---------------------------------------- #
    # FIRE
    # ---------------------------------------- #
    @property
    def fires(self) -> list[Fire]:
        """Returns the currently active fire blasts

        Return value: list[Fire]
            The currently active fire blasts
        """
        return self._fires

    @fires.setter
    def fires(self, value: list[Fire]) -> None:
        """Sets the currently active fire blasts

        Parameters:
            value: list[Fire]
                The currently active fire blasts
        """
        self._fires = value

    def fire_here(self, position: tuple[int, int]) -> bool:
        """Tells if there is a fire blast at given position

        Parameters:
            position: tuple[int, int]
                The position to check

        Return value: bool
            True if a fire blast is raging a position, False otherwise
        """
        return any(f.position == position for f in self._fires)

    # ---------------------------------------- #
    # OTHERS
    # ---------------------------------------- #

    def _init_players_position(self, data: Sequence[Sequence[str]]) -> None:
        """Move players to their respective spawn points

        Used when initializing the map environment at game start

        Parameters:
            data:
                The map initial environment state, containing the players spawn
                points
        """
        to_spawn = self.__SPAWN_CHARS[:len(self._players)]
        for pos_y, row in enumerate(data):
            for pos_x, cell in enumerate(row):
                if cell in to_spawn:
                    num = to_spawn.index(cell)
                    self._players[num].position = Position(pos_x, pos_y)

    def __str__(self) -> str:
        """Returns a printable representation of the map environment state

        Return value:
            A printable representation of the map environment state
        """
        map_str = [[cell.value for cell in row] for row in self._state]
        for player in self._players:
            pos = player.position
            map_str[pos[1]][pos[0]] = player.name[0]
        for bomb in self._bombs:
            pos = bomb.position
            map_str[pos[1]][pos[0]] = "o"
        for fire in self._fires:
            pos = fire.position
            map_str[pos[1]][pos[0]] = "*"
        return "\n".join(["".join(row) for row in map_str])
