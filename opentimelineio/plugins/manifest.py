#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Implementation of an adapter registry system for OTIO."""

import os
import inspect

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
class Manifest(core.SerializableObject):
    """Defines an OTIO plugin Manifest.

    This is an internal OTIO implementation detail.  A manifest tracks a
    collection of adapters and allows finding specific adapters by suffix

    For writing your own adapters, consult:
        https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
    """
    _serializable_label = "PluginManifest.1"

    def __init__(self):
        core.SerializableObject.__init__(self)
        self.adapters = []
        self.media_linkers = []
        self.source_files = []

    adapters = core.serializable_field(
        "adapters",
        type([]),
        "Adapters this manifest describes."
    )
    media_linkers = core.serializable_field(
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
            os.path.dirname(os.path.dirname(inspect.getsourcefile(core))),
            "adapters",
            "builtin_adapters.plugin_manifest.json"
        )
    )

    # layer contrib plugins after built in ones
    try:
        import opentimelineio_contrib as otio_c

        contrib_manifest = manifest_from_file(
            os.path.join(
                os.path.dirname(inspect.getsourcefile(otio_c)),
                "adapters",
                "contrib_adapters.plugin_manifest.json"
            )
        )
        result.adapters.extend(contrib_manifest.adapters)
        result.media_linkers.extend(contrib_manifest.media_linkers)
    except ImportError:
        pass

    # read local adapter manifests, if they exist
    _local_manifest_path = os.environ.get("OTIO_PLUGIN_MANIFEST_PATH", None)
    if _local_manifest_path is not None:
        for json_path in _local_manifest_path.split(":"):
            if not os.path.exists(json_path):
                # XXX: In case error reporting is requested
                # print(
                #     "Warning: OpenTimelineIO cannot access path '{}' from "
                #     "$OTIO_PLUGIN_MANIFEST_PATH".format(json_path)
                # )
                continue

            LOCAL_MANIFEST = manifest_from_file(json_path)
            result.adapters.extend(LOCAL_MANIFEST.adapters)
            result.media_linkers.extend(LOCAL_MANIFEST.media_linkers)

    return result


def ActiveManifest(force_reload=False):
    global _MANIFEST
    if not _MANIFEST or force_reload:
        _MANIFEST = load_manifest()

    return _MANIFEST
