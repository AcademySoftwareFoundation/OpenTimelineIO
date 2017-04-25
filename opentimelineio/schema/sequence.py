""" Imeplement Sequence sublcass of composition. """

from .. import (
    core,
    opentime,
)

from . import (
    filler,
    transition,
    clip,
)


class SequenceKind:
    Video = "Video"
    Audio = "Audio"


class NeighborFillerPolicy:
    """ enum for deciding how to add filler when asking for neighbors """
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
            map(lambda current_item: current_item.duration(), self[:index]),
            opentime.RationalTime(value=0, rate=child.duration().rate)
        )

        return opentime.TimeRange(start_time, child.duration())

    def trimmed_range_of_child_at_index(self, index, reference_space=None):
        range = self.range_of_child_at_index(index)

        if not self.source_range:
            return range

        # cropped out entirely
        if (
            self.source_range.start_time >= range.end_time_exclusive() or
            self.source_range.end_time_exclusive() <= range.start_time
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

    def computed_duration(self):
        durations = []

        # resolve the implicit filler
        if self._children and isinstance(self[0], transition.Transition):
            durations.append(self[0].in_offset)
        if self._children and isinstance(self[-1], transition.Transition):
            durations.append(self[-1].out_offset)

        durations.extend(
            child.duration() for child in self if isinstance(child, core.Item)
        )

        return sum(durations, opentime.RationalTime())

    def each_clip(self, search_range=None):
        return self.each_child(search_range, clip.Clip)

    def neighbors_of(self, item, insert_filler=NeighborFillerPolicy.never):
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
            and insert_filler == NeighborFillerPolicy.around_transitions
            and isinstance(item, transition.Transition)
        ):
            result.append(
                filler.Filler(
                    source_range=opentime.TimeRange(duration=item.in_offset)
                )
            )
        elif index > 0:
            result.append(self[index - 1])

        result.append(item)

        if (
            index == len(self) - 1
            and insert_filler == NeighborFillerPolicy.around_transitions
            and isinstance(item, transition.Transition)
        ):
            result.append(
                filler.Filler(
                    source_range=opentime.TimeRange(duration=item.out_offset)
                )
            )
        elif index < len(self) - 1:
            result.append(self[index + 1])

        return result
