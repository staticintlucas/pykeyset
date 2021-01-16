# -*- coding: utf-8 -*-

from collections.abc import Mapping, MutableMapping
from typing import Any, Iterator, Type

import toml


def load(file: str) -> "TomlNode":
    return toml.load(file, TomlNode)


def loads(string: str) -> "TomlNode":
    return toml.loads(string, TomlNode)


_unset = lambda: None  # noqa: E731


class TomlNode(MutableMapping):
    def __init__(self, tree: dict = {}) -> None:

        self.dict = dict(tree)
        self.section = ""

        for k, v in self.dict.items():
            if isinstance(v, dict):
                self[k] = TomlNode(v)

    def __getitem__(self, key: str) -> Any:
        if key in self.dict:
            return self.dict[key]
        else:
            raise KeyError(key, self.section) from None

    def __setitem__(self, key: str, val: Any) -> None:

        if isinstance(val, Mapping):
            val = TomlNode(val)
            val.section = f"{self.section}.{key}" if self.section else key
        self.dict[key] = val

    def __delitem__(self, key: str) -> None:
        if key in self.dict:
            del self.dict[key]
        else:
            raise KeyError(key, self.section) from None

    def __iter__(self) -> Iterator[str]:
        yield from self.dict.__iter__()

    def __len__(self) -> int:
        return len(self.dict)

    def __contains__(self, key: str) -> bool:
        return key in self.dict

    def getkey(self, key: str, type: Type = None, default: Any = _unset) -> Any:
        if key not in self.dict or isinstance(self[key], TomlNode):
            if default is not _unset:
                val = default
            else:
                raise KeyError(key, self.section)
        elif type is not None and not isinstance(self[key], type):
            raise ValueError(key, self.section)
        else:
            val = self[key]

        return val

    def getsection(self, key: str) -> "TomlNode":
        if key not in self.dict:
            raise KeyError(f"{self.section}.{key}" if self.section else key, self.section)
        else:
            val = self[key]

        if not isinstance(val, TomlNode):
            raise KeyError(f"{self.section}.{key}" if self.section else key, self.section)

        return val
