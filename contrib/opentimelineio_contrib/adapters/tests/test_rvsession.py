# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the rv session file adapter"""

import os
import tempfile
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
TRANSITION_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "transition_test.otio")
BASELINE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.rv")
BASELINE_TRANSITION_PATH = os.path.join(SAMPLE_DATA_DIR, "transition_test.rv")
METADATA_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "rv_metadata.otio")
METADATA_BASELINE_PATH = os.path.join(SAMPLE_DATA_DIR, "rv_metadata.rv")
IMAGE_SEQUENCE_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "image_sequence_example.otio"
)


SAMPLE_DATA = """{
    "OTIO_SCHEMA": "Timeline.1",
    "tracks": {
        "OTIO_SCHEMA": "Stack.1",
        "children": [{
            "OTIO_SCHEMA": "Track.1",
            "kind": "Video",
            "children": [{
                "OTIO_SCHEMA": "Gap.1",
                "source_range": {
                    "OTIO_SCHEMA": "TimeRange.1",
                    "duration": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 24.0, "value": 10.0
                },
                "start_time": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 24.0, "value": 0.0
                }
                }
            },
            {
                "OTIO_SCHEMA": "Transition.1",
                "transition_type": "SMPTE_Dissolve",
                "in_offset": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 24.0, "value": 10.0
                },
                "out_offset": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 24.0, "value": 10.0
                }
            },
            {
                "OTIO_SCHEMA": "Clip.1",
                "media_reference": {
                    "OTIO_SCHEMA": "MissingReference.1"
                },
                "source_range": {
                    "OTIO_SCHEMA": "TimeRange.1",
                    "duration": {
                        "OTIO_SCHEMA": "RationalTime.1",
                        "rate": 24.0, "value": 10.0
                    },
                    "start_time": {
                        "OTIO_SCHEMA": "RationalTime.1",
                        "rate": 24.0, "value": 10.0
                    }
                }
            }]
        }]
    }
}"""


AUDIO_VIDEO_SAMPLE_DATA = """{
    "OTIO_SCHEMA": "Timeline.1",
    "metadata": {},
    "name": null,
    "tracks": {
        "OTIO_SCHEMA": "Stack.1",
        "children": [
            {
                "OTIO_SCHEMA": "Track.1",
                "children": [
                    {
                        "OTIO_SCHEMA": "Clip.1",
                        "effects": [],
                        "markers": [],
                        "media_reference": {
                            "OTIO_SCHEMA": "ExternalReference.1",
                            "available_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 25,
                                    "value": 67
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 25,
                                    "value": 0
                                }
                            },
                            "metadata": {},
                            "name": null,
                            "target_url": "/path/to/video.mov"
                        },
                        "metadata": {},
                        "name": "plyblast",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 25,
                                "value": 67
                            },
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 25,
                                "value": 54
                            }
                        }
                    }
                ],
                "effects": [],
                "kind": "Video",
                "markers": [],
                "metadata": {},
                "name": "v1",
                "source_range": null
            },
            {
                "OTIO_SCHEMA": "Track.1",
                "children": [
                    {
                        "OTIO_SCHEMA": "Clip.1",
                        "effects": [],
                        "markers": [],
                        "media_reference": {
                            "OTIO_SCHEMA": "ExternalReference.1",
                            "available_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 25,
                                    "value": 500
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 25,
                                    "value": 0
                                }
                            },
                            "metadata": {},
                            "name": null,
                            "target_url": "/path/to/audio.wav"
                        },
                        "metadata": {},
                        "name": "sound",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 25,
                                "value": 67
                            },
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 25,
                                "value": 54
                            }
                        }
                    }
                ],
                "effects": [],
                "kind": "Audio",
                "markers": [],
                "metadata": {},
                "name": "a1",
                "source_range": null
            }
        ],
        "effects": [],
        "markers": [],
        "metadata": {},
        "name": "tracks",
        "source_range": null
    }
}"""


NESTED_STACK_SAMPLE_DATA = """{
    "OTIO_SCHEMA": "Timeline.1",
    "metadata": {},
    "name": "My Timeline",
    "tracks": {
        "OTIO_SCHEMA": "Stack.1",
        "children": [
            {
                "OTIO_SCHEMA": "Track.1",
                "children": [
                    {
                        "OTIO_SCHEMA": "Clip.1",
                        "effects": [],
                        "markers": [],
                        "media_reference": {
                            "OTIO_SCHEMA": "ExternalReference.1",
                            "available_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 238
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 0
                                }
                            },
                            "metadata": {},
                            "target_url": "/path/to/some/video.mov"
                        },
                        "metadata": {},
                        "name": "Normal Clip 1",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 238
                            },
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 135
                            }
                        }
                    },
                    {
                        "OTIO_SCHEMA": "Stack.1",
                        "children": [
                            {
                                "OTIO_SCHEMA": "Clip.1",
                                "effects": [],
                                "markers": [],
                                "media_reference": {
                                    "OTIO_SCHEMA": "ExternalReference.1",
                                    "available_range": {
                                        "OTIO_SCHEMA": "TimeRange.1",
                                        "duration": {
                                            "OTIO_SCHEMA": "RationalTime.1",
                                            "rate": 24,
                                            "value": 238
                                        },
                                        "start_time": {
                                            "OTIO_SCHEMA": "RationalTime.1",
                                            "rate": 24,
                                            "value": 0
                                        }
                                    },
                                    "metadata": {},
                                    "target_url": "/path/to/some/video.mov"
                                },
                                "metadata": {},
                                "name": "Clip Inside A Stack 1",
                                "source_range": {
                                    "OTIO_SCHEMA": "TimeRange.1",
                                    "duration": {
                                        "OTIO_SCHEMA": "RationalTime.1",
                                        "rate": 24,
                                        "value": 37
                                    },
                                    "start_time": {
                                        "OTIO_SCHEMA": "RationalTime.1",
                                        "rate": 24,
                                        "value": 373
                                    }
                                }
                            }
                        ],
                        "effects": [],
                        "markers": [],
                        "metadata": {},
                        "name": "Nested Stack 1",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 31
                            },
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 0
                            }
                        }
                    }
                ],
                "effects": [],
                "kind": "Video",
                "markers": [],
                "metadata": {},
                "name": "Top Level Track",
                "source_range": null
            },
            {
                "OTIO_SCHEMA": "Track.1",
                "children": [
                    {
                        "OTIO_SCHEMA": "Clip.1",
                        "effects": [],
                        "markers": [],
                        "media_reference": {
                            "OTIO_SCHEMA": "ExternalReference.1",
                            "available_range": {
                                "OTIO_SCHEMA": "TimeRange.1",
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 238
                                },
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1",
                                    "rate": 24,
                                    "value": 0
                                }
                            },
                            "metadata": {},
                            "target_url": "/path/to/some/audio.wav"
                        },
                        "metadata": {},
                        "name": "Normal Clip 1",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 238
                            },
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 135
                            }
                        }
                    },
                    {
                        "OTIO_SCHEMA": "Stack.1",
                        "children": [
                            {
                                "OTIO_SCHEMA": "Clip.1",
                                "effects": [],
                                "markers": [],
                                "media_reference": {
                                    "OTIO_SCHEMA": "ExternalReference.1",
                                    "available_range": {
                                        "OTIO_SCHEMA": "TimeRange.1",
                                        "duration": {
                                            "OTIO_SCHEMA": "RationalTime.1",
                                            "rate": 24,
                                            "value": 238
                                        },
                                        "start_time": {
                                            "OTIO_SCHEMA": "RationalTime.1",
                                            "rate": 24,
                                            "value": 0
                                        }
                                    },
                                    "metadata": {},
                                    "target_url": "/path/to/some/audio.wav"
                                },
                                "metadata": {},
                                "name": "Clip Inside A Stack 1",
                                "source_range": {
                                    "OTIO_SCHEMA": "TimeRange.1",
                                    "duration": {
                                        "OTIO_SCHEMA": "RationalTime.1",
                                        "rate": 24,
                                        "value": 37
                                    },
                                    "start_time": {
                                        "OTIO_SCHEMA": "RationalTime.1",
                                        "rate": 24,
                                        "value": 373
                                    }
                                }
                            }
                        ],
                        "effects": [],
                        "markers": [],
                        "metadata": {},
                        "name": "Nested Stack 1",
                        "source_range": {
                            "OTIO_SCHEMA": "TimeRange.1",
                            "duration": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 31
                            },
                            "start_time": {
                                "OTIO_SCHEMA": "RationalTime.1",
                                "rate": 24,
                                "value": 0
                            }
                        }
                    }
                ],
                "effects": [],
                "kind": "Audio",
                "markers": [],
                "metadata": {},
                "name": "Top Level Track",
                "source_range": null
            }
        ],
        "effects": [],
        "markers": [],
        "metadata": {},
        "name": "Top Level Stack",
        "source_range": null
    }
}"""


@unittest.skipIf(
    "OTIO_RV_PYTHON_LIB" not in os.environ or
    "OTIO_RV_PYTHON_BIN" not in os.environ,
    "OTIO_RV_PYTHON_BIN or OTIO_RV_PYTHON_LIB not set."
)
class RVSessionAdapterReadTest(unittest.TestCase):
    def setUp(self):
        fd, self.tmp_path = tempfile.mkstemp(suffix=".rv", text=True)

        # Close file descriptor to avoid leak. We only need the tmp_path.
        os.close(fd)

    def tearDown(self):
        os.unlink(self.tmp_path)

    def test_basic_rvsession_read(self):
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        otio.adapters.write_to_file(timeline, self.tmp_path)

        with open(self.tmp_path) as fo:
            test_data = fo.read()

        with open(BASELINE_PATH) as fo:
            baseline_data = fo.read()

        self.maxDiff = None
        self._connectionFreeAssertMultiLineEqual(baseline_data, test_data)

    def test_transition_rvsession_read(self):
        timeline = otio.adapters.read_from_file(TRANSITION_EXAMPLE_PATH)

        otio.adapters.write_to_file(timeline, self.tmp_path)
        self.assertTrue(os.path.exists(self.tmp_path))

        with open(self.tmp_path) as fo:
            test_data = fo.read()

        with open(BASELINE_TRANSITION_PATH) as fo:
            baseline_data = fo.read()

        self.maxDiff = None
        self._connectionFreeAssertMultiLineEqual(baseline_data, test_data)

    def test_image_sequence_example(self):
        # SETUP
        timeline = otio.adapters.read_from_file(IMAGE_SEQUENCE_EXAMPLE_PATH)

        # EXERCISE
        otio.adapters.write_to_file(timeline, self.tmp_path)

        # VERIFY
        self.assertTrue(os.path.exists(self.tmp_path))

        with open(self.tmp_path) as f:
            rv_session = f.read()

        self.assertEqual(
            rv_session.count(
                'string movie = "./sample_sequence/sample_sequence.%04d.exr"'
            ),
            1
        )

    def test_transition_rvsession_covers_entire_shots(self):
        # SETUP
        timeline = otio.adapters.read_from_string(SAMPLE_DATA, "otio_json")

        # EXERCISE
        otio.adapters.write_to_file(timeline, self.tmp_path)

        # VERIFY
        with open(self.tmp_path) as f:
            rv_session = f.read()

        self.assertEqual(rv_session.count('movie = "blank'), 1)
        self.assertEqual(rv_session.count('movie = "smpte'), 1)

    def test_audio_video_tracks(self):
        # SETUP
        timeline = otio.adapters.read_from_string(AUDIO_VIDEO_SAMPLE_DATA, "otio_json")

        # EXERCISE
        otio.adapters.write_to_file(timeline, self.tmp_path)

        # VERIFY
        self.assertTrue(os.path.exists(self.tmp_path))

        audio_video_source = (
            'string movie = '
            '[ "blank,start=0.0,end=499.0,fps=25.0.movieproc" '
            '"blank,start=0.0,end=499.0,fps=25.0.movieproc"'
            ' "/path/to/audio.wav" ]'
        )

        with open(self.tmp_path) as f:
            rv_session = f.read()

        self.assertEqual(rv_session.count("string movie"), 2)
        self.assertEqual(rv_session.count("blank"), 2)
        self.assertEqual(rv_session.count(audio_video_source), 1)

    def test_nested_stack(self):
        # SETUP
        timeline = otio.adapters.read_from_string(
            NESTED_STACK_SAMPLE_DATA,
            "otio_json"
        )

        # EXERCISE
        otio.adapters.write_to_file(timeline, self.tmp_path)

        # VERIFY
        self.assertTrue(os.path.exists(self.tmp_path))

        audio_video_source = (
            'string movie = '
            '[ "blank,start=0.0,end=237.0,fps=24.0.movieproc"'
            ' "blank,start=0.0,end=237.0,fps=24.0.movieproc"'
            ' "/path/to/some/audio.wav" ]'
        )
        video_source = (
            'string movie = "/path/to/some/video.mov"'
        )

        with open(self.tmp_path) as f:
            rv_session = f.read()
            self.assertEqual(rv_session.count(video_source), 2)
            self.assertEqual(rv_session.count(audio_video_source), 2)

    def test_metadata_read(self):
        timeline = otio.adapters.read_from_file(METADATA_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".rv", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(METADATA_BASELINE_PATH) as fo:
            baseline_data = fo.read()

        self.maxDiff = None
        self._connectionFreeAssertMultiLineEqual(baseline_data, test_data)

    def _connectionFreeAssertMultiLineEqual(self, first, second):
        '''
        The "connections" list order is not stable between python versions
        so as a quick hack, simply remove it from our diff
        '''
        def _removeConnections(string):
            return os.linesep.join([line for line in string.splitlines()
                                    if 'connections' not in line])
        self.assertMultiLineEqual(_removeConnections(first),
                                  _removeConnections(second))


if __name__ == '__main__':
    unittest.main()
