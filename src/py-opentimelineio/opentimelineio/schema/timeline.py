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
