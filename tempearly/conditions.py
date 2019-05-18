"""
    This module provides functionality to implement if operator in string templates.
    An 'if' operator can be used as a block operator within block tags, e.g.,
        <% if a == b %>
            ...
        <% endif %>

    Every 'if' operator has to be of that form:
        - opening and closing block tags
        - endif statement at the end
"""
import re


OPERATORS = {}
operators_re = re.compile(r"({}|{}|{}|{})".format(
    re.escape("=="), re.escape(">"), re.escape(">="),
    re.escape("<"), re.escape("<=")
))

class Condition:
    """Simples unit of logic in template. Used with 'if' Block objects."""

    def __init__(self, condition):
        """The condition argument is a simple three part expression, something operator something."""
        s = operators_re.split(condition)
        self.a = s[0].strip()
        self.b = s[2].strip()
        self.op = s[1].strip()

    def check(self):
        """Evaluate the conditional logic."""
        return OPERATORS[self.op](self.a, self.b)


def register_operator(name):
    """A decorator function that registers operator functions with their symbols."""
    def decorator(func):
        OPERATORS[name] = func
        return func
    return decorator


@register_operator("==")
def equals(a, b):
    return a == b
