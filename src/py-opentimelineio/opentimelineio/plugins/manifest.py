#
# Copyright Contributors to the OpenTimelineIO project
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

"""OTIO Python Plugin Manifest system: locates plugins to OTIO."""

import inspect
import logging
import os

# In some circumstances pkg_resources has bad performance characteristics.
# Using the envirionment variable: $OTIO_DISABLE_PKG_RESOURCE_PLUGINS disables
# OpenTimelineIO's import and of use of the pkg_resources module.
if os.environ.get("OTIO_DISABLE_PKG_RESOURCE_PLUGINS", False):
    pkg_resources = None
else:
    try:
        # on some python interpreters, pkg_resources is not available
        import pkg_resources
    except ImportError:
        pkg_resources = None

from .. import (
    core,
    exceptions,
)


# for tracking what kinds of plugins the manifest system supports
OTIO_PLUGIN_TYPES = [
    'adapters',
    'media_linkers',
    'schemadefs',
    'hook_scripts',
    'hooks',
]


def manifest_from_file(filepath):
    """Read the .json file at filepath into a Manifest object."""

    result = core.deserialize_json_from_file(filepath)
    absfilepath = os.path.abspath(filepath)
    result.source_files.append(absfilepath)
    result._update_plugin_source(absfilepath)
    return result


def manifest_from_string(input_string):
    """Deserialize the json string into a manifest object."""

    result = core.deserialize_json_from_string(input_string)

    # try and get the caller's name
    name = "unknown"
    stack = inspect.stack()
    if len(stack) > 1 and len(stack[1]) > 3:
        #                     filename     function name
        name = "{}:{}".format(stack[1][1], stack[1][3])

    # set the value in the manifest
    src_string = "call to manifest_from_string() in {}".format(name)
    result.source_files.append(src_string)
    result._update_plugin_source(src_string)

    return result


@core.register_type
class Manifest(core.SerializableObject):
    """Defines an OTIO plugin Manifest.

    This is considered an internal OTIO implementation detail.

    A manifest tracks a collection of plugins and enables finding them by name
    or other features (in the case of adapters, what file suffixes they
    advertise support for).

    For more information, consult the documenation.
    """
    _serializable_label = "PluginManifest.1"

    def __init__(self):
        core.SerializableObject.__init__(self)
        self.adapters = []
        self.schemadefs = []
        self.media_linkers = []
        self.source_files = []

        # hook system stuff
        self.hooks = {}
        self.hook_scripts = []

    adapters = core.serializable_field(
        "adapters",
        type([]),
        "Adapters this manifest describes."
    )
    schemadefs = core.serializable_field(
        "schemadefs",
        type([]),
        "Schemadefs this manifest describes."
    )
    media_linkers = core.serializable_field(
        "media_linkers",
        type([]),
        "Media Linkers this manifest describes."
    )
    hooks = core.serializable_field(
        "hooks",
        type({}),
        "Hooks that hooks scripts can be attached to."
    )
    hook_scripts = core.serializable_field(
        "hook_scripts",
        type([]),
        "Scripts that can be attached to hooks."
    )

    def extend(self, another_manifest):
        """
        Aggregate another manifest's plugins into this one.

        During startup, OTIO will deserialize the individual manifest JSON files
        and use this function to concatenate them together.
        """
        if not another_manifest:
            return

        self.adapters.extend(another_manifest.adapters)
        self.schemadefs.extend(another_manifest.schemadefs)
        self.media_linkers.extend(another_manifest.media_linkers)
        self.hook_scripts.extend(another_manifest.hook_scripts)

        for trigger_name, hooks in another_manifest.hooks.items():
            if trigger_name not in self.hooks:
                self.hooks[trigger_name] = []
            self.hooks[trigger_name].extend(hooks)

        self.source_files.extend(another_manifest.source_files)

    def _update_plugin_source(self, path):
        """Set the source file path for the manifest."""

        for thing in (
            self.adapters
            + self.schemadefs
            + self.media_linkers
            + self.hook_scripts
        ):
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

    # @TODO: (breaking change) this should search all plugins by default instead
    #        of just adapters
    def from_name(self, name, kind_list="adapters"):
        """Return the plugin object associated with a given plugin name."""

        for thing in getattr(self, kind_list):
            if name == thing.name:
                return thing

        raise exceptions.NotSupportedError(
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

    def schemadef_module_from_name(self, name):
        """Return the schemadef module associated with a given schemadef name."""

        adp = self.from_name(name, kind_list="schemadefs")
        return adp.module()


_MANIFEST = None


def load_manifest():
    """ Walk the plugin manifest discovery systems and accumulate manifests.

    The order of loading (and precedence) is:
        1. manifests specfied via the OTIO_PLUGIN_MANIFEST_PATH variable
        2. builtin plugin manifest
        3. contrib plugin manifest
        4. setuptools.pkg_resources based plugin manifests
    """

    result = Manifest()

    # Read plugin manifests defined on the $OTIO_PLUGIN_MANIFEST_PATH
    # environment variable.  This variable is an os.pathsep separated list of
    # file paths to manifest json files.
    _local_manifest_path = os.environ.get("OTIO_PLUGIN_MANIFEST_PATH", None)
    if _local_manifest_path is not None:
        for src_json_path in _local_manifest_path.split(os.pathsep):
            json_path = os.path.abspath(src_json_path)
            if (
                not os.path.exists(json_path)
                # the manifest has already been loaded
                or json_path in result.source_files
            ):
                # XXX: In case error reporting is requested
                # print(
                #     "Warning: OpenTimelineIO cannot access path '{}' from "
                #     "$OTIO_PLUGIN_MANIFEST_PATH".format(json_path)
                # )
                continue

            result.extend(manifest_from_file(json_path))

    # the builtin plugin manifest
    builtin_manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(inspect.getsourcefile(core))),
        "adapters",
        "builtin_adapters.plugin_manifest.json"
    )
    if os.path.abspath(builtin_manifest_path) not in result.source_files:
        plugin_manifest = manifest_from_file(builtin_manifest_path)
        result.extend(plugin_manifest)

    # the contrib plugin manifest (located in the opentimelineio_contrib package)
    try:
        import opentimelineio_contrib as otio_c

        contrib_manifest_path = os.path.join(
            os.path.dirname(inspect.getsourcefile(otio_c)),
            "adapters",
            "contrib_adapters.plugin_manifest.json"
        )
        if os.path.abspath(contrib_manifest_path) not in result.source_files:
            contrib_manifest = manifest_from_file(contrib_manifest_path)
            result.extend(contrib_manifest)

    except ImportError:
        pass

    # setuptools.pkg_resources based plugins
    if pkg_resources:
        for plugin in pkg_resources.iter_entry_points(
                "opentimelineio.plugins"
        ):
            plugin_name = plugin.name
            try:
                plugin_entry_point = plugin.load()
                try:
                    plugin_manifest = plugin_entry_point.plugin_manifest()

                    # this ignores what the plugin_manifest() function might
                    # put into source_files in favor of using the path to the
                    # python package as the unique identifier

                    manifest_path = os.path.abspath(
                        plugin_entry_point.__file__
                    )

                    if manifest_path in result.source_files:
                        continue

                    plugin_manifest.source_files = [manifest_path]
                    plugin_manifest._update_plugin_source(manifest_path)

                except AttributeError:
                    if not pkg_resources.resource_exists(
                            plugin.module_name,
                            'plugin_manifest.json'
                    ):
                        raise

                    filepath = os.path.abspath(
                        pkg_resources.resource_filename(
                            plugin.module_name,
                            'plugin_manifest.json'
                        )
                    )

                    if filepath in result.source_files:
                        continue

                    manifest_stream = pkg_resources.resource_stream(
                        plugin.module_name,
                        'plugin_manifest.json'
                    )
                    plugin_manifest = core.deserialize_json_from_string(
                        manifest_stream.read().decode('utf-8')
                    )
                    manifest_stream.close()

                    plugin_manifest._update_plugin_source(filepath)
                    plugin_manifest.source_files.append(filepath)

            except Exception:
                logging.exception(
                    "could not load plugin: {}".format(plugin_name)
                )
                continue

            result.extend(plugin_manifest)
    else:
        # XXX: Should we print some kind of warning that pkg_resources isn't
        #        available?
        pass

    # force the schemadefs to load and add to schemadef module namespace
    for s in result.schemadefs:
        s.module()

    return result


def ActiveManifest(force_reload=False):
    """Return the fully resolved plugin manifest."""

    global _MANIFEST
    if not _MANIFEST or force_reload:
        _MANIFEST = load_manifest()

    return _MANIFEST
