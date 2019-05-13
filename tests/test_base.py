"""
Test basic templating functionality.
"""

from tempearly import Template


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
