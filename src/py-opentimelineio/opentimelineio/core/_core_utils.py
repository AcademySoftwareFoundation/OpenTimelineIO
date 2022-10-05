# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import types
import collections.abc
import copy

from .. import (
    _otio,
)
from .. _otio import (
    SerializableObject,
    AnyDictionary,
    AnyVector,
    PyAny
)


SUPPORTED_VALUE_TYPES = (
    "int",
    "float",
    "str",
    "bool",
    "list",
    "dictionary",
    "opentime.RationalTime",
    "opentime.TimeRange",
    "opentime.TimeTransform",
    "opentimelineio.core.SerializableObject"
)


def _is_str(v):
    return isinstance(v, str)


def _is_nonstring_sequence(v):
    return isinstance(v, collections.abc.Sequence) and not _is_str(v)


def _value_to_any(value, ids=None):
    if isinstance(value, PyAny):
        return value

    if isinstance(value, SerializableObject):
        return PyAny(value)
    if isinstance(value, collections.abc.Mapping):
        if ids is None:
            ids = set()
        d = AnyDictionary()
        for (k, v) in value.items():
            if not _is_str(k):
                raise ValueError(f"key '{k}' is not a string")
            if id(v) in ids:
                raise ValueError(
                    "circular reference converting dictionary to C++ datatype"
                )
            ids.add(id(v))
            d[k] = _value_to_any(v, ids)
            ids.discard(id(v))
        return PyAny(d)
    elif _is_nonstring_sequence(value):
        if ids is None:
            ids = set()
        vec = AnyVector()
        for v in value:
            if id(v) in ids:
                raise ValueError(
                    "circular reference converting dictionary to C++ datatype"
                )
            ids.add(id(v))
            vec.append(_value_to_any(v, ids))
            ids.discard(id(v))
        return PyAny(vec)
    else:
        try:
            return PyAny(value)
        except TypeError:
            # raise an OTIO-specific error
            raise TypeError(
                "A value of type '{}' is incompatible with OpenTimelineIO. "
                "OpenTimelineIO only supports the following value types in "
                "AnyDictionary containers (like the .metadata dictionary): "
                "{}.".format(
                    type(value),
                    SUPPORTED_VALUE_TYPES,
                )
            )
        except RuntimeError:
            # communicate about integer range first
            biginttype = int
            if isinstance(value, biginttype):
                raise ValueError(
                    "A value of {} is outside of the range of integers that "
                    "OpenTimelineIO supports, [{}, {}], which is the range of "
                    "C++ int64_t.".format(
                        value,
                        -9223372036854775808,
                        9223372036854775807,
                    )
                )

            # general catch all for invalid type
            raise ValueError(
                "The value '{}' of type '{}' is incompatible with OpenTimelineIO. "
                "OpenTimelineIO only supports the following value types in "
                "AnyDictionary containers (like the .metadata dictionary): "
                "{}.".format(
                    value,
                    type(value),
                    SUPPORTED_VALUE_TYPES,
                )
            )


_marker_ = object()


def _add_mutable_mapping_methods(mapClass):
    def __setitem__(self, key, item):
        self.__internal_setitem__(key, _value_to_any(item))

    def __str__(self):
        return str(dict(self))

    def __repr__(self):
        return repr(dict(self))

    def setdefault(self, key, default_value):
        if key in self:
            return self[key]
        else:
            self[key] = default_value
            return self[key]

    def pop(self, key, default=_marker_):
        try:
            value = self[key]
        except KeyError:
            if default is _marker_:
                raise
            return default
        else:
            del self[key]
            return value

    def __copy__(self):
        m = mapClass()
        m.update({k: v for (k, v) in self.items()})
        return m

    def __deepcopy__(self, memo):
        m = mapClass()
        m.update({k: copy.deepcopy(v, memo) for (k, v) in self.items()})
        return m

    collections.abc.MutableMapping.register(mapClass)
    mapClass.__setitem__ = __setitem__
    mapClass.__str__ = __str__
    mapClass.__repr__ = __repr__

    seen = set()
    for klass in (collections.abc.MutableMapping, collections.abc.Mapping):
        for name in klass.__dict__.keys():
            if name in seen:
                continue

            seen.add(name)
            func = getattr(klass, name)
            if (
                    isinstance(func, types.FunctionType)
                    and name not in klass.__abstractmethods__
            ):
                setattr(mapClass, name, func)
                if name.startswith('__') or name.endswith('__'):  # noqa
                    continue

                # Hide the method frm Sphinx doc.
                # See https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#info-field-lists  # noqa
                getattr(mapClass, name).__doc__ += '\n\n:meta private:'

    mapClass.setdefault = setdefault
    mapClass.pop = pop
    mapClass.__copy__ = __copy__
    mapClass.__deepcopy__ = __deepcopy__


def _add_mutable_sequence_methods(
        sequenceClass,
        conversion_func=None,
        side_effecting_insertions=False
):
    def noop(x):
        return x

    if not conversion_func:
        conversion_func = noop

    def __add__(self, other):
        if isinstance(other, list):
            return list(self) + other
        elif _is_nonstring_sequence(other):
            return list(self) + list(other)
        else:
            raise TypeError(
                f"Cannot add types '{type(self)}' and '{type(other)}'"
            )

    def __radd__(self, other):
        return self.__add__(other)

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return repr(list(self))

    def __getitem__(self, index):
        if isinstance(index, slice):
            indices = index.indices(len(self))
            return [self.__internal_getitem__(i) for i in range(*indices)]
        else:
            return self.__internal_getitem__(index)

    # This has to handle slicing
    def __setitem__(self, index, item):
        if not isinstance(index, slice):
            self.__internal_setitem__(index, conversion_func(item))
        else:
            if not isinstance(item, collections.abc.Iterable):
                raise TypeError("can only assign an iterable")

            indices = range(*index.indices(len(self)))

            if index.step in (1, None):
                if (
                        not side_effecting_insertions
                        and isinstance(item, collections.abc.MutableSequence)
                        and len(item) == len(indices)
                ):
                    for i0, i in enumerate(indices):
                        self.__internal_setitem__(i, conversion_func(item[i0]))
                else:
                    if side_effecting_insertions:
                        cached_items = list(self)

                    for i in reversed(indices):
                        self.__internal_delitem__(i)
                    insertion_index = 0 if index.start is None else index.start

                    if not side_effecting_insertions:
                        for e in item:
                            self.__internal_insert(insertion_index, e)
                            insertion_index += 1
                    else:
                        try:
                            for e in item:
                                self.__internal_insert(insertion_index, e)
                                insertion_index += 1
                        except Exception as e:
                            # restore the old state
                            while len(self):
                                self.pop()
                            self.extend(cached_items)
                            raise e
            else:
                if not isinstance(item, collections.abc.Sequence):
                    raise TypeError("can only assign a sequence")
                if len(item) != len(indices):
                    raise ValueError(
                        "attempt to assign sequence of size {} to extended "
                        "slice of size {}".format(len(item), len(indices))
                    )
                if not side_effecting_insertions:
                    for i, e in enumerate(item):
                        self.__internal_setitem__(indices[i], conversion_func(e))
                else:
                    cached_items = list(self)
                    for index in reversed(indices):
                        self.__internal_del_item__(index)
                    try:
                        for i, e in enumerate(item):
                            self.__internal_insert(indices[i], e)
                    except Exception as e:
                        # restore the old state
                        while len(self):
                            self.pop()
                        self.extend(cached_items)
                        raise e

    # This has to handle slicing
    def __delitem__(self, index):
        if not isinstance(index, slice):
            self.__internal_delitem__(index)
        else:
            for i in reversed(range(*index.indices(len(self)))):
                self.__delitem__(i)

    def insert(self, index, item):
        self.__internal_insert(
            index, conversion_func(item)
            if conversion_func else item
        )

    collections.abc.MutableSequence.register(sequenceClass)
    sequenceClass.__radd__ = __radd__
    sequenceClass.__add__ = __add__
    sequenceClass.__getitem__ = __getitem__
    sequenceClass.__setitem__ = __setitem__
    sequenceClass.__delitem__ = __delitem__
    sequenceClass.insert = insert
    sequenceClass.__str__ = __str__
    sequenceClass.__repr__ = __repr__

    seen = set()
    for klass in (collections.abc.MutableSequence, collections.abc.Sequence):
        for name in klass.__dict__.keys():
            if name not in seen:
                seen.add(name)
                func = getattr(klass, name)
                if (
                        isinstance(func, types.FunctionType)
                        and name not in klass.__abstractmethods__ # noqa and name != "__iter__"
                ):
                    setattr(sequenceClass, name, func)
                    if name.startswith('__') or name.endswith('__'):
                        continue

                    # Hide the method frm Sphinx doc.
                    # See https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#info-field-lists  # noqa
                    getattr(sequenceClass, name).__doc__ += '\n\n:meta private:'

    if not issubclass(sequenceClass, SerializableObject):
        def __copy__(self):
            v = sequenceClass()
            v.extend(e for e in self)
            return v

        def __deepcopy__(self, memo=None):
            v = sequenceClass()
            v.extend(copy.deepcopy(e, memo) for e in self)
            return v

        sequenceClass.__copy__ = __copy__
        sequenceClass.__deepcopy__ = __deepcopy__


_add_mutable_mapping_methods(AnyDictionary)
_add_mutable_sequence_methods(AnyVector, conversion_func=_value_to_any)
_add_mutable_sequence_methods(_otio.MarkerVector)
_add_mutable_sequence_methods(_otio.EffectVector)
_add_mutable_sequence_methods(_otio.Composition, side_effecting_insertions=True)
_add_mutable_sequence_methods(_otio.SerializableCollection)


def __setattr__(self, key, value):
    super(SerializableObject, self).__setattr__(key, value)
    _otio.install_external_keepalive_monitor(self, True)


SerializableObject.__setattr__ = __setattr__


# Decorator that adds a function into a class.
def add_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
    return decorator


@add_method(SerializableObject)
def deepcopy(self, *args, **kwargs):
    return self.clone()


@add_method(SerializableObject)
def __deepcopy__(self, *args, **kwargs):
    return self.clone()


@add_method(SerializableObject)
def __copy__(self, *args, **kwargs):
    raise ValueError("SerializableObjects may not be shallow copied.")
