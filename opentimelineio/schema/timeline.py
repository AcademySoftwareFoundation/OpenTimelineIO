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

"""Implementation of the OTIO built in schema, Timeline object."""

import copy

from .. import (
    core,
    opentime,
)

from . import stack, track


@core.register_type
class Timeline(core.SerializableObject):
    _serializable_label = "Timeline.1"

    def __init__(
        self,
        name=None,
        tracks=None,
        global_start_time=None,
        metadata=None,
    ):
        super(Timeline, self).__init__()
        self.name = name
        self.global_start_time = copy.deepcopy(global_start_time)

        if tracks is None:
            tracks = []
        self.tracks = stack.Stack(name="tracks", children=tracks)

        self.metadata = copy.deepcopy(metadata) if metadata else {}

    name = core.serializable_field("name", doc="Name of this timeline.")
    tracks = core.serializable_field(
        "tracks",
        core.Composition,
        doc="Stack of tracks containing items."
    )
    metadata = core.serializable_field(
        "metadata",
        dict,
        "Metadata dictionary."
    )
    global_start_time = core.serializable_field(
        "global_start_time",
        opentime.RationalTime,
        doc="Global starting time value and rate of the timeline."
    )

    def __str__(self):
        return 'Timeline("{}", {})'.format(str(self.name), str(self.tracks))

    def __repr__(self):
        return (
            "otio.schema.Timeline(name={}, tracks={})".format(
                repr(self.name),
                repr(self.tracks)
            )
        )

    def each_child(self, search_range=None, descended_from_type=core.Composable):
        return self.tracks.each_child(search_range, descended_from_type)

    def each_clip(self, search_range=None):
        """Return a flat list of each clip, limited to the search_range."""

        return self.tracks.each_clip(search_range)

    def duration(self):
        """Duration of this timeline."""

        return self.tracks.duration()

    def range_of_child(self, child):
        """Range of the child object contained in this timeline."""

        return self.tracks.range_of_child(child)

    def video_tracks(self):
        """
        This convenience method returns a list of the top-level video tracks in
        this timeline.
        """
        return [
            trck for trck
            in self.tracks
            if (isinstance(trck, track.Track) and
                trck.kind == track.TrackKind.Video)
        ]

    def audio_tracks(self):
        """
        This convenience method returns a list of the top-level audio tracks in
        this timeline.
        """
        return [
            trck for trck
            in self.tracks
            if (isinstance(trck, track.Track) and
                trck.kind == track.TrackKind.Audio)
        ]


def timeline_from_clips(clips):
    """Convenience for making a single track timeline from a list of clips."""

    trck = track.Track(children=clips)
    return Timeline(tracks=[trck])
