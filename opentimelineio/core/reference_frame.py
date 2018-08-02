"""Represents a reference frame of time associated with an item in OTIO.
"""

import collections

# @TODO: Promote this up to the top level of OTIO
# eg: some_clip.local_space
#     some_clip.duration(otio.TransformSpace.Local)
#     some_clip.duration(otio.TransformSpace.Final)
# result = transformed_to(
#     some_time,
#     some_clip.local_space,
#     other_clip.final_space,
# )
# cl_range = range_of(
#     some_clip,
#     other_clip.final_space,
#     clipped_to=other_clip,
#     transitions=True
# )

def FakeEnum(cl_name, fields):
    return collections.namedtuple(cl_name, fields)(*fields)
#
# # using collections.NamedTuple to make an immutable enum-like object that is
# # python 2 compatible.
# TransformName = collections.namedtuple(
#     "TransformName",
#     (
#         # Goes from 0-pre transform duration
#         # if you want a zero-based coordinate system
#         "Intrinsic",
#
#         # [source_range.start_frame -> pre transform duration]
#         # with the "origin" set to the source_range.start_frame but before scale
#         "Local",
#
#         # [source_range.start_frame -> post transform duration]
#         # what the parent will see
#         # computation is always done in this space
#         "Final",
#     )
# )("Intrinsic", "Local", "Final")

# using collections.NamedTuple to make an immutable enum-like object that is
# python 2 compatible.
TransformName = FakeEnum("TransformName", ("BeforeEffects", "AfterEffects"))

# class TransformName:
#     # Goes from 0-pre transform duration
#     # if you want a zero-based coordinate system
#     Intrinsic = "intrinsic"
#
#     # [source_range.start_frame -> pre transform duration]
#     # with the "origin" set to the source_range.start_frame but before scale
#     Local = "local"
#
#     # [source_range.start_frame -> post transform duration]
#     # what the parent will see
#     # computation is always done in this space
#     Final = "final"

class ReferenceFrame(object):
    def __init__(self, parent, space_enum):
        self._parent = parent
        self._space = space_enum

    @property
    def parent(self):
        return self._parent

    @property
    def space(self):
        return self._space


