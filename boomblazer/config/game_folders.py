"""Configuration variables determining where game folders are located

Global variables:
    game_folders_config: _GameFoldersConfig
        Singleton of _GameFoldersConfig dataclass

Classes:
    _GameFoldersConfig:
        Dataclass containing the game folders location
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


@dataclasses.dataclass(slots=True)
class _GameFoldersConfig(BaseConfig):
    """Dataclass containing the game folders location

    Static Methods:
        _get_default_cache_folder:
            Returns the default location of the cache folder
        _get_default_map_folders:
            Returns the default list of map folders location

    Members:
        cache_folder: pathlib.Path
            Folder containing cache folders
        map_folders: list[pathlib.Path]
            List of folders where map folders can be found
    """

    @staticmethod
    def _get_default_cache_folder() -> pathlib.Path:
        """Returns the default location of the cache file

        Return value: pathlib.Path
            The path where the cache file should be
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

    @staticmethod
    def _get_default_map_folders() -> List[pathlib.Path]:
        """Returns the default list of map folders location

        Return value: list[pathlib.Path]
            The list of paths where the map folders should be stored
        """
        os = platform.system()
        if os == "Linux":
            ...
        if os == "Darwin":
            ...
        if os == "Windows":
            ...
        # else ("Java", ""): pass
        return [
            pathlib.Path(".", "official_maps"),
            pathlib.Path(".", f"{GAME_NAME}_data", "custom_maps"),
        ]

    cache_folder: pathlib.Path = dataclasses.field(
        default_factory=_get_default_cache_folder
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
        cache_folder = new_field_values.get("cache_folder", None)
        if cache_folder is not None:
            self.cache_folder = pathlib.Path(cache_folder)

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
            "cache_folder": str(self.cache_folder),
            "map_folders": [
                str(map_folder) for map_folder in self.map_folders
            ],
        }


game_folders_config=_GameFoldersConfig()
config_instances["game_folders"] = game_folders_config
