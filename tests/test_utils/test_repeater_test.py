"""Tests boomblazer.utils.repeater
"""

import time
import unittest
import queue

from boomblazer.utils.repeater import Repeater


def spam(times: queue.SimpleQueue[float]) -> None:
    times.put(time.monotonic())
    time.sleep(0.01)


class TestRepeater(unittest.TestCase):
    """Tests Repeater
    """

    def test_repeater(self) -> None:
        """Tests Repeater usage
        """
        times : queue.SimpleQueue[float] = queue.SimpleQueue()

        thread = Repeater(
            interval=0.02, target=spam,
            name="RepeaterThread",
            args=(times,)
        )

        thread.start()
        time.sleep(0.07)
        thread.stop()
        thread.join()

        t0 = times.get_nowait()
        for _ in range(2):
            t1 = times.get_nowait()
            self.assertAlmostEqual(
                t1 - t0, 0.02, places=3,
                msg="The function did not repeat in due time"
            )
            t0 = t1
