
from .. import (
    core,
    exceptions,
    plugins,
    schemadef
)


@core.register_type
class SchemaDef(plugins.PythonPlugin):
    _serializable_label = "SchemaDef.1"

    def __init__(
        self,
        name=None,
        execution_scope=None,
        filepath=None,
    ):
        super(SchemaDef, self).__init__(name, execution_scope, filepath)

    def module(self):
        """
        Return the module object for this schemadef plugin.
        If the module hasn't already been imported, it is imported and
        injected into the otio.schemadefs namespace as a side-effect.
        (redefines PythonPlugin.module())
        """

        if not self._module:
            self._module = self._imported_module("schemadef")
            if self.name:
                schemadef._add_schemadef_module(self.name, self._module)

        return self._module


def available_schemadef_names():
    """Return a string list of the available schemadefs."""

    return [str(sd.name) for sd in plugins.ActiveManifest().schemadefs]


def from_name(name):
    """Fetch the schemadef plugin object by the name of the schema directly."""

    try:
        return plugins.ActiveManifest().from_name(name, kind_list="schemadefs")
    except exceptions.NotSupportedError:
        raise exceptions.NotSupportedError(
            "schemadef not supported: {}, available: {}".format(
                name,
                available_schemadef_names()
            )
        )


def module_from_name(name):
    """Fetch the plugin's module by the name of the schemadef.

    Will load the plugin if it has not already been loaded.  Reading a file that
    contains the schemadef will also trigger a load of the plugin.
    """
    plugin = from_name(name)
    return plugin.module()
