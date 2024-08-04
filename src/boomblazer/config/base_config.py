"""Base class for configuration variables dataclasses"""

from __future__ import annotations

import abc
import dataclasses
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence
    from typing import Any


@dataclasses.dataclass
class BaseConfig(abc.ABC):
    """Base class for configuration variables dataclasses"""

    def load(self, new_field_values: Mapping[str, Any]) -> bool:
        """Loads field values from a dict

        Parameters:
            new_field_values: Mapping[str, Any]
                Fields new values. Unknown fields will be ignored

        Return value: bool
            True if all fields could be loaded from new_field_values.
            False if any field was missing
        """
        all_fields_present = True
        fields = dataclasses.fields(self)
        for field in fields:
            new_value = new_field_values.get(field.name)
            if new_value is not None:
                # TODO check type
                # assert isinstance(new_value, field.type)
                setattr(self, field.name, new_value)
            else:
                all_fields_present = False
        return all_fields_present

    def dump(self) -> dict[str, Any]:
        """Dumps field values to a dict

        Return value: dict[str, Any]
            The dataclass as a dict
        """
        return dataclasses.asdict(self)

    def reset(self, fields_to_reset: Sequence[str] | None = None) -> None:
        """Resets all, or some field values to default

        Parameters:
            members_to_reset: Sequence[str] | None (default = None)
                Attributes to reset (all by default)
        """
        fields = dataclasses.fields(self)
        for field in fields:
            if fields_to_reset is not None and field.name not in fields_to_reset:
                continue
            if field.default is not dataclasses.MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not dataclasses.MISSING:
                setattr(self, field.name, field.default_factory())
