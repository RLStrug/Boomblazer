"""Logging configuration variables

Global variables:
    logging_config: _LoggingConfig
        Singleton of _LoggingConfig dataclass

Classes:
    _LoggingConfig:
        Dataclass containing the logging configuration values
"""


import copy
import dataclasses
import functools
from collections.abc import Callable
from collections.abc import MutableMapping
from typing import Any
from typing import ClassVar

from boomblazer.config.base_config import BaseConfig
from boomblazer.config.config_loader import config_instances
from boomblazer.version import GAME_NAME


T = MutableMapping[str, MutableMapping[str, Any]]


@dataclasses.dataclass(slots=True)
class _LoggingConfig(BaseConfig):
    """Dataclass containing the logging configuration values

    Class constants:
        _DEFAULT_FILTERS: dict[str, dict[str, Any]]
            The default filters of the logger
        _DEFAULT_FORMATTERS: dict[str, dict[str, Any]]
            The default formatters of the logger
        _DEFAULT_HANDLERS: dict[str, dict[str, Any]]
            The default handlers of the logger

    Members:
        filters: MutableMapping[str, MutableMapping[str, Any]]
            The filters of the logger
        formatters: MutableMapping[str, MutableMapping[str, Any]]
            The formatters of the logger
        handlers: MutableMapping[str, MutableMapping[str, Any]]
            The handlers of the logger
    """

    _DEFAULT_FILTERS: ClassVar[dict[str, dict[str, Any]]] = {
    }
    _DEFAULT_FILTERS_FACTORY: ClassVar[Callable[[], T]] = functools.partial(
        copy.deepcopy, _DEFAULT_FILTERS
    )

    _DEFAULT_FORMATTERS: ClassVar[dict[str, dict[str, Any]]] = {
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
    _DEFAULT_FORMATTERS_FACTORY: ClassVar[Callable[[], T]] = functools.partial(
        copy.deepcopy, _DEFAULT_FORMATTERS
    )

    _DEFAULT_HANDLERS: ClassVar[dict[str, dict[str, Any]]] = {
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
            "filename": f"{GAME_NAME}_log.jsonl",
            "maxBytes": 100000,  # TODO bigger default
            "backupCount": 1,
        },
    }
    _DEFAULT_HANDLERS_FACTORY: ClassVar[Callable[[], T]] = functools.partial(
        copy.deepcopy, _DEFAULT_HANDLERS
    )

    filters: T = dataclasses.field(
        default_factory=_DEFAULT_FILTERS_FACTORY
    )
    formatters: T = dataclasses.field(
        default_factory=_DEFAULT_FORMATTERS_FACTORY
    )
    handlers: T = dataclasses.field(
        default_factory=_DEFAULT_HANDLERS_FACTORY
    )


logging_config=_LoggingConfig()
config_instances["logging"] = logging_config
