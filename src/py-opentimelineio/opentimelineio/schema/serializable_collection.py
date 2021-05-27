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
    """ Generator that returns each child contained in the serializable
    collection in the order in which it is found.

    Note that this function is now deprecated, please consider using
    children_if() instead.

    Arguments:
        search_range: if specified, only children whose range overlaps with
                      the search range will be yielded.
        descended_from_type: if specified, only children who are a
                      descendent of the descended_from_type will be yielded.
    """
    for child in self.children_if(descended_from_type, search_range):
        yield child


@add_method(_otio.SerializableCollection)
def each_clip(self, search_range=None):
    """ Generator that returns each clip contained in the serializable
    collection in the order in which it is found.

    Note that this function is now deprecated, please consider using
    clip_if() instead.

    Arguments:
        search_range: if specified, only children whose range overlaps with
                      the search range will be yielded.
    """
    for child in self.clip_if(search_range):
        yield child
