"""Implementation of the OTIO internal `Adapter` system.

For information on writing adapters, please consult:
        https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
"""

import os
import imp

from .. import (
    core,
    exceptions,
)


@core.register_type
class Adapter(core.SerializeableObject):
    """Adapters convert between OTIO and other formats.

    Note that this class is not subclassed by adapters.  Rather, an adapter is
    a python module that implements at least one of the following functions:
        write_to_string(input_otio)
        write_to_file(input_otio, filepath) (optionally inferred)
        read_from_string(input_str)
        read_from_file(filepath) (optionally inferred)

    ...as well as a small json file that advertises the features of the adapter
    to OTIO.  This class serves as the wrapper around these modules internal
    to OTIO.  You should not need to extend this class to create new adapters
    for OTIO.

    For more information:
        https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
    """
    _serializeable_label = "Adapter.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
        suffixes=None
    ):
        core.SerializeableObject.__init__(self)
        self.name = name
        self.execution_scope = execution_scope
        self.filepath = filepath
        if suffixes is None:
            suffixes = []
        self.suffixes = suffixes
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
    suffixes = core.serializeable_field(
        "suffixes",
        type([]),
        doc="File suffixes associated with this adapter."
    )

    def module_abs_path(self):
        """Return an absolute path to the module implementing this adapter."""

        filepath = self.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.path.dirname(self._json_path), filepath)

        return filepath

    def _find_and_load_module(self):
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
            self._module = self._find_and_load_module()

        return self._module

    def _execute_function(self, func_name, **kwargs):
        """Execute func_name on this adapter with error checking."""

        # collects the error handling into a common place.
        if not hasattr(self.module(), func_name):
            raise exceptions.AdapterDoesntSupportFunctionError(
                "Sorry, {} doesn't support {}.".format(self.name, func_name)
            )
        return (getattr(self.module(), func_name)(**kwargs))

    def read_from_file(self, filepath):
        """Execute the read_from_file function on this adapter.

        If read_from_string exists, but not read_from_file, execute that with
        a trivial file object wrapper.
        """

        if (
            not hasattr(self.module(), "read_from_file") and
            hasattr(self.module(), "read_from_string")
        ):
            with open(filepath, 'r') as fo:
                contents = fo.read()
            return self._execute_function(
                "read_from_string",
                input_str=contents
            )

        return self._execute_function("read_from_file", filepath=filepath)

    def write_to_file(self, input_otio, filepath):
        """Execute the write_to_file function on this adapter.

        If write_to_string exists, but not write_to_file, execute that with
        a trivial file object wrapper.
        """

        if (
            not hasattr(self.module(), "write_to_file") and
            hasattr(self.module(), "write_to_string")
        ):
            result = self.write_to_string(input_otio)
            with open(filepath, 'w') as fo:
                fo.write(result)
            return filepath

        return self._execute_function(
            "write_to_file",
            input_otio=input_otio,
            filepath=filepath
        )

    def read_from_string(self, input_str):
        """Call the read_from_string function on this adapter."""

        return self._execute_function("read_from_string", input_str=input_str)

    def write_to_string(self, input_otio):
        """Call the write_to_string function on this adapter."""

        return self._execute_function("write_to_string", input_otio=input_otio)
