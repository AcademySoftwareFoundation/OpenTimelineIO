#!/usr/bin/env python
#
# Copyright Contributors to the OpenTimelineIO project
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

import opentimelineio as otio
import sys

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
print("Flattening {} video tracks into one...".format(len(video_tracks)))
onetrack = otio.algorithms.flatten_stack(video_tracks)

# Now make a new empty Timeline and put that one Track into it
newtimeline = otio.schema.Timeline(name="{} Flattened".format(timeline.name))
newtimeline.tracks[:] = [onetrack]

# keep the audio track(s) as-is
newtimeline.tracks.extend(audio_tracks)

# ...and save it to disk.
print("Saving {} video tracks and {} audio tracks.".format(
    len(newtimeline.video_tracks()),
    len(newtimeline.audio_tracks())
))
otio.adapters.write_to_file(newtimeline, outputpath)
