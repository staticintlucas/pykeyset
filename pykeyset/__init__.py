import pykeyset_rust

__all__ = ["__version_info__", "__version__"]

__version_info__ = pykeyset_rust.Version.get()
__version__ = str(__version_info__)
