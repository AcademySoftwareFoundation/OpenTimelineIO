# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from . _core_utils import add_method
from .. import _otio


@add_method(_otio.Composition)
def __str__(self):
    return "{}({}, {}, {}, {})".format(
        self.__class__.__name__,
        str(self.name),
        str(list(self)),
        str(self.source_range),
        str(self.metadata)
    )


@add_method(_otio.Composition)
def __repr__(self):
    return (
        "otio.{}.{}("
        "name={}, "
        "children={}, "
        "source_range={}, "
        "metadata={}"
        ")".format(
            "core" if self.__class__ is _otio.Composition else "schema",
            self.__class__.__name__,
            repr(self.name),
            repr(list(self)),
            repr(self.source_range),
            repr(self.metadata)
        )
    )


@add_method(_otio.Composition)
def each_child(
        self,
        search_range=None,
        descended_from_type=_otio.Composable,
        shallow_search=False,
):
    """
    Generator that returns each child contained in the composition in
    the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`children_if` instead.

    :param TimeRange search_range: if specified, only children whose range overlaps with
                                   the search range will be yielded.
    :param type descended_from_type: if specified, only children who are a descendent
                                     of the descended_from_type will be yielded.
    :param bool shallow_search: if True, will only search children of self, not
                                and not recurse into children of children.
    """
    yield from self.children_if(descended_from_type, search_range, shallow_search)
