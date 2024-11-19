"""Helper class for a choice list"""

from __future__ import annotations

import enum
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Self
    from typing import Any


# class Choice:
#
#     def __init__(self, choices: Mapping[str, str]) -> None:
#         """a"""
#         self.choices = enum.Enum(
#             "choices", " ".join(choices.keys()), start=0
#         )
#         self.labels = choices.values()
#         self.value = 0
#
#     def next(self) -> None:
#         self.value = (self.value + 1 ) % len(self.choices)
#
#
#     def previous(self) -> None:
#         self.value = (self.value + len(self.choices) - 1 ) % len(self.choices)
#
#     def __getattr__(self, attr: str) -> enum.Enum:
#         return self.choices[attr]
#
#     def __eq__(self, other: Any) -> bool:
#         if not isinstance(other, self.choices):


class Choice(enum.Enum):
    """Helper class for a choice list"""

    def __new__(cls, label: str) -> Self:
        """Creates a new Choice enum member

        :returns: The new enum object
        """
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)  # Starts at 0 for easier modulo ops
        obj.label = label
        return obj

    def __init__(self, label: str) -> None:
        """Useless method. All should be in __new__, but mypy complains

        :param label: The label associated to the choice
        """
        self.label = label

    @property
    def next(self) -> Self:
        """Get the next choice in the list

        :returns: The next choice
        """
        return self.__class__((self.value + 1) % len(self.__class__))

    @property
    def previous(self) -> Self:
        """Get the previous choice in the list

        :returns: The previous choice
        """
        cls = self.__class__
        return cls((self.value + len(cls) - 1) % len(cls))

    def __index__(self) -> int:
        """Allows using a choice enum as an array index

        :returns: The index value corresponding to the enum value
        """
        assert isinstance(self._value_, int)
        return self._value_
