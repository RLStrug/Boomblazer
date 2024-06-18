"""Stores the software version of the game

Constants:
    VERSION_TUPLE: tuple[int, int, int]
        The major, minor, and patch version as a tuple
    VERSION: str
        The major, minor, and patch version as a str
    GAME_NAME: str
        The name of the game
"""

VERSION_TUPLE = (0, 5, 1)
VERSION = ".".join([str(n) for n in VERSION_TUPLE])
GAME_NAME = "Boomblazer"
