# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Plugin system for OTIO"""

# flake8: noqa

from .python_plugin import (
    plugin_info_map,
    PythonPlugin,
)

from .manifest import (
    manifest_from_file,
    ActiveManifest,
)
