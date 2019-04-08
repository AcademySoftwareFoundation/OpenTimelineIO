from opentimelineio.core._core_utils import add_method
from opentimelineio import _otio


@add_method(_otio.Track)
def each_clip(self, search_range=None):
    return self.each_child(search_range, _otio.Clip)


