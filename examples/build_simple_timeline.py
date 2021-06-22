#!/usr/bin/env python

"""
Example of how to build a simple timeline given file names and frame lists.
"""

import opentimelineio as otio

FILE_LIST = [
    # first file starts at 0 and goes 100 frames
    (
        "fst.mov",
        otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 24),
            duration=otio.opentime.RationalTime(100, 24)
        )
    ),
    # second file starts 1 hour in and goes 300 frames (at 24)
    (
        "snd.mov",
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


def main():
    """main function for module"""

    # build the structure
    tl = otio.schema.Timeline(name="Example timeline")

    tr = otio.schema.Track(name="example track")
    tl.tracks.append(tr)

    # build the clips
    for i, (fname, available_range) in enumerate(FILE_LIST):
        ref = otio.schema.ExternalReference(
            target_url=fname,
            # available_range=available_range
        )

        cl = otio.schema.Clip(name="Clip{}".format(i + 1))
        cl.media_reference = ref
        tr.append(cl)

    otio.adapters.write_to_file(tl, "/var/tmp/example.otio")


if __name__ == '__main__':
    main()
