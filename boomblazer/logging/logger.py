"""Defines logger related functions

Functions:
    setup:
        Sets up the game logger
"""

import logging
import logging.config

from boomblazer.config.logging import logging_config

def setup() -> None:
    """Sets up the game logger
    """
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": logging_config.filters,
        "formatters": logging_config.formatters,
        "handlers": logging_config.handlers,
        "loggers": {
            "root": {
                "level": "DEBUG",
                "handlers": list(logging_config.handlers),
            }
        },
    })
