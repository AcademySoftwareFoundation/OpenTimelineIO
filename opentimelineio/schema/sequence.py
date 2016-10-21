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

    def computed_duration(self):
        return sum(
            map(lambda child: child.duration(), self),
            opentime.RationalTime())
