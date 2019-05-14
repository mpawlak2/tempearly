"""
This module provides default variables that can be used from
a template string.
"""
import datetime

DEFAULT_VARIABLE_REGISTRY = {}
_KEYS = set()


class DefaultVariableMeta(type):
    """Metaclass that will register default fields."""

    def __new__(meta, name, bases, class_dict):
        """There are some conditions:

        (1) The class_dict must contain `name` key.
        (2) The `key` must be unique
        """
        cls = type.__new__(meta, name, bases, class_dict)
        if len(bases) > 0:
            if "name" not in class_dict:
                raise AttributeError(
                    "You must provide the `name` attribute on your custom"
                    " default variable class"
                )

            default_var_name = class_dict["name"]
            if default_var_name in _KEYS:
                raise AttributeError(
                    f"The default variable with the name `{default_var_name}` already"
                    " exists, choose another name."
                )

            _KEYS.add(default_var_name)
            DEFAULT_VARIABLE_REGISTRY[default_var_name] = cls()
        return cls


class DefaultVariable(metaclass=DefaultVariableMeta):
    """When subclassing always remember to provide the `name` class attribute
    which must be a unique variable name (among default variables that are already defined).

    All you have to do to use your variable is to subclass this class, and implement the `__call__` method
    that will return the value that can be converted to string.

    Usage from a template string:
        From a template string you would use your variable by prefixing it with the
        `D` character, i.e., capital D.
    """
    pass


class DDate(DefaultVariable):
    """Provides a default variable with the name `Ddate`."""
    name = "date"

    def __call__(self):
        return datetime.date.today()


class DDatetime(DefaultVariable):
    name = "datetime"

    def __call__(self):
        return datetime.datetime.today()
