import pkg_resources

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
    # XXX: in python3.5 resource_string returns a 'bytes' object, but
    #      json.loads requires a string, not bytes (only in 3.5 -- 2.7 and 3.6
    #      seem to both be working).  Luckily .decode() seems to work in both
    #      python3 and python2, so this *should* work for both versions.
    return manifest.manifest_from_string(
        pkg_resources.resource_string(
            __name__,
            'unusually_named_plugin_manifest.json'
        ).decode('utf-8')
    )
