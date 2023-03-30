# Change Log

## [v0.1.0](https://github.com/staticintlucas/pykeyset/releases/tag/v0.1.0)

### New

* Use [keyset-rs](staticintlucas/keyset-rs) as the backend

### Changes

* Drop Python 3.6 support
* Support parsing TTF and OTF font files instead of our own XML format.
* Remove support for the old XML font and icon formats.
  A TTF/OTF font (which can contain icon outlines) should be used instead
* Change profile format to map from KLE font sizes to actual font sizes/margins.
  This means the `[legend.alpha]`, `[legend.symbol]`, and `[legend.mod]` should be replaced with
  `[legend.5]`, `[legend.4]`, and `[legend.3]`, respectively
* Replace `homing.bump.radius` with `homing.bump.diameter` in profile files
* Remove key top gradients as they weren't very pretty

### Built in resources

* Profiles: `cherry`, `kat`

## [v0.0.4](https://github.com/staticintlucas/pykeyset/releases/tag/v0.0.4)

### New

* Support for multiple font sizes per key (KLE `f2` and `fa` properties)
* Support for multi-line legends
* Allow for character spacing adjustments
* Support exporting PNG, PDF, and AI (experimental) files

### Changes

* Improve how position of homing keys is calculated
* Better support for ISO enters
* Change the way spherical keys are drawn to better reflect the shape of most spherical profiles

### Fixes

* Change alignment of decals to prevent overlap with keys

### Built in resources

* Profiles: `cherry`, `kat`
* Fonts: `cherry`
* Icons: `cherry` (incomplete)

---

## [v0.0.3](https://github.com/staticintlucas/pykeyset/releases/tag/v0.0.3)

### Fixes

* Fix issue causing PyPI not to detect Python 3.6 support

### Built in resources

* Profiles: `cherry`
* Fonts: `cherry`
* Icons: `cherry` (incomplete)

---

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
* Replace most `recordclass` with immutable `namedtuple` to avoid unnecessary `deepcopy`'s
* Heavily refactor font, icon, and profile loading functionality

### Fixes

* Various miscellaneous fixes
* Disable CI cacheing on Windows/Python 3.6 combination to stop failures
* Fix SVG path arc to Bézier transformation on certain elliptical arcs
* Fix error when loading same builtin resource more than once

### Built in resources

* Profiles: `cherry`
* Fonts: `cherry`
* Icons: `cherry` (incomplete)

---

## [v0.0.1](https://github.com/staticintlucas/pykeyset/releases/tag/v0.0.1)

### New

* Initial release
* Able to generate basic layout diagrams
* Font kerning capabilities
* Basic linting with [pre-commit]

### Built in resources

* Profiles: `cherry`
* Fonts: `cherry`
* Icons: `cherry` (incomplete)

---

[poetry]: https://python-poetry.org/
[typer]: https://typer.tiangolo.com/
[pre-commit]: https://pre-commit.com/
