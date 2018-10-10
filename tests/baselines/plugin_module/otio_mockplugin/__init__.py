import pkg_resources

from opentimelineio.plugins import manifest

"""An example plugin package that generates its package manifest on demand.

In this case, it reads it from another json, but it could be procedurally
adding or removing features as needed.  The plugin_manifest() function will
get called if no plugin_manifest.json is present in the plugin directory.
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
