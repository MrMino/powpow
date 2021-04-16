# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `powpow.GrepResult` is now actually importable from the top-level namespace.
- `powpow.GrepResult` is now guaranteed to have all of the methods the `str`
  class has. These methods operate on the same strings as returned by `__str__`
  of `GrepResult` objects.

### Changed
- `powpow.grep` will no longer accept an empty `pattern` string, raising
  `ValueError` instead.
- `powpow.GrepResult` now holds the string against which the match was
  performed in its `.input` attribute.
- Return values of `powpow.GrepResult`'s `__str__` and `__repr__` methods, and
  `matches` property, are now cached.

### Fixed
- `powpow.GrepResult.__repr__` no longer raises `AtributeError`

## [0.0.3]
### Added
- New `powpow.GrepResult` class. Objects of this class provide detailed
  introspection into results of `powpow.grep`, and their `repr()` handles
  presentation of the output, instead of `print()`ing it out like it was
  before.

### Changed
- `powpow.grep` now returns a `GrepResult` object - `grep` no longer prints its
  results into stdout.

## [0.0.2]
### Changed
- PowPow Grep is now directly importable from `powpow` module as `powpow.grep`.
- `powpow.grep` will now use `pproint.pformat` for translating objects to
  strings, instead of the plain `repr()`.

### Added
- `powpow.grep` can now be `str()`-ingified to obtain the contents that it
  prints.

## [0.0.1]
First version of the library.

### Added
- The most basic, dashed of version of PowPow Grep utility.

[Unreleased]: https://github.com/mrmino/powpow/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/mrmino/powpow/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/mrmino/powpow/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/mrmino/powpow/releases/tag/v0.0.1
