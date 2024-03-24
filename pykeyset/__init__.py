from . import _impl  # type: ignore

__version__ = _impl.version
version = _impl.version
version_info = _impl.version_info

build_info = _impl.build_info


def print_build_info() -> None:
    print(build_info())


__all__ = ["__version__", "version", "version_info", "build_info", "print_build_info"]
