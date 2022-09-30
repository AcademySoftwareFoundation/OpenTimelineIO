# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Timeline)
def __str__(self):
    return f'Timeline("{str(self.name)}", {str(self.tracks)})'


@add_method(_otio.Timeline)
def __repr__(self):
    return (
        "otio.schema.Timeline(name={}, tracks={})".format(
            repr(self.name),
            repr(self.tracks)
        )
    )


@add_method(_otio.Timeline)
def each_child(self, search_range=None, descended_from_type=_otio.Composable,
               shallow_search=False):
    """Generator that returns each child contained in the timeline
    in the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`children_if` instead.

    :param TimeRange search_range: if specified, only children whose range overlaps
                                   with the search range will be yielded.
    :param type descended_from_type: if specified, only children who are a descendent
                                     of the descended_from_type will be yielded.
    :param bool shallow_search: if True, will only search children of self and not
                                recurse into children of children.
    """
    yield from self.children_if(descended_from_type, search_range, shallow_search)


@add_method(_otio.Timeline)
def each_clip(self, search_range=None, shallow_search=False):
    """Generator that returns each clip contained in the timeline
    in the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`clip_if` instead.

    :param TimeRange search_range: if specified, only children whose range overlaps
                                   with the search range will be yielded.
    :param bool shallow_search: if True, will only search children of self and not
                                recurse into children of children.
    """
    yield from self.clip_if(search_range, shallow_search)
