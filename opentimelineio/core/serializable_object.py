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

    For example:
        import opentimelineio as otio

        @otio.core.register_type
        class ExampleChild(otio.core.SerializableObject):
            _serializable_label = "ExampleChild.7"

            child_data = otio.core.serializable_field("child_data", int)

            # @TODO: delete once testing shows nothing is referencing this.
            old_child_data_name = otio.core.deprecated_field()


        @otio.core.upgrade_function_for(ExampleChild, 3)
        def upgrade_child_to_three(data):
            return {"child_data" : data["old_child_data_name"]}
    """

    # Every child must define a _serializable_label attribute.
    # This attribute is a string in the form of: "SchemaName.VersionNumber"
    # Where VersionNumber is an integer.
    # You can use the classmethods .schema_name() and .schema_version() to
    # query these fields.
    _serializable_label = None
    _class_path = "core.SerializableObject"

    def __init__(self):
        self.data = {}

    def __eq__(self, other):
        try:
            return (self.data == other.data)
        except AttributeError:
            return False

    def __hash__(self):
        # Because the children of this class should implement their own
        # versions of __eq__ and __hash__, this is really meant to be a
        # "reasonable default" to get things up and running until that is
        # possible.
        #
        # As such it is using the simple ugly hack implementation of
        # stringifying.
        #
        # If this is ever a problem it should be replaced with a more robust
        # implementation.

        return hash(str(self.data))

    def update(self, d):
        """Like the dictionary .update() method.

        Update the data dictionary of this SerializableObject with the .data
        of d if d is a SerializableObject or if d is a dictionary, d itself.
        """

        if isinstance(d, SerializableObject):
            self.data.update(d.data)
        else:
            self.data.update(d)

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

    def __copy__(self):
        result = self.__class__()
        result.data = copy.copy(self.data)

        return result

    def copy(self):
        return self.__copy__()

    def __deepcopy__(self, md):
        result = type(self)()
        result.data = copy.deepcopy(self.data, md)

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
        return self.data[name]

    def setter(self, val):
        # always allow None values regardless of value of required_type
        if (
            required_type is not None
            and val is not None
            and not isinstance(val, required_type)
        ):
            raise TypeError(
                "attribute '{}' must be an instance of '{}', not: {}".format(
                    name,
                    required_type,
                    type(val)
                )
            )

        self.data[name] = val

    return property(getter, setter, doc=doc)


def deprecated_field():
    """ For marking attributes on a SerializableObject deprecated.  """

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter, doc="Deprecated field, do not use.")
