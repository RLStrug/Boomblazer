"""Tests boomblazer.config.cli module
"""

import unittest

from boomblazer.config.cli import _CLI_Config


class Test_CLI_Config(unittest.TestCase):
    """Tests _CLI_Config
    """

    def setUp(self) -> None:
        """Instanciates a _CLI_Config before each test
        """
        self.config = _CLI_Config()

    def test_up_commands_default_value(self) -> None:
        """Tests if default value for up_commands is set correctly
        """
        self.assertEqual(
            self.config.up_commands, _CLI_Config._DEFAULT_UP_COMMANDS,
            "up_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.up_commands, _CLI_Config._DEFAULT_UP_COMMANDS,
            "up_commands is not a copy (same object id)"
        )

    def test_down_commands_default_value(self) -> None:
        """Tests if default value for down_commands is set correctly
        """
        self.assertEqual(
            self.config.down_commands, _CLI_Config._DEFAULT_DOWN_COMMANDS,
            "down_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.down_commands, _CLI_Config._DEFAULT_DOWN_COMMANDS,
            "down_commands is not a copy (same object id)"
        )

    def test_left_commands_default_value(self) -> None:
        """Tests if default value for left_commands is set correctly
        """
        self.assertEqual(
            self.config.left_commands, _CLI_Config._DEFAULT_LEFT_COMMANDS,
            "left_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.left_commands, _CLI_Config._DEFAULT_LEFT_COMMANDS,
            "left_commands is not a copy (same object id)"
        )

    def test_right_commands_default_value(self) -> None:
        """Tests if default value for right_commands is set correctly
        """
        self.assertEqual(
            self.config.right_commands, _CLI_Config._DEFAULT_RIGHT_COMMANDS,
            "right_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.right_commands, _CLI_Config._DEFAULT_RIGHT_COMMANDS,
            "right_commands is not a copy (same object id)"
        )

    def test_bomb_commands_default_value(self) -> None:
        """Tests if default value for bomb_commands is set correctly
        """
        self.assertEqual(
            self.config.bomb_commands, _CLI_Config._DEFAULT_BOMB_COMMANDS,
            "bomb_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.bomb_commands, _CLI_Config._DEFAULT_BOMB_COMMANDS,
            "bomb_commands is not a copy (same object id)"
        )

    def test_quit_commands_default_value(self) -> None:
        """Tests if default value for quit_commands is set correctly
        """
        self.assertEqual(
            self.config.quit_commands, _CLI_Config._DEFAULT_QUIT_COMMANDS,
            "quit_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.quit_commands, _CLI_Config._DEFAULT_QUIT_COMMANDS,
            "quit_commands is not a copy (same object id)"
        )

    def test_ready_commands_default_value(self) -> None:
        """Tests if default value for ready_commands is set correctly
        """
        self.assertEqual(
            self.config.ready_commands, _CLI_Config._DEFAULT_READY_COMMANDS,
            "ready_commands is not set correctly"
        )
        self.assertIsNot(
            self.config.ready_commands, _CLI_Config._DEFAULT_READY_COMMANDS,
            "ready_commands is not a copy (same object id)"
        )
