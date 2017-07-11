""" unit tests for the rv session file adapter """

import os
import tempfile
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(
    os.path.dirname(otio.__file__),"..","tests", "sample_data"
)
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
TRANSITION_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "transition_test.otio")
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
BASELINE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.rv")
BASELINE_TRANSITION_PATH = os.path.join(SAMPLE_DATA_DIR, "transition_test.rv")


@unittest.skipIf(
    "OTIO_RV_PYTHON_LIB" not in os.environ or
    "OTIO_RV_PYTHON_BIN" not in os.environ,
    "OTIO_RV_PYTHON_BIN or OTIO_RV_PYTHON_LIB not set."
)
class RVSessionAdapterReadTest(unittest.TestCase):
    def test_basic_rvsession_read(self):
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".rv", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(BASELINE_PATH) as fo:
            baseline_data = fo.read()

        self.maxDiff = None
        self.assertMultiLineEqual(baseline_data, test_data)

    def test_transition_rvsession_read(self):
        timeline = otio.adapters.read_from_file(TRANSITION_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".rv", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(BASELINE_TRANSITION_PATH) as fo:
            baseline_data = fo.read()

        self.maxDiff = None
        self.assertMultiLineEqual(baseline_data, test_data)

    def test_transition_rvsession_covers_entire_shots(self):
        # SETUP
        timeline = otio.adapters.read_from_string("""{
            "OTIO_SCHEMA": "Timeline.1",
            "tracks": {
                "OTIO_SCHEMA": "Stack.1",
                "children": [{
                    "OTIO_SCHEMA": "Sequence.1",
                    "kind": "Video",
                    "children": [{
                        "OTIO_SCHEMA": "Gap.1",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": { "OTIO_SCHEMA": "RationalTime.1", "rate": 24.0, "value": 10.0 },
                            "start_time": { "OTIO_SCHEMA": "RationalTime.1", "rate": 24.0, "value": 0.0 }
                        }
                    }, {
                        "OTIO_SCHEMA": "Transition.1",
                        "transition_type": "SMPTE_Dissolve",
                        "in_offset": { "OTIO_SCHEMA": "RationalTime.1", "rate": 24.0, "value": 10.0 },
                        "out_offset": { "OTIO_SCHEMA": "RationalTime.1", "rate": 24.0, "value": 10.0 }
                    }, {
                        "OTIO_SCHEMA": "Clip.1",
                        "media_reference": {
                            "OTIO_SCHEMA": "MissingReference.1"
                        },
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": { "OTIO_SCHEMA": "RationalTime.1", "rate": 24.0, "value": 10.0 },
                            "start_time": { "OTIO_SCHEMA": "RationalTime.1", "rate": 24.0, "value": 10.0 }
                        }
                    }]
                }]
            }
        }""", "otio_json")
        tmp_path = tempfile.mkstemp(suffix=".rv", text=True)[1]

        # EXERCISE
        otio.adapters.write_to_file(timeline, tmp_path)

        # VERIFY
        with open(tmp_path, "r") as f:
            rv_session = f.read()
            self.assertEqual(rv_session.count('movie = "blank'), 1)
            self.assertEqual(rv_session.count('movie = "smpte'), 1)
