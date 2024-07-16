"""Tests boomblazer.logging.json_formatter
"""

import unittest

from boomblazer.logging import json_formatter


class TestJsonFormatter(unittest.TestCase):
    """Tests JsonFormatter
    """

    @unittest.skip("TODO")
    def test_json_formatter(self) -> None:
        """Tests json_formatter
        """
        pass

"""
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
"""
