from .. import core

"""Test Class"""


@core.register_type
class Foo(core.SerializableObjectWithMetadata):
    _serializable_label = "Foo.1"

    def __init__(self, name="", metadata=None):
        core.SerializableObjectWithMetadata.__init__(self, name, metadata)

    abc = core.serializable_field(
        "abc",
        type([]),
        "an int"
    )
