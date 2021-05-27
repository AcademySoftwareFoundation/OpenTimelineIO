from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Timeline)
def __str__(self):
    return 'Timeline("{}", {})'.format(str(self.name), str(self.tracks))


@add_method(_otio.Timeline)
def __repr__(self):
    return (
        "otio.schema.Timeline(name={}, tracks={})".format(
            repr(self.name),
            repr(self.tracks)
        )
    )


@add_method(_otio.Timeline)
def each_child(self, search_range=None, descended_from_type=_otio.Composable):
    """ Generator that returns each child contained in the timeline
    in the order in which it is found.

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


@add_method(_otio.Timeline)
def each_clip(self, search_range=None):
    """ Generator that returns each clip contained in the timeline
    in the order in which it is found.

    Note that this function is now deprecated, please consider using
    clip_if() instead.

    Arguments:
        search_range: if specified, only children whose range overlaps with
                      the search range will be yielded.
    """
    for child in self.clip_if(search_range):
        yield child
