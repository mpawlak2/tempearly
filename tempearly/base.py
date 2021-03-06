"""
This module provides a simple templating functionality.

Presents one class, `Template`, which creates and renders template strings.

Its features and API:

    The Template.from_string() class method constructs a Template object from a template 
    string (i.e., a string containing custom tags). You may also want to provide a context dictionary containing
    your key-value mappings.

    The Template.from_file() method works just like the method from_string() with the exception that the source 
    template string is read from the file on the disk.

    The Template.render() method renders a provided template string with the use of the context dictionary.

The Token class:
The Token class represents template tokens that can be of several types:
    (1) Variable token: this token is representing a custom tag with a variable name in it; when rendered
    will display the `context` dictionary value assigned to a key with the variable name.
    (2) Block token - token that is represented in a template string by <% ... %> tags, available expressions
    inside tags:
        - if expression
        - for loop
"""
from collections import deque
import datetime
import re

from .exceptions import TemplateSyntaxError, TemplateKeyError
from .defaults import DEFAULT_VARIABLE_REGISTRY, DEFAULT_FUNCTION_REGISTRY
from .conditions import Condition


VARIABLE_TAG_START = "<<"
VARIABLE_TAG_END = ">>"
BLOCK_TAG_START = "<%"
BLOCK_TAG_END = "%>"

tags_re = re.compile(r"({}.*?{}|{}.*?{})".format(
    re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
    re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END),
))


def create_exception(message, token=None, exception_class=TemplateSyntaxError):
    """Create an exception instance; a helper function.

    Arguments:
        token
            is the Token object, representing the match in a template string. (None by default)

        exception_class
            is a type of the TemplateError exception class, e.g., create_exception or TemplateKeyError
    """
    return exception_class(message, token=token)


class Template():
    def __init__(self, template, context):
        """Represents a template string."""
        self.template = template
        self.context = context
        self.tokens = []

    def process_token(self, token):
        """Process a token and return rendered value.

        A token can be either string literal or Token instance,
        detect which one and process it accordingly.
        """
        if isinstance(token, Token) or isinstance(token, Block):
            return str(token.render(self.context))
        return str(token)

    def tokenize(self):
        """Generate a token list from the input string.
        
        When finished, the `self.tokens` attribute will be populated.
        """
        tokens = []
        blocks = deque()
        block = None

        rendered = self.template
        line_no = 1

        for token in tags_re.split(rendered):
            prev_line_no = line_no
            line_no += len(re.findall("\n", token))

            if token.startswith(VARIABLE_TAG_START):
                start_l = len(VARIABLE_TAG_START)
                end_l = len(VARIABLE_TAG_END)
                token = Token(token[start_l:-end_l].strip(), line_no=line_no)
            elif VARIABLE_TAG_START in token and VARIABLE_TAG_END in token:
                tiny_line_no = 0
                # TODO: I might want to save that in a list for
                # a later use. Or refactor `token` into the list
                # type, and instead of .append use tokens + token syntax.
                for i, tiny in enumerate(re.split(r"\n", token)):
                    if VARIABLE_TAG_START in tiny:
                        tiny_line_no = i
                        raise create_exception(f"Line {prev_line_no + tiny_line_no}: new line after the opening variable tag (variable tags must be defined in a single line)")
                raise create_exception(f"Lines {prev_line_no} to {line_no}: new line after opening variable tag (variable tags must be defined in a single line)")
            elif VARIABLE_TAG_START in token:
                """Variable opening tag found, but not parsed, may be opened and not closed variable tag."""
                raise create_exception(f"Line {line_no}: not closed variable tag")
            elif VARIABLE_TAG_END in token:
                raise create_exception(f"Line {line_no}: single closed variable tag (did you forget to open variable tag?)")
            elif token.startswith(BLOCK_TAG_START):
                if "endif" not in token and "endfor" not in token:
                    block = Block(token[len(BLOCK_TAG_START): -len(BLOCK_TAG_END)].strip(), line_no)
                    blocks.append(block)
                    continue
                else:
                    # token is equal to something like that <% endif %> or <% endfor %>
                    block = blocks.pop()
                    if len(blocks) == 0:
                        tokens.append(block)
                        block = None
                        continue

            if block:
                block.append_token(token)
            else:
                tokens.append(token)
        return tokens

    def render(self):
        """Render a template string."""
        self.tokens = self.tokenize()

        return "".join([self.process_token(t) for t in self.tokens])

    @classmethod
    def from_string(cls, template, context=None):
        """Instantiate the Template class from a string.

        Arguments:

        `context` is a dictionary containing variables to use when rendering the template
        (by default it is an empty dictionary)

        Sample:
        >>> Template.from_string(template_string, {'variable': 'value'})
        """
        if not context:
            context = {}
        return cls(template, context)

    @classmethod
    def from_file(cls, file_name, context=None):
        """Instantiate the Template class with a template string from the file.

        Please be conscious that this method will load the entire file into the computer memory.
        You might want to use TODO: when dealing with bigger files.

        Arguments:

        `file_name` is the absolute path of a file that you want to use for rendering, TODO: file paths
        are relative to the template's root directory.

        (TODO: for now there is no such thing as a template's root dir)

        `context` is a dictionary containing variables to use when rendering the template
        (by default it is an empty dictionary)
        """
        with open(file_name, encoding="utf") as fh:
            return cls.from_string(fh.read(), context=context)


class Token:
    """Represents an inline token.

    After parsing a template string, the Template class will create tokens to
    represent parts that require additional processing.

    Types of tokens:
    VARIABLE - represents a variable token, for example, `<<VAR>>` string would translate
    into a Token instance with a VARIABLE type. Variable tags inside template strings must be defined in a
    single line.
    """

    # The default attribute, for now, is the dictionary
    # of callables that provide default values.
    defaults = DEFAULT_VARIABLE_REGISTRY
    # Default functions.
    funcs = DEFAULT_FUNCTION_REGISTRY

    def __init__(self, key, line_no):
        """Creates a new token.  

        key is the name of the variable that the `Template.render()` method parsed from a template string

        line_no is a number of a line at which token tags were discovered
        """
        self.key = key
        self.func = None
        self.line_no = line_no

        # Check if this is a two part expression in a format: XY variable/string
        # (1) It would have to start with one to two letter symbol followed by at least one space
        expression_match = re.match(r"(\w\w?)\s+[\w\W]", self.key)
        if expression_match:
            self.func = expression_match[1]
            self.key = self.key[len(self.func):].strip()

            if self.func not in self.funcs:
                raise create_exception(f"Line {self.line_no}: the function `{self.func}` does not exist")

    def render(self, context):
        """Use actual values from the Template's context to render a token.

        Every token represents a single variable from a template string. Hence it
        is a relatively simple operation. All we have to do here is to return the value of 
        `self.key` key of the `context` dictionary.
        """
        if len(self.key) == 0:
            raise create_exception(f"Line {self.line_no}: empty token variable on line")

        if self.key.isdigit():
            return int(self.key)

        if self.is_string_statement():
            """If the `self.key` is the string, i.e., template string for that fragment could look like: <<"STR">>."""
            q = self.key[0]
            stripped = self.key[1:-1]
            if q in stripped:
                """When the variable tag contains two strings, or an incorrect string."""
                raise create_exception(f"Line {self.line_no}: incorrect string in the variable tag")
            return self.compute(stripped)

        if len(self.key) <= 2:
            raise create_exception(f"Line {self.line_no}: the variable name is too short; variable names should be at leas 3 characters long")

        if not self.key.isidentifier():
            raise create_exception(f"Line {self.line_no}: incorrect variable name `{self.key}`")

        if self.key.startswith("D") and self.key[1:] in self.defaults:
            """Default variables start with the `D` prefix.
            TODO: If there is a variable in the context dictionary under the `self.key` key then use that one.
            """
            return self.compute(self.defaults[self.key[1:]]())

        if self.key not in context:
            raise create_exception(f"Line {self.line_no}: the variable `{self.key}` is not defined in the context dictionary", token=self, exception_class=TemplateKeyError)

        return self.compute(context[self.key])

    def compute(self, variable):
        """Compute with the use of a function if specified."""
        if self.func:
            try:
                return self.funcs[self.func](variable)
            except Exception as e:
                raise type(e)(f"Line {self.line_no}: (function error, correct attribute type?) {e}")
        return variable

    def is_string_statement(self):
        """Checks if the `self.key` contained between quotes."""
        if self.key.startswith("\"") and self.key.endswith("\""):
            return True
        elif self.key.startswith("'") and self.key.endswith("'"):
            return True
        return False

    def __str__(self):
        return self.key


class Block:
    """The Block class represents the template block expression, it may be an 'if' statement
    or a loop. Each block can contain Token objects and other Block objects.

    A self.tokens attribute stores strings, Token objects, and Block objects.
    """

    def __init__(self, token, line_no):
        """The expression (token argument) is some kind of comparison expression that
        contains Token objects.
        """
        self.condition = False
        self.conditions = []
        self.loop = False

        if "if" in token:
            self.condition = True
        elif "for" in token:
            self.loop = True

        self.operand = token
        self.tokens = []

        # Prepare an 'if' expression.
        if self.condition:
            self.operand = self.operand.replace("if", "", 1)
            self.conditions.append(Condition(self.operand, line_no))


    def append_token(self, token):
        """`token` is a string, Token or a Block object."""
        self.tokens.append(token)

    def render(self, context):
        """Similar to the Token.render() method."""
        if not self.conditions[0].check(context):
            return ""

        resp = ""
        for t in self.tokens:
            if isinstance(t, Token):
                resp = resp + str(t.render(context))
            else:
                resp = resp + t
        return resp
