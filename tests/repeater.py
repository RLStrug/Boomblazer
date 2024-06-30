#!/usr/bin/env python3

import io
import logging
import logging.config
import time
import typing

from boomblazer.utils.repeater import Repeater


####################
# Initialization
####################

logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "f1": {
            "format": "%(relativeCreated)f::%(threadName)s::%(message)s",
        },
    },
    "handlers": {
        "h1": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "f1",
        },
        "h2": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "f1",
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": [
                "h1",
                "h2",
            ]
        },
    },
})
logger = logging.getLogger("Test-Repeater")
buffer = io.StringIO()
h2 = logging.getHandlerByName("h2")
h2.setStream(buffer)

def spam(*args, **kwargs):
    logger.info("eggs args=%r kwargs=%r", args, kwargs)
    time.sleep(0.1)

####################
# Test
####################

thread = Repeater(
    interval=0.2, target=spam,
    name="RepeaterThread",
    args=("monthy", "python"), kwargs={"spanish": "inquisition"}
)

thread.start()
time.sleep(1.1)

logger.info("Stopping repeater")
thread.stop()

thread.join()
logger.info("Repeater stopped")

####################
# Check results
####################

Record = typing.NamedTuple(
    "Record",
    (("relative_created", float), ("thread_name", str), ("message", str))
)
log_records = buffer.getvalue().splitlines()
repeater_records = []
main_records = []

for log_record in log_records:
    relative_created, thread_name, message = log_record.split("::", 2)
    record = Record(float(relative_created), thread_name, message)
    if record.thread_name == "RepeaterThread":
        repeater_records.append(record)
    else:
        main_records.append(record)

repeater_records.sort()
main_records.sort()

# We check if the repetitons occured around 200ms one after another
for record_1, record_2 in zip(repeater_records, repeater_records[1:]):
    assert record_2.relative_created - record_1.relative_created < 201

# We check if the positional and keyword arguments were passed correctly
for record in repeater_records:
    assert record.message == "eggs args=('monthy', 'python') kwargs={'spanish': 'inquisition'}"
