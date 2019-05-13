"""
Test basic templating functionality.
"""

from tempearly import Template


def test_no_tags():
	"""Test simple template strings without any tags.

	The Template.render() method should return the same string as on the input.
	"""
	templates = [
		"simple template",
		"<p>hello there</p>",
		"<html><div></div></html>"
	]

	for t in templates:
		t = Template.from_string(t)
		assert t.render() == t
