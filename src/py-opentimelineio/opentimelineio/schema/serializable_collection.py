from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.SerializableCollection)
def __str__(self):
    return "SerializableCollection({}, {}, {})".format(
        str(self.name),
        str(list(self)),
        str(self.metadata)
    )


@add_method(_otio.SerializableCollection)
def __repr__(self):
    return (
        "otio.{}("
        "name={}, "
        "children={}, "
        "metadata={}"
        ")".format(
            "schema.SerializableCollection",
            repr(self.name),
            repr(list(self)),
            repr(self.metadata)
        )
    )


@add_method(_otio.SerializableCollection)
def each_child(self, search_range=None, descended_from_type=_otio.Composable):
    is_descendant = descended_from_type is _otio.Composable
    for child in self:
        # filter out children who are not descended from the specified type
        if is_descendant or isinstance(child, descended_from_type):
            yield child

        # for children that are compositions, recurse into their children
        if hasattr(child, "each_child"):
            for c in child.each_child(search_range, descended_from_type):
                yield c


@add_method(_otio.SerializableCollection)
def each_clip(self, search_range=None):
    return self.each_child(search_range, _otio.Clip)
