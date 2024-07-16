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
    _get_default_map_folder:
        Returns the default list of map folders location
"""

import dataclasses
import functools
import importlib
import importlib.resources
import pathlib
import platform
from collections.abc import Mapping
from typing import Any

from ..metadata import PACKAGE_NAME
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

def _get_default_custom_maps_folder() -> pathlib.Path:
    """Returns the default list of the custom maps folder

    Return value: pathlib.Path
        The path where the custom maps should be stored
    """
    return _get_default_data_folder() / "custom_maps"


@dataclasses.dataclass
class _GameFoldersConfig(BaseConfig):
    """Dataclass containing the game folders location

    Members:
        log_folder: pathlib.Path
            Folder containing log files
        custom_maps_folder: pathlib.Path
            List of folders where maps folders can be found

    Properties:
        resources_folder: importlib.resources.abc.Traversable
            The folder containing the package resources
        official_maps_folder: importlib.resources.abc.Traversable
            The folder containing the official maps
        maps_folders: list[importlib.resources.abc.Traversable]
            The list of the folder containing maps
    """

    log_folder: pathlib.Path = dataclasses.field(
        default_factory=_get_default_log_folder
    )
    custom_maps_folder: pathlib.Path = dataclasses.field(
        default_factory=_get_default_custom_maps_folder
    )

    @functools.cached_property
    def resources_folder(self) -> importlib.abc.Traversable:
        """Return the folder containing the package resources

        Return value: importlib.resources.abc.Traversable
            The folder containing the package resources
        """
        return importlib.resources.files(PACKAGE_NAME)

    @functools.cached_property
    def official_maps_folder(self) -> importlib.abc.Traversable:
        """Return the folder containing the official maps

        Return value: importlib.resources.abc.Traversable
            The folder containing the official maps
        """
        return self.resources_folder / "official_maps"

    @property
    def maps_folders(self) -> list[importlib.abc.Traversable]:
        """Return the list of the folders containing maps

        Return value: importlib.resources.abc.Traversable
            The list of the folders containing maps
        """
        return [self.official_maps_folder, self.custom_maps_folder]

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
        # true subclass. This feature is unavailable in python 3.9, but will be
        # used as soon as possible
        ret_val = BaseConfig.load(self, new_field_values)
        self.log_folder = pathlib.Path(self.log_folder)
        self.custom_maps_folder = pathlib.Path(self.custom_maps_folder)
        return ret_val

    # @override
    def dump(self) -> dict[str, Any]:
        """Dumps field values to a dict

        Return value: dict
            The dataclass as a dict
        """
        return {
            "log_folder": str(self.log_folder),
            "custom_maps_folder": str(self.custom_maps_folder),
        }


game_folders_config=_GameFoldersConfig()
