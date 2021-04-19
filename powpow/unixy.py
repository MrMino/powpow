# coding: utf-8
import re

from pprint import pformat
from typing import List

ANSI_RED = '\u001b[31m'
ANSI_DARK_RED = '\u001b[1;31m'
ANSI_RESET = '\u001b[0m'


LineMatches = List[re.Match]


# TODO: grep(pattern, file1, file2, obj, obj2) should be possible too
class grep:
    """Finds matches of a simple string in the object string representation.

    Unless a plain string is used or a ``GrepResult`` object, the
    representation of the object is obtained by using ``pprint.pformat()``.

    Strings are matched by their contents (not their ``repr()``s).

    ``GrepResult`` object is returned on a match. When matching ``GrepResult``,
    its ``str()`` representation is used.

    Raises ``ValueError`` if ``pattern`` is an empty string.
    """
    def __init__(self, pattern: str, highlight: bool = True):
        if not pattern:
            raise ValueError("Empty pattern is not allowed.")

        self.pattern = pattern
        self.highlight = highlight

    def __ror__(self, obj):
        parent_result = None

        if isinstance(obj, GrepResult):
            text = str(obj)
            parent_result = obj
        elif isinstance(obj, str):
            text = obj
        else:
            text = pformat(obj)

        matches = self._match(self.pattern, text)

        return GrepResult(
            self.pattern, text, matches,
            parent=parent_result,
            highlight=self.highlight
        )

    @staticmethod
    def _match(pattern, text: str) -> LineMatches:
        """Match lines to a fixed string"""
        return list(re.finditer(re.escape(pattern), text))


# TODO: document properties (numpy style)
class GrepResult:
    """Stores, formats, and presents the result of a match

    Using ``str()`` on the objects of this class returns a concatenation of
    matched lines (e.g. for further grepping).

    If ``highlight`` is set to ``True``, using ``repr()`` on an object of this
    class gives a visual (colored) representation of matched lines, otherwise
    the returned string is the same as the one returned by using ``str()``.

    Objects of this class evaluate truthily only if there are any matches in
    the result.
    """

    def __init__(self, pattern: str, string: str, matches: LineMatches,
                 *, parent: 'GrepResult' = None, highlight: bool = True):
        self._parrent = parent
        self._string = string
        self._pattern = pattern
        self._matches = matches

        self.highlight = highlight

        if self.highlight:
            # TODO: get parents repr, recolorize it (ANSII_RED → ANSI_DARK_RED)
            # by slices inside parent.match, add colors for this results match
            # on top.
            if parent is not None:
                raise NotImplementedError
            else:
                matched_lines = self.matched_lines

            self._repr = self._colorize(pattern, matched_lines)

    def __str__(self):
        return '\n'.join(self.matched_lines)

    def __repr__(self):
        return self._repr

    def __bool__(self):
        return bool(self._matches)

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def string(self) -> str:
        return self._string

    @property
    def matches(self) -> LineMatches:
        return self._matches

    @property
    def matched_lines(self) -> List[str]:
        return [match.string for match in self._matches]

    @staticmethod
    def _colorize(pattern: str, lines: List[str]):
        return '\n'.join([
            line.replace(
                pattern, ANSI_RED + pattern + ANSI_RESET
            ) for line in lines
        ])
