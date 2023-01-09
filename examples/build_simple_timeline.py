#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """
Generate a simple timeline from scratch and write it to the specified path.
"""

import argparse

import opentimelineio as otio

FILE_LIST = [
    # first file starts at 0 and goes 100 frames
    (
        "first.mov",
        otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 24),
            duration=otio.opentime.RationalTime(100, 24)
        )
    ),
    # second file starts 1 hour in and goes 300 frames (at 24)
    (
        "second.mov",
        otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(86400, 24),
            duration=otio.opentime.RationalTime(300, 24)
        )
    ),
    # third file starts at 0 and goes 400 frames @ 24)
    (
        "thrd.mov",
        otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 24),
            duration=otio.opentime.RationalTime(400, 24)
        )
    )
]


def parse_args():
    """ parse arguments out of sys.argv """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'filepath',
        type=str,
        help=(
            'Path to write example file to.  Example: /var/tmp/example.otio or '
            'c:\\example.xml'
        )
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # build the structure
    tl = otio.schema.Timeline(name="Example timeline")

    tr = otio.schema.Track(name="example track")
    tl.tracks.append(tr)

    # build the clips
    for i, (fname, available_range_from_list) in enumerate(FILE_LIST):
        ref = otio.schema.ExternalReference(
            target_url=fname,
            # available range is the content available for editing
            available_range=available_range_from_list
        )

        # attach the reference to the clip
        cl = otio.schema.Clip(
            name=f"Clip{i + 1}",
            media_reference=ref,

            # the source range represents the range of the media that is being
            # 'cut into' the clip. This is an artificial example, so its just
            # a bit shorter than the available range.
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(
                    available_range_from_list.start_time.value + 10,
                    available_range_from_list.start_time.rate
                ),
                duration=otio.opentime.RationalTime(
                    available_range_from_list.duration.value - 20,
                    available_range_from_list.duration.rate
                ),
            )
        )

        # put the clip into the track
        tr.append(cl)

    # write the file to disk
    otio.adapters.write_to_file(tl, args.filepath)


if __name__ == '__main__':
    main()
