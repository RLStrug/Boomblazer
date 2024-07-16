"""Tests boomblazer.config.base_config
"""

import dataclasses
import unittest

from boomblazer.config.base_config import BaseConfig


@dataclasses.dataclass
class MockupConfig(BaseConfig):
    """Mockup config class
    """

    i: int = 1
    s: str = dataclasses.field(default_factory="abc".upper)


class TestBaseConfig(unittest.TestCase):
    """Tests BaseConfig
    """

    __slots__ = ("mockup_config",)

    def setUp(self) -> None:
        """Instanciates mockup_config before each test
        """
        self.mockup_config = MockupConfig()

    def test_load_all(self) -> None:
        """Tests BaseConfig.load with all fields specified
        """
        self.assertTrue(
            self.mockup_config.load({"i": 2, "s": "def"}),
            "Load of all fields did not return True"
        )
        self.assertEqual(
            self.mockup_config, MockupConfig(2, "def"),
            "Load of all fields did not set data correctly"
        )

    def test_load_1(self) -> None:
        """Tests BaseConfig.load with 1 field / 2 specified
        """
        self.assertFalse(
            self.mockup_config.load({"s": "def"}),
            "Load of 1 field / 2 did not return False"
        )
        self.assertEqual(
            self.mockup_config, MockupConfig(1, "def"),
            "Load of 1 field did not set data correctly"
        )

    def test_load_all_and_1_bad(self) -> None:
        """Tests BaseConfig.load with all fields + 1 bad field specified
        """
        self.assertTrue(
            self.mockup_config.load({"i": 2, "s": "def", "bad_field": -1}),
            "Load of all fields + 1 bad field did not return True"
        )
        self.assertEqual(
            self.mockup_config, MockupConfig(2, "def"),
            "Load of all fields + 1 bad field did not set data correctly"
        )

    def test_load_1_and_1_bad(self) -> None:
        """Tests BaseConfig.load with 1 field / 2 + 1 bad field specified 
        """
        self.assertFalse(
            self.mockup_config.load({"i": 2, "bad_field": -1}),
            "Load of 1 field / 2 + 1 bad field did not return False"
        )
        self.assertEqual(
            self.mockup_config, MockupConfig(2, "ABC"),
            "Load of 1 field + 1 bad field did not set data correctly"
        )

    def test_load_none(self) -> None:
        """Tests BaseConfig.load with no fields specified
        """
        self.assertFalse(
            self.mockup_config.load({}),
            "Load of 0 fields / 2 did not return False"
        )
        self.assertEqual(
            self.mockup_config, MockupConfig(1, "ABC"),
            "Load of 0 fields modified data"
        )

    def test_dump(self) -> None:
        """Tests BaseConfig.dump
        """
        self.mockup_config.i = 2
        self.mockup_config.s = "def"
        mockup_dump = self.mockup_config.dump()

        self.assertEqual(
            self.mockup_config, MockupConfig(2, "def"), "Dump modified data"
        )

        self.assertEqual(
            mockup_dump,
            {"i": 2, "s": "def"},
            "Dump did not copy data correctly"
        )

    def test_reset_1(self) -> None:
        """Tests.BaseConfig.reset with 1 field specified
        """
        self.mockup_config.i = 2
        self.mockup_config.s = "def"
        self.mockup_config.reset(["i"])
        self.assertEqual(
            self.mockup_config, MockupConfig(1, "def"),
            "Reset of one field did not restore data correctly"
        )

    def test_reset_1_bad(self) -> None:
        """Tests.BaseConfig.reset with 1 bad field specified
        """
        self.mockup_config.i = 2
        self.mockup_config.s = "def"
        self.mockup_config.reset(["bad_field"])
        self.assertEqual(
            self.mockup_config, MockupConfig(2, "def"),
            "Reset of unknown field did not restore data correctly"
        )

    def test_reset_all(self) -> None:
        """Tests.BaseConfig.reset with no field specified (all should be reset)
        """
        self.mockup_config.i = 2
        self.mockup_config.s = "def"
        self.mockup_config.reset()
        self.assertEqual(
            self.mockup_config, MockupConfig(1, "ABC"),
            "Reset of all fields did not restore data correctly"
        )
