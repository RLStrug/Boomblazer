"""Defines some utility functions

Functions:
    verbose_to_log_level:
        Converts a verbosity level to a logger level usable by logging module
    create_logger:
        Creates a new logger from a verbosity level
"""

import logging
from pathlib import Path
from typing import Optional


def verbose_to_log_level(verbosity: int) -> int:
    """Converts a verbosity level to a logger level usable by logging module

    Parameters:
        verbosity: int
            The verbosity level to convert

    Return value: int
        The logging level corresponding to `verbosity`
    """

    if verbosity <= -1:
        log_level = logging.CRITICAL
    elif verbosity == 0:
        log_level = logging.ERROR
    elif verbosity == 1:
        log_level = logging.WARNING
    elif verbosity == 2:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    return log_level


def create_logger(name: str, verbosity: int,
        log_file: Optional[Path] = None) -> logging.Logger:
    """Creates a new logger from a verbosity level

    The logger will be applied a `logging.Formatter` to specify that records
    should look like: [TIME] [LEVEL]: [MESSAGE]
    Example: [1970-01-01 00:00:00,000] [CRITICAL]: Server crashed somehow

    Parameters:
        name: str
            The name of the logger
            Warning: this utility will not check if a logger with the same name
            already exists.
        verbosity: int
            Defines how verbose the logger should be
        log_file: Path
            Defines which file the logger should record its messages to.
            Defaults to stderr if not specified
    """

    logger = logging.getLogger(name)
    logger.setLevel(verbose_to_log_level(verbosity))
    formatter = logging.Formatter(
        "[{asctime}] [{levelname}]: {message}", style="{"
    )
    if log_file is not None:
        handler = logging.FileHandler(log_file, mode="w")
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
