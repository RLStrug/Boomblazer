"""Tests boomblazer.config.config_loader
"""

import itertools
import pathlib
import unittest
import unittest.mock

from boomblazer.config import config_loader
from boomblazer.metadata import GAME_NAME


@unittest.mock.patch("boomblazer.config.config_loader.platform.system")
class TestFindConfigFile(unittest.TestCase):
    """Tests the function _find_config_file"""

    @unittest.expectedFailure
    def test_find_config_file_linux(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _find_config_file behaviour on Linux platforms"""
        mock_platform_system.return_value = "Linux"
        expected = (
            "TODO",
            pathlib.Path(f"{GAME_NAME}_data", "config", f"{GAME_NAME}_config.json"),
        )
        for expected_file, config_file in itertools.zip_longest(
            expected, config_loader._find_config_file()
        ):
            self.assertEqual(
                expected_file,
                config_file,
                f"Bad value for default cache folder on Linux",
            )

    @unittest.expectedFailure
    def test_find_config_file_windows(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _find_config_file behaviour on Windows platforms"""
        mock_platform_system.return_value = "Windows"
        expected = (
            "TODO",
            pathlib.Path(f"{GAME_NAME}_data", "config", f"{GAME_NAME}_config.json"),
        )
        for expected_file, config_file in itertools.zip_longest(
            expected, config_loader._find_config_file()
        ):
            self.assertEqual(
                expected_file,
                config_file,
                f"Bad value for default cache folder on Windows",
            )

    @unittest.expectedFailure
    def test_find_config_file_macos(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _find_config_file behaviour on MacOS platforms"""
        mock_platform_system.return_value = "Darwin"
        expected = (
            "TODO",
            pathlib.Path(f"{GAME_NAME}_data", "config", f"{GAME_NAME}_config.json"),
        )
        for expected_file, config_file in itertools.zip_longest(
            expected, config_loader._find_config_file()
        ):
            self.assertEqual(
                expected_file,
                config_file,
                f"Bad value for default cache folder on MacOS",
            )

    def test_find_config_file_other(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _find_config_file behaviour on other platforms"""
        for platform in ("Java", ""):
            with self.subTest(platform=platform):
                mock_platform_system.return_value = platform
                expected = (
                    pathlib.Path(
                        f"{GAME_NAME}_data", "config", f"{GAME_NAME}_config.json"
                    ),
                )
                for expected_file, config_file in itertools.zip_longest(
                    expected, config_loader._find_config_file()
                ):
                    self.assertEqual(
                        expected_file,
                        config_file,
                        f"Bad value for default cache folder on {platform!r}",
                    )


class TestLoadConfig(unittest.TestCase):
    """Tests the function load_config"""

    @unittest.skip("TODO")
    def test_load_config(self) -> None:
        """Tests load_config"""
        pass


class TestSaveConfig(unittest.TestCase):
    """Tests the function save_config"""

    @unittest.skip("TODO")
    def test_save_config(self) -> None:
        """Tests save_config"""
        pass
