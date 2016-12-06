import os

from .. import exceptions

from .manifest import Manifest, manifest_from_file # noqa
from .adapter import Adapter # noqa

""" The adapter module allows you to extend OTIO to read and write more
formats.
"""

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
    return [str(adp.name) for adp in MANIFEST.adapters]


def from_filepath(filepath):
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
    if adapter_name is None:
        adapter_name = from_filepath(filepath)
    adapter = MANIFEST.from_name(adapter_name)
    return adapter.read_from_file(filepath)


def read_from_string(input_str, adapter_name):
    adapter = MANIFEST.from_name(adapter_name)
    return adapter.read_from_string(input_str)


def write_to_file(input_otio, filepath, adapter_name=None):
    if adapter_name is None:
        adapter_name = from_filepath(filepath)
    adapter = MANIFEST.from_name(adapter_name)
    return adapter.write_to_file(input_otio, filepath)


def write_to_string(input_otio, adapter_name):
    adapter = MANIFEST.from_name(adapter_name)
    return adapter.write_to_string(input_otio)
