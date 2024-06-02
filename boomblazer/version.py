"""Stores the software version of the game

Constants:
    VERSION: tuple[int, int, int]
        The major, minor, and patch version as a tuple
    VERSION_STR: str
        The major, minor, and patch version as a str
    GAME_NAME: str
        The name of the game
"""

VERSION = (0, 4, 4)
VERSION_STR = ".".join([str(n) for n in VERSION])
GAME_NAME = "Boomblazer"
