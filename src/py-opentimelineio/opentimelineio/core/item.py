from . _core_utils import add_method
from .. import _otio


@add_method(_otio.Item)
def __str__(self):
    return "{}({}, {}, {}, {}, {})".format(
        self.__class__.__name__,
        self.name,
        str(self.source_range),
        str(self.effects),
        str(self.markers),
        str(self.metadata)
    )


@add_method(_otio.Item)
def __repr__(self):
    return (
        "otio.{}.{}("
        "name={}, "
        "source_range={}, "
        "effects={}, "
        "markers={}, "
        "metadata={}"
        ")".format(
            "core" if self.__class__ is _otio.Item else "schema",
            self.__class__.__name__,
            repr(self.name),
            repr(self.source_range),
            repr(self.effects),
            repr(self.markers),
            repr(self.metadata)
        )
    )
