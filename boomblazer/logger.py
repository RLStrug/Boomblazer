"""Defines logger related functions

Functions:
    _verbose_to_log_level:
        Converts a verbosity level to a logger level usable by logging module
    create_logger:
        Creates a new logger from a verbosity level
"""

import logging
from typing import Iterable
from typing import Optional


def _verbose_to_log_level(verbosity: int) -> int:
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


def create_logger(
        name: str, verbosity: int,
        log_files: Optional[Iterable[str]] = None
) -> logging.Logger:
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
        log_file: Iterable[str]
            Defines which files the logger should record its messages to.
            If the file name is '-', then it will log to stderr.
    """

    logger = logging.getLogger(name)
    logger.setLevel(_verbose_to_log_level(verbosity))
    formatter = logging.Formatter(
        "[{asctime}] [{levelname}]: {message}", style="{"
    )
    if log_files is None:
        logger.addHandler(logging.NullHandler())
        log_files = ()

    for log_file in log_files:
        if log_file == "-":
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(log_file, mode="w")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
