from powpow import grep


def test_grep_a_string():
    output = ("this is a string" | grep("string"))
    assert bool(output) is True
