"""Logging configuration variables

Global variables:
    logging_config: _LoggingConfig
        Singleton of _LoggingConfig dataclass

Classes:
    _LoggingConfig:
        Dataclass containing the logging configuration values
"""


import dataclasses
from collections.abc import MutableMapping
from typing import Any

from .base_config import BaseConfig


_FiltersConfig = MutableMapping[str, MutableMapping[str, Any]]
_FormattersConfig = MutableMapping[str, MutableMapping[str, Any]]
_HandlersConfig = MutableMapping[str, MutableMapping[str, Any]]


@dataclasses.dataclass(slots=True)
class _LoggingConfig(BaseConfig):
    """Dataclass containing the logging configuration values

    Static methods:
        _default_filters_factory:
            Returns the default filters of the logger
        _default_formatters_factory:
            Returns the default formatters of the logger
        _default_handlers_factory:
            Returns the default handlers of the logger

    Members:
        filters: _FiltersConfig
            The filters of the logger
        formatters: _FormattersConfig
            The formatters of the logger
        handlers: _HandlersConfig
            The handlers of the logger
    """

    @staticmethod
    def _default_filters_factory() -> _FiltersConfig:
        """Returns the default filters of the logger

        Return value: MutableMapping[str, MutableMapping[str, Any]]
            The default filters of the logger
        """
        return {
        }

    @staticmethod
    def _default_formatters_factory() -> _FormattersConfig:
        """Returns the default formatters of the logger

        Return value: MutableMapping[str, MutableMapping[str, Any]]
            The default formatters of the logger
        """
        return {
            "simple" : {
                "class": "logging.Formatter",
                "format": "[{asctime}] [{levelname}]: {message}",
                "style": "{",
            },
            # JSON lines format
            "jsonl" : {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": [
                    "message", "asctime", "levelname", "name", "module",
                    "funcName", "lineno", "threadName",
                ],
                "style": "compact-extra",
            },
        }

    @staticmethod
    def _default_handlers_factory() -> _HandlersConfig:
        """Returns the default handlers of the logger

        Return value: MutableMapping[str, MutableMapping[str, Any]]
            The default handlers of the logger
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
                "filename": f"log.jsonl",
                "maxBytes": 1000000,  # 1Mb
                "backupCount": 1,
            },
        }

    filters: _FiltersConfig = dataclasses.field(
        default_factory=_default_filters_factory
    )
    formatters: _FormattersConfig = dataclasses.field(
        default_factory=_default_formatters_factory
    )
    handlers: _HandlersConfig = dataclasses.field(
        default_factory=_default_handlers_factory
    )


logging_config=_LoggingConfig()
