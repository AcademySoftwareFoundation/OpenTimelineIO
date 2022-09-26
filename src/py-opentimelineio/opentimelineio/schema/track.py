# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Track)
def each_clip(self, search_range=None, shallow_search=False):
    """Generator that returns each clip contained in the track
    in the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`clip_if` instead.

    :param TimeRange search_range: if specified, only children whose range overlaps with
                                   the search range will be yielded.
    :param bool shallow_search: if True, will only search children of self and not
                                recurse into children of children.
    """
    yield from self.clip_if(search_range, shallow_search)
