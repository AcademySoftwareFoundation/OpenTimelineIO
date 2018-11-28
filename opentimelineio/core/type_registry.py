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

"""Core type registry system for registering OTIO types for serialization."""

from .. import (
    exceptions
)


# Types decorate use register_type() to insert themselves into this map
_OTIO_TYPES = {}

# maps types to a map of versions to upgrade functions
_UPGRADE_FUNCTIONS = {}


def schema_name_from_label(label):
    """Return the schema name from the label name."""

    return label.split(".")[0]


def schema_version_from_label(label):
    """Return the schema version from the label name."""

    return int(label.split(".")[1])


def schema_label_from_name_version(schema_name, schema_version):
    """Return the serializeable object schema label given the name and version."""

    return "{}.{}".format(schema_name, schema_version)


def register_type(classobj, schemaname=None):
    """ Register a class to a Schema Label.

    Normally this is used as a decorator.  However, in special cases where a
    type has been renamed, you might need to register the new type to multiple
    schema names.  To do this:

    >>>    @core.register_type
    ...    class MyNewClass(...):
    ...        pass

    >>>    core.register_type(MyNewClass, "MyOldName")

    This will parse the old schema name into the new class type.  You may also
    need to write an upgrade function if the schema itself has changed.
    """

    if schemaname is None:
        schemaname = schema_name_from_label(classobj._serializable_label)

    _OTIO_TYPES[schemaname] = classobj

    return classobj


def upgrade_function_for(cls, version_to_upgrade_to):
    """Decorator for identifying schema class upgrade functions.

    Example
    >>>    @upgrade_function_for(MyClass, 5)
    ...    def upgrade_to_version_five(data):
    ...        pass

    This will get called to upgrade a schema of MyClass to version 5.  My class
    must be a class deriving from otio.core.SerializableObject.

    The upgrade function should take a single argument - the dictionary to
    upgrade, and return a dictionary with the fields upgraded.

    Remember that you don't need to provide an upgrade function for upgrades
    that add or remove fields, only for schema versions that change the field
    names.
    """

    def decorator_func(func):
        """ Decorator for marking upgrade functions """

        _UPGRADE_FUNCTIONS.setdefault(cls, {})[version_to_upgrade_to] = func

        return func

    return decorator_func


def instance_from_schema(schema_name, schema_version, data_dict):
    """Return an instance, of the schema from data in the data_dict."""

    if schema_name not in _OTIO_TYPES:
        from .unknown_schema import UnknownSchema

        # create an object of UnknownSchema type to represent the data
        schema_label = schema_label_from_name_version(schema_name, schema_version)
        data_dict[UnknownSchema._original_label] = schema_label
        unknown_label = UnknownSchema._serializable_label
        schema_name = schema_name_from_label(unknown_label)
        schema_version = schema_version_from_label(unknown_label)

    cls = _OTIO_TYPES[schema_name]

    schema_version = int(schema_version)
    if cls.schema_version() < schema_version:
        raise exceptions.UnsupportedSchemaError(
            "Schema '{}' has highest version available '{}', which is lower "
            "than requested schema version '{}'".format(
                schema_name,
                cls.schema_version(),
                schema_version
            )
        )

    if cls.schema_version() != schema_version:
        # since the keys are the versions to upgrade to, sorting the keys
        # before iterating through them should ensure that upgrade functions
        # are called in order.
        for version, upgrade_func in sorted(
            _UPGRADE_FUNCTIONS[cls].items()
        ):
            if version < schema_version:
                continue

            data_dict = upgrade_func(data_dict)

    obj = cls()
    obj._update(data_dict)

    return obj
