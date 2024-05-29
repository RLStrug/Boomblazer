"""Base class for configuration variables dataclasses

Classes:
    BaseConfig:
        Base class for configuration variables dataclasses
"""


import abc
import dataclasses
from typing import Mapping
from typing import Optional
from typing import Sequence


@dataclasses.dataclass(slots=True)
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

    def load(self, new_field_values: Mapping) -> None:
        """Loads field values from a dict

        Parameters:
            new_field_values: dict
                The names and new values of fields to be updated
                Unknown fields will be ignored
        """
        fields = dataclasses.fields(self)
        for field in fields:
            new_value = new_field_values.get(field.name)
            if new_value is not None:
                # TODO check type
                # assert isinstance(new_value, field.type)
                setattr(self, field.name, new_value)

    def dump(self) -> dict:
        """Dumps field values to a dict

        Return value: dict
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
