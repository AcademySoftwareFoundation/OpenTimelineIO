# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. _otio import ( # noqa
    # errors
    CannotComputeAvailableRangeError,

    # classes
    Composable,
    Composition,
    Item,
    MediaReference,
    SerializableObject,
    SerializableObjectWithMetadata,
    Track,

    # functions
    deserialize_json_from_file,
    deserialize_json_from_string,
    flatten_stack,
    install_external_keepalive_monitor,
    instance_from_schema,
    register_serializable_object_type,
    register_upgrade_function,
    register_downgrade_function,
    set_type_record,
    _serialize_json_to_string,
    _serialize_json_to_file,
    type_version_map,
)

from . _core_utils import ( # noqa
    add_method,
    _value_to_any,
    _value_to_so_vector,
    _add_mutable_mapping_methods,
    _add_mutable_sequence_methods,
)
from . import ( # noqa
    mediaReference,
    composition,
    composable,
    item,
)

__all__ = [
    'Composable',
    'Composition',
    'Item',
    'MediaReference',
    'SerializableObject',
    'SerializableObjectWithMetadata',
    'Track',
    'deserialize_json_from_file',
    'deserialize_json_from_string',
    'flatten_stack',
    'install_external_keepalive_monitor',
    'instance_from_schema',
    'register_serializable_object_type',
    'register_upgrade_function',
    'register_downgrade_function',
    'set_type_record',
    'add_method',
    'upgrade_function_for',
    'downgrade_function_for',
    'serializable_field',
    'deprecated_field',
    'serialize_json_to_string',
    'serialize_json_to_file',
    'register_type',
    'type_version_map',
]


def serialize_json_to_string(root, downgrade_version_manifest=None, indent=4):
    return _serialize_json_to_string(
            _value_to_any(root),
            downgrade_version_manifest or {},
            indent
    )


def serialize_json_to_file(root, filename, indent=4):
    return _serialize_json_to_file(_value_to_any(root), filename, indent)


def register_type(classobj, schemaname=None):
    label = classobj._serializable_label
    if schemaname is None:
        schema_name, schema_version = label.split(".", 2)
    else:
        schema_name, schema_version = schemaname, 1

    register_serializable_object_type(classobj, schema_name, int(schema_version))

    orig_init = classobj.__init__

    def __init__(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        set_type_record(self, schema_name)

    classobj.__init__ = __init__
    return classobj


def upgrade_function_for(cls, version_to_upgrade_to):
    """
    Decorator for identifying schema class upgrade functions.

    Example:

    .. code-block:: python

        @upgrade_function_for(MyClass, 5)
        def upgrade_to_version_five(data):
            pass

    This will get called to upgrade a schema of MyClass to version 5. MyClass
    must be a class deriving from :class:`~SerializableObject`.

    The upgrade function should take a single argument - the dictionary to
    upgrade, and return a dictionary with the fields upgraded.

    Remember that you don't need to provide an upgrade function for upgrades
    that add or remove fields, only for schema versions that change the field
    names.

    :param type cls: class to upgrade
    :param int version_to_upgrade_to: the version to upgrade to
    """

    def decorator_func(func):
        """ Decorator for marking upgrade functions """
        def wrapped_update(data):
            modified = func(data)
            data.clear()
            data.update(modified)

        register_upgrade_function(cls._serializable_label.split(".")[0],
                                  version_to_upgrade_to, wrapped_update)
        return func

    return decorator_func


def downgrade_function_for(cls, version_to_upgrade_to):
    """
    @TODO <- fix docs
    Decorator for identifying schema class downgrade functions.

    Example:

    .. code-block:: python

        @upgrade_function_for(MyClass, 5)
        def upgrade_to_version_five(data):
            pass

    This will get called to upgrade a schema of MyClass to version 5. MyClass
    must be a class deriving from :class:`~SerializableObject`.

    The upgrade function should take a single argument - the dictionary to
    upgrade, and return a dictionary with the fields upgraded.

    Remember that you don't need to provide an upgrade function for upgrades
    that add or remove fields, only for schema versions that change the field
    names.

    :param type cls: class to upgrade
    :param int version_to_upgrade_to: the version to upgrade to
    """

    def decorator_func(func):
        """ Decorator for marking upgrade functions """
        def wrapped_update(data):
            modified = func(data)
            data.clear()
            data.update(modified)

        register_downgrade_function(cls._serializable_label.split(".")[0],
                version_to_upgrade_to, wrapped_update)
        return func

    return decorator_func


def serializable_field(name, required_type=None, doc=None):
    """
    Convienence function for adding attributes to child classes of
    :class:`~SerializableObject` in such a way that they will be serialized/deserialized
    automatically.

    Use it like this:

    .. code-block:: python

        @core.register_type
        class Foo(SerializableObject):
            bar = serializable_field("bar", required_type=int, doc="example")

    This would indicate that class "foo" has a serializable field "bar".  So:

    .. code-block:: python

        f = foo()
        f.bar = "stuff"

        # serialize & deserialize
        otio_json = otio.adapters.from_name("otio")
        f2 = otio_json.read_from_string(otio_json.write_to_string(f))

        # fields should be equal
        f.bar == f2.bar

    Additionally, the "doc" field will become the documentation for the
    property.

    :param str name: name of the field to add
    :param type required_type: type required for the field
    :param str doc: field documentation

    :return: property object
    :rtype: :py:class:`property`
    """

    def getter(self):
        return self._dynamic_fields[name]

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

        self._dynamic_fields[name] = val

    return property(getter, setter, doc=doc)


def deprecated_field():
    """For marking attributes on a SerializableObject deprecated."""

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter, doc="Deprecated field, do not use.")
