# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.SerializableCollection)
def __str__(self):
    return "SerializableCollection({}, {}, {})".format(
        str(self.name),
        str(list(self)),
        str(self.metadata)
    )


@add_method(_otio.SerializableCollection)
def __repr__(self):
    return (
        "otio.{}("
        "name={}, "
        "children={}, "
        "metadata={}"
        ")".format(
            "schema.SerializableCollection",
            repr(self.name),
            repr(list(self)),
            repr(self.metadata)
        )
    )


@add_method(_otio.SerializableCollection)
def each_child(self, search_range=None, descended_from_type=_otio.Composable,
               shallow_search=False):
    """ Generator that returns each child contained in the serializable
    collection in the order in which it is found.

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


@add_method(_otio.SerializableCollection)
def each_clip(self, search_range=None, shallow_search=False):
    """ Generator that returns each clip contained in the serializable
    collection in the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`each_clip` instead.

    :param TimeRange search_range: if specified, only children whose range overlaps
                                   with the search range will be yielded.
    :param bool shallow_search: if True, will only search children of self and not
                                recurse into children of children.
    """
    yield from self.clip_if(search_range, shallow_search)
