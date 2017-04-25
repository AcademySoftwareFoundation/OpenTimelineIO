"""
Implement Sequence and Stack.
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
    _serializeable_label = "Stack.1"
    _composition_kind = "Stack"
    _modname = "schema"

    def __init__(
        self,
        name=None,
        children=None,
        source_range=None,
        metadata=None
    ):
        core.Composition.__init__(
            self,
            name=name,
            children=children,
            source_range=source_range,
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
            duration = duration
        )

    def trimmed_range_of_child_at_index(self, index, reference_space=None):
        range = self.range_of_child_at_index(index)

        if not self.source_range:
            return range

        range.start_time = self.source_range.start_time
        range.duration = min(range.duration, self.source_range.duration)

        return range
