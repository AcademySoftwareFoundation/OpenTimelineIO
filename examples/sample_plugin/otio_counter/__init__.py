# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import importlib.resources

from opentimelineio.plugins import manifest

"""
In the ``setup.py`` the top-level module was provided as the entry point. When
OTIO loads a plugin, it will look for ``plugin_manifest.json`` in the package
and register the plugins declared.

If you wish to programmatically generate the manifest, you may return a
:class:`Manifest` instance from your entry point's ``plugin_manifest``
function.

For example purposes, this simply deserializes it from the json file included
in the package.

Below is an example of what the manifest json might look like (also included
as a file in this package).

.. codeblock:: JSON

    {
        "OTIO_SCHEMA" : "PluginManifest.1",
        "adapters": [
            {
                "OTIO_SCHEMA": "Adapter.1",
                "name": "track_counter",
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
        "filepath" : "linker.py"
    }

"""


def plugin_manifest():
    """
    If, for some reason, the Manifest needs to be generated at runtime, it can
    be done here. This function takes precedence over ``plugin_manifest.json``
    automatic discovery.

    Note the example implemenation's behavior is identical to the default when
    this function isn't defined. In most cases ``plugin_manifest.json`` should
    be sufficient and the ``__init__.py`` file can be left empty.
    """

    # XXX: note, this doesn't get called.  For an example of this working,
    #      see the mockplugin unit test.

    filepath = importlib.resources.files(__package__) / "plugin_manifest.json"
    return manifest.manifest_from_string(
        filepath.read_text()
    )
