"""Defines a thread that executes a function at regular interval

Classes:
    Repeater: threading.Thread
        A thread that repeats the execution of a function at regular interval
"""

import threading
import time
from collections.abc import Callable
from typing import Optional


class Repeater(threading.Thread):
    """A thread that repeats the execution of a function at regular interval

    Members:
        interval: float
        function: Callable[[...], None]
        finished: threading.Event

    Special Methods:
        __init__:

    Methods:
        stop:
            Stops the repeater
        repeat:
            Repeats the given function until the repeater is stopped
    """

    def __init__(
            self, interval: float = 0.0,
            target: Optional[Callable[..., None]] = None,
            **kwargs
    ) -> None:
        """Initializes the Repeater

        Parameters:
            interval: float (default = 0.0)
                The interval in seconds between 2 repeats
            target: Optional[Callable[[...], None]]
                The function that should be repeated.
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
        """Stops the repeater
        """
        self.finished.set()

    def repeat(self, *args, **kwargs) -> None:
        """Repeats the given function until the repeater is stopped

        Parameters:
            *args:
                Positional arguments to be passed to the function
            **kwargs:
                Keyword arguments to be passed to the function
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
