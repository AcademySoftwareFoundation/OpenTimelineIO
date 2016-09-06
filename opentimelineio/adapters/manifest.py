from .. import (
    core,
    exceptions,
)

from . import (
    otio_json
)


def manifest_from_file(filepath):
    result = otio_json.read_from_file(filepath)
    result.source_files.append(filepath)
    result._update_adapter_source(filepath)
    return result


@core.register_type
class Manifest(core.SerializeableObject):
    serializeable_label = "PluginManifest.1"

    def __init__(self):
        core.SerializeableObject.__init__(self)
        self.adapters = []
        self.source_files = []

    adapters = core.serializeable_field("adapters", type([]))

    def _update_adapter_source(self, path):
        for adapter in self.adapters:
            adapter._json_path = path

    def from_filepath(self, suffix):
        for adapter in self.adapters:
            if suffix in adapter.suffixes:
                return adapter
        raise exceptions.NoKnownAdapterForExtensionError(suffix)

    def adapter_module_from_suffix(self, suffix):
        adp = self.from_filepath(suffix)
        return adp.module()

    def from_name(self, name):
        for adapter in self.adapters:
            if name == adapter.name:
                return adapter
        raise NotImplementedError(name)

    def adapter_module_from_name(self, name):
        adp = self.from_name(name)
        return adp.module()
