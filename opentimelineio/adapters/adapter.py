"""Implementation of the OTIO internal `Adapter` system.

For information on writing adapters, please consult:
        https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
"""

from .. import (
    core,
    plugins,
)

@core.register_type
class Adapter(plugins.PythonPlugin):
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
        plugins.PythonPlugin.__init__(
            self,
            name,
            execution_scope,
            filepath
        )

        if suffixes is None:
            suffixes = []
        self.suffixes = suffixes

    suffixes = core.serializeable_field(
        "suffixes",
        type([]),
        doc="File suffixes associated with this adapter."
    )

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
