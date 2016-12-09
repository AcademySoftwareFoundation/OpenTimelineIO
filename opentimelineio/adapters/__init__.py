"""Expose the adapter interface to developers.

To read from an existing representation, use the read_from_string and
read_from_file functions.  To query the list of references, use the
available_adapter_names function.

The otio_json adapter is provided as a the canonical, lossless, serialization
of the in-memory otio schema.  Other adapters are to varying degrees lossy.
For more information, consult the documentation in the individual adapter
modules.
"""

import os

from .. import exceptions

from .manifest import Manifest, manifest_from_file # noqa
from .adapter import Adapter # noqa


# build the manifest of adapters, starting with builtin adapters
MANIFEST = manifest_from_file(
    os.path.join(
        os.path.dirname(__file__),
        "builtin_adapters.plugin_manifest.json"
    )
)

# read local adapter manifest, if it exists
_local_manifest_path = os.environ.get("OTIO_PLUGIN_MANIFEST_PATH", None)
if _local_manifest_path is not None:
    for json_path in _local_manifest_path.split(":"):
        LOCAL_MANIFEST = manifest_from_file(_local_manifest_path)
        MANIFEST.adapters.extend(LOCAL_MANIFEST.adapters)


def available_adapter_names():
    """Return a string list of the available adapters."""

    return [str(adp.name) for adp in MANIFEST.adapters]


def from_filepath(filepath):
    """Guess the adapter to use for a given filepath.

    For example: .otio returns the otio_json adapter.
    """

    outext = os.path.splitext(filepath)[1][1:]

    try:
        return MANIFEST.from_filepath(outext).name
    except exceptions.NoKnownAdapterForExtensionError:
        raise exceptions.NoKnownAdapterForExtensionError(
            "No adapter for suffix '{}' on file '{}'".format(
                outext,
                filepath
            )
        )


def from_name(name):
    """Fetch the adapter object by the name of the adapter directly."""

    try:
        return MANIFEST.from_name(name)
    except exceptions.NotSupportedError:
        raise exceptions.NotSupportedError(
            "adapter not supported: {}, available: {}".format(
                name,
                available_adapter_names()
            )
        )


def read_from_file(filepath, adapter_name=None):
    """Read filepath using adapter_name.

    If adapter_name is None, try and infer the adapter name from the filepath.

    For example: .otio returns the otio_json adapter.
    """

    if adapter_name is None:
        adapter_name = from_filepath(filepath)
    adapter = MANIFEST.from_name(adapter_name)
    return adapter.read_from_file(filepath)


def read_from_string(input_str, adapter_name):
    """Read input_str using adapter_name."""

    adapter = MANIFEST.from_name(adapter_name)
    return adapter.read_from_string(input_str)


def write_to_file(input_otio, filepath, adapter_name=None):
    """Write input_otio to filepath using adapter_name.

    If adapter_name is None, infer the adapter_name to use based on the
    filepath.

    For example: .otio returns the otio_json adapter.
    """

    if adapter_name is None:
        adapter_name = from_filepath(filepath)
    adapter = MANIFEST.from_name(adapter_name)
    return adapter.write_to_file(input_otio, filepath)


def write_to_string(input_otio, adapter_name):
    """Return input_otio written to a string using adapter_name."""

    adapter = MANIFEST.from_name(adapter_name)
    return adapter.write_to_string(input_otio)
