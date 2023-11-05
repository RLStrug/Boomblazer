"""Implements a game map environment

Enumerations:
    MapCellEnum:
        Represents a cell content on the map

Classes:
    Map:
        The current game map state

Type aliases:
    MapDict:
        Result of the conversion from a Map to a dict
    MapMapping:
        Mapping that can be used to create a Map

Exception classes:
    MapError: Exception
        Error raised when a Map intialization data is invalid
"""

import json
import string
from enum import Enum
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Sequence
from typing import Tuple
from typing import Union

from bomb import Bomb
from bomb import BombDict
from bomb import BombMapping
from fire import Fire
from player import Player
from player import PlayerDict
from player import PlayerMapping


class MapError(Exception):
    """Error raised when a Map intialization data is invalid

    This can happen if the map version number is missing, the map environment
    is too high or too large, the environment contains invalid cells, too many
    players are registered
    """


class MapCellEnum(Enum):
    """Represents a cell content on the map"""
    WALL = "X"  # not destructible wall
    BOX = "+"  # destructible
    EMPTY = " "
    # fire = "*"  # fire created by an explosion


MapMapping = Mapping[str, Union[
    int, Sequence[Sequence[str]], Sequence[PlayerMapping],
    Sequence[BombMapping]
]]
MapDict = Dict[str, Union[
    int, List[List[str]], List[PlayerDict],
    List[BombDict]
]]


class Map:
    """Represents a game map current state

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
        _players[Player]
            The currently living players
        _fires: list[Fire]
            The currently active fire blasts

    Class methods:
        from_file:
            Instanciates a Map from a file
        from_dict:
            Instanciates a Map from a dict
        from_json:
            Instanciates a Map from json data

    Special methods:
        __init__:
            Initializes a game Map
        __getitem__:
            Gets a cell from the current map environment state
        __setitem__:
            Sets a cell from the current map environment state
        __str__:
            Returns a printable representation of the map environment state

    Methods:
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
        self, version: int, state: Sequence[Sequence[MapCellEnum]],
        bombs: Iterable[Bomb], players: Iterable[Player]
    ) -> None:
        """Initializes a game Map

        Parameters:
            version: int
                The map version number. This ensures compatibility between
                server, clients, and map file
            state: Sequence[Sequence[MapCellEnum]]
                The current map environment state
            bombs: Iterable[Bomb]
                The bombs currently planted on the map
            players: Iterable[Player]
                The currently living players
        """
        self._version = version
        self._state = [list(row) for row in state]
        self._bombs = list(bombs)
        self._players = list(players)
        self._fires = []

        # check version
        if self._version != 1:
            raise NotImplementedError(
                "Map version other than 1 is not implemented yet"
            )

        # check size
        if len(self._state) > self.MAX_HEIGHT:
            raise MapError("Map high as fuck")
        if any(len(i) > self.MAX_WIDTH for i in self._state):
            raise MapError("Map wide as your mama")

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_file(cls, map_filename: str, players: Iterable[Player]) -> "Map":
        """Instanciates a Map from a file

        Used by the server when starting a new game

        Parameters:
            map_filename: str
                Path to teh file containing the initial map data
            players: Iterable[Player]
                Players that joined the game

        Return value: Map
            A map instance initialized from the file
        """
        with open(map_filename, "r", encoding="ascii") as map_file:
            data = map_file.read().splitlines()

        # get version number
        version_tag = data.pop(0)
        if not version_tag.startswith("#V"):
            raise MapError(
                "Map file must start with version number (e.g. '#V1')"
            )
        try:
            version_number = int(version_tag[2:])
        except ValueError as exc:
            raise MapError("Version number should be a number... >:(") from exc

        # check content
        if any(cell not in cls.__ALLOWED_CHARS for row in data for cell in row):
            raise MapError("Bad characters in map")

        # create state
        state: List[List[MapCellEnum]] = [
            [
                MapCellEnum.EMPTY
                if cell in cls.__SPAWN_CHARS else MapCellEnum(cell)
                for cell in row
            ]
            for row in data
        ]

        # create bombs list
        bombs: List[Bomb] = []

        # create players
        if len(players) > len(cls.__SPAWN_CHARS):
            raise MapError("Too many players")
        players: List[Player] = players

        map_ = cls(version_number, state, bombs, players)
        map_._init_players_position(data)

        return map_

    @classmethod
    def from_dict(cls, data: MapMapping) -> "Map":
        """Instanciates a Map from a dict

        Used as intermediate constructor from JSON data

        Parameters:
            data: MapMapping
                A mapping that should contain the following keys and values:
                    version: int
                        The map version number
                    state: Sequence[Sequence[str]]
                        The map current environment state
                    players: Iterable[Player]
                        The currently living players
                    bombs: Iterable[Bomb]
                        The bombs currently planted

        Return value: Map
            A map instance initialized from data
        """
        data2 = {
            "version": data["version"],
            "state": [
                [
                    MapCellEnum.EMPTY
                    if cell in cls.__SPAWN_CHARS else MapCellEnum(cell)
                    for cell in row
                ]
                for row in data["state"]
            ],
            "players": [Player.from_dict(p) for p in data["players"]],
        }
        # Bombs need to be attached to a player, so we need to reconstruct
        # bombs after players
        data2["bombs"] =  [
            Bomb.from_dict(b, data2["players"]) for b in data["bombs"]
        ]
        return cls(**data2)

    @classmethod
    def from_json(cls, json_str: str, *args, **kwargs) -> "Map":
        """Instanciates a Map from json data

        Used when a client recieves an update from the server

        Parameters:
            json_str: str
                JSON data representing the map current environment state
            *args:
                positional arguments to pass to json.loads
            **kwargs:
                keyword arguments to pass to json.loads

        Return value: Map
            A map instance initialized from the JSON data
        """
        json_data = json.loads(json_str, *args, **kwargs)
        return cls.from_dict(json_data)

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> MapDict:
        """Returns the current instance data in the form of a dict

        Return value: MapDict
            A dictionary containing the map version number, the environment
            state, the living players, and the planted bombs
        """
        return {
            "version": self._version,
            "state": [[cell.value for cell in row] for row in self._state],
            "bombs": [bomb.to_dict() for bomb in self._bombs],
            "players": [player.to_dict() for player in self._players],
        }

    def to_json(self, *args, **kwargs) -> str:
        """Returns the current instance data in the form of json data

        Parameters:
            *args:
                positional arguments to pass to json.loads
            **kwargs:
                keyword arguments to pass to json.loads

        Return value: str
            Serialized Map data as a JSON object
        """
        return json.dumps(self.to_dict(), *args, **kwargs)

    # ---------------------------------------- #
    # CELL GET/SET
    # ---------------------------------------- #

    def __getitem__(self, position: Tuple[int, int]) -> MapCellEnum:
        """Gets a cell from the current map environment state

        Parameters:
            position: tuple[int, int]
                The coordinates of the cell to fetch
        """
        return self._state[position[1]][position[0]]

    def __setitem__(
            self, position: Tuple[int, int], value: MapCellEnum
    ) -> None:
        """Sets a cell from the current map environment state

        Parameters:
            position: tuple[int, int]
                The coordinates of the cell to update
            value: MapCellEnum
                The new value of the selected cell
        """
        self._state[position[1]][position[0]] = value

    # ---------------------------------------- #
    # BOMBS
    # ---------------------------------------- #
    @property
    def bombs(self) -> List[Bomb]:
        """Returns the bombs currently planted on the map

        Return value: List[Bomb]
            The bombs currently planted on the map
        """
        return self._bombs

    @bombs.setter
    def bombs(self, value: List[Bomb]) -> None:
        """Sets the bombs currently planted on the map

        Parameters:
            value: List[Bomb]
                The bombs currently planted on the map
        """
        self._bombs = value

    def bomb_here(self, position: Tuple[int, int]) -> bool:
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
    def players(self) -> List[Player]:
        """Returns the currently living players

        Return value: List[Player]
            The currently living players
        """
        return self._players

    @players.setter
    def players(self, value: List[Player]):
        """Sets the currently living players

        Parameters:
            value: List[Player]
                The currently living players
        """
        self._players = value

    # ---------------------------------------- #
    # FIRE
    # ---------------------------------------- #
    @property
    def fires(self) -> List[Fire]:
        """Returns the currently active fire blasts

        Return value: List[Fire]
            The currently active fire blasts
        """
        return self._fires

    @fires.setter
    def fires(self, value: List[Fire]) -> None:
        """Sets the currently active fire blasts

        Parameters:
            value: List[Fire]
                The currently active fire blasts
        """
        self._fires = value

    def fire_here(self, position: Tuple[int, int]) -> bool:
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
                    self._players[num].position = (pos_x, pos_y)

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


def __test_module() -> None:
    """Test the correct behaviour of GameHandler"""

    player_1 = Player("p1")
    player_2 = Player("p2")
    map_1 = Map.from_file("res/maps/map.txt", [player_1, player_2])
    print(map_1)
    json_map = map_1.to_json(indent=4)
    print(json_map)
    map_2 = Map.from_json(json_map)
    print(map_2)


if __name__ == "__main__":
    __test_module()
