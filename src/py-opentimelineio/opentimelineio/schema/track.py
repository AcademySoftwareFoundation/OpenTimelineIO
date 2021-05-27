from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Track)
def each_clip(self, search_range=None, shallow_search=False):
    """ Generator that returns each clip contained in the track
    in the order in which it is found.

    Note that this function is now deprecated, please consider using
    clip_if() instead.

    Arguments:
        search_range: if specified, only children whose range overlaps with
                      the search range will be yielded.
        shallow_search: if True, will only search children of self, not
                        and not recurse into children of children.
    """
    for child in self.clip_if(search_range):
        yield child
