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
import tempearly.base


OPERATORS = {}
operators_re = re.compile(r"({}|{}|{}|{})".format(
    re.escape("=="), re.escape(">"), re.escape(">="),
    re.escape("<"), re.escape("<=")
))

class Condition:
    """Simples unit of logic in template. Used with 'if' Block objects."""

    def __init__(self, condition, line_no):
        """The condition argument is a simple three part expression, something operator something."""
        s = operators_re.split(condition)
        a, self.op, b = [i.strip() for i in s]
        self.a_tok = tempearly.base.Token(a, line_no)
        self.b_tok = tempearly.base.Token(b, line_no)

    def check(self, context):
        """Evaluate the conditional logic.

        Arguments:

        `context` is a context dictionary used to render the whole template.
        """
        a_ren = self.a_tok.render(context)
        b_ren = self.b_tok.render(context)
        return OPERATORS[self.op](a_ren, b_ren)


def register_operator(name):
    """A decorator function that registers operator functions with their symbols."""
    def decorator(func):
        OPERATORS[name] = func
        return func
    return decorator


@register_operator("==")
def equals(a, b):
    return a == b
