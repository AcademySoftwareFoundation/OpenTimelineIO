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

"""Imeplement Sequence sublcass of composition."""

from .. import (
    core,
    opentime,
)

from . import (
    gap,
    transition,
    clip,
)


class SequenceKind:
    Video = "Video"
    Audio = "Audio"


class NeighborGapPolicy:
    """ enum for deciding how to add gap when asking for neighbors """
    never = 0
    around_transitions = 1


@core.register_type
class Sequence(core.Composition):
    _serializeable_label = "Sequence.1"
    _composition_kind = "Sequence"
    _modname = "schema"

    def __init__(
        self,
        name=None,
        children=None,
        source_range=None,
        kind=SequenceKind.Video,
        metadata=None,
    ):
        core.Composition.__init__(
            self,
            name=name,
            children=children,
            source_range=source_range,
            metadata=metadata
        )
        self.kind = kind

    kind = core.serializeable_field(
        "kind",
        doc="Composition kind (Stack, Sequence)"
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
        range = self.range_of_child_at_index(index)

        if not self.source_range:
            return range

        # cropped out entirely
        if (
            self.source_range.start_time >= range.end_time_exclusive()
            or self.source_range.end_time_exclusive() <= range.start_time
        ):
            return None

        if range.start_time < self.source_range.start_time:
            range = opentime.range_from_start_end_time(
                self.source_range.start_time,
                range.end_time_exclusive()
            )

        if range.end_time_exclusive() > self.source_range.end_time_exclusive():
            range = opentime.range_from_start_end_time(
                range.start_time,
                self.source_range.end_time_exclusive()
            )

        return range

    def available_range(self):
        durations = []

        # resolve the implicit gap
        if self._children and isinstance(self[0], transition.Transition):
            durations.append(self[0].in_offset)
        if self._children and isinstance(self[-1], transition.Transition):
            durations.append(self[-1].out_offset)

        durations.extend(
            child.duration() for child in self if isinstance(child, core.Item)
        )

        result = opentime.TimeRange(
            duration=sum(durations, opentime.RationalTime())
        )

        result.start_time = opentime.RationalTime(0, result.duration.rate)

        return result

    def each_clip(self, search_range=None):
        return self.each_child(search_range, clip.Clip)

    def neighbors_of(self, item, insert_gap=NeighborGapPolicy.never):
        try:
            index = self.index(item)
        except ValueError:
            raise ValueError(
                "item: {} is not in composition: {}".format(
                    item,
                    self
                )
            )

        result = []

        # look before index
        if (
            index == 0
            and insert_gap == NeighborGapPolicy.around_transitions
            and isinstance(item, transition.Transition)
        ):
            result.append(
                gap.Gap(
                    source_range=opentime.TimeRange(duration=item.in_offset)
                )
            )
        elif index > 0:
            result.append(self[index - 1])

        result.append(item)

        if (
            index == len(self) - 1
            and insert_gap == NeighborGapPolicy.around_transitions
            and isinstance(item, transition.Transition)
        ):
            result.append(
                gap.Gap(
                    source_range=opentime.TimeRange(duration=item.out_offset)
                )
            )
        elif index < len(self) - 1:
            result.append(self[index + 1])

        return result
