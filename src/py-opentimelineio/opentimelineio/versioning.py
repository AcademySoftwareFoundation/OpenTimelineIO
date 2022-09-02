import copy

from . import (
    core,
    plugins
)


def full_map():
    """Return the full map of schema version sets, including core and plugins.

    Organized as follows:
    {
        "FAMILY_NAME": {
            "LABEL": {
                "SchemaName": schemaversion,
                "Clip": 2,
                "Timeline": 3,
                ...
            }
        }
    }

    The "OTIO_CORE" family is always provided and represents the built in
    schemas defined in the C++ core.
    IE:
    {
            "OTIO_CORE": {
                "0.15.0": {
                    "Clip": 2,
                    ...
                }
            }
    }
    """
    result = copy.deepcopy(plugins.ActiveManifest().version_manifests)
    result.update(
        {
            "OTIO_CORE": core.release_to_schema_version_map(),
        }
    )
    return result


def fetch_map(family, label):
    if family == "OTIO_CORE":
        src = core.release_to_schema_version_map()
    else:
        src = plugins.ActiveManifest().version_manifests[family]

    return copy.deepcopy(src[label])
