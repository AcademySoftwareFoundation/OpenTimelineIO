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

"""RvSession Adapter harness"""

import subprocess
import os
import copy

from .. import adapters

import opentimelineio as otio


def write_to_file(input_otio, filepath):
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

    input_data = adapters.write_to_string(input_otio, "otio_json")

    base_environment = copy.deepcopy(os.environ)

    base_environment['PYTHONPATH'] = (
        os.pathsep.join(
            [
                base_environment.setdefault('PYTHONPATH', ''),

                # ensure that OTIO is on the pythonpath
                os.path.dirname(os.path.dirname(otio.__file__)),

                # ensure that the rv adapter is on the pythonpath
                os.path.dirname(__file__),
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

    # If the subprocess fails before writing to stdin is complete, python will
    # throw a IOError exception.  If it fails after writing to stdin, there
    # won't be an exception.  Either way, the return code will be non-0 so the
    # rest of the code should catch the error case and print the (presumably)
    # helpful message from the subprocess.
    try:
        proc.stdin.write(input_data)
    except IOError:
        pass

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
