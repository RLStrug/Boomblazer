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
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping

from boomblazer.config.base_config import BaseConfig
from boomblazer.config.config_loader import config_instances
from boomblazer.version import GAME_NAME

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

def _get_default_map_folders() -> List[pathlib.Path]:
    """Returns the default list of map folders location

    Return value: list[pathlib.Path]
        The list of paths where the map folders should be stored
    """
    return [
        pathlib.Path(".", "official_maps"),  # DEBUG
        _get_default_data_folder() / "official_maps",
        _get_default_data_folder() / "custom_maps",
    ]


@dataclasses.dataclass(slots=True)
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
    map_folders: List[pathlib.Path] = dataclasses.field(
        default_factory=_get_default_map_folders
    )

    def load(self, new_field_values: Mapping[str, Any]) -> None:
        """Loads field values from a dict

        Parameters:
            new_field_values: dict
                The names and new values of fields to be updated
                Unknown fields will be ignored
        """
        log_folder = new_field_values.get("log_folder", None)
        if log_folder is not None:
            self.log_folder = pathlib.Path(log_folder)

        map_folders = new_field_values.get("map_folders", None)
        if map_folders is not None:
            self.map_folders = [
                pathlib.Path(map_folder) for map_folder in map_folders
            ]

    def dump(self) -> Dict[str, Any]:
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
config_instances["game_folders"] = game_folders_config
