"""Tests boomblazer.config.ncurses
"""

import unittest

from boomblazer.config.ncurses import _NcursesConfig


class Test_NcursesConfig(unittest.TestCase):
    """Tests _NcursesConfig
    """

    def setUp(self) -> None:
        """Instanciates a _NcursesConfig before each test
        """
        self.config = _NcursesConfig()

    def test_menu_up_buttons_default_value(self) -> None:
        """Tests if default value for menu_up_buttons is set correctly
        """
        self.assertEqual(
            self.config.menu_up_buttons,
            _NcursesConfig._DEFAULT_MENU_UP_BUTTONS,
            "menu_up_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.menu_up_buttons,
            _NcursesConfig._DEFAULT_MENU_UP_BUTTONS,
            "menu_up_buttons is not a copy (same object id)"
        )

    def test_menu_down_buttons_default_value(self) -> None:
        """Tests if default value for menu_down_buttons is set correctly
        """
        self.assertEqual(
            self.config.menu_down_buttons,
            _NcursesConfig._DEFAULT_MENU_DOWN_BUTTONS,
            "menu_down_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.menu_down_buttons,
            _NcursesConfig._DEFAULT_MENU_DOWN_BUTTONS,
            "menu_down_buttons is not a copy (same object id)"
        )

    def test_move_up_buttons_default_value(self) -> None:
        """Tests if default value for move_up_buttons is set correctly
        """
        self.assertEqual(
            self.config.move_up_buttons,
            _NcursesConfig._DEFAULT_MOVE_UP_BUTTONS,
            "move_up_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.move_up_buttons,
            _NcursesConfig._DEFAULT_MOVE_UP_BUTTONS,
            "move_up_buttons is not a copy (same object id)"
        )

    def test_move_down_buttons_default_value(self) -> None:
        """Tests if default value for move_down_buttons is set correctly
        """
        self.assertEqual(
            self.config.move_down_buttons,
            _NcursesConfig._DEFAULT_MOVE_DOWN_BUTTONS,
            "move_down_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.move_down_buttons,
            _NcursesConfig._DEFAULT_MOVE_DOWN_BUTTONS,
            "move_down_buttons is not a copy (same object id)"
        )

    def test_move_left_buttons_default_value(self) -> None:
        """Tests if default value for move_left_buttons is set correctly
        """
        self.assertEqual(
            self.config.move_left_buttons,
            _NcursesConfig._DEFAULT_MOVE_LEFT_BUTTONS,
            "move_left_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.move_left_buttons,
            _NcursesConfig._DEFAULT_MOVE_LEFT_BUTTONS,
            "move_left_buttons is not a copy (same object id)"
        )

    def test_move_right_buttons_default_value(self) -> None:
        """Tests if default value for move_right_buttons is set correctly
        """
        self.assertEqual(
            self.config.move_right_buttons,
            _NcursesConfig._DEFAULT_MOVE_RIGHT_BUTTONS,
            "move_right_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.move_right_buttons,
            _NcursesConfig._DEFAULT_MOVE_RIGHT_BUTTONS,
            "move_right_buttons is not a copy (same object id)"
        )

    def test_drop_bomb_buttons_default_value(self) -> None:
        """Tests if default value for bomb_buttons is set correctly
        """
        self.assertEqual(
            self.config.drop_bomb_buttons,
            _NcursesConfig._DEFAULT_DROP_BOMB_BUTTONS,
            "drop_bomb_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.drop_bomb_buttons,
            _NcursesConfig._DEFAULT_DROP_BOMB_BUTTONS,
            "drop_bomb_buttons is not a copy (same object id)"
        )

    def test_quit_buttons_default_value(self) -> None:
        """Tests if default value for quit_buttons is set correctly
        """
        self.assertEqual(
            self.config.quit_buttons, _NcursesConfig._DEFAULT_QUIT_BUTTONS,
            "quit_buttons is not set correctly"
        )
        self.assertIsNot(
            self.config.quit_buttons, _NcursesConfig._DEFAULT_QUIT_BUTTONS,
            "quit_buttons is not a copy (same object id)"
        )
