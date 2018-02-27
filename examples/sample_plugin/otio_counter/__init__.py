import os
from opentimelineio.plugins import manifest


def plugin_manifest():
    return manifest.manifest_from_file(
        os.path.join(os.path.dirname(__file__), 'plugin_manifest.json')
    )
