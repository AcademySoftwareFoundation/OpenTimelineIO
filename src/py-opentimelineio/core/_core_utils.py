import types
import collections
from .. import _otio
from .. _otio import (SerializableObject, AnyDictionary, AnyVector, PyAny)

def _is_nonstring_sequence(v):
    return isinstance(v, collections.Sequence) and not isinstance(v, (str, unicode))

def _value_to_any(value, ids=None):
    if isinstance(value, PyAny):
        return value
    
    if isinstance(value, SerializableObject):
        return PyAny(value)
    if isinstance(value, collections.Mapping):
        if ids is None:
            ids = set()
        d = AnyDictionary()
        for (k,v) in value.iteritems():
            if not isinstance(k, (str, unicode)):
                raise ValueError("key '%s' is not a string" % k)
            if id(v) in ids:
                raise ValueError("circular reference converting dictionary to C++ datatype")
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
                raise ValueError("circular reference converting dictionary to C++ datatype")
            ids.add(id(v))
            vec.append(_value_to_any(v, ids))
            ids.discard(id(v))
        return PyAny(vec)
    else:
        return PyAny(value)

def _value_to_so_vector(value, ids=None):
    if not isinstance(value, collections.Sequence) or isinstance(value, (str, unicode)):
        raise TypeError("Expected list/sequence of SerializableObjects; found type %s" % type(value))
                        
    av = AnyVector()
    for e in value:
        if not isinstance(e, SerializableObject):
            raise TypeError("Expected list/sequence of SerializableObjects; found element of type %s" % type(e))
        av.append(e)
    return PyAny(av)

def _add_mutable_mapping_methods(mapClass):
    def __setitem__(self, key, item):
        self.__internal_setitem__(key, _value_to_any(item))

    def __str__(self):
        return str(dict(self))

    def __repr__(self):
        return repr(dict(self))

    collections.MutableMapping.register(mapClass)
    mapClass.__setitem__ = types.MethodType(__setitem__, None, mapClass)
    mapClass.__str__ = types.MethodType(__str__, None, mapClass)
    mapClass.__repr__ = types.MethodType(__repr__, None, mapClass)

    seen = set()
    for klass in (collections.MutableMapping, collections.Mapping):
        for name in klass.__dict__.keys():
            if name not in seen:
                seen.add(name)
                func = getattr(klass, name)
                if isinstance(func, types.MethodType) and name not in klass.__abstractmethods__:
                    setattr(mapClass, name, types.MethodType(func.im_func, None, mapClass))

def _add_mutable_sequence_methods(sequenceClass, conversion_func=None, side_effecting_insertions=False):
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
            raise TypeError("Cannot add types '%s' and '%s'" % (type(self), type(other)))

    def __radd__(self, other):
        return self.__add__(other)
        
    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return repr(list(self))

    def __getitem__(self, index):
        if isinstance(index, slice):
            indices = index.indices(len(self))
            return [self.__internal_getitem__(i) for i in xrange(*indices)]
        else:
            return self.__internal_getitem__(index)

    # This has to handle slicing
    def __setitem__(self, index, item):
        if not isinstance(index, slice):
            self.__internal_setitem__(index, conversion_func(item))
        else:
            if not isinstance(item, collections.Iterable):
                raise TypeError("can only assign an iterable")

            indices = range(*index.indices(len(self)))
            
            if index.step in (1, None):
                if not side_effecting_insertions and isinstance(item, collections.MutableSequence) \
                       and len(item) == len(indices):
                    for i in indices:
                        self.__internal_setitem__(i, conversion_func(item))
                else:
                    if side_effecting_insertions:
                        cached_items = list(self)
                        
                    for i in reversed(indices):
                        self.__internal_delitem__(i)
                    insertion_index = 0 if not indices else indices[0]

                    if not side_effecting_insertions:
                        for e in item:
                            self.__internal_insert(insertion_index, e)
                            insertion_index += 1
                    else:
                        try:
                            for e in item:
                                self.__internal_insert(insertion_index, e)
                                insertion_index += 1
                        except Exception, e:
                            # restore the old state
                            while len(self):
                                self.pop()
                            self.extend(cached_items)
                            raise e
            else:
                if not isinstance(item, collections.Sequence):
                    raise TypeError("can only assign a sequence")
                if len(item) != len(indices):
                    raise ValueError("attempt to assign sequence of size %s to extended slice of size %s" %
                                     (len(item), len(indices)))
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
                    except Exception, e:
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
            for i in reversed(xrange(*index.indices(len(self)))):
                self.__delitem__(i)

    def insert(self, index, item):
        self.__internal_insert(index, conversion_func(item) if conversion_func else item)

    collections.MutableSequence.register(sequenceClass)
    sequenceClass.__radd__ = types.MethodType(__radd__, None, sequenceClass)
    sequenceClass.__add__ = types.MethodType(__add__, None, sequenceClass)
    sequenceClass.__getitem__ = types.MethodType(__getitem__, None, sequenceClass)
    sequenceClass.__setitem__ = types.MethodType(__setitem__, None, sequenceClass)
    sequenceClass.__delitem__ = types.MethodType(__delitem__, None, sequenceClass)
    sequenceClass.insert = types.MethodType(insert, None, sequenceClass)
    sequenceClass.__str__ = types.MethodType(__str__, None, sequenceClass)
    sequenceClass.__repr__ = types.MethodType(__repr__, None, sequenceClass)

    seen = set()
    for klass in (collections.MutableSequence, collections.Sequence):
        for name in klass.__dict__.keys():
            if name not in seen:
                seen.add(name)
                func = getattr(klass, name)
                if isinstance(func, types.MethodType) and name not in klass.__abstractmethods__:
                    setattr(sequenceClass, name, types.MethodType(func.im_func, None, sequenceClass))

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
    import types
    def decorator(func):
        setattr(cls, func.__name__, types.MethodType(func, None, cls))
    return decorator


@add_method(SerializableObject)
def __deepcopy__(self, *args, **kwargs):
    return self.clone()

@add_method(SerializableObject)
def __copy__(self, *args, **kwargs):
    raise ValueError("SerializableObjects may not be shallow copied.")

