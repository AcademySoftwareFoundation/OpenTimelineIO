# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""This adapter lets you read and write native .otio files"""

from .. import (
    core,
    versioning
)

import os

DEFAULT_VERSION_ENVVAR = "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"


def read_from_file(filepath):
    """
    De-serializes an OpenTimelineIO object from a file

    Args:
        filepath (str): The path to an otio file to read from

    Returns:
        OpenTimeline: An OpenTimeline object
    """
    return core.deserialize_json_from_file(filepath)


def read_from_string(input_str):
    """
    De-serializes an OpenTimelineIO object from a json string

    Args:
        input_str (str): A string containing json serialized otio contents

    Returns:
        OpenTimeline: An OpenTimeline object
    """
    return core.deserialize_json_from_string(input_str)


def write_to_string(input_otio, target_schema_versions=None, indent=4):
    """
    Serializes an OpenTimelineIO object into a string

    Args:
        input_otio (OpenTimeline): An OpenTimeline object
        indent (int): number of spaces for each json indentation level. Use\
            -1 for no indentation or newlines.

    If target_schema_versions is None and the environment variable
    "{}" is set, will read a map out of
    that for downgrade target.  The variable should be of the form FAMILY:LABEL,
    for example "MYSTUDIO:JUNE2022".

    Returns:
        str: A json serialized string representation
    """.format(DEFAULT_VERSION_ENVVAR)

    if target_schema_versions is None and DEFAULT_VERSION_ENVVAR in os.environ:
        version_envvar = os.environ[DEFAULT_VERSION_ENVVAR]
        family, label = version_envvar.split(":")
        # @TODO: something isn't right, I shouldn't need to do this extra hop...
        #        if I don't, I end up with an AnyDictionary instead of a python
        #        {}, which pybind doesn't quite map into the std::map the way
        #        I'd hope when calling serialize_json_to_string()
        target_schema_versions = versioning.fetch_map(family, label)
        d = {}
        d.update(target_schema_versions)
        target_schema_versions = d

    return core.serialize_json_to_string(
            input_otio,
            target_schema_versions,
            indent
    )


def write_to_file(
        input_otio,
        filepath,
        target_schema_versions=None,
        indent=4
):
    """
    Serializes an OpenTimelineIO object into a file

    Args:

        input_otio (OpenTimeline): An OpenTimeline object
        filepath (str): The name of an otio file to write to
        indent (int): number of spaces for each json indentation level.\
            Use -1 for no indentation or newlines.

    If target_schema_versions is None and the environment variable
    "{}" is set, will read a map out of
    that for downgrade target.  The variable should be of the form FAMILY:LABEL,
    for example "MYSTUDIO:JUNE2022".

    Returns:
        bool: Write success

    Raises:
        ValueError: on write error
    """.format(DEFAULT_VERSION_ENVVAR)

    if target_schema_versions is None and DEFAULT_VERSION_ENVVAR in os.environ:
        version_envvar = os.environ[DEFAULT_VERSION_ENVVAR]
        family, label = version_envvar.split(":")
        target_schema_versions = versioning.fetch_map(family, label)

    return core.serialize_json_to_file(
            input_otio,
            filepath,
            target_schema_versions,
            indent
    )
