# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Base class for OTIO plugins that are exposed by manifests."""

import os
import inspect
import collections
import copy
import importlib.util

from .. import (
    core,
    exceptions,
)

from . import (
    manifest
)


def plugin_info_map():
    result = {}
    active_manifest = manifest.ActiveManifest()
    for pt in manifest.OTIO_PLUGIN_TYPES:
        # hooks get handled specially, see below
        if pt == "hooks":
            continue

        type_map = {}
        for plug in getattr(active_manifest, pt):
            try:
                type_map[plug.name] = plug.plugin_info_map()
            except Exception as err:
                type_map[plug.name] = (
                    "ERROR: could not compute plugin_info_map because:"
                    " {}".format(err)
                )

        result[pt] = type_map

    result['hooks'] = copy.deepcopy(active_manifest.hooks)

    result['manifests'] = copy.deepcopy(active_manifest.source_files)

    return result


class PythonPlugin(core.SerializableObject):
    """A class of plugin that is encoded in a python module, exposed via a
    manifest.
    """

    _serializable_label = "PythonPlugin.1"

    def __init__(
        self,
        name=None,
        filepath=None,
    ):
        core.SerializableObject.__init__(self)
        self.name = name
        self.filepath = filepath
        self._json_path = None
        self._module = None

    name = core.serializable_field("name", doc="Adapter name.")
    filepath = core.serializable_field(
        "filepath",
        str,
        doc=(
            "Absolute path or relative path to adapter module from location of"
            " json."
        )
    )

    def plugin_info_map(self):
        """Returns a map with information about the plugin."""

        result = collections.OrderedDict()

        result['name'] = self.name
        result['doc'] = inspect.getdoc(self.module())
        result['path'] = self.module_abs_path()
        result['from manifest'] = self._json_path

        return result

    def module_abs_path(self):
        """Return an absolute path to the module implementing this adapter."""

        filepath = self.filepath
        if not os.path.isabs(filepath):
            if not self._json_path:
                raise exceptions.MisconfiguredPluginError(
                    "{} plugin is misconfigured, missing json path. "
                    "plugin: {}".format(
                        self.name,
                        repr(self)
                    )
                )

            filepath = os.path.join(os.path.dirname(self._json_path), filepath)

        return filepath

    def _imported_module(self, namespace):
        """Load the module this plugin points at."""

        module_name = f"opentimelineio.{namespace}.{self.name}"
        try:
            # Attempt to import the module using importlib first
            mod = importlib.import_module(module_name)
        except ImportError:
            # If the module couldn't be imported, import it manually
            pyname = os.path.splitext(os.path.basename(self.module_abs_path()))[0]
            pydir = os.path.dirname(self.module_abs_path())
            spec = importlib.util.spec_from_file_location(
                module_name,
                os.path.join(pydir, f"{pyname}.py"),
            )

            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

        return mod

    def module(self):
        """Return the module object for this adapter. """

        if not self._module:
            self._module = self._imported_module("adapters")

        print(f"Retrieved plugin module: {self._module}")
        return self._module

    def _execute_function(self, func_name, **kwargs):
        """Execute func_name on this adapter with error checking."""

        print(f"Invoking plugin function: {func_name} with args: {kwargs}")
        # collects the error handling into a common place.
        if not hasattr(self.module(), func_name):
            raise exceptions.AdapterDoesntSupportFunctionError(
                f"Sorry, {self.name} doesn't support {func_name}."
            )
        return (getattr(self.module(), func_name)(**kwargs))
