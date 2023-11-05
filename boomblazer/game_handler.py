"""Handles the game state

Enumerations:
    MoveActionEnum: Enum
        Represents the movements performed by players

Classes:
    GameHandler:
        Handles a game by updating its state tick by tick
"""

from enum import Enum
from typing import Iterable
from typing import List
from typing import Tuple

from bomb import Bomb
from fire import Fire
from map import Map
from map import MapCellEnum
from player import CannotDropBombError
from player import Player


class MoveActionEnum(Enum):
    """Represents the movements performed by players"""
    DONT_MOVE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4


class GameHandler:
    """Handles a game by updating its state tick by tick

    Members:
        _map: Map
            The current game map state

    Special methods:
        __init__:
            Initializes the game state

    Methods:
        tick:
            Updates the game state to the next tick
        _explode_bomb:
            Detonates a bomb, spawing Fire objects on the map
        _treat_exploded_boxes:
            Removes boxes destroyed by a bomb explosion from the map

    Properties:
        map: (Read only)
            The current game map state
    """

    __slots__ = ("_map",)

    def __init__(self, map_: Map) -> None:
        """Initializes a new game state

        Parameters:
            map_: Map
                The starting state of the game map
        """
        self._map = map_

    # ---------------------------------------- #
    # RUN GAME
    # ---------------------------------------- #
    # TODO Separate in smaller methods
    def tick(self, *actions: Tuple[Player, bool, MoveActionEnum]) -> None:
        """Updates the game state to the next tick

        This will update the game map, players, bombs and fire blasts

        Parameters:
            actions (variadic positionals): tuple[Player, bool, MoveActionEnum]
                Represent the action of a player during this tick
                The first member of the tuple is the player performing the
                action
                The second is True if the player is planting a bomb, else False
                The third is the player's movement
        """

        # treat players' actions
        dropped_bombs = []
        for player, drop_bomb, move in actions:
            if player not in self._map.players:
                continue
            px, py = player.position
            # if cell is fire, do not drop because player will be killed
            if (drop_bomb and not self._map.bomb_here((px, py)) and
                    self._map[(px, py)] == MapCellEnum.EMPTY):
                try:
                    dropped_bombs.append(player.create_bomb())
                except CannotDropBombError:
                    pass
            if move == MoveActionEnum.MOVE_UP:
                if self._map[(px, py-1)] == MapCellEnum.EMPTY:
                    player.position = (px, py-1)
            elif move == MoveActionEnum.MOVE_DOWN:
                if self._map[(px, py+1)] == MapCellEnum.EMPTY:
                    player.position = (px, py+1)
            elif move == MoveActionEnum.MOVE_RIGHT:
                if self._map[(px+1, py)] == MapCellEnum.EMPTY:
                    player.position = (px+1, py)
            elif move == MoveActionEnum.MOVE_LEFT:
                if self._map[(px-1, py)] == MapCellEnum.EMPTY:
                    player.position = (px-1, py)

        # decrement bomb ticks, treat explosions and update list of bombs
        new_bombs = []
        exploded_boxes_coord = []
        fires_from_bombs = []
        for bomb in self._map.bombs:
            bomb.decrement_tick()
            if bomb.tick == 0:
                tmp_bombs, tmp_fire = self._explode_bomb(bomb)
                exploded_boxes_coord += tmp_bombs
                fires_from_bombs += tmp_fire
                if bomb.player is not None:
                    bomb.player.decrement_current_bomb_count()
                del bomb
            else:
                new_bombs.append(bomb)
        self._map.bombs = new_bombs + dropped_bombs
        # treat all exploded boxes after because multiple explosions break only 1 box
        self._treat_exploded_boxes(exploded_boxes_coord)

        # decrement fire ticks
        new_fires = []
        for fire in self._map.fires:
            fire.decrement_tick()
            if fire.tick > 0:
                new_fires.append(fire)
            else:
                del fire
        self._map.fires = new_fires + fires_from_bombs

        # kill players
        new_players = []
        for player in self._map.players:
            if self._map.fire_here(player.position):
                del player
            else:
                new_players.append(player)
        self._map.players = new_players

    # ---------------------------------------- #
    # HELPERS
    # ---------------------------------------- #
    # TODO Create type alias Coord = Tuple[int, int]
    # TODO Simplify logic to avoid copied code
    def _explode_bomb(
        self, bomb: Bomb
    ) -> Tuple[List[Tuple[int, int]], List[Fire]]:
        """Detonates a bomb, spawing Fire objects on the map

        Parameters:
            bomb: Bomb
                The bomb that is exploding

        Return value: tuple[list[tuple[int, int], list[Fire]]
            A list of all the coordinates of destroyed boxes,
            and a list of the Fire objects created by the explosion
        """

        exploded_boxes_coord = []
        fires = [Fire(bomb.position)]

        b_range = bomb.bomb_range
        x, y = bomb.position
        # direction: right
        for r in range(1, b_range+1):  # until range is reached
            cell = self._map[(x + r, y)]
            if cell == MapCellEnum.WALL:
                break
            elif cell == MapCellEnum.BOX:
                exploded_boxes_coord.append((x + r, y))
                fires.append(Fire((x + r, y)))
                break
            elif cell == MapCellEnum.EMPTY:
                fires.append(Fire((x + r, y)))

        # direction: left
        for r in range(1, b_range + 1):  # until range is reached
            cell = self._map[(x - r, y)]
            if cell == MapCellEnum.WALL:
                break
            elif cell == MapCellEnum.BOX:
                exploded_boxes_coord.append((x - r, y))
                fires.append(Fire((x - r, y)))
                break
            elif cell == MapCellEnum.EMPTY:
                fires.append(Fire((x - r, y)))

        # direction: up
        for r in range(1, b_range + 1):  # until range is reached
            cell = self._map[(x, y + r)]
            if cell == MapCellEnum.WALL:
                break
            elif cell == MapCellEnum.BOX:
                exploded_boxes_coord.append((x, y + r))
                fires.append(Fire((x, y + r)))
                break
            elif cell == MapCellEnum.EMPTY:
                fires.append(Fire((x, y + r)))

        # direction: down
        for r in range(1, b_range + 1):  # until range is reached
            cell = self._map[(x, y - r)]
            if cell == MapCellEnum.WALL:
                break
            elif cell == MapCellEnum.BOX:
                exploded_boxes_coord.append((x, y - r))
                fires.append(Fire((x, y - r)))
                break
            elif cell == MapCellEnum.EMPTY:
                fires.append(Fire((x, y - r)))

        return exploded_boxes_coord, fires

    def _treat_exploded_boxes(
        self, boxes_coord: Iterable[Tuple[int, int]]
    ) -> None:
        """Removes boxes destroyed by a bomb explosion from the map

        Parameters:
            boxes_coord: Iterable[Tuple[int, int]]
                The coordinates of all boxes destroyed by an explosion
        """

        for box in boxes_coord:
            self._map[box] = MapCellEnum.EMPTY

    # ---------------------------------------- #
    # GETTERS / SETTERS
    # ---------------------------------------- #
    @property
    def map(self):
        """Return the current game map state

        Return value: Map
            The current game map state
        """
        return self._map


def __test_module() -> None:
    """Test the correct behaviour of GameHandler"""

    player_1 = Player("1")
    player_2 = Player("2", max_bomb_count=10)
    map_ = Map.from_file("map.txt", [player_1, player_2])
    game_handler = GameHandler(map_)
    print(map_)

    def step_enter(*actions):
        input()
        game_handler.tick(*actions)
        print(game_handler.map)

    step_enter((player_1, False, MoveActionEnum.MOVE_DOWN))

    step_enter((player_1, True, MoveActionEnum.MOVE_RIGHT))

    for _ in range(40):
        step_enter((player_1, False, MoveActionEnum.MOVE_RIGHT))

    step_enter((player_1, True, MoveActionEnum.MOVE_LEFT))
    for _ in range(40):
        step_enter((player_1, False, MoveActionEnum.DONT_MOVE))

    step_enter((player_2, False, MoveActionEnum.MOVE_UP))
    for _ in range(20):
        step_enter((player_2, True, MoveActionEnum.MOVE_LEFT))

    for _ in range(40):
        step_enter((player_2, False, MoveActionEnum.DONT_MOVE))


if __name__ == "__main__":
    __test_module()
