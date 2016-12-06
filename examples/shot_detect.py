#!/usr/bin/env python

"""
Example OTIO script that generates an OTIO from a single quicktime by using
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
        '-d',
        '--dryrun',
        action="store_true",
        default=False,
        help="Print ffprobe command instead of running it."
    )
    return parser.parse_args()


_MEDIA_RANGE_MAP = {}


def _media_start_end_of(media_path):
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
        otio.opentime.RationalTime(0, 1),
        otio.opentime.RationalTime(float(out), 1)
    )

    _MEDIA_RANGE_MAP[media_path] = available_range

    return available_range


def _timeline_with_breaks(name, full_path, dryrun=False):

    timeline = otio.schema.Timeline()
    timeline.name = name
    track = otio.schema.Sequence()
    track.name = name
    timeline.tracks.append(track)

    out = _ffprobe_output(name, full_path, dryrun)

    if dryrun:
        return

    # saving time in base 1.0 to demonstrate that you can
    playhead = otio.opentime.RationalTime(0, 1.0)
    shot_index = 1
    for line in out.split("\n"):
        info = dict(re.findall(r'(\w+)=(\d+\.\d*)', line))

        end_time_in_seconds = info.get('pkt_pts_time')

        if end_time_in_seconds is None:
            continue

        start_time = playhead

        # Note: if you wanted to snap to a particular frame rate, you would do
        # it here.
        end_time = otio.opentime.RationalTime(
            float(end_time_in_seconds),
            1.0
        )

        clip = otio.schema.Clip()
        clip.name = "shot {}".format(shot_index)
        clip.source_range = otio.opentime.range_from_start_end_time(
            start_time,
            end_time
        )

        available_range = _media_start_end_of(full_path)

        clip.media_reference = otio.media_reference.External(
            target_url="file://" + full_path,
            available_range=available_range
        )
        track.append(clip)

        playhead = end_time
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
    try:
        out, err = proc.communicate()
    except:
        print out
        print err
        raise FFProbeFailedError(
            "FFProbe Failed with error: {}, output: {}".format(
                err, out
            )
        )


def _ffprobe_output(name, full_path, dryrun=False):
    """ Run ffprobe and return resulting output """

    print "Scanning {} for shot breaks...".format(name)
    cmd = [
        "ffprobe",
        "-show_frames",
        "-of",
        "compact=p=0",
        "-f",
        "lavfi",
        "movie={},select=gt(scene\\,.1)".format(full_path)
    ]

    if dryrun:
        print " ".join(cmd)
        return

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

    return out


def main():
    args = parse_args()

    _verify_ffprobe()

    for full_path in args.filepath:
        name = os.path.basename(full_path)
        new_tl = _timeline_with_breaks(name, full_path, args.dryrun)

        if args.dryrun:
            continue

        otio_filename = os.path.splitext(name)[0] + ".otio"
        otio.adapters.write_to_file(new_tl, otio_filename)
        print "SAVED: {} with {} clips.".format(
            otio_filename,
            len(new_tl.tracks[0])
        )


if __name__ == '__main__':
    main()
