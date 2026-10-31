#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

set -euo pipefail

# Use the Reference Platform interpreter rather than downloading another Python.
platform_python="$(/usr/local/bin/python -c 'import sys; print(sys.executable)')"
uv sync --locked --group docs --reinstall-package opentimelineio --python "$platform_python"
