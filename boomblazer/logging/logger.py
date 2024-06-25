"""Defines logger related functions

Functions:
    _get_handlers_real_path:
        Gets handlers from config with log folder prepended to filenames
    setup:
        Sets up the game logger
"""

import logging
import logging.config
from typing import Any

from boomblazer.config.game_folders import game_folders_config
from boomblazer.config.logging import logging_config


def _get_handlers_real_path() -> dict[str, dict[str, Any]]:
    """Gets handlers from config with log folder prepended to filenames

    Return value: dict[str, dict[str, Any]]
        The config handlers, with the log folder prepended to the destination
        files of file handlers and dervatives
    """
    real_handlers: dict[str, dict[str, Any]] = {
        name: dict(value)
        for name, value in logging_config.handlers.items()
    }
    for handler in real_handlers.values():
        filename = handler.get("filename")
        if filename is not None:
            handler["filename"] = game_folders_config.log_folder / filename
    return real_handlers


def setup() -> None:
    """Sets up the game logger
    """
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            name: dict(value)
            for name, value in logging_config.filters.items()
        },
        "formatters": {
            name: dict(value)
            for name, value in logging_config.formatters.items()
        },
        "handlers": _get_handlers_real_path(),
        "loggers": {
            "root": {
                "level": "DEBUG",
                "handlers": list(logging_config.handlers),
            }
        },
    })
