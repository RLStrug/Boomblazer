"""Defines logger related functions"""

from __future__ import annotations

import logging
import logging.config
import typing

from ..config.game_folders import game_folders_config
from ..config.logging import logging_config

if typing.TYPE_CHECKING:
    from typing import Any


def _get_handlers_real_path() -> dict[str, dict[str, Any]]:
    """Gets handlers from config with log folder prepended to filenames

    :returns: Config handlers, with the log folder prepended to the destination files
    """
    real_handlers: dict[str, dict[str, Any]] = {
        name: dict(value) for name, value in logging_config.handlers.items()
    }
    for handler in real_handlers.values():
        filename = handler.get("filename")
        if filename is not None:
            handler["filename"] = game_folders_config.log_folder / filename
    return real_handlers


def setup() -> None:
    """Sets up the game logger"""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                name: dict(value) for name, value in logging_config.filters.items()
            },
            "formatters": {
                name: dict(value) for name, value in logging_config.formatters.items()
            },
            "handlers": _get_handlers_real_path(),
            "loggers": {
                "root": {
                    "level": "DEBUG",
                    "handlers": list(logging_config.handlers),
                }
            },
        }
    )
