"""
Implementation of the OTIO built in schema, Timeline object.
"""

from .. import (
    core,
    opentime,
)

from . import stack, sequence


@core.register_type
class Timeline(core.SerializeableObject):
    serializeable_label = "Timeline.1"

    def __init__(
        self,
        name=None,
        tracks=None,
        global_start_time=None,
        metadata=None,
    ):
        core.SerializeableObject.__init__(self)
        self.name = name
        if global_start_time is None:
            global_start_time = opentime.RationalTime(0, 24)
        self.global_start_time = global_start_time

        if tracks is None:
            tracks = []
        self.tracks = stack.Stack(name="tracks", children=tracks)

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    name = core.serializeable_field("name")
    tracks = core.serializeable_field("tracks", core.Composition)
    metadata = core.serializeable_field("metadata", dict)

    def __str__(self):
        return 'Timeline("{}", {})'.format(str(self.name), str(self.tracks))

    def __repr__(self):
        return (
            "otio.schema.Timeline(name={}, tracks={})".format(
                repr(self.name),
                repr(self.tracks)
            )
        )

    def each_clip(self, search_range=None):
        """ return a flat list of each clip, limited to the search_range """
        return self.tracks.each_clip(search_range)

    def duration(self):
        return self.tracks.duration()


def timeline_from_clips(clips):
    """Convenience for making a single track timeline from a list of clips."""

    track = sequence.Sequence(children=clips)
    return Timeline(tracks=[track])
