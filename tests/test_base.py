"""
Test basic templating functionality.
"""
import datetime
import os

import pytest

from tempearly import Template
from tempearly.exceptions import TemplateKeyError, TemplateSyntaxError


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


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


def test_simple_html_file():
    """Render a simple html file.

    There are no variable tags in that HTML file. Just make sure that a real-world HTML template
    would not cause any name clashes. I chose tags << and >> to indicate a variable context. Although
    there is a lot of < and > in HTML, you wouldn't usually use double < (<<) or > (>>).
    """
    with open(os.path.join(TEMPLATE_DIR, "reddit.html"), encoding="utf") as fh:
        contents = fh.read()
        t = Template.from_string(contents)
        assert t.render() == contents


def test_html_file():
    """The Template class should load files itself."""
    template = Template.from_file(os.path.join(TEMPLATE_DIR, "reddit.html"))
    assert template.render()

    # Html file with a variable tag.
    template = Template.from_file(os.path.join(TEMPLATE_DIR, "variable_date.html"))
    assert str(datetime.date.today()) in template.render()


def test_variables():
    """Test template strings with simple variable tokens

    The Template.render() method should replace these tokens with
    appropriate values. If the contents within variable tag are put
    between quotes, then that tag should evaluate to that string.
    """
    template_strings = [
        ("<<VAR>>", {"VAR": 12,}, "12"),
        ("<div><<VAR>></div>", {"VAR": 1,}, "<div>1</div>"),
        ("""<div><< VAR >></div>""", {"VAR": 1,}, "<div>1</div>"),
        ("""<div><< "VAR" >></div>""", {"VAR": 1,}, "<div>VAR</div>"),
        ("""<div><< " VAR" >></div>""", {"VAR": 1,}, "<div> VAR</div>"),
        ("""<div><< ' VAR' >></div>""", {"VAR": 1,}, "<div> VAR</div>"),
        ("""<div><< " " >></div>""", {"VAR": 1,}, "<div> </div>"),
        ("""<div><< "" >></div>""", {"VAR": 1,}, "<div></div>"),
    ]

    for ts in template_strings:
        template = Template.from_string(ts[0], context=ts[1])
        assert template.render() == ts[-1]

    # A variable tag with two string declarations should raise an exception.
    t = Template.from_string("<<'' ''>>")
    with pytest.raises(TemplateSyntaxError) as e:
        t.render()
    assert "incorrect" in str(e)
    assert "string" in str(e)

    # An incorrect string, three quotes.
    t = Template.from_string("<< ''' >>")
    with pytest.raises(TemplateSyntaxError) as e:
        t.render()
    assert "incorrect" in str(e)
    assert "string" in str(e)


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
            True, # We can get millisecond differences.
        ],
        [
            "<<Denv>>",
            {},
            str(dict(os.environ)),
        ],
        [
            "<<Dlorem>>",
            {},
            True,
        ],
    ]

    for t in templates:
        template = Template.from_string(t[0], t[1])
        if t[2] == True:
            assert template.render() is not None
        else:
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


def test_variable_funcs():
    """By using one to two letter symbol before the variable name or a string,
    template engine should apply functions.

    All the functions should be one to two letter words.
    """
    # DY function would get year from the date
    template = Template.from_string("<<DY Ddate>>")
    assert template.render() == str(datetime.date.today().year)

    # Should raise when wrong type, e.g., passing string.
    template = Template.from_string("<<DY 'test'>>")
    with pytest.raises(AttributeError) as e:
        template.render()
    # And should add line number to the error message.
    assert "Line 1" in str(e)

    # Should raise when the function does not exist
    template = Template.from_string("<<XX 'test'>>")
    with pytest.raises(TemplateSyntaxError):
        template.render()

    # Should raise when the function has more than 2 letters.
    template = Template.from_string("<<XXC 'test'>>")
    with pytest.raises(TemplateSyntaxError):
        template.render()

    # SU - string upper
    # Convert string to the upper case.
    messages = [
        "test test test",
        "",
    ]
    for m in messages:
        template = Template.from_string(f"<<SU '{m}'>>")
        assert template.render() == (m.upper() if m else "")
