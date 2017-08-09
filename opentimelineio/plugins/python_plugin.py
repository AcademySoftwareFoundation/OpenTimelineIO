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

"""Base class for OTIO plugins that are exposed by manifests."""

import os
import imp

from .. import (
    core,
    exceptions,
)


class PythonPlugin(core.SerializableObject):
    """A class of plugin that is encoded in a python module, exposed via a
    manifest.
    """

    _serializable_label = "PythonPlugin.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
    ):
        core.SerializableObject.__init__(self)
        self.name = name
        self.execution_scope = execution_scope
        self.filepath = filepath
        self._json_path = None
        self._module = None

    name = core.serializable_field("name", str, "Adapter name.")
    execution_scope = core.serializable_field(
        "execution_scope",
        str,
        doc=(
            "Describes whether this adapter is executed in the current python"
            " process or in a subshell.  Options are: "
            "['in process', 'out of process']."
        )
    )
    filepath = core.serializable_field(
        "filepath",
        str,
        doc=(
            "Absolute path or relative path to adapter module from location of"
            " json."
        )
    )

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

    def _imported_module(self):
        """Load the module this adapter points at."""

        pyname = os.path.splitext(os.path.basename(self.module_abs_path()))[0]
        pydir = os.path.dirname(self.module_abs_path())

        (file_obj, pathname, description) = imp.find_module(pyname, [pydir])

        with file_obj:
            # this will reload the module if it has already been loaded.
            mod = imp.load_module(
                "opentimelineio.adapters.{}".format(self.name),
                file_obj,
                pathname,
                description
            )

            return mod

    def module(self):
        """Return the module object for this adapter. """

        if not self._module:
            self._module = self._imported_module()

        return self._module

    def _execute_function(self, func_name, **kwargs):
        """Execute func_name on this adapter with error checking."""

        # collects the error handling into a common place.
        if not hasattr(self.module(), func_name):
            raise exceptions.AdapterDoesntSupportFunctionError(
                "Sorry, {} doesn't support {}.".format(self.name, func_name)
            )
        return (getattr(self.module(), func_name)(**kwargs))
