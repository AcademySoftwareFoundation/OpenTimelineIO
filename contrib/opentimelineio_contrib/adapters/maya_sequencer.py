#
# Copyright Contributors to the OpenTimelineIO project
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

"""Maya Sequencer Adapter Harness"""

import os
import subprocess

from .. import adapters


def write_to_file(input_otio, filepath):
    if "OTIO_MAYA_PYTHON_BIN" not in os.environ:
        raise RuntimeError(
            "'OTIO_MAYA_PYTHON_BIN' not set, please set this to path to "
            "mayapy within the Maya installation."
        )
    maya_python_path = os.environ["OTIO_MAYA_PYTHON_BIN"]
    if not os.path.exists(maya_python_path):
        raise RuntimeError(
            'Cannot access file at OTIO_MAYA_PYTHON_BIN: "{}"'.format(
                maya_python_path
            )
        )
    if os.path.isdir(maya_python_path):
        raise RuntimeError(
            "OTIO_MAYA_PYTHON_BIN contains a path to a directory, not to an "
            "executable file: {}".format(maya_python_path)
        )

    input_data = adapters.write_to_string(input_otio, "otio_json")

    os.environ['PYTHONPATH'] = (
        os.pathsep.join(
            [
                os.environ.setdefault('PYTHONPATH', ''),
                os.path.dirname(__file__)
            ]
        )
    )

    proc = subprocess.Popen(
        [
            os.environ["OTIO_MAYA_PYTHON_BIN"],
            '-m',
            'extern_maya_sequencer',
            'write',
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=os.environ
    )
    proc.stdin.write(input_data)
    out, err = proc.communicate()

    if proc.returncode:
        raise RuntimeError(
            "ERROR: extern_maya_sequencer (called through the maya sequencer "
            "file adapter) failed. stderr output: " + err
        )


def read_from_file(filepath):
    if "OTIO_MAYA_PYTHON_BIN" not in os.environ:
        raise RuntimeError(
            "'OTIO_MAYA_PYTHON_BIN' not set, please set this to path to "
            "mayapy within the Maya installation."
        )

    os.environ['PYTHONPATH'] = (
        os.pathsep.join(
            [
                os.environ.setdefault('PYTHONPATH', ''),
                os.path.dirname(__file__)
            ]
        )
    )

    proc = subprocess.Popen(
        [
            os.environ["OTIO_MAYA_PYTHON_BIN"],
            '-m',
            'extern_maya_sequencer',
            'read',
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=os.environ
    )
    out, err = proc.communicate()

    # maya probably puts a bunch of crap on the stdout
    sentinel_str = "OTIO_JSON_BEGIN\n"
    end_sentinel_str = "\nOTIO_JSON_END\n"
    start = out.find(sentinel_str)
    end = out.find(end_sentinel_str)
    result = adapters.read_from_string(
        out[start + len(sentinel_str):end],
        "otio_json"
    )

    if proc.returncode:
        raise RuntimeError(
            "ERROR: extern_maya_sequencer (called through the maya sequencer "
            "file adapter) failed. stderr output: " + err
        )
    return result
