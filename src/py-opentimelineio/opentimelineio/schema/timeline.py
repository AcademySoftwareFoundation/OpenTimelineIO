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
    return self.tracks.each_child(search_range, descended_from_type)


@add_method(_otio.Timeline)
def each_clip(self, search_range=None):
    """Return a flat list of each clip, limited to the search_range."""

    return self.tracks.each_clip(search_range)
