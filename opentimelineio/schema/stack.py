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

        duration = child.duration()

        return opentime.TimeRange(
            opentime.RationalTime(value=0, rate=duration.rate),
            duration
        )

    def computed_duration(self):
        if len(self) == 0:
            return None
        return max(map(lambda child: child.duration(), self))
