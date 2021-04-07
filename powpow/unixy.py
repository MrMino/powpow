# coding: utf-8
from pprint import pformat

ANSI_RED = '\u001b[31m'
ANSI_RESET = '\u001b[0m'


# TODO: make this such that match results aren't inclued in its state
class grep:  # noqa
    """Finds matches of a simple string in the object string representation.

    Unless a plain string is used, the representation of the object is obtained
    by using ``pprint.pformat()``.
    """
    def __init__(self, pattern: str, highlight: bool = True):
        self.pattern = pattern
        self.highlight = highlight

    # TODO: this should return some kind of a result object with repr, instead
    # of printing.
    # FIXME: TypeError: unsupported operand type(s) for |: 'grep' and 'grep'
    def __ror__(self, obj):
        if isinstance(obj, str):
            lines = obj.splitlines()
        else:
            lines = pformat(obj).splitlines()
        matches = list(filter(lambda line: self.pattern in line, lines))
        if self.highlight:
            self._highlight(matches)

        self.matches = matches
        print(str(self))
        return self

    def __str__(self):
        return '\n'.join(self.matches)

    def _highlight(self, matches):
        for idx, line in enumerate(matches):
            match_pos = 0

            while True:
                match_pos = line.find(self.pattern, match_pos + 1)
                if match_pos < 0:
                    break

                line = (
                    line[:match_pos]
                    + ANSI_RED
                    + line[match_pos:match_pos + len(self.pattern)]
                    + ANSI_RESET
                    + line[match_pos + len(self.pattern):]
                )

                matches[idx] = line
                match_pos += len(ANSI_RED) + len(ANSI_RESET)
