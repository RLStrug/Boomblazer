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
import pathlib
import platform
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Mapping

from boomblazer.config.base_config import BaseConfig
from boomblazer.config.config_loader import config_instances
from boomblazer.version import GAME_NAME


@dataclasses.dataclass(slots=True)
class _LoggingConfig(BaseConfig):
    """Dataclass containing the logging configuration values

    Class constants:
        _DEFAULT_FILTERS: dict[str, dict[str, str]]
            The default filters of the logger
        _DEFAULT_FORMATTERS: dict[str, dict[str, str]]
            The default formatters of the logger
        _DEFAULT_HANDLERS: dict[str, dict[str, str]]
            The default handlers of the logger

    Static methods:
        _get_default_log_file_location:
            Returns the default location for log files

    Members:
        filters: MutableSequence[Mapping]
            The filters of the logger
        formatters: MutableSequence[Mapping]
            The formatters of the logger
        handlers: MutableSequence[Mapping]
            The handlers of the logger
    """

    @staticmethod
    def _get_default_log_file_location() -> pathlib.Path:
        """Returns the default location for log files

        Return value: pathlib.Path
            The path where the log files should be
        """
        os = platform.system()
        if os == "Linux":
            ...
        if os == "Darwin":
            ...
        if os == "Windows":
            ...
        # else ("Java", ""): pass
        return pathlib.Path(".", f"{GAME_NAME}_log.jsonl")

    _DEFAULT_FILTERS: ClassVar[Dict[str, Dict[str, Any]]] = {
    }

    _DEFAULT_FORMATTERS: ClassVar[Dict[str, Dict[str, Any]]] = {
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

    _DEFAULT_HANDLERS: ClassVar[Dict[str, Dict[str, Any]]] = {
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

    filters: Mapping[str, Mapping[str, str]] = dataclasses.field(
        default_factory=functools.partial(copy.deepcopy, _DEFAULT_FILTERS)
    )
    formatters: Mapping[str, Mapping[str, str]] = dataclasses.field(
        default_factory=functools.partial(copy.deepcopy, _DEFAULT_FORMATTERS)
    )
    handlers: Mapping[str, Mapping[str, str]] = dataclasses.field(
        default_factory=functools.partial(copy.deepcopy, _DEFAULT_HANDLERS)
    )


logging_config=_LoggingConfig()
config_instances["logging"] = logging_config
