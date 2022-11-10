# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from importlib import resources
from pathlib import Path

from opentimelineio.plugins import manifest

"""An example plugin package that generates its package manifest on demand.

If you create a plugin that doesn't have a plugin_manifest.json, OTIO will
attempt to call the plugin_manifest() function from the __init__.py directory.

This would allow you to programmatically generate a manifest rather than have
it be static on disk, allowing you to switch features on or off or do some
template substition or any other kind of procedural processing.

This unit test uses a very simple example that just reads the manifest from
a non-standard json file path.
"""


def plugin_manifest():
    try:
        filepath = resources.files(__package__) / "unusually_named_plugin_manifest.json"
    except AttributeError:
        # For python <= 3.7
        with resources.path(__package__, "unusually_named_plugin_manifest.json") as p:
            filepath = Path(p)

    return manifest.manifest_from_string(
        filepath.read_text()
    )
