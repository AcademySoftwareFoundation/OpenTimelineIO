import pkg_resources

from opentimelineio.plugins import manifest

# XXX: seems like the json deserializer in python3.5 is more sensitive and
# the string coming back from pkg_resources needs to be sanitized.
#
# if you're using this code as an example, you might not need to do
# replace/strip, especially if you're generating your own manifest file some
# other way than reading a file off the disk.

def plugin_manifest():
    return manifest.manifest_from_string(
        str(
            pkg_resources.resource_string(
                __name__,
                'unusually_named_plugin_manifest.json'
            )
        ).replace('\n', '').strip()
    )
