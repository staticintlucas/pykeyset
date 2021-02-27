# Change Log

## [v0.0.2](https://github.com/staticintlucas/pykeyset/releases/tag/v0.0.2)

### New

* Added example under the [*examples/*](examples/) directory
* Testing and linting
  * Added some unit tests; increased test coverage to > 75% :partying_face:
  * More comprehensive code linting
  * Automate these with GitHub Actions CI

### Changes

* Migrate the project to [Poetry]
* Migrate CLI to use [Typer]
* Tweaked kerning for some charaters in the `cherry` font
* Refactored error handling
* Improved cmdlist parsing
* Replace `recordclass` with immutable `namedtuple` to avoid unnecessary `deepcopy`'s
* Heavily refactor font, icon, and profile loading functionality

### Fixes

* Various miscellaneous fixes
* Disable CI cacheing on Windows/Python 3.6 combination to stop failures
* Fix SVG path arc to Bézier transformation on certain elliptical arcs
* Fix error when loading same builtin resource more than once

### Built in resources

Profiles: `cherry`  \
Fonts: `cherry`  \
Icons: `cherry` (incomplete)

---

## [v0.0.1](https://github.com/staticintlucas/pykeyset/releases/tag/v0.0.1)

### New

* Initial release
* Able to generate basic layout diagrams
* Font kerning capabilities
* Basic linting with [pre-commit]

### Built in resources

Profiles: `cherry`  \
Fonts: `cherry`  \
Icons: `cherry` (incomplete)

---

[poetry]: https://python-poetry.org/
[typer]: https://typer.tiangolo.com/
[pre-commit]: https://pre-commit.com/
