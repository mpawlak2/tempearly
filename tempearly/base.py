"""
This module provides simple templating functionality.

How it works:
TODO:
"""
import re


VARIABLE_TAG_START = "*"
VARIABLE_TAG_END = "*"

tags_re = re.compile(r"{}.*?{}".format(
	re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
))


class Template():
	def __init__(self, template, context):
		"""Represents template string."""
		self.template = template

	def render(self):
		"""Render template string"""
		return self.template

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
