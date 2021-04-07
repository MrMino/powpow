# coding: utf-8
from pprint import pformat
from typing import List, Tuple

ANSI_RED = '\u001b[31m'
ANSI_RESET = '\u001b[0m'


LineMatches = List[Tuple[str, List[slice]]]


# FIXME: ("aaabbb" | grep('a') | grep('b')).matches contains ANSI colors
class grep:  # noqa
    """Finds matches of a simple string in the object string representation.

    Unless a plain string is used, the representation of the object is obtained
    by using ``pprint.pformat()``.
    """
    def __init__(self, pattern: str, highlight: bool = True):
        self.pattern = pattern
        self.highlight = highlight

    def __ror__(self, obj):
        if isinstance(obj, str):
            lines = obj.splitlines()
        else:
            lines = pformat(obj).splitlines()

        matches = self._match(self.pattern, lines)

        return GrepResult(self.pattern, matches, highlight=self.highlight)

    @staticmethod
    def _match(pattern, lines: List[str]) -> LineMatches:
        """Match lines to a fixed string

        Returns a list of (line, [slice, ...]) tuples, where each slice points
        to a substring of line that contains the pattern.
        """
        pattern_len = len(pattern)
        matches: LineMatches = []

        for line_idx, line in enumerate(lines):
            if pattern not in line:
                continue

            line_matches = []
            match_pos = 0
            while True:
                match_pos = line.find(pattern, match_pos)
                if match_pos < 0:
                    break

                line_matches.append(slice(match_pos, pattern_len))
                match_pos += pattern_len

            matches.append((line, line_matches))

        return matches


# TODO: document properties (numpy style)
class GrepResult:
    """Stores, formats, and presents the result of a match

    Using ``str()`` on the objects of this class returns a concatenation of
    matched lines (e.g. for further grepping).

    If ``highlight`` is set to ``True``, using ``repr()`` on an object of this
    class gives a visual (colored) representation of matched lines, otherwise
    the returned string is the same as the one returned by using ``str()``.
    """

    def __init__(self, pattern: str, matches: LineMatches,
                 *, highlight: bool = True):
        self._pattern = pattern
        self._matches = matches

        self.highlight = highlight

        if self.highlight:
            self._repr = self._colorize(pattern, self.matched_lines)

    def __str__(self):
        return '\n'.join(self.matched_lines)

    def __repr__(self):
        return self._repr

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def matches(self) -> LineMatches:
        return self._matches

    @property
    def matched_lines(self) -> List[str]:
        return [line for line, _ in self._matches]

    @staticmethod
    def _colorize(pattern: str, lines: List[str]):
        return '\n'.join([
            line.replace(
                pattern, ANSI_RED + pattern + ANSI_RESET
            ) for line in lines
        ])
