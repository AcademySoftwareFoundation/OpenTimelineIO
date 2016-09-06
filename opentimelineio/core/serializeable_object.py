"""
OpenTimelineIO core.py - Implement core classes and functions.

Currently a json backed python implementation, with intent to port this to c.

From a user's point of view, the objects in the OTIO stack are designed such
that they probably won't need to reach into core.

SerializeableObject - The JSON backend knows how to serialize this.
^^^
Item - defines the essential fields of OTIO data.
^^^
Timeline - user facing object that exposes the mose convienence functions.

"""


def serializeable_field(name, required_type=None):
    """
    Convienence function for adding properties to children of
    SerializeableObject that stashes their data in the correct way.

    Use it like this:
        class foo(SerializeableObject):
            bar = serializeable_field("bar", required_type=int)
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

    return property(getter, setter)


def deprecated_field():
    """ For marking properties on a SerializeableObject deprecated.  """

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter)


class SerializeableObject(object):
    """
    Core object the json backend knows how to serialize. Also provides eq.
    """

    # child classes must override this
    serializeable_label = None
    class_path = "core.SerializeableObject"

    def __init__(self):
        self.data = {}

    def __eq__(self, other):
        try:
            return (self.data == other.data)
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.data))

    def update(self, d):
        self.data.update(d)
