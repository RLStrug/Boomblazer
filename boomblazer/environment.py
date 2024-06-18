"""Implements a game environment

Classes:
    Environment:
        The current game environment state

Type aliases:
    EnvironmentDict:
        Result of the conversion from a Environment to a dict

Exception classes:
    EnvironmentError: Exception
        Error raised when a Environment intialization data is invalid
"""

import contextlib
import json
from collections.abc import Mapping
from typing import Any
from typing import Optional
from typing import TypedDict
from typing import Union

from boomblazer.entity.bomb import Bomb
from boomblazer.entity.bomb import BombDict
from boomblazer.entity.fire import Fire
from boomblazer.entity.fire import FireDict
from boomblazer.entity.player import Player
from boomblazer.entity.player import PlayerDict
from boomblazer.entity.position import Position
from boomblazer.map import Map
from boomblazer.map import MapCell
from boomblazer.map import MapDict


EnvironmentDict = TypedDict(
    "EnvironmentDict",
    {
        "map": MapDict, "players": list[PlayerDict], "boxes": list[Position],
        "bombs": list[BombDict], "fires": list[FireDict]
    }
)


class Environment:
    """Represents a game environment current state

    An instance of this class contains data about everything on the map.
    This includes spawn points, players, boxes, bombs, fire blasts and the map
    itself.

    Members:
        map: Map
            The map
        spawn_points: list[Position]
            The current map environment state
        boxes: list[Position]
            The boxes currently present on the map
        bombs: list[Bomb]
            The bombs currently planted on the map
        players: list[Player]
            The currently living players
        fires: list[Fire]
            The currently active fire blasts

    Class methods:
        from_dict:
            Instanciates a Environment from a dict
        from_json:
            Instanciates a Environment from json data

    Special methods:
        __init__:
            Initializes a game Environment

    Methods:
        load_map:
            Loads the map cells, and extracts boxes and spawn points
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
    """

    __slots__ = ("map", "spawn_points", "boxes", "bombs", "players", "fires")

    def __init__(
            self, map_: Optional[Map] = None,
    ) -> None:
        """Initializes a game Environment

        Parameters:
            map: Optional[Map] (default = None)
                The map data. If not None, it will extract spawn points and
                boxes from the map cells
        """
        if map_ is not None:
            self.load_map(map_)
        else:
            self.map = Map()
            self.spawn_points: list[Position] = []
            self.boxes: list[Position] = []

        self.players: list[Player] = []
        self.bombs: list[Bomb] = []
        self.fires: list[Fire] = []

    def load_map(self, map_: Map) -> None:
        """Loads the map cells, and extracts boxes and spawn points

        Parameters:
            map_: Map
                The map data
        """
        self.map = map_
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell is MapCell.BOX:
                    # self.map[Position(x, y)] = MapCell.EMPTY  # XXX Later
                    self.boxes.append(Position(x, y))
                elif cell is MapCell.SPAWN:
                    self.map[Position(x, y)] = MapCell.EMPTY
                    self.spawn_points.append(Position(x, y))

    # ---------------------------------------- #
    # IMPORT
    # ---------------------------------------- #

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Environment":
        """Instanciates a Environment from a dict

        Used as intermediate constructor from JSON data

        Parameters:
            data: Mapping[str, Any]
                A mapping that should contain the following keys and values:
                    map: MapDict
                        The map data
                    players: Iterable[PlayerDict]
                        The currently living players
                    boxes: Iterable[Position]
                        The boxes currently on the map
                    bombs: Iterable[BombDict]
                        The bombs currently planted
                    fires: Iterable[FireDict]
                        The fire blasts currently raging

        Return value: Environment
            A Environment instance initialized from data
        """
        environment = Environment()
        environment.map = Map.from_dict(data["map"])
        environment.players = [
                Player.from_dict(player) for player in data["players"]
        ]
        environment.boxes = [
            Position(*box) for box in data["boxes"]
        ]
        environment.bombs = [
            Bomb.from_dict(bomb, environment.players) for bomb in data["bombs"]
        ]
        environment.fires =  [
            Fire.from_dict(fire) for fire in data["fires"]
        ]
        return environment

    @classmethod
    def from_json(
            cls, json_str: Union[str, bytes, bytearray], *args, **kwargs
    ) -> "Environment":
        """Instanciates a Environment from json data

        Used when a client recieves an update from the server

        Parameters:
            json_str: str | bytes | bytearray
                JSON data representing the map current environment state
            *args:
                positional arguments to pass to json.loads
            **kwargs:
                keyword arguments to pass to json.loads

        Return value: Environment
            A Environment instance initialized from the JSON data
        """
        json_data = json.loads(json_str, *args, **kwargs)
        return cls.from_dict(json_data)

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> EnvironmentDict:
        """Returns the current instance data in the form of a dict

        Return value: EnvironmentDict
            A dictionary containing the map version number, the environment
            state, the living players, and the planted bombs
        """
        return EnvironmentDict({
            "map": self.map.to_dict(),
            "boxes": self.boxes,
            "players": [player.to_dict() for player in self.players],
            "bombs": [bomb.to_dict() for bomb in self.bombs],
            "fires": [fire.to_dict() for fire in self.fires],
        })

    def to_json(self, *args, **kwargs) -> str:
        """Returns the current instance data in the form of json data

        Parameters:
            *args:
                positional arguments to pass to json.loads
            **kwargs:
                keyword arguments to pass to json.loads

        Return value: str
            Serialized Environment data as a JSON object
        """
        return json.dumps(self.to_dict(), *args, **kwargs)

    # ---------------------------------------- #
    # BOMBS
    # ---------------------------------------- #

    def bomb_here(self, position: tuple[int, int]) -> bool:
        """Tells if there is a bomb at given position

        Parameters:
            position: tuple[int, int]
                The position to check

        Return value: bool
            True if a bomb is planted a position, False otherwise
        """
        return any(b.position == position for b in self.bombs)

    # ---------------------------------------- #
    # PLAYERS
    # ---------------------------------------- #

    def add_player(self, player_name: str) -> Optional[Player]:
        """Adds a player to the game environment

        Parameters:
            player_name: str
                The name of the player

        Return value: Optional[Player]
            The player if it could be added to the players list, None otherwise
        """
        if len(self.spawn_points) < len(self.players):
            return None
        player = Player(player_name)
        self.players.append(player)
        return player

    def remove_player(self, player: Player) -> None:
        """Removes a player from the game environment

        Will fail silently if the player does not exist

        Parameters:
            player: Player
                The player to remove
        """
        with contextlib.suppress(ValueError):
            self.players.remove(player)

    def spawn_players(self) -> None:
        """Moves all players to their spawn points
        """
        for player, spawn_point in zip(self.players, self.spawn_points):
            player.position = spawn_point

    # ---------------------------------------- #
    # FIRE
    # ---------------------------------------- #

    def fire_here(self, position: tuple[int, int]) -> bool:
        """Tells if there is a fire blast at given position

        Parameters:
            position: tuple[int, int]
                The position to check

        Return value: bool
            True if a fire blast is raging a position, False otherwise
        """
        return any(f.position == position for f in self.fires)

    # ---------------------------------------- #
    # OTHERS
    # ---------------------------------------- #

    def __str__(self) -> str:
        """Returns a printable representation of the map environment state

        Return value:
            A printable representation of the map environment state
        """
        map_str = [[cell.value for cell in row] for row in self.map]
        for player in self.players:
            pos = player.position
            map_str[pos[1]][pos[0]] = player.name[0]
        # for box in self.boxes:  # XXX Later
        #     pos = box
        #     map_str[pos[1]][pos[0]] = "+"
        for bomb in self.bombs:
            pos = bomb.position
            map_str[pos[1]][pos[0]] = "o"
        for fire in self.fires:
            pos = fire.position
            map_str[pos[1]][pos[0]] = "*"
        return "\n".join(["".join(row) for row in map_str])
