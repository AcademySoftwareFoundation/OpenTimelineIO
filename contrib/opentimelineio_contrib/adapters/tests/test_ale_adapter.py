# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test the ALE adapter."""

# python
import os
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "sample.ale")
EXAMPLE2_PATH = os.path.join(SAMPLE_DATA_DIR, "sample2.ale")
EXAMPLE_CDL_PATH = os.path.join(SAMPLE_DATA_DIR, "sample_cdl.ale")
EXAMPLEUHD_PATH = os.path.join(SAMPLE_DATA_DIR, "sampleUHD.ale")


class ALEAdapterTest(unittest.TestCase):

    def test_ale_read(self):
        ale_path = EXAMPLE_PATH
        collection = otio.adapters.read_from_file(ale_path)
        self.assertTrue(collection is not None)
        self.assertEqual(type(collection), otio.schema.SerializableCollection)
        self.assertEqual(len(collection), 4)
        fps = float(collection.metadata.get("ALE").get("header").get("FPS"))
        self.assertEqual(fps, 24)
        self.assertEqual(
            [c.name for c in collection],
            ["test_017056", "test_017057", "test_017058", "Something"]
        )
        self.assertEqual(
            [c.source_range for c in collection],
            [
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:03", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:04", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:05", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:06", fps)
                )
            ]
        )

    def test_ale_read2(self):
        ale_path = EXAMPLE2_PATH
        collection = otio.adapters.read_from_file(ale_path)
        self.assertTrue(collection is not None)
        self.assertEqual(type(collection), otio.schema.SerializableCollection)
        self.assertEqual(len(collection), 2)
        fps = float(collection.metadata.get("ALE").get("header").get("FPS"))
        self.assertEqual(fps, 23.98)
        self.assertEqual(
            [c.name for c in collection],
            ["19A-1xa", "19A-2xa"]
        )
        self.assertEqual(
            [c.source_range for c in collection],
            [
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("04:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:46:16", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("04:00:46:16", fps),
                    otio.opentime.from_timecode("00:00:50:16", fps)
                )
            ]
        )

    def test_ale_read_cdl(self):
        ale_path = EXAMPLE_CDL_PATH
        collection = otio.adapters.read_from_file(ale_path)
        self.assertTrue(collection is not None)
        self.assertEqual(type(collection), otio.schema.SerializableCollection)
        self.assertEqual(len(collection), 4)
        fps = float(collection.metadata.get("ALE").get("header").get("FPS"))
        self.assertEqual(fps, 23.976)
        self.assertEqual([c.name for c in collection], [
            "A005_C010_0501J0", "A005_C010_0501J0", "A005_C009_0501A0",
            "A005_C010_0501J0"
        ])
        self.assertEqual([c.source_range for c in collection], [

            otio.opentime.TimeRange(
                otio.opentime.from_timecode("17:49:33:01", fps),
                otio.opentime.from_timecode("00:00:02:09", fps)),

            otio.opentime.TimeRange(
                otio.opentime.from_timecode("17:49:55:19", fps),
                otio.opentime.from_timecode("00:00:06:09", fps)),

            otio.opentime.TimeRange(
                otio.opentime.from_timecode("17:40:25:06", fps),
                otio.opentime.from_timecode("00:00:02:20", fps)),

            otio.opentime.TimeRange(
                otio.opentime.from_timecode("17:50:21:23", fps),
                otio.opentime.from_timecode("00:00:03:14", fps))
        ])

        # Slope, offset, and power values are of type _otio.AnyVector
        # So we have to convert them to lists otherwise
        # the comparison between those two types would fail

        # FIRST CLIP
        self.assertEqual(
            list(collection[0].metadata['cdl']['asc_sop']['slope']),
            [0.8714, 0.9334, 0.9947])
        self.assertEqual(
            list(collection[0].metadata['cdl']['asc_sop']['offset']),
            [-0.087, -0.0922, -0.0808])
        self.assertEqual(
            list(collection[0].metadata['cdl']['asc_sop']['power']),
            [0.9988, 1.0218, 1.0101])
        self.assertEqual(collection[0].metadata['cdl']['asc_sat'], 0.9)

        # SECOND CLIP
        self.assertEqual(
            list(collection[1].metadata['cdl']['asc_sop']['slope']),
            [0.8714, 0.9334, 0.9947])
        self.assertEqual(
            list(collection[1].metadata['cdl']['asc_sop']['offset']),
            [-0.087, -0.0922, -0.0808])
        self.assertEqual(
            list(collection[1].metadata['cdl']['asc_sop']['power']),
            [0.9988, 1.0218, 1.0101])
        self.assertEqual(collection[1].metadata['cdl']['asc_sat'], 0.9)

        # THIRD CLIP
        self.assertEqual(
            list(collection[2].metadata['cdl']['asc_sop']['slope']),
            [0.8604, 0.9252, 0.9755])
        self.assertEqual(
            list(collection[2].metadata['cdl']['asc_sop']['offset']),
            [-0.0735, -0.0813, -0.0737])
        self.assertEqual(
            list(collection[2].metadata['cdl']['asc_sop']['power']),
            [0.9988, 1.0218, 1.0101])
        self.assertEqual(collection[2].metadata['cdl']['asc_sat'], 0.9)

        # FOURTH CLIP
        self.assertEqual(
            list(collection[3].metadata['cdl']['asc_sop']['slope']),
            [0.8714, 0.9334, 0.9947])
        self.assertEqual(
            list(collection[3].metadata['cdl']['asc_sop']['offset']),
            [-0.087, -0.0922, -0.0808])
        self.assertEqual(
            list(collection[3].metadata['cdl']['asc_sop']['power']),
            [0.9988, 1.0218, 1.0101])
        self.assertEqual(collection[3].metadata['cdl']['asc_sat'], 0.9)

    def test_ale_uhd(self):
        ale_path = EXAMPLEUHD_PATH
        collection = otio.adapters.read_from_file(ale_path)
        frmt = str(collection.metadata.get("ALE").get("header").get("VIDEO_FORMAT"))
        self.assertEqual(frmt, "CUSTOM")

    def test_ale_add_format(self):

        # adds a clip to the supplied timeline, sets the clips "Image Size"
        # metadata and then rountrips the ALE verifying the supplied format is detected
        def add_then_check(timeline, size, expected_format):
            cl = otio.schema.Clip(
                metadata={'ALE': {'Image Size': size}},
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0, 23.976),
                    duration=otio.opentime.RationalTime(48, 23.976)
                )
            )
            timeline.tracks[0].extend([cl])
            collection = otio.adapters.read_from_string(
                otio.adapters.write_to_string(
                    timeline,
                    adapter_name='ale'
                ),
                adapter_name="ale"
            )
            ale_meta = collection.metadata.get('ALE')
            vid_format = str(ale_meta.get('header').get('VIDEO_FORMAT'))
            self.assertEqual(vid_format, expected_format)

        track = otio.schema.Track()
        tl = otio.schema.Timeline("Add Format", tracks=[track])

        # add multiple clips with various resolutions,
        # we want the ALE to return a project format
        # that is compatible with the largest resolution

        add_then_check(tl, '720 x 486', 'NTSC')
        add_then_check(tl, '720 x 576', 'PAL')
        add_then_check(tl, '1280x 720', '720')
        add_then_check(tl, '1920x1080', '1080')
        add_then_check(tl, '2048x1080', 'CUSTOM')
        add_then_check(tl, '4096x2304', 'CUSTOM')

    def test_ale_roundtrip(self):
        ale_path = EXAMPLE_PATH

        with open(ale_path) as fi:
            original = fi.read()
            collection = otio.adapters.read_from_string(original, "ale")
            output = otio.adapters.write_to_string(collection, "ale")
            self.maxDiff = None
            self.assertMultiLineEqual(original, output)


if __name__ == '__main__':
    unittest.main()
