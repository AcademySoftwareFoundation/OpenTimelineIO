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

"""Implement Track sublcass of composition."""

import collections

from .. import (
    core,
    opentime,
)

from . import (
    gap,
    transition,
    clip,
)


class TrackKind:
    Video = "Video"
    Audio = "Audio"


class NeighborGapPolicy:
    """ enum for deciding how to add gap when asking for neighbors """
    never = 0
    around_transitions = 1


@core.register_type
class Track(core.Composition):
    _serializable_label = "Track.1"
    _composition_kind = "Track"
    _modname = "schema"

    def __init__(
        self,
        name=None,
        children=None,
        kind=TrackKind.Video,
        source_range=None,
        markers=None,
        effects=None,
        metadata=None,
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
        self.kind = kind

    kind = core.serializable_field(
        "kind",
        doc="Composition kind (Stack, Track)"
    )

    def range_of_child_at_index(self, index):
        child = self[index]

        # sum the durations of all the children leading up to the chosen one
        start_time = sum(
            (
                o_c.duration()
                for o_c in (c for c in self[:index] if not c.overlapping())
            ),
            opentime.RationalTime(value=0, rate=child.duration().rate)
        )
        if isinstance(child, transition.Transition):
            start_time -= child.in_offset

        return opentime.TimeRange(start_time, child.duration())

    def trimmed_range_of_child_at_index(self, index, reference_space=None):
        child_range = self.range_of_child_at_index(index)

        return self.trim_child_range(child_range)

    def handles_of_child(self, child):
        """If media beyond the ends of this child are visible due to adjacent
        Transitions (only applicable in a Track) then this will return the
        head and tail offsets as a tuple of RationalTime objects. If no handles
        are present on either side, then None is returned instead of a
        RationalTime.

        Example usage

        >>> head, tail = track.handles_of_child(clip)
        >>> if head:
        ...     print('do something')
        >>> if tail:
        ...     print('do something else')
        """
        head, tail = None, None
        before, after = self.neighbors_of(child)
        if isinstance(before, transition.Transition):
            head = before.in_offset
        if isinstance(after, transition.Transition):
            tail = after.out_offset

        return head, tail

    def available_range(self):
        # Sum up our child items' durations
        duration = sum(
            (c.duration() for c in self if isinstance(c, core.Item)),
            opentime.RationalTime()
        )

        # Add the implicit gap when a Transition is at the start/end
        if self and isinstance(self[0], transition.Transition):
            duration += self[0].in_offset
        if self and isinstance(self[-1], transition.Transition):
            duration += self[-1].out_offset

        result = opentime.TimeRange(
            start_time=opentime.RationalTime(0, duration.rate),
            duration=duration
        )

        return result

    def each_clip(self, search_range=None, shallow_search=False):
        return self.each_child(search_range, clip.Clip, shallow_search)

    def neighbors_of(self, item, insert_gap=NeighborGapPolicy.never):
        """Returns the neighbors of the item as a namedtuple, (previous, next).

        Can optionally fill in gaps when transitions have no gaps next to them.

        with insert_gap == NeighborGapPolicy.never:
        [A, B, C] :: neighbors_of(B) -> (A, C)
        [A, B, C] :: neighbors_of(A) -> (None, B)
        [A, B, C] :: neighbors_of(C) -> (B, None)
        [A] :: neighbors_of(A) -> (None, None)

        with insert_gap == NeighborGapPolicy.around_transitions:
        (assuming A and C are transitions)
        [A, B, C] :: neighbors_of(B) -> (A, C)
        [A, B, C] :: neighbors_of(A) -> (Gap, B)
        [A, B, C] :: neighbors_of(C) -> (B, Gap)
        [A] :: neighbors_of(A) -> (Gap, Gap)
        """

        try:
            index = self.index(item)
        except ValueError:
            raise ValueError(
                "item: {} is not in composition: {}".format(
                    item,
                    self
                )
            )

        previous, next_item = None, None

        # look before index
        if index == 0:
            if insert_gap == NeighborGapPolicy.around_transitions:
                if isinstance(item, transition.Transition):
                    previous = gap.Gap(
                        source_range=opentime.TimeRange(duration=item.in_offset))
        elif index > 0:
            previous = self[index - 1]

        if index == len(self) - 1:
            if insert_gap == NeighborGapPolicy.around_transitions:
                if isinstance(item, transition.Transition):
                    next_item = gap.Gap(
                        source_range=opentime.TimeRange(duration=item.out_offset))
        elif index < len(self) - 1:
            next_item = self[index + 1]

        return collections.namedtuple('neighbors', ('previous', 'next'))(
            previous,
            next_item
        )

    def range_of_all_children(self):
        """Return a dict mapping children to their range in this track."""

        if not self._children:
            return {}

        result_map = {}

        # Heuristic to guess what the rate should be set to based on the first
        # thing in the track.
        first_thing = self._children[0]
        if isinstance(first_thing, transition.Transition):
            rate = first_thing.in_offset.rate
        else:
            rate = first_thing.trimmed_range().duration.rate

        last_end_time = opentime.RationalTime(0, rate)

        for thing in self._children:
            if isinstance(thing, transition.Transition):
                result_map[thing] = opentime.TimeRange(
                    last_end_time - thing.in_offset,
                    thing.out_offset + thing.in_offset,
                )
            else:
                last_range = opentime.TimeRange(
                    last_end_time,
                    thing.trimmed_range().duration
                )
                result_map[thing] = last_range
                last_end_time = last_range.end_time_exclusive()

        return result_map


# the original name for "track" was "sequence" - this will turn "Sequence"
# found in OTIO files into Track automatically.
core.register_type(Track, "Sequence")
