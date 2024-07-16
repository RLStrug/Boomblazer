"""Tests boomblazer.config.config_loader
"""

import unittest
import unittest.mock

from boomblazer.config import config_loader


@unittest.mock.patch("boomblazer.config.config_loader.platform.system")
class TestFindConfigFile(unittest.TestCase):
    """Tests the function _find_config_file
    """

    @unittest.skip("TODO")
    def test_find_config_file(
            self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _find_config_file
        """
        pass


class TestLoadConfig(unittest.TestCase):
    """Tests the function load_config
    """

    @unittest.skip("TODO")
    def test_load_config(self) -> None:
        """Tests load_config
        """
        pass


class TestSaveConfig(unittest.TestCase):
    """Tests the function save_config
    """

    @unittest.skip("TODO")
    def test_save_config(self) -> None:
        """Tests save_config
        """
        pass
