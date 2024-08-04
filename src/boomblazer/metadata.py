"""Stores the package metadata

Constants:
    PACKAGE_NAME: str
        Name of this python package
    METADATA: importlib.metadata._adapteres.Message
        Mapping of all the metadata
    VERSION: str
        Major, minor, and patch version as a str
    GAME_NAME: str
        Name of the game
"""

import importlib.metadata

PACKAGE_NAME = "boomblazer"
METADATA = importlib.metadata.metadata(PACKAGE_NAME)

VERSION = METADATA["Version"]
GAME_NAME = METADATA["Name"]
