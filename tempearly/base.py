"""
This module provides simple templating functionality.

How it works:
TODO:
"""


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
