"""
This module provides simple templating functionality.

How it works:
TODO:
"""


class Template():
	def __init__(self, template):
		self.template = template

	@classmethod
	def from_string(cls, template):
		return cls(template)
