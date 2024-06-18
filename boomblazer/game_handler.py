"""Handles the game state

Classes:
    GameHandler:
        Handles a game by updating its state tick by tick
"""

import enum
from collections.abc import Iterable
from collections.abc import Sequence
from typing import Optional

from boomblazer.environment.entity.bomb import Bomb
from boomblazer.environment.entity.fire import Fire
from boomblazer.environment.environment import Environment
from boomblazer.environment.map import MapCell
from boomblazer.environment.entity.player import CannotDropBombError
from boomblazer.environment.entity.player import Player
from boomblazer.environment.entity.player import PlayerAction
from boomblazer.environment.position import Position


class GameHandler:
    """Handles a game by updating its state tick by tick

    Members:
        environment: Environment
            The current game environment state

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
    """

    __slots__ = ("environment",)

    def __init__(
            self, environment: Optional[Environment] = None
    ) -> None:
        """Initializes a new game state

        Parameters:
            environment: Environment
                The game environment state
        """
        if environment is None:
            environment = Environment()
        self.environment = environment

    # ---------------------------------------- #
    # RUN GAME
    # ---------------------------------------- #
    def tick(
            self, players_actions: Iterable[tuple[Player, PlayerAction]]
    ) -> None:
        """Updates the game state to the next tick

        This will update the game map, players, bombs and fire blasts

        Parameters:
            actions : Iterable[tuple[Player, PlayerAction]]
                Represent the action of players during this tick
                The first member of the tuple is the player performing the
                action
                The second is True if the player is planting a bomb, else False
                The third is the player's movement
        """
        dropped_bombs = self._treat_players_actions(players_actions)
        fires_from_bombs = self._update_bombs(dropped_bombs)
        self._update_fire_blasts(fires_from_bombs)
        self._kill_players()

    def _treat_players_actions(
            self, players_actions: Iterable[tuple[Player, PlayerAction]]
    ) -> list[Bomb]:
        """Treat players'actions for this tick (move or drop bomb)

        Parameters:
            players_actions : Iterable[tuple[Player, PlayerAction]]
                Represent the action of players during this tick
                The first member of the tuple is the player performing the
                action
                The second is True if the player is planting a bomb, else False
                The third is the player's movement

        Return value: list[bomb]
            The bombs planted by players
        """
        dropped_bombs = []
        for player, action in players_actions:
            if player not in self.environment.players:
                continue

            # if cell is fire, do not drop because player will be killed
            if (
                    action & PlayerAction.PLANT_BOMB and
                    not self.environment.bomb_here(player.position) and
                    self.environment.map[player.position] == MapCell.EMPTY
            ):
                try:
                    dropped_bombs.append(player.create_bomb())
                except CannotDropBombError:
                    pass

            new_player_position = player.position
            if action & PlayerAction.MOVE_UP:
                new_player_position = player.position.up()
            elif action & PlayerAction.MOVE_DOWN:
                new_player_position = player.position.down()
            elif action & PlayerAction.MOVE_RIGHT:
                new_player_position = player.position.right()
            elif action & PlayerAction.MOVE_LEFT:
                new_player_position = player.position.left()

            if self.environment.map[new_player_position] == MapCell.EMPTY:
                player.position = new_player_position

        return dropped_bombs

    def _update_bombs(self, dropped_bombs: Sequence[Bomb]) -> list[Fire]:
        """Decrement the remaining ticks for all active bombs

        Bombs that reach 0 will explode and generate fire blasts

        Parameters:
            dropped_bombs: Sequence[Bomb]
                Bombs that have been planted by players during this tick

        Return value: list[Fire]
            New fire blasts generated from bombs that exploded
        """
        active_bombs = []
        exploded_boxes = []
        fires_from_bombs = []
        for bomb in self.environment.bombs:
            bomb.decrement_tick()
            if bomb.tick == 0:
                boxes, fires = self._explode_bomb(bomb)
                exploded_boxes.extend(boxes)
                fires_from_bombs.extend(fires)
                if bomb.player is not None:
                    bomb.player.decrement_current_bomb_count()
            else:
                active_bombs.append(bomb)
        active_bombs.extend(dropped_bombs)
        self.environment.bombs = active_bombs
        # Treat all exploded boxes after because multiple explosions break only
        # one box
        self._treat_exploded_boxes(exploded_boxes)

        return fires_from_bombs

    def _update_fire_blasts(self, fires_from_bombs: Sequence[Fire]) -> None:
        """Decrement the remaining ticks for all raging fire blasts

        Parameters:
            fires_from_bombs: Sequence[Fire]
                New fire blasts generated from bombs that exploded during this
                tick
        """
        raging_fires = []
        for fire in self.environment.fires:
            fire.decrement_tick()
            if fire.tick > 0:
                raging_fires.append(fire)
        raging_fires.extend(fires_from_bombs)
        self.environment.fires = raging_fires

    def _kill_players(self) -> None:
        """Kills players that are engulfed in a fire blast
        """
        living_players = []
        for player in self.environment.players:
            if not self.environment.fire_here(player.position):
                living_players.append(player)
        self.environment.players = living_players

    # ---------------------------------------- #
    # HELPERS
    # ---------------------------------------- #
    def _explode_bomb(
        self, bomb: Bomb
    ) -> tuple[list[Position], list[Fire]]:
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

        directions = (
            bomb.position.up, bomb.position.down, bomb.position.left,
            bomb.position.right
        )

        for move in directions:
            for distance in range(1, bomb.bomb_range + 1):
                blast_coords = move(distance)
                blasted_cell = self.environment.map[blast_coords]
                if blasted_cell is MapCell.WALL:
                    break
                if blasted_cell is MapCell.BOX:
                    exploded_boxes_coord.append(blast_coords)
                    fires.append(Fire(blast_coords))
                    break
                if blasted_cell is MapCell.EMPTY:
                    fires.append(Fire(blast_coords))

        return exploded_boxes_coord, fires

    def _treat_exploded_boxes(
        self, boxes_coord: Iterable[Position]
    ) -> None:
        """Removes boxes destroyed by a bomb explosion from the map

        Parameters:
            boxes_coord: Iterable[tuple[int, int]]
                The coordinates of all boxes destroyed by an explosion
        """

        for box in boxes_coord:
            self.environment.map[box] = MapCell.EMPTY
