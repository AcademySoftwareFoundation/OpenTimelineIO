"""
Implement Sequence and Stack.
"""

from .. import (
    core,
    opentime,
    exceptions
)


@core.register_type
class Stack(core.Composition):
    _serializeable_label = "Stack.1"
    _composition_kind = "Stack"
    _modname = "schema"
    # only allow descendents of item in the stack
    _composable_base_class = core.Item

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

    def computed_duration(self):
        if len(self) == 0:
            return opentime.RationalTime()
        return max(map(lambda child: child.duration(), self))

    def trimmed_range_of_child_at_index(self, index, reference_space=None):
        range = self.range_of_child_at_index(index)

        if not self.source_range:
            return range

        range.start_time = self.source_range.start_time
        range.duration = min(range.duration, self.source_range.duration)

        return range
