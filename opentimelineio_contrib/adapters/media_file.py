#
# Copyright 2018 Pixar Animation Studios
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

__doc__ = """ Media file read-only adapter. This adapter just wraps a video
or audio file in a single-clip timeline with the correct duration. """


import os
import subprocess
import re
import json

import opentimelineio as otio


def get_metadata(filepath):
    proc = subprocess.Popen(
        [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=os.environ
    )
    out, err = proc.communicate()
    metadata = {}

    metadata = json.loads(out)

    return metadata


def guess_media_range(metadata, default_fps):

    format = metadata.get('format', {})
    streams = metadata.get('streams', [])

    time_base_str = None
    duration_str = None
    start_time_str = None
    timecode_str = None
    fps = default_fps

    # try to get duration and start_time from the top-level first
    duration_str = format.get('duration')
    start_time_str = format.get('start_time')

    # now go looking in the streams to get more info
    for stream in streams:
        codec_type = stream.get('codec_type')
        tags = stream.get('tags', {})

        if codec_type == 'video':
            # trust this over anything from non-video tracks
            time_base_str = stream.get('time_base', time_base_str)
            timecode_str = tags.get('timecode', timecode_str)

        elif codec_type == 'audio':
            # use this only if we didn't get info from other tracks
            if not time_base_str and stream.get('time_base'):
                time_base_str = stream.get('time_base')

            # use this only if we didn't get info from other tracks
            if not timecode_str and tags.get('timecode'):
                timecode_str = tags.get('timecode')

        else:
            # don't pull metadata from non-audio/video tracks
            pass

    if time_base_str:
        numerator, denominator = time_base_str.split('/')
        if numerator == '1':
            fps = int(denominator)
        else:
            fps = float(denominator) / float(numerator)

    if duration_str:
        duration = otio.opentime.from_seconds(float(duration_str))
    else:
        duration = otio.opentime.RationalTime()

    if start_time_str:
        start = otio.opentime.from_seconds(float(start_time_str))
    else:
        start = otio.opentime.RationalTime()

    if timecode_str:
        # overwrite start with timecode if we have it
        start = otio.opentime.from_timecode(timecode_str, fps)

    return otio.opentime.TimeRange(
        start_time=start.rescaled_to(fps),
        duration=duration.rescaled_to(fps)
    )


def guess_track_type(metadata):

    streams = metadata.get('streams', [])
    has_audio = False
    has_video = False

    for stream in streams:
        codec_type = stream.get('codec_type')

        if codec_type == 'video':
            has_video = True

        elif codec_type == 'audio':
            has_audio = True

    if has_video:
        return otio.schema.TrackKind.Video
    elif has_audio:
        return otio.schema.TrackKind.Audio
    else:
        return None


def read_from_file(filepath, default_fps=24):

    if not os.path.exists(filepath):
        raise otio.exceptions.CouldNotReadFileError(
            "File not found: {}".format(filepath)
        )

    timeline = otio.schema.Timeline()
    timeline.name = os.path.splitext(os.path.basename(filepath))[0]
    clip = otio.schema.Clip()
    clip.name = os.path.basename(filepath)
    clip.media_reference = otio.schema.ExternalReference(
        target_url=filepath,
    )
    metadata = get_metadata(filepath)
    clip.media_reference.available_range = guess_media_range(
        metadata, default_fps
    )
    clip.media_reference.metadata['ffprobe'] = metadata
    track = otio.schema.Track()
    track.kind = guess_track_type(metadata)

    track.append(clip)
    timeline.tracks.append(track)
    return timeline
