"""Implements a formatter that outputs log records as json objects"""

from __future__ import annotations

import logging
import logging.config
import json
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Mapping
    from typing import Any


class JsonFormatterStyleTuple(typing.NamedTuple):
    """Data type that can be passed to the style parameter of JsonFormatter

    Members:
        ident: str | int | None
            See indent parameter of json.dump function
        separators: tuple[str, str] | None
            See separators parameter of json.dump function
        extra: bool
            Determines if extra fields should be logged
    """

    indent: str | int | None
    separators: tuple[str, str] | None
    extra: bool


class JsonFormatter(logging.Formatter):
    """Formats a log record as a json object

    Class Constants:
        PREDEFINED_STYLES: dict[str, JsonFormatterStyleTuple]
            Mapping that can be used to convert a style name to a
            JsonFormatterStyleTuple
        DEFAULT_FORMAT: tuple[str]
            Default format if none was given
        BASIC_RECORD_FIELDS: tuple[str, ...]
            Fields that are always present in a record. Used to determine which
            fields were passed via the extra argument
    """

    __slots__ = {
        "fmt_keys": "(tuple[str, ...]) Fields to be logged",
        "datefmt": "(str) Date format for asctime. See time.strftime",
        "indent": "(int | str | None) See indent parameter of json.dump",
        "separators": "(tuple[str, str] | None) See separators parameter of json.dump",
        "extra": "(bool) Determines if extra fields are logged",
        "defaults": "(dict[str, Any]) Default values for given fields",
    }

    PREDEFINED_STYLES: typing.ClassVar[dict[str, JsonFormatterStyleTuple]] = {
        "compact": JsonFormatterStyleTuple(None, (",", ":"), False),
        "space": JsonFormatterStyleTuple(None, None, False),
        "nl": JsonFormatterStyleTuple("\t", None, False),
    }
    PREDEFINED_STYLES.update(
        {
            f"{key}-extra": JsonFormatterStyleTuple(indent, separators, True)
            for key, (indent, separators, _) in PREDEFINED_STYLES.items()
        }
    )

    DEFAULT_FORMAT: typing.ClassVar[tuple[str]] = ("message",)

    BASIC_RECORD_FIELDS: typing.ClassVar[tuple[str, ...]] = (
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
        "message",
        "asctime",
    )

    def __init__(
        self,
        fmt: Iterable[str] | None = None,
        datefmt: str | None = None,
        style: str | JsonFormatterStyleTuple = "compact-extra",
        *,
        defaults: Mapping[str, Any] = {},
    ) -> None:
        """Initializes the formatter

        Parameters:
            fmt: Iterable[str] | None = None
                List of log record fields that should be included in the json object
            datefmt: str | None = None
                Date format that should be used for the field asctime.
                Format is the same as for time.strftime
            style: str | JsonFormatterStyleTuple = "compact-extra"
                If a str is passed, a default style will be used.
                "compact": (None, (",", ":"), False)
                "space": (None, None, False)
                "nl": ("\t", None, False)
                "-extra" suffix sets extra to True
        Keyword-only parameters:
            defaults: Mapping[str, Any] = {}
                Sets default values for fields
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
        self.defaults = dict(defaults)

    def usesTime(self) -> bool:
        """Checks if the format uses the creation time of the record

        Return value: bool
            True if "asctime" is in self.fmt_keys
        """
        return "asctime" in self.fmt_keys

    def format(self, record: logging.LogRecord) -> str:
        """Formats the specified record as json object

        Parameters:
            record: logging.LogRecord
                Record to log

        Return value: str
            JSON representation of the record data
        """
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        record_values = self.defaults
        record_values.update(vars(record))

        json_record = {key: record_values[key] for key in self.fmt_keys}

        if self.extra:
            json_record.update(
                {
                    key: value
                    for key, value in record_values.items()
                    if key not in self.BASIC_RECORD_FIELDS
                }
            )

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            json_record["exc_text"] = record.exc_text
        if record.stack_info:
            json_record["stack_info"] = record.stack_info

        return json.dumps(json_record, indent=self.indent, separators=self.separators)
