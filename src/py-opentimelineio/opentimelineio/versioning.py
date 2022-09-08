# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
import copy

from . import (
    core,
    plugins
)


def full_map():
    """Return the full map of schema version sets, including core and plugins.
    Organized as follows:

    .. code-block:: python

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

    .. code-block:: python

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
    """Fetch the version map for the given family and label.  OpenTimelineIO
    includes a built in family called "OTIO_CORE", this is compiled into the
    C++ core and represents the core interchange schemas of OpenTimelineIO.

    Users may define more family/label/schema:version mappings by way of the
    version manifest plugins.

    Returns a dictionary mapping Schema name to schema version, like:

    .. code-block:: python

        {
            "Clip": 2,
            "Timeline": 1,
            ...
        }

    """

    if family == "OTIO_CORE":
        src = core.release_to_schema_version_map()
    else:
        src = plugins.ActiveManifest().version_manifests[family]

    return copy.deepcopy(src[label])
