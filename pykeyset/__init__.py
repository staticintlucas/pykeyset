from . import _impl  # type: ignore

__version__ = _impl.__version__
__version_info__ = _impl.__version_info__
__build__ = _impl.__build__

__all__ = ["__version__", "__version_info__", "__build__"]
