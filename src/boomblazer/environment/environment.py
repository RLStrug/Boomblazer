"""Implements a game environment"""

from __future__ import annotations

import collections
import contextlib
import json
import typing

from .entity.bomb import Bomb
from .entity.bomb import BombDict
from .entity.fire import Fire
from .entity.fire import FireDict
from .entity.player import Player
from .entity.player import PlayerAction
from .entity.player import PlayerDict
from .map import Map
from .map import MapCell
from .map import MapDict
from .position import Position

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


class EnvironmentDict(typing.TypedDict):
    """Environment serialization"""

    map: MapDict
    players: list[PlayerDict]
    boxes: list[Position]
    bombs: list[BombDict]
    fires: list[FireDict]


class Environment:
    """Represents a game environment current state

    An instance of this class contains data about everything on the map.
    This includes spawn points, players, boxes, bombs, fire blasts and the map
    itself.
    """

    __slots__ = {
        "map": "(Map) Map data",
        "spawn_points": "(list[Position]) Players spawn points",
        "boxes": "(set[Position]) Boxes currently present on the map",
        "bombs": "(collections.deque[Bomb]) Bombs currently planted on the map",
        "players": "(list[Player]) Currently living players",
        "fires": "(collections.deque[Fire]) Currently active fire blasts",
    }

    def __init__(
        self,
        map_: Map | None = None,
    ) -> None:
        """Initializes a game Environment

        :param map: Map data. If not None, extract spawn points and boxes from map cells
        """
        self.spawn_points: list[Position] = []
        self.boxes: set[Position] = set()
        self.players: list[Player] = []
        self.bombs: collections.deque[Bomb] = collections.deque()
        self.fires: collections.deque[Fire] = collections.deque()

        if map_ is not None:
            self.load_map(map_)
        else:
            self.map = Map()

    def load_map(self, map_: Map) -> None:
        """Loads map cells, and extracts boxes and spawn points

        :param map_: Map data
        """
        self.map = map_
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell is MapCell.BOX:
                    # self.map[Position(x, y)] = MapCell.EMPTY  # XXX Later
                    self.boxes.add(Position(x, y))
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

        :param data: A mapping that should be like EnvironmentDict
        :returns: Environment instance initialized from data
        """
        environment = Environment()
        environment.map = Map.from_dict(data["map"])
        environment.players = [Player.from_dict(player) for player in data["players"]]
        environment.boxes = {Position(*box) for box in data["boxes"]}
        environment.bombs = collections.deque(
            Bomb.from_dict(bomb, environment.players) for bomb in data["bombs"]
        )
        environment.fires = collections.deque(
            Fire.from_dict(fire) for fire in data["fires"]
        )
        return environment

    @classmethod
    def from_json(
        cls, json_str: str | bytes | bytearray, **kwargs: Any
    ) -> "Environment":
        """Instanciates a Environment from json data

        Used when a client recieves an update from the server

        :param json_str: JSON data representing the map current environment state
        :param **kwargs: keyword arguments to pass to json.loads
        :returns: Environment instance initialized from the JSON data
        """
        json_data = json.loads(json_str, **kwargs)
        return cls.from_dict(json_data)

    # ---------------------------------------- #
    # EXPORT
    # ---------------------------------------- #

    def to_dict(self) -> EnvironmentDict:
        """Returns the current instance data serialized

        :returns: Serialized Environment
        """
        return EnvironmentDict(
            map=self.map.to_dict(),
            boxes=list(self.boxes),
            players=[player.to_dict() for player in self.players],
            bombs=[bomb.to_dict() for bomb in self.bombs],
            fires=[fire.to_dict() for fire in self.fires],
        )

    def to_json(self, **kwargs: Any) -> str:
        """Returns the current instance data in the form of json data

        :param **kwargs: keyword arguments to pass to json.loads
        :returns: Serialized Environment data as a JSON object
        """
        return json.dumps(self.to_dict(), **kwargs)

    # ---------------------------------------- #
    # BOMBS
    # ---------------------------------------- #

    def bomb_here(self, position: tuple[int, int]) -> bool:
        """Tells if there is a bomb at given position

        :param position: Position to check
        :returns: True if a bomb is planted a position, False otherwise
        """
        return any(b.position == position for b in self.bombs)

    # ---------------------------------------- #
    # PLAYERS
    # ---------------------------------------- #

    def add_player(self, player_name: str) -> Player | None:
        """Adds a player to the game environment

        :param player_name: Name of the player
        :returns: Player, if it could be added to the players list, None otherwise
        """
        if len(self.spawn_points) < len(self.players):
            return None
        player = Player(player_name)
        self.players.append(player)
        return player

    def remove_player(self, player: Player) -> None:
        """Removes a player from the game environment

        Will fail silently if player does not exist

        :param player: Player to remove
        """
        with contextlib.suppress(ValueError):
            self.players.remove(player)

    def spawn_players(self) -> None:
        """Moves all players to their spawn points"""
        for player, spawn_point in zip(self.players, self.spawn_points):
            player.position = spawn_point

    # ---------------------------------------- #
    # FIRE
    # ---------------------------------------- #

    def fire_here(self, position: tuple[int, int]) -> bool:
        """Tells if there is a fire blast at given position

        :param position: Position to check
        :returns: True if a fire blast is raging a position, False otherwise
        """
        return any(f.position == position for f in self.fires)

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, players_actions: Mapping[Player, PlayerAction]) -> None:
        """Updates the game environment state

        :param players_actions: Actions to be performed by players
        """
        for player in self.players:
            player_action = players_actions.get(player, PlayerAction(0))
            player.tick(player_action, self)

        for bomb in self.bombs:
            bomb.tick(self)
        while len(self.bombs) > 0 and self.bombs[0].timer <= 0:
            self.bombs.popleft()

        for fire in self.fires:
            fire.tick(self)
        while len(self.fires) > 0 and self.fires[0].timer <= 0:
            self.fires.popleft()

    # ---------------------------------------- #
    # OTHERS
    # ---------------------------------------- #

    def __str__(self) -> str:
        """Returns a printable representation of the game environment

        :returns: Printable representation of the map environment state
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
