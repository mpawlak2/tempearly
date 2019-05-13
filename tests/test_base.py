"""
Test basic templating functionality.
"""
import pytest
from tempearly import Template
from tempearly.exceptions import TemplateSyntaxError


def test_no_tags():
	"""Test simple template strings without any tags.

	The Template.render() method should return the same string it was initialize with.
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
	"""Test template strings with simple variable tokens

	The Template.render() method should replace these tokens with
	appropriate values.
	"""
	template_strings = [
		("<<VAR>>", {"VAR": 12,}, "12"),
		("<div><<VAR>></div>", {"VAR": 1,}, "<div>1</div>"),
		("""<div><< VAR >></div>""", {"VAR": 1,}, "<div>1</div>"),
	]

	for ts in template_strings:
		template = Template.from_string(ts[0], context=ts[1])
		assert template.render() == ts[-1]


def test_incorrect_tags():
	"""Tests that a Template object can handle incorrect template strings."""
	# (template string, context, part of an expected exception)
	template_strings = [
		("<div><<>></div>", {}),
		("<div><<</div>", {}),
		("<div>>></div>", {}),
		("<div><<<VAR>></div>", {}),
		("""<div>
			<<<VAR>></div>""", {}),
		("""<div>

			<<<VAR>></div>""", {}),
	]

	exception_msgs = [
		["Line 1"],
		["Line 1", "not closed"],
		["Line 1", "forget"],
		["Line 1"],
		["Line 2"],
		["Line 3"],
	]

	for i, ts in enumerate(template_strings):
		template = Template.from_string(ts[0], context=ts[1])

		with pytest.raises(TemplateSyntaxError) as e:
			template.render()
		for m in exception_msgs[i]:
			assert m in str(e)
