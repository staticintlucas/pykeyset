from contextlib import contextmanager
from math import isclose
import pytest

import pykeyset

# A simple file-like wrapper around a real file object, but does not inherit
# from io.IOBase which is a different code path in Rust.
class FileLike:
    def __init__(self, inner):
        self.inner = inner

    def read(self, size=-1):
        return self.inner.read(size)

    def write(self, data):
        return self.inner.write(data)

@contextmanager
def open_file_like(file, mode):
    with open(file, mode) as f:
        yield FileLike(f)

@pytest.mark.parametrize("open_fn", [
    open,
    open_file_like,
])
@pytest.mark.parametrize("mode, check", [
    ("r", pykeyset.test.read_text_file_noop),
    ("rb", pykeyset.test.read_binary_file_noop),
    ("r", pykeyset.test.read_any_file_noop),
    ("rb", pykeyset.test.read_any_file_noop),
    ("w", pykeyset.test.write_text_file_noop),
    ("wb", pykeyset.test.write_binary_file_noop),
    ("w", pykeyset.test.write_any_file_noop),
    ("wb", pykeyset.test.write_any_file_noop),
])
def test_check_file(tmp_path, open_fn, mode, check):
    file = tmp_path / "test"
    if "r" in mode:
        file.touch()

    with open_fn(file, mode) as f:
        check(f)

@pytest.mark.parametrize("open_fn", [
    open,
    open_file_like,
])
@pytest.mark.parametrize("mode, check", [
    ("w", pykeyset.test.read_text_file_noop),
    ("rb", pykeyset.test.read_text_file_noop),
    ("wb", pykeyset.test.read_binary_file_noop),
    ("r", pykeyset.test.read_binary_file_noop),
    ("w", pykeyset.test.read_any_file_noop),
    ("r", pykeyset.test.write_text_file_noop),
    ("wb", pykeyset.test.write_text_file_noop),
    ("rb", pykeyset.test.write_binary_file_noop),
    ("w", pykeyset.test.write_binary_file_noop),
    ("r", pykeyset.test.write_any_file_noop),
])
def test_check_wrong_file_type(tmp_path, open_fn, mode, check):
    file = tmp_path / "test"
    if "r" in mode:
        file.touch()

    with pytest.raises(ValueError):
        with open_fn(file, mode) as f:
            check(f)
