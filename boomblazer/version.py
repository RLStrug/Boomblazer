"""
Stores the software version of the game

Constants:
    version: tuple[int, int, int]
        The major, minor, and patch version as a tuple
    version_str: str
        The major, minor, and patch version as a str
"""
VERSION = (0, 1, 0)
VERSION_STR = ".".join([str(n) for n in VERSION])
