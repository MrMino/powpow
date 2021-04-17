# coding: utf-8
import os
from pathlib import Path
from pprint import pformat
from typing import List, Tuple, Any, Union

from functools import lru_cache
try:
    from functools import cached_property
except ImportError:
    from ._backports import cached_property  # type: ignore

ANSI_RED = '\u001b[31m'
ANSI_RESET = '\u001b[0m'


LineMatches = List[Tuple[str, List[slice]]]


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
        lines = text.splitlines()
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

        if self.highlight:
            self._repr = self._colorize(pattern, self.matched_lines)
        else:
            self._repr = '\n'.join(self.matched_lines)

    @lru_cache(maxsize=1)
    def __str__(self):
        return '\n'.join(self.matched_lines)

    @lru_cache(maxsize=1)
    def __repr__(self):
        return self._repr

    def __bool__(self):
        return bool(self._matches)

    def __getattr__(self, name):
        return getattr(self._input, name)

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
    def matched_lines(self) -> List[str]:
        return [line for line, _ in self._matches]

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
