import pytest

from textwrap import dedent

from powpow import grep, GrepResult


class TestGrep:

    def test_grep_a_string(self):
        output = ("this is a string" | grep("string"))
        assert bool(output) is True

    def test_grep_multiple_times(self):
        output = ("this is a string" | grep("string") | grep("string"))
        assert bool(output) is True

    def test_results_in_GrepResult(self):
        output = ("this is a string" | grep("string"))
        assert isinstance(output, GrepResult)

    def test_empty_pattern_is_not_allowed(self):
        with pytest.raises(ValueError):
            grep('')

    def test_parameters_are_directly_available(self):
        g = grep('pattern', highlight='highlight')
        assert g.pattern == 'pattern' and g.highlight == 'highlight'

    def test_highlights_matches_in_repr(self):
        output = ("this is a string" | grep("this"))
        assert repr(output).startswith('\u001b[31m')

    def test_highlight_resets_after_match(self):
        output = repr("this is a string" | grep("a"))
        assert output[output.find('a') + 1:].startswith('\u001b[0m')

    def test_highligh_can_be_turned_off(self):
        output = ("this is a string" | grep("string", highlight=False))
        assert repr(output) == "this is a string"

    def test_finds_matched_lines(self):
        lines = dedent("""
        this
        is
        a
        string
        """)

        assert (lines | grep("i")).matched_lines == ['this', 'is', 'string']
