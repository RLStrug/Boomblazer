# #!/usr/bin/env python3
# """Tests the correct behaviour of boomblazer.game_handler
# """
#
# import io
#
# from boomblazer.entity.player import Player
# from boomblazer.map_environment import MapEnvironment
# from boomblazer.game_handler import GameHandler
# from boomblazer.game_handler import MoveActionEnum
#
# player_1 = Player("1")
# player_2 = Player("2", max_bomb_count=10)
#
# map_io = io.StringIO(
# "#V1\n"
# "XXXXX\n"
# "XA  X\n"
# "X + X\n"
# "X  BX\n"
# "XXXXX\n"
# )
#
# map_environment = MapEnvironment.from_io_data(map_io, [player_1, player_2])
# game_handler = GameHandler(map_environment)
#
# def step_enter(actions):
# input("Press <Enter> to continue")
# game_handler.tick(actions)
# print(game_handler.map_environment)
#
# step_enter([(player_1, False, MoveActionEnum.MOVE_DOWN)])
#
# step_enter([(player_1, True, MoveActionEnum.MOVE_RIGHT)])
#
# for _ in range(40):
# step_enter([(player_1, False, MoveActionEnum.MOVE_RIGHT)])
#
# step_enter([(player_1, True, MoveActionEnum.MOVE_LEFT)])
# for _ in range(40):
# step_enter([(player_1, False, MoveActionEnum.DONT_MOVE)])
#
# step_enter([(player_2, False, MoveActionEnum.MOVE_UP)])
# for _ in range(20):
# step_enter([(player_2, True, MoveActionEnum.MOVE_LEFT)])
#
# for _ in range(40):
# step_enter([(player_2, False, MoveActionEnum.DONT_MOVE)])
