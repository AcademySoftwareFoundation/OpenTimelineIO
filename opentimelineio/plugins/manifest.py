"""Implementation of an adapter registry system for OTIO."""

import os

from .. import (
    core,
    exceptions,
)


def manifest_from_file(filepath):
    """Read the .json file at filepath into a Manifest object."""

    result = core.deserialize_json_from_file(filepath)
    result.source_files.append(filepath)
    result._update_plugin_source(filepath)
    return result


@core.register_type
class Manifest(core.SerializeableObject):
    """Defines an OTIO plugin Manifest.

    This is an internal OTIO implementation detail.  A manifest tracks a
    collection of adapters and allows finding specific adapters by suffix

    For writing your own adapters, consult:
        https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
    """
    _serializeable_label = "PluginManifest.1"

    def __init__(self):
        core.SerializeableObject.__init__(self)
        self.adapters = []
        self.media_linkers = []
        self.source_files = []

    adapters = core.serializeable_field(
        "adapters",
        type([]),
        "Adapters this manifest describes."
    )
    media_linkers = core.serializeable_field(
        "media_linkers",
        type([]),
        "Media Linkers this manifest describes."
    )

    def _update_plugin_source(self, path):
        """Track the source .json for a given adapter."""

        for thing in (self.adapters + self.media_linkers):
            thing._json_path = path

    def from_filepath(self, suffix):
        """Return the adapter object associated with a given file suffix."""

        for adapter in self.adapters:
            if suffix.lower() in adapter.suffixes:
                return adapter
        raise exceptions.NoKnownAdapterForExtensionError(suffix)

    def adapter_module_from_suffix(self, suffix):
        """Return the adapter module associated with a given file suffix."""

        adp = self.from_filepath(suffix)
        return adp.module()

    def from_name(self, name, kind_list="adapters"):
        """Return the adapter object associated with a given adapter name."""

        for thing in getattr(self, kind_list):
            if name == thing.name:
                return thing

        raise NotImplementedError(
            "Could not find plugin: '{}' in kind_list: '{}'."
            " options: {}".format(
                name,
                kind_list,
                getattr(self, kind_list)
            )
        )

    def adapter_module_from_name(self, name):
        """Return the adapter module associated with a given adapter name."""

        adp = self.from_name(name)
        return adp.module()


_MANIFEST = None


def load_manifest():
    # build the manifest of adapters, starting with builtin adapters
    result = manifest_from_file(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "adapters",
            "builtin_adapters.plugin_manifest.json"
        )
    )

    # read local adapter manifests, if they exist
    _local_manifest_path = os.environ.get("OTIO_PLUGIN_MANIFEST_PATH", None)
    if _local_manifest_path is not None:
        for json_path in _local_manifest_path.split(":"):
            LOCAL_MANIFEST = manifest_from_file(json_path)
            result.adapters.extend(LOCAL_MANIFEST.adapters)
            result.media_linkers.extend(LOCAL_MANIFEST.media_linkers)

    return result


def ActiveManifest(force_reload=False):
    global _MANIFEST
    if not _MANIFEST or force_reload:
        _MANIFEST = load_manifest()

    return _MANIFEST
