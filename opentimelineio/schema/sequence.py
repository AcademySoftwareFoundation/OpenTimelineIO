""" Imeplement Sequence sublcass of composition. """

from .. import (
    core,
    opentime,
)


class SequenceKind:
    Video = "Video"
    Audio = "Audio"


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

    kind = core.serializeable_field("kind")

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
            self.source_range.start_time >= range.end_time() or
            self.source_range.end_time() <= range.start_time
        ):
            return None

        if range.start_time < self.source_range.start_time:
            range = opentime.range_from_start_end_time(
                self.source_range.start_time,
                range.end_time()
            )

        if range.end_time() > self.source_range.end_time():
            range = opentime.range_from_start_end_time(
                range.start_time,
                self.source_range.end_time()
            )

        return range

    def computed_duration(self):
        return sum(
            [child.duration() for child in self],
            opentime.RationalTime()
        )
