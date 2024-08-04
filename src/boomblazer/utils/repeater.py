"""Defines a thread that executes a function at regular interval"""

from __future__ import annotations

import threading
import time
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


class Repeater(threading.Thread):
    """A thread that repeats the execution of a function at regular interval

    Members:
        interval: float
        function: Callable[[...], None]
        finished: threading.Event
    """

    def __init__(
        self,
        interval: float = 0.0,
        target: Callable[..., None] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the Repeater

        Parameters:
            interval: float (default = 0.0)
                Interval in seconds between 2 repeats
            target: Callable[[...], None] | None
                Function that should be repeated.
                If None, nothing will be executed
            **kwargs:
                Keyword arguments to pass to threading.Thread constructor
                Positionals are not allowed.
        """
        super().__init__(target=self.repeat, **kwargs)
        self.interval = interval
        self.function = target
        self.finished = threading.Event()

    def stop(self) -> None:
        """Stops the repeater"""
        self.finished.set()

    def repeat(self, *args: Any, **kwargs: Any) -> None:
        """Repeats the given function until the repeater is stopped

        Parameters:
            *args:
                Positional arguments to be passed to self.function
            **kwargs:
                Keyword arguments to be passed to self.function
        """
        timer = self.interval
        try:
            if self.function is not None:
                while not self.finished.wait(timer):
                    t0 = time.monotonic()
                    self.function(*args, **kwargs)
                    # Remove the execution time from the wait time
                    timer = self.interval - (time.monotonic() - t0)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # a bounded argument or captured variable that has a member that
            # points to the thread.
            # Regular arguments will be deleted by the parent run method
            del self.function
