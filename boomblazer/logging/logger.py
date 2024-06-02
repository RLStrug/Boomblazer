"""Defines logger related functions

Functions:
    _get_handlers_real_path:
        Gets handlers from config with cache folder prepended to filenames
    setup:
        Sets up the game logger
"""

import copy
import logging
import logging.config
from typing import Any
from typing import Dict

from boomblazer.config.game_folders import game_folders_config
from boomblazer.config.logging import logging_config


def _get_handlers_real_path() -> Dict[str, Dict[str, Any]]:
    """Gets handlers from config with cache folder prepended to filenames

    Return value: dict[str, dict[str, Any]]
        The config handlers, with the cache folder prepended to the destination
        files of file handlers and dervatives
    """
    real_handlers = copy.deepcopy(logging_config.handlers)
    for handler in real_handlers.values():
        if "filename" in handler:
            handler["filename"] = (
                game_folders_config.cache_folder / handler["filename"]
            )
    return real_handlers


def setup() -> None:
    """Sets up the game logger
    """
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": logging_config.filters,
        "formatters": logging_config.formatters,
        "handlers": _get_handlers_real_path(),
        "loggers": {
            "root": {
                "level": "DEBUG",
                "handlers": list(logging_config.handlers),
            }
        },
    })
