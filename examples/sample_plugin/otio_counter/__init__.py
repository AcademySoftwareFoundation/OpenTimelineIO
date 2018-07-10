import os
from opentimelineio.plugins import manifest

"""
In the ``setup.py`` the top-level module was provided as the entry point. When
OTIO loads a plugin, it then looks for a manifest object provided by the
``plugin_manifest`` function. In this case we deserialize it from a json file
we include in the module.

Below is an example of what the manifest json might look like (also included
as a file in this package.)

.. codeblock:: JSON

    {
        "OTIO_SCHEMA" : "PluginManifest.1",
        "adapters": [
            {
                "OTIO_SCHEMA": "Adapter.1",
                "name": "track_counter",
                "execution_scope": "in process",
                "filepath": "adapter.py",
                "suffixes": ["count"]
            }
        ]
    }


While this example shows an adapter, you may also define Media Linker plugins
as below.

.. codeblock:: JSON

    {
        "OTIO_SCHEMA" : "MediaLinker.1",
        "name" : "linker_example",
        "execution_scope" : "in process",
        "filepath" : "linker.py"
    }

"""


def plugin_manifest():
    return manifest.manifest_from_file(
        os.path.join(os.path.dirname(__file__), 'plugin_manifest.json')
    )
