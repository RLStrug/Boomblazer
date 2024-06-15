#!/usr/bin/env python3
"""Test the correct behaviour of boomblazer.map_environment
"""

import io

from boomblazer.entity.player import Player
from boomblazer.map_environment import MapEnvironment


player_1 = Player("p1")
player_2 = Player("p2")
map_io = io.StringIO(
    "#V1\n"
    "XXXXX\n"
    "XA BX\n"
    "XXXXX\n"
)

map_1 = MapEnvironment.from_io_data(map_io, [player_1, player_2])
print(map_1)

json_map = map_1.to_json(indent=4)
print(json_map)

map_2 = MapEnvironment.from_json(json_map)
print(map_2)
