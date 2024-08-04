"""Logging configuration variables

Global variables:
    logging_config: _LoggingConfig
        Singleton of _LoggingConfig dataclass

Type aliases:
    _FiltersConfig:
        Type of the filters config
    _FormattersConfig:
        Type of the formatters config
    _HandlersConfig:
        Type of the handlers config
"""

from __future__ import annotations

import dataclasses
import typing

from .base_config import BaseConfig

if typing.TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any

    _FiltersConfig = MutableMapping[str, MutableMapping[str, Any]]
    _FormattersConfig = MutableMapping[str, MutableMapping[str, Any]]
    _HandlersConfig = MutableMapping[str, MutableMapping[str, Any]]


def _default_filters_factory() -> _FiltersConfig:
    """Returns the default filters of the logger

    Return value: MutableMapping[str, MutableMapping[str, Any]]
        Default filters of the logger
    """
    return {}


def _default_formatters_factory() -> _FormattersConfig:
    """Returns the default formatters of the logger

    Return value: MutableMapping[str, MutableMapping[str, Any]]
        Default formatters of the logger
    """
    return {
        "simple": {
            "class": "logging.Formatter",
            "format": "[{asctime}] [{levelname}]: {message}",
            "style": "{",
        },
        # JSON lines format
        "jsonl": {
            "class": "boomblazer.logging.json_formatter.JsonFormatter",
            "format": [
                "message",
                "asctime",
                "levelname",
                "name",
                "module",
                "funcName",
                "lineno",
                "threadName",
            ],
            "style": "compact-extra",
        },
    }


def _default_handlers_factory() -> _HandlersConfig:
    """Returns the default handlers of the logger

    Return value: MutableMapping[str, MutableMapping[str, Any]]
        Default handlers of the logger
    """
    return {
        "handler_1": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "handler_2": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "jsonl",
            "filename": "log.jsonl",
            "maxBytes": 1000000,  # 1Mb
            "backupCount": 1,
        },
    }


@dataclasses.dataclass
class _LoggingConfig(BaseConfig):
    """Dataclass containing the logging configuration values

    Members:
        filters: _FiltersConfig
            Filters of the logger
        formatters: _FormattersConfig
            Formatters of the logger
        handlers: _HandlersConfig
            Handlers of the logger
    """

    filters: _FiltersConfig = dataclasses.field(
        default_factory=_default_filters_factory
    )
    formatters: _FormattersConfig = dataclasses.field(
        default_factory=_default_formatters_factory
    )
    handlers: _HandlersConfig = dataclasses.field(
        default_factory=_default_handlers_factory
    )


logging_config = _LoggingConfig()
