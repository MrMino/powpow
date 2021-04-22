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
        result = lines | grep("i")
        assert result.matched_lines == ['this\n', 'is\n', 'string\n']

    def test_has_eq_with_other_strings(self):
        assert "string" | grep("s") == "string"

    def test_is_hashable(self):
        hash("a" | grep("a"))

    def test_different_matches_dont_hash_the_same(self):
        text = "This is what we'll grep"
        r1 = text | grep("This")
        r2 = text | grep("we'll")
        assert hash(r1) != hash(r2)

    def test_preserves_last_newline(self):
        text = "This input has a newline that should be preserved \n"
        assert str(text | grep("This")).endswith('\n')
