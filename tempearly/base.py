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
		self.context = context

	def process_token(self, token):
		"""Process a token and return rendered value.

		A token can be either string literal or Token instance,
		detect which is it and process it accordingly.
		"""
		if isinstance(token, Token):
			return str(token.render(self.context))
		return str(token)

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

		print(tokens)
		return "".join([self.process_token(t) for t in tokens])

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

	def __init__(self, key):
		"""Creates a new token

		key is the name of the variable that the `Template.render()` method parsed from a template string
		"""
		self.key = key

	def render(self, context):
		"""Use actual values from Template's context to render the token.

		Every token represents a single variable from a template string. Hence it
		is a relatively simple operation. All we have to do here is to return the value of 
		`self.key` key of the `context` dictionary.
		"""
		return context[self.key]

	def __str__(self):
		return self.key
