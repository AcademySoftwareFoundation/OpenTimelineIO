from opentimelineio._otio import *
from opentimelineio._otio import _testing
from opentimelineio import _otio

from . _core_utils import (add_method, _value_to_any, _value_to_so_vector,
                          _add_mutable_mapping_methods, _add_mutable_sequence_methods)
from . import mediaReference, composition, composable, item

def serialize_json_to_string(root, indent=4):
    return _otio._serialize_json_to_string(_value_to_any(root), indent)
    
def serialize_json_to_file(root, filename, indent=4):
    return _otio._serialize_json_to_file(_value_to_any(root), filename, indent)

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
    
def serializable_field(name, required_type=None, doc=None):
    """Create a serializable_field for child classes of SerializableObject.

    Convienence function for adding attributes to child classes of
    SerializableObject in such a way that they will be serialized/deserialized
    automatically.

    Use it like this:
        @core.register_type
        class Foo(SerializableObject):
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
    """ For marking attributes on a SerializableObject deprecated.  """

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter, doc="Deprecated field, do not use.")

