from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Track)
def each_clip(self, search_range=None, shallow_search=False):
    return self.each_child(search_range, _otio.Clip, shallow_search)
