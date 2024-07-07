"""Configuration variables determining where game folders are located

Global variables:
    game_folders_config: _GameFoldersConfig
        Singleton of _GameFoldersConfig dataclass

Classes:
    _GameFoldersConfig:
        Dataclass containing the game folders location

Functions:
    _get_default_cache_folder:
        Returns the default location of the cache folder
    _get_default_log_folder:
        Returns the default location of the log folder
    _get_default_data_folder:
        Returns the default location of the data folder
    _get_default_map_folders:
        Returns the default list of map folders location
"""

import dataclasses
import pathlib
import platform
from collections.abc import Mapping
from typing import Any

from ..metadata import GAME_NAME
from .base_config import BaseConfig

def _get_default_cache_folder() -> pathlib.Path:
    """Returns the default location of the cache folder

    Return value: pathlib.Path
        The path where the cache folder should be
    """
    os = platform.system()
    if os == "Linux":
        ...
    if os == "Darwin":
        ...
    if os == "Windows":
        ...
    # else ("Java", ""): pass
    return pathlib.Path(".", f"{GAME_NAME}_data", "cache")

def _get_default_log_folder() -> pathlib.Path:
    """Returns the default location of the log folder

    Return value: pathlib.Path
        The path where the log folder should be
    """
    return _get_default_cache_folder() / "log"

def _get_default_data_folder() -> pathlib.Path:
    """Returns the default location of the data folder

    Return value: pathlib.Path
        The path where the data folder should be
    """
    os = platform.system()
    if os == "Linux":
        ...
    if os == "Darwin":
        ...
    if os == "Windows":
        ...
    # else ("Java", ""): pass
    return pathlib.Path(".", f"{GAME_NAME}_data", "share")

def _get_default_map_folders() -> list[pathlib.Path]:
    """Returns the default list of map folders location

    Return value: list[pathlib.Path]
        The list of paths where the map folders should be stored
    """
    return [
        pathlib.Path(".", "official_maps"),  # DEBUG
        _get_default_data_folder() / "official_maps",
        _get_default_data_folder() / "custom_maps",
    ]


@dataclasses.dataclass
class _GameFoldersConfig(BaseConfig):
    """Dataclass containing the game folders location

    Members:
        log_folder: pathlib.Path
            Folder containing log files
        map_folders: list[pathlib.Path]
            List of folders where map folders can be found
    """

    log_folder: pathlib.Path = dataclasses.field(
        default_factory=_get_default_log_folder
    )
    map_folders: list[pathlib.Path] = dataclasses.field(
        default_factory=_get_default_map_folders
    )

    # @override
    def load(self, new_field_values: Mapping[str, Any]) -> bool:
        """Loads field values from a dict

        Parameters:
            new_field_values: dict
                The names and new values of fields to be updated
                Unknown fields will be ignored

        Return value: bool
            True if all fields could be loaded from new_field_values.
            False if any field was missing
        """
        # Cannot use super() because dataclass(slots=True) does not produce
        # true subclass
        ret_val = BaseConfig.load(self, new_field_values)
        self.log_folder = pathlib.Path(self.log_folder)
        self.map_folders = [
            pathlib.Path(map_folder) for map_folder in self.map_folders
        ]
        return ret_val

    # @override
    def dump(self) -> dict[str, Any]:
        """Dumps field values to a dict

        Return value: dict
            The dataclass as a dict
        """
        return {
            "log_folder": str(self.log_folder),
            "map_folders": [
                str(map_folder) for map_folder in self.map_folders
            ],
        }


game_folders_config=_GameFoldersConfig()
