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

from .. import adapters


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
            os.environ["OTIO_RV_PYTHON_BIN"],
            '-m',
            'extern_rv',
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=os.environ
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
