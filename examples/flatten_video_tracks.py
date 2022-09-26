#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import opentimelineio as otio
import sys
import copy

inputpath, outputpath = sys.argv[1:]

# Read the file
timeline = otio.adapters.read_from_file(inputpath)
video_tracks = timeline.video_tracks()
audio_tracks = timeline.audio_tracks()

print("Read {} video tracks and {} audio tracks.".format(
    len(video_tracks),
    len(audio_tracks)
))

# Take just the video tracks - and flatten them into one.
# This will trim away any overlapping segments, collapsing everything
# into a single track.
print(f"Flattening {len(video_tracks)} video tracks into one...")
onetrack = otio.algorithms.flatten_stack(video_tracks)

# Now make a new empty Timeline and put that one Track into it
newtimeline = otio.schema.Timeline(name=f"{timeline.name} Flattened")
newtimeline.tracks[:] = [onetrack]

# keep the audio track(s) as-is
newtimeline.tracks.extend(copy.deepcopy(audio_tracks))

# ...and save it to disk.
print("Saving {} video tracks and {} audio tracks.".format(
    len(newtimeline.video_tracks()),
    len(newtimeline.audio_tracks())
))
otio.adapters.write_to_file(newtimeline, outputpath)
