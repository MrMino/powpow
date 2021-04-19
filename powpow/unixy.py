# coding: utf-8
import re
import os
from collections import defaultdict
from pathlib import Path
from pprint import pformat
from typing import Dict, List, Any, Union

from functools import lru_cache
try:
    from functools import cached_property
except ImportError:
    from ._backports import cached_property  # type: ignore

ANSI_RED = '\u001b[31m'
ANSI_RESET = '\u001b[0m'


try:
    match_cls = re.Match
except AttributeError:      # re.Match class is not available in Python 3.6
    import _sre             # type: ignore
    match_cls = _sre.Match  # type: ignore


LineMatches = List[match_cls]


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
        if isinstance(obj, GrepResult):
            text = str(obj)
        elif isinstance(obj, str):
            text = obj
        else:
            text = pformat(obj)

        matches = self._match(self.pattern, text)

        return GrepResult(
            self.pattern, text, matches,
            highlight=self.highlight
        )

    @staticmethod
    def _match(pattern, text: str) -> LineMatches:
        """Match lines to a fixed string

        Returns a list of (line, [slice, ...]) tuples, where each slice points
        to a substring of line that contains the pattern.
        """
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

    Objects of this class are guaranteed to have all of the methods the `str`
    class has. These methods operate on the same string as returned by
    `__str__` of this class.
    """

    def __init__(self, pattern: str, string: str, matches: LineMatches,
                 *, highlight: bool = True):
        self._input = string
        self._pattern = pattern
        self._matches = matches

        self.highlight = highlight

    @lru_cache(maxsize=1)
    def __str__(self):
        return '\n'.join(self.matched_lines)

    def __repr__(self):
        if self.highlight:
            return self._colorize(self.pattern, self.matched_lines)
        else:
            return str(self)

    def __bool__(self):
        return bool(self._matches)

    def __getattr__(self, name):
        return getattr(str(self), name)

    def __dir__(self):
        return list(set(dir(self._input) + super().__dir__()))

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def input(self) -> str:
        return self._input

    @property
    def matches(self) -> LineMatches:
        return self._matches

    @cached_property
    def line_matches(self) -> Dict[int, LineMatches]:
        newline_iterator = re.finditer('$', self.input, re.MULTILINE)

        line_matches = defaultdict(list)

        line_idx = 0
        start = 0
        end = next(newline_iterator).start() + 1

        for match in self.matches:
            while not (start <= match.start() < end):
                line_idx += 1
                start = end
                end = next(newline_iterator).start() + 1

            line_matches[line_idx].append(match)

        return dict(line_matches)

    @cached_property
    def matched_lines(self) -> List[str]:
        line_spans = tuple((m.start(), m.end())
                           for m
                           in re.finditer('^.*$', self.input, re.MULTILINE))

        lines_to_add = self.line_matches.keys()
        lines = [''] * len(self.line_matches)

        for matched_line_idx, input_line_idx in enumerate(lines_to_add):
            matched_line = self.input[slice(*line_spans[matched_line_idx])]
            lines[matched_line_idx] = matched_line

        return lines

    @staticmethod
    def _colorize(pattern: str, lines: List[str]):
        return '\n'.join([
            line.replace(
                pattern, ANSI_RED + pattern + ANSI_RESET
            ) for line in lines
        ])


def cat(*paths: Union[str, 'os.PathLike[Any]']) -> 'CatResult':
    """Reads text from files & CATenates it."""
    _paths = tuple(Path(path) for path in paths)
    contents = tuple(p.read_text() for p in _paths)
    return CatResult(paths, contents)


class CatResult:
    def __init__(self, paths, contents):
        assert len(paths) == len(contents)

        self._paths = paths
        self._contents = contents

    @lru_cache(maxsize=1)
    def __str__(self):
        return ''.join(self.contents)

    def __repr__(self):
        return str(self)

    @property
    def paths(self):
        return self._paths

    @property
    def contents(self):
        return self._contents

    @property
    def per_file(self):
        # This is specifically done here to forbid mutation of the return value
        return {p: c for p, c in zip(self._paths, self._contents)}
