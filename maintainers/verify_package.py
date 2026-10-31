#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Smoke-test an installed distribution, including native modules and package data.

Run using a fresh environment containing the wheel built from the sdist:
    path/to/venv/bin/python maintainers/verify_package.py
"""

import importlib.machinery
import importlib.metadata
import importlib.resources
import json
import subprocess
import sys
import sysconfig
from pathlib import Path

import opentimelineio as otio


def main():
    distribution = importlib.metadata.distribution("OpenTimelineIO")
    assert distribution.version == otio.__version__
    assert not distribution.requires, (
        "The core library must have no runtime dependencies"
    )
    assert otio._otio.__file__.endswith(tuple(importlib.machinery.EXTENSION_SUFFIXES))
    assert otio._opentime.__file__.endswith(
        tuple(importlib.machinery.EXTENSION_SUFFIXES)
    )

    manifest = importlib.resources.files("opentimelineio.adapters").joinpath(
        "builtin_adapters.plugin_manifest.json"
    )
    assert json.loads(manifest.read_text())["adapters"]
    assert {"otio_json", "otiod", "otioz"} <= set(
        otio.adapters.available_adapter_names()
    )

    timeline = otio.schema.Timeline(name="Packaging smoke test")
    encoded = otio.adapters.write_to_string(timeline, adapter_name="otio_json")
    decoded = otio.adapters.read_from_string(encoded, adapter_name="otio_json")
    assert decoded.name == timeline.name
    assert otio.opentime.RationalTime(24, 24).to_seconds() == 1

    scripts = Path(sysconfig.get_path("scripts"))
    for entry in distribution.entry_points:
        if entry.group == "console_scripts":
            suffix = ".exe" if sys.platform == "win32" else ""
            subprocess.run(
                [str(scripts / (entry.name + suffix)), "--help"],
                check=True,
                stdout=subprocess.DEVNULL,
            )

    files = [str(file) for file in distribution.files]
    assert any(file.endswith("LICENSE.txt") for file in files)
    assert any(file.endswith("NOTICE.txt") for file in files)
    print(f"Verified OpenTimelineIO {distribution.version}: {otio.__file__}")


if __name__ == "__main__":
    main()
