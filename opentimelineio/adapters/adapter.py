import os
import imp

from .. import (
    core,
    exceptions,
)


@core.register_type
class Adapter(core.SerializeableObject):
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

    name = core.serializeable_field("name", str)
    execution_scope = core.serializeable_field("execution_scope", str)
    filepath = core.serializeable_field("filepath", str)
    suffixes = core.serializeable_field("suffixes", type([]))

    def module_abs_path(self):
        filepath = self.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.path.dirname(self._json_path), filepath)

        return filepath

    def module(self):
        mod = imp.load_source(
            "opentimelineio.adapters.{}".format(self.name),
            self.module_abs_path()
        )
        return mod

    def _execute_function(self, func_name, **kwargs):
        if not hasattr(self.module(), func_name):
            raise exceptions.AdapterDoesntSupportFunctionError(
                "Sorry, {} doesn't support {}.".format(self.name, func_name)
            )
        return (getattr(self.module(), func_name)(**kwargs))

    def read_from_file(self, filepath):
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
        return self._execute_function("read_from_string", input_str=input_str)

    def write_to_string(self, input_otio):
        return self._execute_function("write_to_string", input_otio=input_otio)
