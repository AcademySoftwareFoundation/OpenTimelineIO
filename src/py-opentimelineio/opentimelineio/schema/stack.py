from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Stack)
def each_clip(self, search_range=None):
    """ Generator that returns each clip contained in the stack
    in the order in which it is found.

    Note that this function is now deprecated, please consider using
    clip_if() instead.

    Arguments:
        search_range: if specified, only children whose range overlaps with
                      the search range will be yielded.
    """
    for child in self.clip_if(search_range):
        yield child
