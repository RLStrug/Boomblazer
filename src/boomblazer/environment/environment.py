"""Implements a game environment"""

from __future__ import annotations

import collections
import typing

from ..config.game import game_config
from .entity.bomb import Bomb
from .entity.fire import Fire
from .entity.player import Player
from .entity.player import PlayerAction
from .map import Map
from .map import MapCell
from .map import NULL_MAP
from .position import Position
from .position import NULL_POSITION

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


class Environment:
    """Represents a game environment current state

    An instance of this class contains data about everything on the map.
    This includes spawn points, players, boxes, bombs, fire blasts and the map
    itself.
    """

    __slots__ = {
        "map": "(Map) Map data",
        "spawn_points": "(set[Position]) Players spawn points",
        "boxes": "(set[Position]) Boxes currently present on the map",
        "bombs": "(collections.deque[Bomb]) Bombs currently planted on the map",
        "players": "(dict[int, Player]) Currently living players",
        "fires": "(collections.deque[Fire]) Currently active fire blasts",
    }

    def __init__(self) -> None:
        """Initializes a game Environment"""
        self.spawn_points: set[Position] = set()
        self.boxes: set[Position] = set()
        self.players: dict[int, Player] = {}
        self.bombs: collections.deque[Bomb] = collections.deque()
        self.fires: collections.deque[Fire] = collections.deque()

        self.map = NULL_MAP

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
                    # XXX self.map[Position(x, y)] = MapCell.EMPTY
                    self.spawn_points.add(Position(x, y))

    def spawn_player(self, id_: int, spawn_point: Position) -> None:
        """Spawns a new player into the environment

        :param id_: the player's id
        :param spawn_point: The player's spawn point
        """
        self.players[id_] = Player(
            spawn_point, game_config.player_bomb_range, game_config.player_bomb_count
        )

    def plant_bomb(
        self, position: Position, player: Player, range_: int, time: float
    ) -> None:
        """Adds a bomb to the environment and compute its explosion time

        :param position: The position at which the bomb is planted
        :param player: The player who planted the bomb
        :param range_: The bomb explosion range
        :param time: The time at which the bomb is planted
        """
        self.bombs.append(
            Bomb(position, player, range_, time + game_config.bomb_timer_seconds)
        )

    def blast_fire(self, position: Position, time: float) -> None:
        """Adds a fire blast to the environment and compute when it will extinguish

        :param position: The position at which the fire rages
        :param time: The time at which the fire was blasted
        """
        self.fires.append(Fire(position, time + game_config.fire_timer_seconds))

    # ---------------------------------------- #
    # GAME LOGIC
    # ---------------------------------------- #

    def tick(self, players_actions: Mapping[int, PlayerAction], time: float) -> None:
        """Updates the game environment state

        :param players_actions: Actions to be performed by players
        :param time: Current time
        """
        for player_id, player in self.players.items():
            # Pass dead players
            if player.position is NULL_POSITION:
                continue
            player_action = players_actions.get(player_id, PlayerAction(0))
            player.tick(player_action, self, time)

        for bomb in self.bombs:
            bomb.tick(self, time)
        while len(self.bombs) > 0 and self.bombs[0].timer <= time:
            self.bombs.popleft()

        for fire in self.fires:
            fire.tick(self, time)
        while len(self.fires) > 0 and self.fires[0].timer <= time:
            self.fires.popleft()

    # ---------------------------------------- #
    # OTHERS
    # ---------------------------------------- #

    def __str__(self) -> str:
        """Returns a printable representation of the game environment

        :returns: Printable representation of the map environment state
        """
        map_str = [[cell.value for cell in row] for row in self.map]
        for player in self.players.values():
            pos = player.position
            map_str[pos.y][pos.x] = "P"
        # for box in self.boxes:  # XXX Later
        #     pos = box
        #     map_str[pos[1]][pos[0]] = "+"
        for bomb in self.bombs:
            pos = bomb.position
            map_str[pos.y][pos.x] = "o"
        for fire in self.fires:
            pos = fire.position
            map_str[pos.y][pos.x] = "*"
        return "\n".join(["".join(row) for row in map_str])
