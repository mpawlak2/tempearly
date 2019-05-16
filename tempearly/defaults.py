"""
This module provides default variables that can be used from
a template string.

Default variables consist of:
(1) date
    usage: <<Ddate>>
    Returns today's date. By default will be cast to the string.

(2) datetime
    usage: <<Ddatetime>>
    Returns the current time through the datetime.datetime object.

(3)
    lorem
    usage: <<Dlorem>>
    Returns lorem ipsum hard-coded text.
"""
import datetime
import os


DEFAULT_VARIABLE_REGISTRY = {}
DEFAULT_FUNCTION_REGISTRY = {}
_KEYS = set()


def register_func(name):
    """Register a function to use it from a template string under the `name` name."""
    def decorator(func):
        DEFAULT_FUNCTION_REGISTRY[name] = func
        return func
    return decorator


@register_func("DY")
def get_date_year(date):
    """Get the year part from the date."""
    return date.year


class DefaultVariableMeta(type):
    """Metaclass that will register default fields."""

    def __new__(meta, name, bases, class_dict):
        """There are some conditions:

        (1) The class_dict must contain `name` key
        (2) The `key` must be unique
        (3) The class must define __call__ method
        """
        cls = type.__new__(meta, name, bases, class_dict)
        if len(bases) > 0:
            if "__call__" not in class_dict:
                raise AttributeError(
                    "You must implement the `__call__` method in your"
                    " custom default variable."
                )

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


class DEnv(DefaultVariable):
    """Default variable that returns a list of environmental variables in an operating system."""

    name = "env"

    def __call__(self):
        return dict(os.environ)


class DLorem(DefaultVariable):
    """Default variable providing lorem ipsum text.

    The hard-coded text is used as I do not want to use an external lib
    or write one myself.
    """
    name = "lorem"

    def __call__(self):
        return """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed quis vehicula turpis. Vestibulum eu blandit libero. Praesent cursus felis imperdiet porta ornare. Quisque tincidunt lectus id egestas semper. In hac habitasse platea dictumst. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Nunc cursus ante eros, id euismod libero congue nec. Vivamus hendrerit turpis vel hendrerit pulvinar. Curabitur eget urna sit amet erat euismod tincidunt ut sed velit. Praesent at odio odio.
Praesent non varius dolor, et ullamcorper velit. Mauris a ipsum interdum nunc luctus pulvinar. Donec viverra ultricies nibh, ac dapibus elit. Nulla scelerisque lorem et libero molestie scelerisque. Suspendisse maximus tortor vitae efficitur consectetur. In ornare felis a neque gravida dictum. Quisque quis risus a enim pellentesque sollicitudin. Nunc eu lorem a augue tempor pellentesque. Mauris vestibulum commodo porta. Curabitur varius odio ac porttitor consequat."""
