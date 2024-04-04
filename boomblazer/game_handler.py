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
from typing import Optional
from typing import Sequence
from typing import Tuple

from boomblazer.entity.bomb import Bomb
from boomblazer.entity.fire import Fire
from boomblazer.map_environment import MapEnvironment
from boomblazer.map_environment import MapCellEnum
from boomblazer.entity.player import CannotDropBombError
from boomblazer.entity.player import Player


class MoveActionEnum(Enum):
    """Represents the movements performed by players
    """
    DONT_MOVE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4


class GameHandler:
    """Handles a game by updating its state tick by tick

    Members:
        _map_environment: MapEnvironment
            The current game map state

    Special methods:
        __init__:
            Initializes the game state

    Methods:
        tick:
            Updates the game state to the next tick
        _treat_players_actions:
            Treat players'actions for this tick (move or drop bomb)
        _update_bombs:
            Decrement the remaining ticks for all active bombs
        _update_fire_blasts:
            Decrement the remaining ticks for all raging fire blasts
        _kill_players:
            Kills players that are engulfed in a fire blast
        _explode_bomb:
            Detonates a bomb, spawing Fire objects on the map
        _treat_exploded_boxes:
            Removes boxes destroyed by a bomb explosion from the map

    Properties:
        map_environment: (Read only)
            The current game map environment state
    """

    __slots__ = ("_map_environment",)

    def __init__(
            self, map_environment: Optional[MapEnvironment] = None
    ) -> None:
        """Initializes a new game state

        Parameters:
            map_environment: MapEnvironment
                The starting state of the game map
        """
        if map_environment is None:
            self._map_environment = MapEnvironment(0)
        else:
            self._map_environment = map_environment

    # ---------------------------------------- #
    # RUN GAME
    # ---------------------------------------- #
    def tick(
            self, actions: Iterable[Tuple[Player, bool, MoveActionEnum]]
    ) -> None:
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
        dropped_bombs = self._treat_players_actions(actions)
        fires_from_bombs = self._update_bombs(dropped_bombs)
        self._update_fire_blasts(fires_from_bombs)
        self._kill_players()

    def _treat_players_actions(
            self, actions: Iterable[Tuple[Player, bool, MoveActionEnum]]
    ) -> List[Bomb]:
        """Treat players'actions for this tick (move or drop bomb)

        Parameters:
            actions (variadic positionals): tuple[Player, bool, MoveActionEnum]
                Represent the action of a player during this tick
                The first member of the tuple is the player performing the
                action
                The second is True if the player is planting a bomb, else False
                The third is the player's movement

        Return value: List[bomb]
            The bombs planted by players
        """
        dropped_bombs = []
        for player, drop_bomb, move in actions:
            if player not in self._map_environment.players:
                continue

            player_x, player_y = player.position
            # if cell is fire, do not drop because player will be killed
            if (
                    drop_bomb and
                    not self._map_environment.bomb_here((player_x, player_y)) and
                    self._map_environment[(player_x, player_y)] == MapCellEnum.EMPTY
            ):
                try:
                    dropped_bombs.append(player.create_bomb())
                except CannotDropBombError:
                    pass

            new_player_position = (player_x, player_y)
            if move == MoveActionEnum.MOVE_UP:
                new_player_position = (player_x, player_y - 1)
            elif move == MoveActionEnum.MOVE_DOWN:
                new_player_position = (player_x, player_y + 1)
            elif move == MoveActionEnum.MOVE_RIGHT:
                new_player_position = (player_x + 1, player_y)
            elif move == MoveActionEnum.MOVE_LEFT:
                new_player_position = (player_x - 1, player_y)

            if self._map_environment[new_player_position] == MapCellEnum.EMPTY:
                player.position = new_player_position

        return dropped_bombs

    def _update_bombs(self, dropped_bombs: Sequence[Bomb]) -> List[Fire]:
        """Decrement the remaining ticks for all active bombs

        Bombs that reach 0 will explode and generate fire blasts

        Parameters:
            dropped_bombs: Sequence[Bomb]
                Bombs that have been planted by players during this tick

        Return value: List[Fire]
            New fire blasts generated from bombs that exploded
        """
        new_bombs = []
        exploded_boxes_coord = []
        fires_from_bombs = []
        for bomb in self._map_environment.bombs:
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
        self._map_environment.bombs = new_bombs + dropped_bombs
        # treat all exploded boxes after because multiple explosions break only
        # one box
        self._treat_exploded_boxes(exploded_boxes_coord)

        return fires_from_bombs

    def _update_fire_blasts(self, fires_from_bombs: Sequence[Fire]) -> None:
        """Decrement the remaining ticks for all raging fire blasts

        Parameters:
            fires_from_bombs: Sequence[Fire]
                New fire blasts generated from bombs that exploded during this
                tick
        """
        new_fires = []
        for fire in self._map_environment.fires:
            fire.decrement_tick()
            if fire.tick > 0:
                new_fires.append(fire)
            else:
                del fire
        self._map_environment.fires = new_fires + fires_from_bombs

    def _kill_players(self) -> None:
        """Kills players that are engulfed in a fire blast
        """
        new_players = []
        for player in self._map_environment.players:
            if self._map_environment.fire_here(player.position):
                del player
            else:
                new_players.append(player)
        self._map_environment.players = new_players

    # ---------------------------------------- #
    # HELPERS
    # ---------------------------------------- #
    # TODO Create type alias Coord = Tuple[int, int]
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

        bomb_range = bomb.bomb_range
        bomb_x, bomb_y = bomb.position
        directions = (
            # DOWN,      UP,  RIGHT,   LEFT
            (0, 1), (0, -1), (1, 0), (-1, 0),
        )

        for move_x, move_y in directions:
            for distance in range(1, bomb_range + 1):
                blast_coords = (
                    bomb_x + (move_x * distance), bomb_y + (move_y * distance)
                )
                blasted_cell = self._map_environment[blast_coords]
                if blasted_cell is MapCellEnum.WALL:
                    break
                if blasted_cell is MapCellEnum.BOX:
                    exploded_boxes_coord.append(blast_coords)
                    fires.append(Fire(blast_coords))
                    break
                if blasted_cell is MapCellEnum.EMPTY:
                    fires.append(Fire(blast_coords))

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
            self._map_environment[box] = MapCellEnum.EMPTY

    # ---------------------------------------- #
    # GETTERS / SETTERS
    # ---------------------------------------- #
    @property
    def map_environment(self):
        """Returns the current game map state

        Return value: MapEnvironment
            The current game map state
        """
        return self._map_environment


def __test_module() -> None:
    """Tests the correct behaviour of GameHandler
    """

    player_1 = Player("1")
    player_2 = Player("2", max_bomb_count=10)
    map_environment = MapEnvironment.from_file("map.txt", [player_1, player_2])
    game_handler = GameHandler(map_environment)
    print(map_environment)

    def step_enter(actions):
        input()
        game_handler.tick(actions)
        print(game_handler.map_environment)

    step_enter([(player_1, False, MoveActionEnum.MOVE_DOWN)])

    step_enter([(player_1, True, MoveActionEnum.MOVE_RIGHT)])

    for _ in range(40):
        step_enter([(player_1, False, MoveActionEnum.MOVE_RIGHT)])

    step_enter([(player_1, True, MoveActionEnum.MOVE_LEFT)])
    for _ in range(40):
        step_enter([(player_1, False, MoveActionEnum.DONT_MOVE)])

    step_enter([(player_2, False, MoveActionEnum.MOVE_UP)])
    for _ in range(20):
        step_enter([(player_2, True, MoveActionEnum.MOVE_LEFT)])

    for _ in range(40):
        step_enter([(player_2, False, MoveActionEnum.DONT_MOVE)])


if __name__ == "__main__":
    __test_module()
