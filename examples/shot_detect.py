#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Example OTIO script that generates an OTIO from a single quicktime by using
ffprobe to detect shot breaks.
"""

import subprocess
import re
import os
import argparse

import opentimelineio as otio


class ShotDetectError(Exception):
    pass


class FFProbeFailedError(ShotDetectError):
    pass


"""
@NOTE EXAMPLE LINE from ffprobe:
media_type=video|stream_index=0|key_frame=1|pkt_pts=385875|pkt_pts_time=128.753754|pkt_dts=385875|pkt_dts_time=128.753754|best_effort_timestamp=385875|best_effort_timestamp_time=128.753754|pkt_duration=125|pkt_duration_time=0.041708|pkt_pos=160853826|pkt_size=4608000|width=1920|height=800|pix_fmt=rgb24|sample_aspect_ratio=1:1|pict_type=I|coded_picture_number=0|display_picture_number=0|interlaced_frame=0|top_field_first=0|repeat_pict=0|tag:lavfi.scene_score=0.421988
"""


def parse_args():
    """ parse arguments out of sys.argv """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'filepath',
        type=str,
        nargs='+',
        help='Files to look for splits in.'
    )
    parser.add_argument(
        '-r',
        '--reference-clip',
        action='store_true',
        default=False,
        help="instead of detecting shots, write a timeline with a single clip "
        "referencing the file."
    )
    parser.add_argument(
        '-d',
        '--dryrun',
        action="store_true",
        default=False,
        help="Print ffprobe command instead of running it."
    )
    return parser.parse_args()


_MEDIA_RANGE_MAP = {}


def _media_start_end_of(media_path, fps):
    if media_path in _MEDIA_RANGE_MAP:
        return _MEDIA_RANGE_MAP[media_path]

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        media_path
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise FFProbeFailedError(
            "FFProbe Failed with error: {}, output: {}".format(
                err, out
            )
        )

    available_range = otio.opentime.TimeRange(
        otio.opentime.RationalTime(0, 1).rescaled_to(fps),
        otio.opentime.RationalTime(float(out), 1).rescaled_to(fps)
    )

    _MEDIA_RANGE_MAP[media_path] = available_range

    return available_range


def _timeline_with_single_clip(name, full_path, dryrun=False):
    timeline = otio.schema.Timeline()
    timeline.name = name
    track = otio.schema.Track()
    track.name = name
    timeline.tracks.append(track)

    fps = _ffprobe_fps(name, full_path, dryrun)
    available_range = _media_start_end_of(full_path, fps)

    media_reference = otio.schema.ExternalReference(
        target_url="file://" + full_path,
        available_range=available_range
    )

    if dryrun:
        return

    clip = otio.schema.Clip(name=name)
    clip.media_reference = media_reference
    track.append(clip)
    return timeline


def _timeline_with_breaks(name, full_path, dryrun=False):

    timeline = otio.schema.Timeline()
    timeline.name = name
    track = otio.schema.Track()
    track.name = name
    timeline.tracks.append(track)

    fps = _ffprobe_fps(name, full_path, dryrun)

    out, _ = _ffprobe_output(name, full_path, dryrun)

    if dryrun:
        return ("", "")

    # saving time in base 1.0 to demonstrate that you can
    playhead = otio.opentime.RationalTime(0, 1.0)
    shot_index = 1

    for line in out.split("\n"):
        info = dict(re.findall(r'(\w+)=(\d+\.\d*)', line))

        end_time_in_seconds = info.get('pkt_pts_time')

        if end_time_in_seconds is None:
            continue

        start_time = playhead.rescaled_to(fps)

        # Note: if you wanted to snap to a particular frame rate, you would do
        # it here.
        end_time_exclusive = otio.opentime.RationalTime(
            float(end_time_in_seconds),
            1.0
        ).rescaled_to(fps)

        clip = otio.schema.Clip()
        clip.name = f"shot {shot_index}"
        clip.source_range = otio.opentime.range_from_start_end_time(
            start_time,
            end_time_exclusive
        )

        available_range = _media_start_end_of(full_path, fps)

        clip.media_reference = otio.schema.ExternalReference(
            target_url="file://" + full_path,
            available_range=available_range
        )
        track.append(clip)

        playhead = end_time_exclusive
        shot_index += 1

    return timeline


def _verify_ffprobe():
    cmd = [
        "ffprobe",
        "-h"
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    except OSError:
        raise FFProbeFailedError(
            "Unable to run ffprobe command line tool. It might not be in your "
            "path, or you might need to get it from https://www.ffmpeg.org"
        )
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise FFProbeFailedError(
            "FFProbe Failed with error: {}, output: {}".format(
                err, out
            )
        )


def _ffprobe_fps(name, full_path, dryrun=False):
    """Parse the framerate from the file using ffprobe."""

    _, err = _ffprobe_output(
        name,
        full_path,
        dryrun,
        arguments=[f"{full_path}"],
        message="framerate"
    )

    if dryrun:
        return 1.0

    err_str = err.decode("utf-8")

    for line in err_str.split('\n'):
        if not ("Stream" in line and "Video" in line):
            continue

        bits = line.split(",")
        for bit in bits:
            if "fps" not in bit:
                continue
            return float([b for b in bit.split(" ") if b][0])

    # fallback FPS is just 1.0 -- seconds
    return 1.0


def _ffprobe_output(
    name,
    full_path,
    dryrun=False,
    arguments=None,
    message="shot breaks"
):
    """ Run ffprobe and return resulting output """

    arguments = arguments or [
        "-show_frames",
        "-of",
        "compact=p=0",
        "-f",
        "lavfi",
        f"movie={full_path},select=gt(scene\\,.1)"
    ]

    if message:
        print(f"Scanning {name} for {message}...")

    cmd = ["ffprobe"] + arguments

    if dryrun:
        print(" ".join(cmd))
        return ("", "")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise FFProbeFailedError(
            "FFProbe Failed with error: {}, output: {}".format(
                err, out
            )
        )

    return out, err


def main():
    args = parse_args()

    # make sure that ffprobe exists before continuing
    _verify_ffprobe()

    for full_path in args.filepath:
        name = os.path.basename(full_path)

        if args.reference_clip:
            new_tl = _timeline_with_single_clip(name, full_path, args.dryrun)
        else:
            new_tl = _timeline_with_breaks(name, full_path, args.dryrun)

        if args.dryrun:
            continue

        # @TODO: this should be an argument
        otio_filename = os.path.splitext(name)[0] + ".otio"
        otio.adapters.write_to_file(new_tl, otio_filename)
        print(
            "SAVED: {} with {} clips.".format(
                otio_filename,
                len(new_tl.tracks[0])
            )
        )


if __name__ == '__main__':
    main()
