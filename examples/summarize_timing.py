#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Example OTIO script that reads a timeline and then prints a summary
of the video clips found, including re-timing effects on each one.
"""

import sys
import opentimelineio as otio


def _summarize_effects(item):
    if hasattr(item, "effects"):
        for effect in item.effects:
            if isinstance(effect, otio.schema.FreezeFrame):
                print(
                    "Effect: Freeze Frame"
                )
            elif isinstance(effect, otio.schema.LinearTimeWarp):
                print(
                    "Effect: Linear Time Warp ({}%)".format(
                        effect.time_scalar * 100.0
                    )
                )
            else:
                print(
                    "Effect: {} ({})".format(
                        effect.name,
                        str(type(effect))
                    )
                )


def _summarize_range(label, time_range):
    if time_range is None:
        print(f"\t{label}: None")
    else:
        print(
            "\t{}: {} - {} (Duration: {})".format(
                label,
                otio.opentime.to_timecode(
                    time_range.start_time
                ),
                otio.opentime.to_timecode(
                    time_range.end_time_exclusive()
                ),
                otio.opentime.to_timecode(time_range.duration)
            )
        )


def _summarize_timeline(timeline):
    # Here we iterate over each video track, and then just the top-level
    # items in each track. If you want to traverse the whole nested structure
    # then you can use: for item in timeline.children_if()
    # or just clips via: for clip in timeline.clip_if()
    # See also: https://opentimelineio.readthedocs.io/en/latest/tutorials/otio-timeline-structure.html  # noqa
    for track in timeline.video_tracks():
        print(
            "Track: {}\n\tKind: {}\n\tDuration: {}".format(
                track.name,
                track.kind,
                track.duration()
            )
        )
        _summarize_effects(track)

        for item in track:
            if isinstance(item, otio.schema.Clip):
                clip = item
                print(f"Clip: {clip.name}")
                # See the documentation to understand the difference
                # between each of these ranges:
                # https://opentimelineio.readthedocs.io/en/latest/tutorials/time-ranges.html
                _summarize_range("  Trimmed Range", clip.trimmed_range())
                _summarize_range("  Visible Range", clip.visible_range())
                _summarize_range("Available Range", clip.available_range())

            elif isinstance(item, otio.schema.Gap):
                continue

            elif isinstance(item, otio.schema.Transition):
                transition = item
                print(
                    "Transition: {}\n\tDuration: {}".format(
                        transition.transition_type,
                        otio.opentime.to_timecode(transition.duration())
                    )
                )

            elif isinstance(item, otio.core.Composition):
                composition = item
                print(
                    "Nested Composition: {}\n\tDuration: {}".format(
                        composition.name,
                        otio.opentime.to_timecode(composition.duration())
                    )
                )

            else:
                print(
                    "Other: {} ({})\n\tDuration: {}".format(
                        item.name,
                        str(type(item)),
                        otio.opentime.to_timecode(item.duration())
                    )
                )

            _summarize_effects(item)


def main():
    for filename in sys.argv[1:]:

        timeline = otio.adapters.read_from_file(filename)
        _summarize_timeline(timeline)


if __name__ == '__main__':
    main()
