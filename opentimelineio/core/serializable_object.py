#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Implements the otio.core.SerializableObject"""

import copy

from . import (
    type_registry,
)


class SerializableObject(object):
    """Base object for things that can be [de]serialized to/from .otio files.

    To define a new child class of this, you inherit from it and also use the
    register_type decorator.  Then you use the serializable_field function
    above to create attributes that can be serialized/deserialized.

    You can use the upgrade_function_for decorator to upgrade older schemas
    to newer ones.

    Finally, if you're in the process of upgrading schemas and you want to
    catch code that refers to old attribute names, you can use the
    deprecated_field function. This raises an exception if code attempts to
    read or write to that attribute.  After testing and before pushing, please
    remove references to deprecated_field.

    For example

    >>>    import opentimelineio as otio

    >>>    @otio.core.register_type
    ...    class ExampleChild(otio.core.SerializableObject):
    ...        _serializable_label = "ExampleChild.7"
    ...        child_data = otio.core.serializable_field("child_data", int)

    # @TODO: delete once testing shows nothing is referencing this.
    >>>         old_child_data_name = otio.core.deprecated_field()

    >>>    @otio.core.upgrade_function_for(ExampleChild, 3)
    ...    def upgrade_child_to_three(_data):
    ...        return {"child_data" : _data["old_child_data_name"]}
    """

    # Every child must define a _serializable_label attribute.
    # This attribute is a string in the form of: "SchemaName.VersionNumber"
    # Where VersionNumber is an integer.
    # You can use the classmethods .schema_name() and .schema_version() to
    # query these fields.
    _serializable_label = None
    _class_path = "core.SerializableObject"

    def __init__(self):
        self._data = {}

    # @{ "Reference Type" semantics for SerializableObject
    # We think of the SerializableObject as a reference type - by default
    # comparison is pointer comparison, but you can use 'is_equivalent_to' to
    # check if the contents of the SerializableObject are the same as some
    # other SerializableObject's contents.
    #
    # Implicitly:
    # def __eq__(self, other):
    #     return self is other

    def is_equivalent_to(self, other):
        """Returns true if the contents of self and other match."""

        try:
            if self._data == other._data:
                return True

            # XXX: Gross hack takes OTIO->JSON String->Python Dictionaries
            #
            # using the serializer ensures that we only compare fields that are
            # serializable, which is how we define equivalence.
            #
            # we use json.loads() to turn the string back into dictionaries
            # so we can use python's equivalence for things like floating
            # point numbers (ie 5.0 == 5) without having to do string
            # processing.

            from . import json_serializer
            import json

            lhs_str = json_serializer.serialize_json_to_string(self)
            lhs = json.loads(lhs_str)

            rhs_str = json_serializer.serialize_json_to_string(other)
            rhs = json.loads(rhs_str)

            return (lhs == rhs)
        except AttributeError:
            return False
    # @}

    def _update(self, d):
        """Like the dictionary .update() method.

        Update the _data dictionary of this SerializableObject with the ._data
        of d if d is a SerializableObject or if d is a dictionary, d itself.
        """

        if isinstance(d, SerializableObject):
            self._data.update(d._data)
        else:
            self._data.update(d)

    @classmethod
    def schema_name(cls):
        return type_registry.schema_name_from_label(
            cls._serializable_label
        )

    @classmethod
    def schema_version(cls):
        return type_registry.schema_version_from_label(
            cls._serializable_label
        )

    @property
    def is_unknown_schema(self):
        # in general, SerializableObject will have a known schema
        # but UnknownSchema subclass will redefine this property to be True
        return False

    def __copy__(self):
        raise NotImplementedError(
            "Shallow copying is not permitted.  Use a deep copy."
        )

    def __deepcopy__(self, md):
        result = type(self)()
        result._data = copy.deepcopy(self._data, md)

        return result

    def deepcopy(self):
        return self.__deepcopy__({})


def serializable_field(name, required_type=None, doc=None):
    """Create a serializable_field for child classes of SerializableObject.

    Convienence function for adding attributes to child classes of
    SerializableObject in such a way that they will be serialized/deserialized
    automatically.

    Use it like this:
        class foo(SerializableObject):
            bar = serializable_field("bar", required_type=int, doc="example")

    This would indicate that class "foo" has a serializable field "bar".  So:
        f = foo()
        f.bar = "stuff"

        # serialize & deserialize
        otio_json = otio.adapters.from_name("otio")
        f2 = otio_json.read_from_string(otio_json.write_to_string(f))

        # fields should be equal
        f.bar == f2.bar

    Additionally, the "doc" field will become the documentation for the
    property.
    """

    def getter(self):
        return self._data[name]

    def setter(self, val):
        # always allow None values regardless of value of required_type
        if required_type is not None and val is not None:
            if not isinstance(val, required_type):
                raise TypeError(
                    "attribute '{}' must be an instance of '{}', not: {}".format(
                        name,
                        required_type,
                        type(val)
                    )
                )

        self._data[name] = val

    return property(getter, setter, doc=doc)


def deprecated_field():
    """ For marking attributes on a SerializableObject deprecated.  """

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter, doc="Deprecated field, do not use.")
