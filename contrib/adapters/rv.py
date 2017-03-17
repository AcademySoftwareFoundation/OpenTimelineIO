""" RvSession Adapter harness """

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

    if proc.returncode:
        raise RuntimeError(
            "ERROR: extern_rv (called through the rv session file adapter) "
            "failed. stderr output: " + err
        )
