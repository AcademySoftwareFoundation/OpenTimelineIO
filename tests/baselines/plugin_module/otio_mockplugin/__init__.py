import pkg_resources

from opentimelineio.plugins import manifest


def plugin_manifest():
    return manifest.manifest_from_string(
        pkg_resources.resource_string(__name__, 'unusually_named_plugin_manifest.json')
    )
