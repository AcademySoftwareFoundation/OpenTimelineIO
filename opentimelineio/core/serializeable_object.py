""" Implements the otio.core.SerializeableObject """

from . import (
    type_registry,
)


class SerializeableObject(object):

    """
    Base object for things that can be serialized to/deserialized from .otio
    files.

    To define a new child class of this, you inherit from it and also use the
    register_type decorator.  Then you use the serializeable_field function
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
        class ExampleChild(otio.core.SerializeableObject):
            _serializeable_label = "ExampleChild.7"

            child_data = otio.core.serializeable_field("child_data", int)

            # @TODO: delete once testing shows nothing is referencing this.
            old_child_data_name = otio.core.deprecated_field()


        @otio.core.upgrade_function_for(ExampleChild, 3)
        def upgrade_child_to_three(data):
            return {"child_data" : data["old_child_data_name"]}
    """

    # Every child must define a _serializeable_label attribute.
    # This attribute is a string in the form of: "SchemaName.VersionNumber"
    # Where VersionNumber is an integer.
    # You can use the classmethods .schema_name() and .schema_version() to
    # query these fields.
    _serializeable_label = None
    _class_path = "core.SerializeableObject"

    def __init__(self):
        self.data = {}

    def __eq__(self, other):
        try:
            return (self.data == other.data)
        except AttributeError:
            return False

    def __hash__(self):
        """ 
        hash method for SerializeableObject.

        Because the children of this class should implement their own versions
        of __eq__ and __hash__, this is really meant to be a "reasonable 
        default" to get things up and running until that is possible.

        As such its using the simple ugly hack implementation of stringifying.

        If this is ever a problem it should be replaced with a more robust
        implementation.
        """

        return hash(str(self.data))

    def update(self, d):
        """ 
        Update the data dictionary of this SerializeableObject with the .data 
        of d if d is a SerializeableObject or if d is a dictionary, d itself.
        """

        if isinstance(d, SerializeableObject):
            self.data.update(d.data)
        else:
            self.data.update(d)

    @classmethod
    def schema_name(cls):
        return type_registry.schema_name_from_label(
            cls._serializeable_label
        )

    @classmethod
    def schema_version(cls):
        return type_registry.schema_version_from_label(
            cls._serializeable_label
        )


def serializeable_field(name, required_type=None, doc=None):
    """
    Convienence function for adding attributes to child classes of
    SerializeableObject in such a way that they will be serialized/deserialized
    automatically.

    Use it like this:
        class foo(SerializeableObject):
            bar = serializeable_field("bar", required_type=int, doc="example")

    This would indicate that class "foo" has a serializeable field "bar".  So:
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
            required_type is not None and
            val is not None and
            not isinstance(val, required_type)
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
    """ For marking attributes on a SerializeableObject deprecated.  """

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter)
