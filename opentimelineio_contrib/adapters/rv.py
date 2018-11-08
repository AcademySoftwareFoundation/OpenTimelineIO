#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""RvSession Adapter harness"""

import subprocess
import os
import copy

import opentimelineio as otio
from .. import adapters


def write_to_file(input_otio, filepath, link_audio=False):
    if "OTIO_RV_PYTHON_BIN" not in os.environ:
        raise RuntimeError(
            "'OTIO_RV_PYTHON_BIN' not set, please set this to path to "
            "py-interp within the RV installation."
        )

    if "OTIO_RV_PYTHON_LIB" not in os.environ:
        raise RuntimeError(
            "'OTIO_RV_PYTHON_LIB' not set, please set this to path to python "
            "directory within the RV installation."
        )

    # Find audio clips at same position as video clips and register in metadata
    if link_audio and type(input_otio) == otio.schema.Timeline:
        video_stack = otio.schema.Stack(
            name="videotracks",
            children=input_otio.video_tracks()
        )
        audio_stack = otio.schema.Stack(
            name="audiotracks",
            children=input_otio.audio_tracks()
        )

        for video_track in video_stack:
            for clip in video_track:
                # Search for audio clip
                for audio_clip in audio_stack.each_clip(clip.source_range):
                    ref = audio_clip.media_reference
                    if not isinstance(ref, otio.schema.ExternalReference):
                        # Ignore missing media
                        continue

                    # Gather metadata
                    audio_metadata = {
                        'audiofile': ref.target_url,
                        'offset': (
                            clip.source_range.start_time.value -
                            audio_clip.source_range.start_time.value /
                            float(clip.source_range.start_time.rate)
                        )
                    }

                    # Add metadata to pick up in extern_rv.py
                    clip.media_reference.metadata['rvaudio'] = audio_metadata

                    # Only use first available audio file
                    continue

        # Remove audio tracks to avoid duplicates
        input_otio.tracks = video_stack

    input_data = adapters.write_to_string(input_otio, "otio_json")

    base_environment = copy.deepcopy(os.environ)

    base_environment['PYTHONPATH'] = (
        os.pathsep.join(
            [
                base_environment.setdefault('PYTHONPATH', ''),
                os.path.dirname(__file__)
            ]
        )
    )

    proc = subprocess.Popen(
        [
            base_environment["OTIO_RV_PYTHON_BIN"],
            '-m',
            'extern_rv',
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=base_environment
    )
    proc.stdin.write(input_data)
    out, err = proc.communicate()

    if out.strip():
        print("stdout: {}".format(out))
    if err.strip():
        print("stderr: {}".format(err))

    if proc.returncode:
        raise RuntimeError(
            "ERROR: extern_rv (called through the rv session file adapter) "
            "failed. stderr output: " + err
        )
