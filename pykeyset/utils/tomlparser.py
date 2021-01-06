# -*- coding: utf-8 -*-

from collections.abc import Mapping, MutableMapping

import toml


def load(file):
    return toml.load(file, TomlNode)


def loads(string):
    return toml.loads(string, TomlNode)


_unset = lambda: None  # noqa: E731


class TomlNode(MutableMapping):
    def __init__(self, tree={}):

        self.dict = dict(tree)
        self.section = ""

        for k, v in self.dict:
            if isinstance(v, dict):
                self[k] = TomlNode(v)

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            raise KeyError(key, self.section) from None

    def __setitem__(self, key, val):

        if isinstance(val, Mapping):
            val = TomlNode(val)
            val.section = f"{self.section}.{key}" if self.section else key
        self.dict[key] = val

    def __delitem__(self, key):
        if key in self.dict:
            del self.dict[key]
        else:
            raise KeyError(key, self.section) from None

    def __iter__(self):
        yield from self.dict.__iter__()

    def __len__(self):
        return len(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def getkey(self, key, type=None, default=_unset):
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

    def getsection(self, key):
        if key not in self.dict:
            raise KeyError(f"{self.section}.{key}" if self.section else key, self.section)
        else:
            val = self[key]

        if not isinstance(val, TomlNode):
            raise KeyError(f"{self.section}.{key}" if self.section else key, self.section)

        return val
