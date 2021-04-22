# coding: utf-8
import io
import re
import os
from collections import defaultdict
from pathlib import Path
from pprint import pformat
from typing import Dict, List, Any, Union, Tuple

from functools import lru_cache
try:
    from functools import cached_property
except ImportError:
    from ._backports import cached_property  # type: ignore

ANSI_RED = '\u001b[31m'
ANSI_RESET = '\u001b[0m'


try:
    match_cls = re.Match
except AttributeError:  # re.Match class is not available in Python 3.6
    match_cls = type(re.compile('', 0).match(''))  # type: ignore


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

    Objects of this class implement equality comparison by ``str()``-ing the
    object they're being comparred to, and comparing that to the result of
    their own ``__str__()``.
    """

    def __init__(self, pattern: str, string: str, matches: LineMatches,
                 *, highlight: bool = True):
        self._input = string
        self._pattern = pattern
        self._matches = matches

        self._str = None

        self.highlight = highlight

    def __str__(self):
        # This cannot be cached using lru_cache, otherwise it causes unbound
        # recursion between lru_cache → __hash__ → __str__ → lru_cache
        if self._str is None:
            self._str = ''.join(self.matched_lines)
        return self._str

    def __repr__(self):
        if self.highlight:
            return self._colorized().rstrip('\n')
        else:
            return str(self)

    def __bool__(self):
        return bool(self._matches)

    def __getattr__(self, name):
        return getattr(str(self), name)

    def __dir__(self):
        return list(set(dir(self._input) + super().__dir__()))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        # On its own, str(self) will not be enough - it is not highlighted, and
        # so its the same on different patterns, hence we also hash
        # self._pattern here.
        return hash((str(self), self._pattern))

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
        # each span stops right before the newline character
        line_spans = tuple((m.start(), m.end() + 1)  # +1 for newline
                           for m
                           in re.finditer('^.*$', self.input, re.MULTILINE))

        lines_to_add = self.line_matches.keys()
        lines = [''] * len(self.line_matches)

        for matched_line_idx, line_to_add_idx in enumerate(lines_to_add):
            matched_line = self.input[slice(*line_spans[line_to_add_idx])]
            lines[matched_line_idx] = matched_line

        return lines

    @lru_cache(maxsize=1)
    def _colorized(self):
        buf = io.StringIO()
        line_spans = tuple((m.start(), m.end())
                           for m
                           in re.finditer('^.*$', self.input, re.MULTILINE))
        for line, line_idx, matches in zip(self.matched_lines,
                                           self.line_matches.keys(),
                                           self.line_matches.values()):
            start = line_spans[line_idx][0]
            for match in matches:
                end = match.start()
                buf.write(self.input[start:end])

                start = match.start()
                end = match.end()
                buf.write(ANSI_RED)
                buf.write(self.input[start:end])
                buf.write(ANSI_RESET)

                start = match.end()
            end = line_spans[line_idx][1]
            buf.write(self.input[start:end + 1])  # +1 for newline
        return buf.getvalue()


def cat(*paths: Union[str, 'os.PathLike[Any]']) -> 'CatResult':
    """Reads text from files & CATenates it."""
    _paths = tuple(Path(path) for path in paths)
    contents = tuple(p.read_text() for p in _paths)
    return CatResult(_paths, contents)


# TODO: document properties (numpy style)
class CatResult:
    """Stores and provides introspection of results of calls to ``cat``.

    ``str()``-ing and ``repr()``-ing objects of this class returns catenation
    of the contents of files specified in the call to ``cat``.

    Objects of this class evaluate truthily as long as the result of the
    catenation is not empty.

    Objects of this class are guaranteed to have all of the methods the `str`
    class has. These methods operate on the same string as returned by
    `__str__` of this class.

    Objects of this class implement equality comparison by ``str()``-ing the
    object they're being comparred to, and comparing that to the result of
    their own ``__str__()``.
    """

    def __init__(self,
                 paths: Tuple[Path, ...],
                 contents: Tuple[str, ...]):
        assert len(paths) == len(contents)

        self._paths = paths
        self._contents = contents

        self._str = None

    def __str__(self):
        # This cannot be cached using lru_cache, otherwise it causes unbound
        # recursion between lru_cache → __hash__ → __str__ → lru_cache
        if self._str is None:
            self._str = ''.join(self.contents)
        return self._str

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        return getattr(str(self), name)

    def __dir__(self):
        return list(set(dir(self._input) + super().__dir__()))

    def __bool__(self):
        return any(self._contents)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @property
    def paths(self) -> Tuple[Path, ...]:
        return self._paths

    @property
    def contents(self) -> Tuple[str, ...]:
        return self._contents

    @property
    def per_file(self):
        # This is specifically done here to forbid mutation of the return value
        # Do not cache this.
        return {p: c for p, c in zip(self._paths, self._contents)}

    def json(self, **loads_kwargs) -> Any:
        """Interpret this catenation as json, parse it, and return the result.

        Keyword arguments of this method are passed as-is to ``json.loads``.
        """
        import json
        return json.loads(str(self), **loads_kwargs)

    def file(self) -> io.TextIOBase:
        """Return a file-like object with the result of the catenation."""
        return io.StringIO(str(self))
