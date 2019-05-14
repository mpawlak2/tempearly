"""
Test basic templating functionality.
"""
import datetime
import pytest
from tempearly import Template
from tempearly.exceptions import TemplateSyntaxError, TemplateKeyError


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
		assert len(template.tokens) > 0


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
		("""<div>

			<<



			<VAR>></div>""", {}),
		("""<div><<



			<VAR>></div>""", {}),
	]

	exception_msgs = [
		["Line 1"],
		["Line 1", "not closed"],
		["Line 1", "forget"],
		["Line 1"],
		["Line 2"],
		["Line 3"],
		["Line 3", "must", "single", "line"],
		["Line 1", "must", "single", "line"],
	]

	for i, ts in enumerate(template_strings):
		template = Template.from_string(ts[0], context=ts[1])

		with pytest.raises(TemplateSyntaxError) as e:
			template.render()
		for m in exception_msgs[i]:
			assert m in str(e), f"Testing index: {i}"


def test_variable_does_not_exist():
	"""A variable name used in the variable tags must be defined in the context."""
	templates = ("<<div>>", {}) # Notice there is no "div" key in the dictionary.
	template = Template.from_string(templates[0], templates[1])
	with pytest.raises(TemplateKeyError) as e:
		template.render()
	assert "context" in str(e)
	assert "Line 1" in str(e)
	try:
		template.render()
	except TemplateKeyError as e:
		assert e.token


def test_default_variables():
    """The Template should provide some variables by default.

    Default variables are prefixed with the `D` character, e.g., Ddate.
    """
    templates = [
        [
            "<<Ddate>>",
            {},
            f"{datetime.date.today()}",
        ],
        [
            "<<Ddatetime>>",
            {},
            f"{datetime.datetime.now()}",
        ],
    ]

    for t in templates:
        template = Template.from_string(t[0], t[1])
        assert template.render() == t[2]

    # If the default variable does not exist
    # the TemplateKeyError exception should be raised.
    with pytest.raises(TemplateKeyError) as e:
        template = Template.from_string("<<DtotallyDoesNotExists>>")
        template.render()

    # If you pass just the `D` character there should
    # be an exception raised.
    with pytest.raises(TemplateSyntaxError) as e:
        template = Template.from_string("<<D>>")
        template.render()
    assert "characters" in str(e)
    assert "Line 1" in str(e)
