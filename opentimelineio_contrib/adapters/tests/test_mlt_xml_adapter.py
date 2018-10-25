# python
import os
#import tempfile
import unittest
#import collections
#from xml.etree import cElementTree

import opentimelineio as otio
#from opentimelineio.exceptions import CannotComputeAvailableRangeError

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
MLT_XML_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "melt_xml.mlt")


class TestMLTXMLAdapter(unittest.TestCase):
    def create_otio_timeline(self, videotracks=1, audiotracks=1):
        timeline = otio.schema.Timeline()
        for tracknum in range(videotracks):
            track = otio.schema.VideoTrack()
            timeline.tracks.append(track)

        for tracknum in audiotracks:
            track = otio.schema.AudioTrack()
            timeline.tracks.append(track)


        fade_in = otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=otio.opentime.RationalTime(0, fps),
            out_offset=otio.opentime.RationalTime(25, fps)
        )

        fade_out = otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=otio.opentime.RationalTime(25, fps),
            out_offset=otio.opentime.RationalTime(0, fps)
        )

        gap_1 = otio.schema.Gap(
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, fps),
                duration=otio.opentime.RationalTime(50, fps)
            )
        )

        gap_2 = otio.schema.Gap(
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, fps),
                duration=otio.opentime.RationalTime(50, fps)
            )
        )

        online_clip_1 = otio.schema.Clip(
            name='onloneclip1',
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(100, fps),
                duration=otio.opentime.RationalTime(300, fps)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url='/mnt/data/video/bernhard_2010_01.mov',
                available_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, fps),
                    duration=otio.opentime.RationalTime(16870, fps)
                )
            )
        )

        online_clip_2 = otio.schema.Clip(
            name='onlineclip2',
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(2500, fps),
                duration=otio.opentime.RationalTime(100, fps)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url='/mnt/data/video/bernhard_2010_02.mov',
                available_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, fps),
                    duration=otio.opentime.RationalTime(35480, fps)
                )
            )
        )

        offline_clip_1 = otio.schema.Clip(
            name='offloneclip1',
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(100, fps),
                duration=otio.opentime.RationalTime(300, fps)
            )
        )

        dissolve_1 = otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=otio.opentime.RationalTime(25, fps),
            out_offset=otio.opentime.RationalTime(25, fps)
        )

        track.append(gap_1)
        track.append(fade_in)
        track.append(online_clip_1)
        track.append(dissolve_1)
        track.append(online_clip_2)
        track.append(fade_out)
        track.append(gap_2)

        return timeline

    def test_otio_in_mem_to_mlt(self):
        timeline = otio.schema.Timeline()
        track = otio.schema.Track()
        timeline.tracks.append(track)

        clip_1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(1000, 25),
                duration=otio.opentime.RationalTime(100, 25)
                ),
            media_reference=otio.schema.ExternalReference(
                target_url='/mnt/data/video/bernhard_2010_01.mov',
                available_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, 25),
                    duration=otio.opentime.RationalTime(39956, 25)
                    )
                )
            )

        clip_2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(1000, 25),
                duration=otio.opentime.RationalTime(100, 25)
                ),
            media_reference=otio.schema.ExternalReference(
                target_url='/mnt/data/video/bernhard_2010_02.mov',
                available_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, 25),
                    duration=otio.opentime.RationalTime(79912, 25)
                    )
                )
            )

        dissolve_1 = otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=otio.opentime.RationalTime(25, 25),
            out_offset=otio.opentime.RationalTime(25, 25)
            )

        track.append(clip_1)
        track.append(dissolve_1)
        track.append(clip_2)

        otio.adapters.write_to_string(timeline)

