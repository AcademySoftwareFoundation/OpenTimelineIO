# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os
import subprocess
import sys
import unittest
import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
from opentimelineio_contrib.adapters.fcpx_xml import format_name

try:
    # Python 3.3 forward includes the mock module
    from unittest import mock
    could_import_mock = True
except ImportError:
    # Fallback for older python (not included in standard library)
    try:
        from unittest import mock
        could_import_mock = True
    except ImportError:
        # Mock appears to not be installed
        could_import_mock = False

SAMPLE_LIBRARY_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_library.fcpxml"
)
SAMPLE_PROJECT_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_project.fcpxml"
)
SAMPLE_EVENT_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_event.fcpxml"
)
SAMPLE_CLIPS_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_clips.fcpxml"
)


class AdaptersFcpXXmlTest(unittest.TestCase, otio_test_utils.OTIOAssertions):
    """
    The test class for the FCP X XML adapter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_library_roundtrip(self):
        container = otio.adapters.read_from_file(SAMPLE_LIBRARY_XML)
        timeline = next(
            container.each_child(descended_from_type=otio.schema.Timeline)
        )

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)

    def test_event_roundtrip(self):
        container = otio.adapters.read_from_file(SAMPLE_EVENT_XML)
        timeline = next(
            container.each_child(descended_from_type=otio.schema.Timeline)
        )

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)

    def test_project_roundtrip(self):
        timeline = otio.adapters.read_from_file(SAMPLE_PROJECT_XML)

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(timeline, new_timeline)

    def test_clips_roundtrip(self):
        container = otio.adapters.read_from_file(SAMPLE_CLIPS_XML)
        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)

    @unittest.skipIf(
        not could_import_mock,
        "mock module not found. Install mock from pypi or use python >= 3.3."
    )
    def test_format_name(self):
        rvalue = subprocess.check_output([sys.executable, '-c', 'print("640x360")'])
        with mock.patch.object(subprocess, 'check_output', return_value=rvalue):
            with mock.patch.object(os.path, 'exists', return_value=True):
                self.assertEqual(format_name(
                    25, "file:///dummy.me"), 'FFVideoFormat640x360p25')


if __name__ == '__main__':
    unittest.main()
