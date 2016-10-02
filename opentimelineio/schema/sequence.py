""" Imeplement Sequence sublcass of composition. """

from .. import (
    core,
    opentime,
    exceptions
)

from ..core import (
    item
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
        try:
            child = self[index]
        except IndexError:
            raise exceptions.NoSuchChildAtIndex(index)

        # sum the durations of all the children leading up to the chosen one
        start_time = sum(
            map(
                lambda child: child.duration(),
                self[0: index]
            ),
            opentime.RationalTime(value=0, rate=child.duration().rate)
        )

        result = opentime.TimeRange(
            start_time,
            child.duration()
        )

        return result

    def range_of_child(self, child):
        """ Return range of the child in this object.  """

        if not isinstance(child, item.Item):
            raise TypeError(
                "range_of_child requires a object child of 'Item', not '{}'"
                "".format(type(child))
            )

        current = child
        parents = []

        while(current is not self):
            try:
                current = current._parent
            except AttributeError:
                raise exceptions.NotAChildError(
                    "Item '{}' is not a child of '{}', cannot compute range."
                    "".format(child, self)
                )

            parents.append(current)

        result_range = child.source_range

        # @TODO: apply the transform to the range, then clip the durations

        current = child
        result_range = None

        for parent in parents:
            index = parent.index(current)
            parent_range = parent.range_of_child_at_index(index)

            if not result_range:
                result_range = parent_range
                current = parent
                continue

            result_range.start_time = (
                result_range.start_time +
                parent_range.start_time +
                parent_range.duration
            )
            result_range.duration = result_range.duration
            current = parent

        return result_range

    def computed_duration(self):
        return sum(
            map(lambda child: child.duration(), self),
            opentime.RationalTime())
