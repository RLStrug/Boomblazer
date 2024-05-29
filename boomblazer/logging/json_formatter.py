"""Implements a formatter that outputs log records as json objects

Classes:
    JsonFormatterStyleTuple:
        Data type that can be passed to the style parameter of JsonFormatter
    JsonFormatter:
        Formats log records as a json object
"""

import logging
import logging.config
import json
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Mapping
from typing import NamedTuple
from typing import Tuple
from typing import Union


class JsonFormatterStyleTuple(NamedTuple):
    """Data type that can be passed to the style parameter of JsonFormatter

    Members:
        ident: Optional[str | int]
            See indent parameter of json.dump function
        separators: Optional[Tuple[str, str]]
            See separators parameter of json.dump function
        extra: bool
            Determines if all extra fields passed through the extra parameter
            of the logger debug, info, ... methods should be included in the
            json object
    """
    indent: Optional[Union[str, int]]
    separators: Optional[Tuple[str, str]]
    extra: bool


class JsonFormatter(logging.Formatter):
    """Formats a log record as a json object

    Class Constants:
        PREDEFINED_STYLES: dict[str, JsonFormatterStyleTuple]
            Mapping that can be used to convert a style name to a
            JsonFormatterStyleTuple
        DEFAULT_FORMAT: tuple[str]
            The default format if none was given
        BASIC_RECORD_FIELDS: tuple[str, ...]
            Fields that are always present in a record. Used to determine which
            fields were passed via the extra argument
    Members:
        fmt_keys: tuple[str, ...]
            The fields that will be included in the resulting json object
        datefmt: str
            The date format that should be used for the field asctime.
            The format is the same as for time.strftime
        indent: Optional[int | str]
            See indent parameter of json.dump function
        separators: Optional[tuple[str, str]]
            See separators parameter of json.dump function
        extra: bool
            Determines if all extra fields passed through the extra parameter
            of the logger debug, info, ... methods should be included in the
            json object
        defaults: dict[str, Any]
            Sets default values for fields in case it is not present in the
            record
    Special methods:
        __init__:
            Initializes the formatter
    Methods:
        usesTime:
            Checks if the format uses the creation time of the record
        format:
            Formats the specified record as json object
    """

    __slots__ = (
        "fmt_keys", "datefmt", "indent", "separators", "extra", "defaults"
    )

    PREDEFINED_STYLES: ClassVar[Dict[str, JsonFormatterStyleTuple]] = {
        "compact": (None, (",", ":"), False),
        "space": (None, None, False),
        "nl": ("\t", None, False),
    }
    PREDEFINED_STYLES.update({
        f"{key}-extra": (indent, separators, True)
        for key, (indent, separators, _) in PREDEFINED_STYLES.items()
    })

    DEFAULT_FORMAT: ClassVar[Tuple[str]] = ("message",)

    BASIC_RECORD_FIELDS: ClassVar[Tuple[str, ...]] = (
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "taskName", "message", "asctime",
    )


    def __init__(
            self, fmt: Optional[Iterable[str]] = None,
            datefmt: Optional[str] = None,
            style: Union[str, JsonFormatterStyleTuple] = "compact-extra",
            *, defaults: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Initializes the formatter

        Parameters:
            fmt: Optional[Iterable[str]] = None
                The list of the log record fields that should be included in
                the json object
            datefmt: Optional[str] = None
                The date format that should be used for the field asctime.
                The format is the same as for time.strftime
            style: str | JsonFormatterStyleTuple = "compact-extra"
                If a str is passed, a default style will be used.
                "compact": (None, (",", ":"), False)
                "space": (None, None, False)
                "nl": ("\t", None, False)
                If "-extra" is appended after one of these style names, the
                extra member of the tuple will be True
        Keyword-only parameters:
            defaults: Optional[Mapping[str, Any]] = None
                Sets default values for fields in case it is not present in the
                record
        """
        if fmt is None:
            fmt = self.DEFAULT_FORMAT

        if isinstance(style, str):
            if style not in self.PREDEFINED_STYLES:
                raise ValueError(
                    "Style must be one of: "
                    f"{', '.join(self.PREDEFINED_STYLES.keys())}"
                )
            style = self.PREDEFINED_STYLES[style]
        style = JsonFormatterStyleTuple(*style)

        self.fmt_keys = tuple(fmt)
        self.datefmt = datefmt
        self.indent = style.indent
        self.separators = style.separators
        self.extra = style.extra
        self.defaults = defaults

    def usesTime(self):
        """Checks if the format uses the creation time of the record

        Return value: bool
            True if "asctime" is in self.fmt_keys
        """
        return "asctime" in self.fmt_keys

    def format(self, record: logging.LogRecord) -> str:
        """Formats the specified record as json object

        Parameters:
            record: logging.LogRecord
                The record to log

        Return value: str
            The string representation of the json object containing the record
            data
        """
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        record_values = {}
        if self.defaults:
            record_values.update(self.defaults)
        record_values.update(record.__dict__)

        json_record = {
            key: record_values[key]
            for key in self.fmt_keys
        }

        if self.extra:
            json_record.update({
                key: value
                for key, value in record_values.items()
                if key not in self.BASIC_RECORD_FIELDS
            })

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            json_record["exc_text"] = record.exc_text
        if record.stack_info:
            json_record["stack_info"] = record.stack_info

        return json.dumps(
            json_record, indent=self.indent, separators=self.separators
        )


def __test_module() -> int:
    logger_names = (
        "compact", "space", "nl", "custom", "compact-extra", "space-extra",
        "nl-extra", "custom-extra",
    )
    logging.config.dictConfig({
        "version": 1,
        "formatters": {
            "compact": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "style": "compact",
                "defaults": {"yyy": "www",},
            },
            "space": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": ("name", "levelname", "asctime", "message",),
                "style": "space",
            },
            "nl": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": (
                    "name", "levelname", "asctime", "message", "lineno",
                    "processName",
                ),
                "datefmt": "%Y-%m-%d %H:%M:%s.%f%z",
                "style": "nl",
            },
            "custom": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": ("name", "levelname", "asctime", "message",),
                "style": (2, ("/", "="), False),
            },
            "compact-extra": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "style": "compact-extra",
                "defaults": {"yyy": "www",},
            },
            "space-extra": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": ("name", "levelname", "asctime", "message",),
                "style": "space-extra",
            },
            "nl-extra": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": (
                    "name", "levelname", "asctime", "message", "lineno",
                    "processName",
                ),
                "datefmt": "%Y-%m-%d %H:%M:%s.%f%z",
                "style": "nl-extra",
            },
            "custom-extra": {
                "class": "boomblazer.logging.json_formatter.JsonFormatter",
                "format": ("name", "levelname", "asctime", "message",),
                "style": (2, ("/", "="), True),
            },
        },
        "filters": {
        },
        "handlers": {
            name: {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": name,
            }
            for name in logger_names
        },
        "loggers": {
            name: {
                "level": "DEBUG",
                "handlers": [name, ],
            }
            for name in logger_names
        },
    })

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.debug("aaa %s", "zzz")
        logger.info("bbb", extra={"yyy": "xxx"})
        try:
            1 / 0
        except ZeroDivisionError:
            logger.exception("eee")

    return 0


if __name__ == "__main__":
    raise SystemExit(__test_module())
