"""
Test basic templating functionality.
"""
import pytest
from tempearly import Template
from tempearly.exceptions import TemplateSyntaxError


def test_no_tags():
	"""Test simple template strings without any tags.

	The Template.render() method should return the same string as on the input.
	"""
	template_strings = [
		"simple template",
		"<p>hello there</p>",
		"<html><div></div></html>"
	]

	for ts in template_strings:
		template = Template.from_string(ts)
		assert template.render() == ts


def test_variables():
	"""Test template strings with simple variables tokens

	Template.render() method should replace these with appropriate
	values.
	"""
	template_strings = [
		("<<VAR>>", {"VAR": 12,}, "12"),
		("<div><<VAR>></div>", {"VAR": 1,}, "<div>1</div>"),
	]

	for ts in template_strings:
		template = Template.from_string(ts[0], context=ts[1])
		assert template.render() == ts[-1]


def test_incorrect_tags():
	"""Test that Template can handle an incorrect template strings."""
	template_strings = [
		("<div><<>></div>", {}), # Empty variable tag
		("<div><<<VAR>></div>", {}), # Incorrect tag opening
	]

	for ts in template_strings:
		template = Template.from_string(ts[0], context=ts[1])

		with pytest.raises(TemplateSyntaxError):
			template.render()
