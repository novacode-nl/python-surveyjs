# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Elements keyed by name, refusing a lookup of a name that is not unique."""

from collections import OrderedDict


class AmbiguousNameError(LookupError):
    """More than one element has the name that was looked up.

    A `LookupError` but not a `KeyError`, so `except KeyError` and a caller
    of `.get()` do not take it for a missing name."""

    def __init__(self, name, paths):
        self.name = name
        self.paths = paths
        super().__init__(
            '%r is ambiguous: %s; use get_element_by_path() or get_elements_by_name()'
            % (name, ', '.join(paths)))


class ElementsByName(OrderedDict):
    """Elements keyed by name, as `elements`, `all_elements` and `questions`.

    A name is unique per data level only: two dynamic panels can each hold a
    `year`. The map keeps the last one, as a plain dict would, but looking up
    such a name (`[name]` or `.get(name)`) raises `AmbiguousNameError`
    instead of returning one of them. `in` and iterating are unchanged.

    An element is registered under its name before its parent is known, so
    the clashing elements are kept and their paths read only when needed.
    """

    def __init__(self, *args, **kwargs):
        self._clashes = {}
        super().__init__(*args, **kwargs)

    def __setitem__(self, name, element):
        existing = OrderedDict.get(self, name)
        if existing is not None and existing is not element:
            self._clashes.setdefault(name, [existing]).append(element)
        super().__setitem__(name, element)

    def __getitem__(self, name):
        self._check(name)
        return super().__getitem__(name)

    def get(self, name, default=None):
        self._check(name)
        return super().get(name, default)

    @property
    def ambiguous(self):
        """{name: [path, ...]}, for each name more than one element has."""
        result = {}
        for name in self._clashes:
            paths = self._paths(name)
            if paths:
                result[name] = paths
        return result

    def _paths(self, name):
        """The distinct paths of the elements registered under `name`, or
        [] when they are one element (re-registered)."""
        paths = list(dict.fromkeys(element.path_str for element in self._clashes.get(name, [])))
        return paths if len(paths) > 1 else []

    def _check(self, name):
        if name in self._clashes:
            paths = self._paths(name)
            if paths:
                raise AmbiguousNameError(name, paths)
