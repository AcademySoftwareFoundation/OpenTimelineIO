""" RvSession Adapter harness """

import tempfile
import subprocess
import os

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

    fname = tempfile.mkstemp(suffix=".otio")[1]
    otio.adapters.write_to_file(input_otio, fname)

    proc = subprocess.Popen(
        [
            os.environ["OTIO_RV_PYTHON_BIN"],
            '{}/extern_rv.py'.format(os.path.dirname(__file__)),
            fname,
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = proc.communicate()

    if proc.returncode:
        raise RuntimeError(
            "ERROR: extern_rv (called through the rv session file adapter) "
            "failed. stderr output: " + err
        )
