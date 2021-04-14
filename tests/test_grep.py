from powpow import grep, GrepResult


class TestGrep:

    def test_grep_a_string(self):
        output = ("this is a string" | grep("string"))
        assert bool(output) is True

    def test_results_in_GrepResult(self):
        output = ("this is a string" | grep("string"))
        assert isinstance(output, GrepResult)

    def test_parameters_are_directly_available(self):
        g = grep('pattern', highlight='highlight')
        assert g.pattern == 'pattern' and g.highlight == 'highlight'
