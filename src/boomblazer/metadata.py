"""Stores the package metadata

Constants:
    PACKAGE_NAME: str
        The name of this python package
    METADATA: importlib.metadata._adapteres.Message
        Mapping of all the metadata
    VERSION: str
        The major, minor, and patch version as a str
    GAME_NAME: str
        The name of the game
"""

import importlib.metadata

PACKAGE_NAME = "boomblazer"
METADATA = importlib.metadata.metadata(PACKAGE_NAME)

VERSION = METADATA["Version"]
GAME_NAME = METADATA["Name"]
