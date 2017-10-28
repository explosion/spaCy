# coding: utf8
from __future__ import unicode_literals

import functools


class Underscore(object):
    doc_extensions = {}
    span_extensions = {}
    token_extensions = {}

    def __init__(self, extensions, obj, start=None, end=None):
        object.__setattr__(self, '_extensions', extensions)
        object.__setattr__(self, '_obj', obj)
        # Assumption is that for doc values, _start and _end will both be None
        # Span will set non-None values for _start and _end
        # Token will have _start be non-None, _end be None
        # This lets us key everything into the doc.user_data dictionary,
        # (see _get_key), and lets us use a single Underscore class.
        object.__setattr__(self, '_doc', obj.doc)
        object.__setattr__(self, '_start', start)
        object.__setattr__(self, '_end', end)

    def __getattr__(self, name):
        if name not in self._extensions:
            raise AttributeError(name)
        default, method, getter, setter = self._extensions[name]
        if getter is not None:
            return getter(self._obj)
        elif method is not None:
            return functools.partial(method, self._obj)
        else:
            return self._doc.user_data.get(self._get_key(name), default)

    def __setattr__(self, name, value):
        if name not in self._extensions:
            raise AttributeError(name)
        default, method, getter, setter = self._extensions[name]
        if setter is not None:
            return setter(self._obj, value)
        else:
            self._doc.user_data[self._get_key(name)] = value

    def set(self, name, value):
        return self.__setattr__(name, value)

    def get(self, name):
        return self.__getattr__(name)

    def has(self, name):
        return name in self._extensions

    def _get_key(self, name):
        return ('._.', name, self._start, self._end)
