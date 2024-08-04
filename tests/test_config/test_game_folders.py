"""Tests boomblazer.config.game_folders
"""

import pathlib
import unittest
import unittest.mock

from boomblazer.config import game_folders
from boomblazer.metadata import GAME_NAME


@unittest.mock.patch("boomblazer.config.game_folders.platform.system")
class TestDefaultCacheFolder(unittest.TestCase):
    """Tests the function _get_default_cache_folder"""

    @unittest.expectedFailure
    def test_default_cache_folder_linux(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_cache_folder behaviour on Linux platforms"""
        mock_platform_system.return_value = "Linux"
        self.assertEqual(game_folders._get_default_cache_folder(), "", "TODO")

    @unittest.expectedFailure
    def test_default_cache_folder_windows(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_cache_folder behaviour on Windows platforms"""
        mock_platform_system.return_value = "Windows"
        self.assertEqual(game_folders._get_default_cache_folder(), "", "TODO")

    @unittest.expectedFailure
    def test_default_cache_folder_macos(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_cache_folder behaviour on MacOS platforms"""
        mock_platform_system.return_value = "Darwin"
        self.assertEqual(game_folders._get_default_cache_folder(), "", "TODO")

    def test_default_cache_folder_other(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_cache_folder behaviour on other platforms"""
        for platform in ("Java", ""):
            with self.subTest(platform=platform):
                mock_platform_system.return_value = platform
                self.assertEqual(
                    game_folders._get_default_cache_folder(),
                    pathlib.Path(f"{GAME_NAME}_data", "cache"),
                    f"Bad value for default cache folder on {platform!r}",
                )


@unittest.mock.patch("boomblazer.config.game_folders.platform.system")
class TestDefaultLogFolder(unittest.TestCase):
    """Tests the function _get_default_log_folder"""

    def test_default_log_folder(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_log_folder"""
        for platform in ("Linux", "Windows", "Darwin", "Java", ""):
            with self.subTest(platform=platform):
                mock_platform_system.return_value = platform
                self.assertEqual(
                    game_folders._get_default_log_folder(),
                    game_folders._get_default_cache_folder() / "log",
                    f"Bad value for default log folder on {platform!r}",
                )


@unittest.mock.patch("boomblazer.config.game_folders.platform.system")
class TestDefaultDataFolder(unittest.TestCase):
    """Tests the function _get_default_data_folder"""

    @unittest.expectedFailure
    def test_default_data_folder_linux(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_data_folder behaviour on Linux platforms"""
        mock_platform_system.return_value = "Linux"
        self.assertEqual(game_folders._get_default_data_folder(), "", "TODO")

    @unittest.expectedFailure
    def test_default_data_folder_windows(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_data_folder behaviour on Windows platforms"""
        mock_platform_system.return_value = "Windows"
        self.assertEqual(game_folders._get_default_data_folder(), "", "TODO")

    @unittest.expectedFailure
    def test_default_data_folder_macos(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_data_folder behaviour on MacOS platforms"""
        mock_platform_system.return_value = "Darwin"
        self.assertEqual(game_folders._get_default_data_folder(), "", "TODO")

    def test_default_data_folder_other(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_data_folder behaviour on other platforms"""
        for platform in ("Java", ""):
            with self.subTest(platform=platform):
                mock_platform_system.return_value = platform
                self.assertEqual(
                    game_folders._get_default_data_folder(),
                    pathlib.Path(f"{GAME_NAME}_data", "share"),
                    f"Bad value for default data folder on {platform!r}",
                )


@unittest.mock.patch("boomblazer.config.game_folders.platform.system")
class TestDefaultCustomMapFolder(unittest.TestCase):
    """Tests the function _get_default_custom_maps_folder"""

    def test_default_custom_map_folder(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests _get_default_custom_maps_folder"""
        for platform in ("Linux", "Windows", "Darwin", "Java", ""):
            with self.subTest(platform=platform):
                mock_platform_system.return_value = platform
                self.assertEqual(
                    game_folders._get_default_custom_maps_folder(),
                    game_folders._get_default_data_folder() / "custom_maps",
                    f"Bad value for default custom maps folder on {platform!r}",
                )


class TestGameFoldersConfig(unittest.TestCase):
    """Tests game_folders._GameFoldersConfig"""

    def setUp(self) -> None:
        """Instanciates a _GameFoldersConfig before each test"""
        self.config = game_folders._GameFoldersConfig()

    @unittest.mock.patch("boomblazer.config.game_folders.platform.system")
    def test_log_folder_default_value(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests if _GameFoldersConfig.log_folder is set correctly"""
        for platform in ("Linux", "Windows", "Darwin", "Java", ""):
            with self.subTest(platform=platform):
                self.assertEqual(
                    self.config.log_folder, game_folders._get_default_log_folder()
                )

    @unittest.mock.patch("boomblazer.config.game_folders.platform.system")
    def test_custom_map_folder_default_value(
        self, mock_platform_system: unittest.mock.MagicMock
    ) -> None:
        """Tests if default value for custom_maps_folder is set correctly"""
        for platform in ("Linux", "Windows", "Darwin", "Java", ""):
            with self.subTest(platform=platform):
                self.assertEqual(
                    self.config.custom_maps_folder,
                    game_folders._get_default_custom_maps_folder(),
                )

    @unittest.skip("Must learn how package behaves if in zip")
    def test_resource_folder_property(self) -> None:
        """Tests if resources_folder property is returned correctly"""
        pass

    @unittest.skip("Must learn how package behaves if in zip")
    def test_official_map_folder_property(self) -> None:
        """Tests if official_maps_folder property is returned correctly"""
        pass

    def test_map_folders(self) -> None:
        """Tests if maps_folders property is returned correctly"""
        self.assertEqual(
            [self.config.official_maps_folder, self.config.custom_maps_folder],
            self.config.maps_folders,
        )

    def test_load_all(self) -> None:
        """Tests _GameFoldersConfig.load with all fields specified"""
        self.assertTrue(
            self.config.load({"log_folder": "a", "custom_maps_folder": "b"}),
            "Load of all fields did not return True",
        )
        self.assertEqual(
            self.config,
            game_folders._GameFoldersConfig(pathlib.Path("a"), pathlib.Path("b")),
            "Load of all fields did not set data correctly",
        )

    def test_load_1(self) -> None:
        """Tests _GameFoldersConfig.load with 1 field / 2 specified"""
        self.assertFalse(
            self.config.load({"log_folder": "a"}),
            "Load of 1 field / 2 did not return False",
        )
        self.assertEqual(
            self.config,
            game_folders._GameFoldersConfig(
                pathlib.Path("a"), game_folders._get_default_custom_maps_folder()
            ),
            "Load of 1 field did not set data correctly",
        )

    def test_load_all_and_1_bad(self) -> None:
        """Tests _GameFoldersConfig.load with all fields + 1 bad field specified"""
        self.assertTrue(
            self.config.load(
                {"log_folder": "a", "custom_maps_folder": "b", "bad_field": -1}
            ),
            "Load of all fields + 1 bad field did not return True",
        )
        self.assertEqual(
            self.config,
            game_folders._GameFoldersConfig(pathlib.Path("a"), pathlib.Path("b")),
            "Load of all fields + 1 bad field did not set data correctly",
        )

    def test_load_1_and_1_bad(self) -> None:
        """Tests _GameFoldersConfig.load with 1 field / 2 + 1 bad field specified"""
        self.assertFalse(
            self.config.load({"custom_maps_folder": "b", "bad_field": -1}),
            "Load of 1 field / 2 + 1 bad field did not return False",
        )
        self.assertEqual(
            self.config,
            game_folders._GameFoldersConfig(
                game_folders._get_default_log_folder(), pathlib.Path("b")
            ),
            "Load of 1 field + 1 bad field did not set data correctly",
        )

    def test_load_none(self) -> None:
        """Tests _GameFoldersConfig.load with no fields specified"""
        self.assertFalse(
            self.config.load({}), "Load of 0 fields / 2 did not return False"
        )
        self.assertEqual(
            self.config,
            game_folders._GameFoldersConfig(
                game_folders._get_default_log_folder(),
                game_folders._get_default_custom_maps_folder(),
            ),
            "Load of 0 fields modified data",
        )

    def test_dump(self) -> None:
        """Tests _GameFoldersConfig.dump"""
        self.config.log_folder = pathlib.Path("a")
        self.config.custom_maps_folder = pathlib.Path("b")
        dump = self.config.dump()

        self.assertEqual(
            self.config,
            game_folders._GameFoldersConfig(pathlib.Path("a"), pathlib.Path("b")),
            "Dump modified data",
        )

        self.assertEqual(
            dump,
            {"log_folder": "a", "custom_maps_folder": "b"},
            "Dump did not copy data correctly",
        )
