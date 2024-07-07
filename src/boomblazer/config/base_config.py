"""Base class for configuration variables dataclasses

Classes:
    BaseConfig:
        Base class for configuration variables dataclasses
"""


import abc
import dataclasses
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import Optional


@dataclasses.dataclass
class BaseConfig(abc.ABC):
    """Base class for configuration variables dataclasses

    Methods:
        load:
            Loads field values from a dict
        dump:
            Dumps field values to a dict
        reset:
            Resets all, or some field values to default
    """

    def load(self, new_field_values: Mapping[str, Any]) -> bool:
        """Loads field values from a dict

        Parameters:
            new_field_values: Mapping[str, Any]
                The names and new values of fields to be updated
                Unknown fields will be ignored

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

    def reset(self, fields_to_reset: Optional[Sequence[str]] = None) -> None:
        """Resets all, or some field values to default

        Parameters:
            members_to_reset: Optional[Sequence[str]] (default = None)
                The name of attributes to reset (all by default)
        """
        if fields_to_reset is None:
            fields_to_reset = self.__slots__

        fields = dataclasses.fields(self)
        for field in fields:
            if field.name not in fields_to_reset:
                continue
            if field.default is not dataclasses.MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not dataclasses.MISSING:
                setattr(self, field.name, field.default_factory())
