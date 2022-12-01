# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the maya sequencer adapter"""

import os
import tempfile
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.otio")
BASELINE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.ma")
SETATTR_TO_CHECK = (".ef", ".sf", ".sn", ".se", ".ssf")


def filter_maya_file(contents):
    return '\n'.join(
        line for line in contents.split('\n')
        if (
            line.strip().startswith('setAttr') and
            any(a in line for a in SETATTR_TO_CHECK) or
            (
                not line.startswith('//') and
                not line.startswith('requires') and
                not line.startswith('fileInfo') and
                not line.startswith('currentUnit') and
                not line.strip().startswith('rename') and
                not line.strip().startswith('select') and
                not line.strip().startswith('setAttr') and
                not line.strip().startswith('0') and
                not line.strip().startswith('1')
            )
        )
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


if __name__ == '__main__':
    unittest.main()
