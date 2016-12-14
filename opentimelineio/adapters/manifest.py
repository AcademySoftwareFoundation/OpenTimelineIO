"""Implementation of an adapter registry system for OTIO."""

from .. import (
    core,
    exceptions,
)

from . import (
    otio_json
)


def manifest_from_file(filepath):
    """Read the .json file at filepath into a Manifest object."""

    result = otio_json.read_from_file(filepath)
    result.source_files.append(filepath)
    result._update_adapter_source(filepath)
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
        self.source_files = []

    adapters = core.serializeable_field(
        "adapters",
        type([]),
        "Adapters this manifest describes."
    )

    def _update_adapter_source(self, path):
        """Track the source .json for a given adapter."""

        for adapter in self.adapters:
            adapter._json_path = path

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

    def from_name(self, name):
        """Return the adapter object associated with a given adapter name."""

        for adapter in self.adapters:
            if name == adapter.name:
                return adapter
        raise NotImplementedError(name)

    def adapter_module_from_name(self, name):
        """Return the adapter module associated with a given adapter name."""

        adp = self.from_name(name)
        return adp.module()
