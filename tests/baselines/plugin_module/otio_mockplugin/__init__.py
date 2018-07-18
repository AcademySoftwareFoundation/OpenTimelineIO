import pkg_resources

from opentimelineio.plugins import manifest


def plugin_manifest():
    return manifest.manifest_from_string(
        pkg_resources.resource_string(__name__, 'plugin_manifest.json')
    )
