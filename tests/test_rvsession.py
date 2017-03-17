""" unit tests for the rv session file adapter """

import os
import tempfile
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
BASELINE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.rv")


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

        self.assertMultiLineEqual(baseline_data, test_data)
