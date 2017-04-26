""" Base class for OTIO plugins that are exposed by manifests. """

import os
import imp

from .. import (
    core,
    exceptions,
)


class PythonPlugin(core.SerializeableObject):
    """ A class of plugin that is encoded in a python module, exposed via a
    manifest.
    """

    _serializeable_label = "PythonPlugin.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
    ):
        core.SerializeableObject.__init__(self)
        self.name = name
        self.execution_scope = execution_scope
        self.filepath = filepath
        self._json_path = None
        self._module = None

    name = core.serializeable_field("name", str, "Adapter name.")
    execution_scope = core.serializeable_field(
        "execution_scope",
        str,
        doc=(
            "Describes whether this adapter is executed in the current python"
            " process or in a subshell.  Options are: "
            "['in process', 'out of process']."
        )
    )
    filepath = core.serializeable_field(
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
                        self
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
