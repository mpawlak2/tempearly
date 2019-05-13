"""
This module provides simple templating functionality.

How it works:
TODO:
"""
import re


VARIABLE_TAG_START = "*"
VARIABLE_TAG_END = "*"

tags_re = re.compile(r"({}.*?{})".format(
	re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
))


class Template():
	def __init__(self, template, context):
		"""Represents template string."""
		self.template = template

	def render(self):
		"""Render template string"""
		tokens = []
		rendered = self.template

		for token in tags_re.split(rendered):
			if token.startswith(VARIABLE_TAG_START):
				start_l = len(VARIABLE_TAG_START)
				end_l = len(VARIABLE_TAG_END)

				token = Token(token[start_l:-end_l])
			tokens.append(token)

		return "".join([str(e) for e in tokens])

	@classmethod
	def from_string(cls, template, context=None):
		"""Initialize template from string

		context is a dictionary containing your variables, by default
		it is an empty dictionary

		Sample:
		>>> Template.from_string(template_string, {'variable': 'value'})
		"""
		if not context:
			context = {}
		return cls(template, context)


class Token:
	"""Represents inline token

	After parsing the whole string, Template class will create tokens to
	represent parts of the code that require additional processing.

	Types of tokens:
	VARIABLE - represents a variable token, for example, *VAR* would translate
	to Token instance with VARIABLE type.

	"""

	def __init__(self, content):
		self.content = content

	def __str__(self):
		return self.content