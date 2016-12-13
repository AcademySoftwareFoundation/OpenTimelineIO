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


def register_type(classobj):
    """ Register a class to a Schema Label.  """
    _OTIO_TYPES[
        schema_name_from_label(classobj._serializeable_label)
    ] = classobj

    return classobj


def upgrade_function_for(cls, version_to_upgrade_to):
    """Decorator for identifying schema class upgrade functions.

    example:
        @upgrade_function_for(MyClass, 5)
        def upgrade_to_version_five(data):
            # ...

    This will get called to upgrade a schema of MyClass to version 5.  My class
    must be a class deriving from otio.core.SerializeableObject.

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
        raise exceptions.NotSupportedError(
            "OTIO_SCHEMA: '{}' not in type registry.".format(schema_name)
        )

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
        for version, upgrade_func in (
            _UPGRADE_FUNCTIONS[cls].items()
        ):
            if version < schema_version:
                continue

            data_dict = upgrade_func(data_dict)

    obj = cls()
    obj.data.update(data_dict)

    return obj
