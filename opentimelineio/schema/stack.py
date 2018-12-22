#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""A stack represents a series of composable.Composables that are arranged such
that their start times are at the same point.

Most commonly, this would be a series of schema.Track objects that then
contain clips.  The 0 time of those tracks would be coincide with the 0-time of
the stack.

Stacks are in compositing order, with later children obscuring earlier
children. In other words, from bottom to top.  If a stack has three children,
[A, B, C], C is above B which is above A.

A stack is the length of its longest child.  If a child ends before the other
children, then an earlier index child would be visible before it.
"""

from .. import (
    core,
    opentime,
    exceptions
)

from . import (
    clip
)


@core.register_type
class Stack(core.Composition):
    _serializable_label = "Stack.1"
    _composition_kind = "Stack"
    _modname = "schema"

    def __init__(
        self,
        name=None,
        children=None,
        source_range=None,
        markers=None,
        effects=None,
        metadata=None
    ):
        core.Composition.__init__(
            self,
            name=name,
            children=children,
            source_range=source_range,
            markers=markers,
            effects=effects,
            metadata=metadata
        )

    def range_of_child_at_index(self, index):
        try:
            child = self[index]
        except IndexError:
            raise exceptions.NoSuchChildAtIndex(index)

        dur = child.duration()

        return opentime.TimeRange(
            start_time=opentime.RationalTime(0, dur.rate),
            duration=dur
        )

    def each_clip(self, search_range=None):
        return self.each_child(search_range, clip.Clip)

    def available_range(self):
        if len(self) == 0:
            return opentime.TimeRange()

        duration = max(child.duration() for child in self)

        return opentime.TimeRange(
            opentime.RationalTime(0, duration.rate),
            duration=duration
        )

    def range_of_all_children(self):
        child_map = {}
        for i, c in enumerate(self._children):
            child_map[c] = self.range_of_child_at_index(i)
        return child_map

    def trimmed_range_of_child_at_index(self, index, reference_space=None):
        range = self.range_of_child_at_index(index)

        if not self.source_range:
            return range

        range = opentime.TimeRange(
            start_time=self.source_range.start_time,
            duration=min(range.duration, self.source_range.duration)
        )

        return range
