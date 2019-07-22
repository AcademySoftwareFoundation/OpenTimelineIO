from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Stack)
def each_clip(self, search_range=None):
    return self.each_child(search_range, _otio.Clip)
