"""
This module provides default variables that can be used from
a template string.
"""
import datetime

DEFAULT_VARIABLE_REGISTRY = {}


class DefaultVariableMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if len(bases) > 0:
            DEFAULT_VARIABLE_REGISTRY[class_dict["name"]] = cls()
        return cls


class DefaultVariable(metaclass=DefaultVariableMeta):
    pass


class DDate(DefaultVariable):
    """Provides a default variable with the name `Ddate`."""
    name = "date"

    def __call__(self):
        return datetime.date.today()
