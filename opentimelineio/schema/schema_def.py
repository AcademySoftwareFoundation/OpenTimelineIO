
from .. import (
    core,
    exceptions,
    plugins
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
        plugins.PythonPlugin.__init__(self, name, execution_scope, filepath)


def available_schemadef_names():
    """Return a string list of the available schemadefs."""

    return [str(sd.name) for sd in plugins.ActiveManifest().schemadefs]


def from_name(name):
    """Fetch the schemadef object by the name of the schema directly."""

    try:
        return plugins.ActiveManifest().from_name(name, kind_list="schemadefs")
    except exceptions.NotSupportedError:
        raise exceptions.NotSupportedError(
            "schemadef not supported: {}, available: {}".format(
                name,
                available_schemadef_names()
            )
        )
