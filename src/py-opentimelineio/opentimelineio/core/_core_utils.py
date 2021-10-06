import types
try:
    # Python 3.3+
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc
import copy
import collections
import sys

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


# XXX: python 2 vs python 3 guards
if sys.version_info[0] >= 3:
    def _is_str(v):
        return isinstance(v, str)

    def _iteritems(x):
        return x.items()

    def _im_func(func):
        return func

    def _xrange(*args):
        return range(*args)

    _methodType = types.FunctionType
else:
    # XXX Marked for no qa so that flake8 in python3 doesn't trip over these
    #     lines and falsely report them as bad.
    def _is_str(v):
        return isinstance(v, (str, unicode)) # noqa

    def _iteritems(x):
        return x.items()

    def _im_func(func):
        return func.im_func

    def _xrange(*args):
        return xrange(*args) # noqa

    _methodType = types.MethodType


def _is_nonstring_sequence(v):
    return isinstance(v, collections_abc.Sequence) and not _is_str(v)


def _value_to_any(value, ids=None):
    if isinstance(value, PyAny):
        return value

    if isinstance(value, SerializableObject):
        return PyAny(value)
    if isinstance(value, collections_abc.Mapping):
        if ids is None:
            ids = set()
        d = AnyDictionary()
        for (k, v) in _iteritems(value):
            if not _is_str(k):
                raise ValueError("key '{}' is not a string".format(k))
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
            if sys.version_info[0] < 3:
                biginttype = long  # noqa: F821
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


def _value_to_so_vector(value, ids=None):
    if not isinstance(value, collections_abc.Sequence) or _is_str(value):
        raise TypeError(
            "Expected list/sequence of SerializableObjects;"
            " found type '{}'".format(type(value))
        )

    av = AnyVector()
    for e in value:
        if not isinstance(e, SerializableObject):
            raise TypeError(
                "Expected list/sequence of SerializableObjects;"
                " found element of type '{}'".format(type(e)))
        av.append(e)
    return PyAny(av)


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
        m.update(dict((k, v) for (k, v) in _iteritems(self)))
        return m

    def __deepcopy__(self, memo):
        m = mapClass()
        m.update(
            dict(
                (k, copy.deepcopy(v, memo))
                for (k, v) in _iteritems(self)
            )
        )
        return m

    collections_abc.MutableMapping.register(mapClass)
    mapClass.__setitem__ = __setitem__
    mapClass.__str__ = __str__
    mapClass.__repr__ = __repr__

    seen = set()
    for klass in (collections_abc.MutableMapping, collections_abc.Mapping):
        for name in klass.__dict__.keys():
            if name in seen:
                continue

            seen.add(name)
            func = getattr(klass, name)
            if (
                    isinstance(func, _methodType)
                    and name not in klass.__abstractmethods__
            ):
                setattr(mapClass, name, _im_func(func))

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
                "Cannot add types '{}' and '{}'".format(type(self), type(other))
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
            return [self.__internal_getitem__(i) for i in _xrange(*indices)]
        else:
            return self.__internal_getitem__(index)

    # This has to handle slicing
    def __setitem__(self, index, item):
        if not isinstance(index, slice):
            self.__internal_setitem__(index, conversion_func(item))
        else:
            if not isinstance(item, collections_abc.Iterable):
                raise TypeError("can only assign an iterable")

            indices = range(*index.indices(len(self)))

            if index.step in (1, None):
                if (
                        not side_effecting_insertions
                        and isinstance(item, collections_abc.MutableSequence)
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
                if not isinstance(item, collections_abc.Sequence):
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
            for i in reversed(_xrange(*index.indices(len(self)))):
                self.__delitem__(i)

    def insert(self, index, item):
        self.__internal_insert(
            index, conversion_func(item)
            if conversion_func else item
        )

    collections_abc.MutableSequence.register(sequenceClass)
    sequenceClass.__radd__ = __radd__
    sequenceClass.__add__ = __add__
    sequenceClass.__getitem__ = __getitem__
    sequenceClass.__setitem__ = __setitem__
    sequenceClass.__delitem__ = __delitem__
    sequenceClass.insert = insert
    sequenceClass.__str__ = __str__
    sequenceClass.__repr__ = __repr__

    seen = set()
    for klass in (collections_abc.MutableSequence, collections_abc.Sequence):
        for name in klass.__dict__.keys():
            if name not in seen:
                seen.add(name)
                func = getattr(klass, name)
                if (
                        isinstance(func, _methodType)
                        and name not in klass.__abstractmethods__
                ):
                    setattr(sequenceClass, name, _im_func(func))

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
