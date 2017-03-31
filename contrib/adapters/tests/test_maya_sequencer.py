""" unit tests for the maya sequencer adapter """

import os
import re
import tempfile
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(
    os.path.dirname(otio.__file__),
    "..",
    "tests",
    "sample_data"
)
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
BASELINE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.ma")

def filter_maya_file(contents):
    contents = re.sub('rename -uid ".*";', 'rename -uid "foo";', contents)
    return '\n'.join(
        l for l in contents.split('\n') if not l.startswith('//')
    )


@unittest.skipIf(
    "OTIO_MAYA_PYTHON_BIN" not in os.environ,
    "OTIO_MAYA_PYTHON_BIN not set, required for the maya adapter"
)
class MayaSequencerAdapterWriteTest(unittest.TestCase):
    def test_basic_maya_sequencer_write(self):
        self.maxDiff = None
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".ma", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(BASELINE_PATH) as fo:
            baseline_data = fo.read()

        self.assertMultiLineEqual(
            filter_maya_file(baseline_data),
            filter_maya_file(test_data)
        )
