# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Adapter for reading and writing native .otio json files."""

from .. import (
    core,
    versioning,
    exceptions
)

import os

_DEFAULT_VERSION_ENVVAR = "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"


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


def _fetch_downgrade_map_from_env():
    version_envvar = os.environ[_DEFAULT_VERSION_ENVVAR]

    try:
        family, label = version_envvar.split(":")
    except ValueError:
        raise exceptions.InvalidEnvironmentVariableError(
            "Environment variable '{}' is incorrectly formatted with '{}'."
            "Variable must be formatted as 'FAMILY:LABEL'".format(
                _DEFAULT_VERSION_ENVVAR,
                version_envvar,
            )
        )

    try:
        # technically fetch_map returns an AnyDictionary, but the pybind11
        # code wrapping the call to the serializer expects a python
        # dictionary.  This turns it back into a normal dictionary.
        return dict(versioning.fetch_map(family, label))
    except KeyError:
        raise exceptions.InvalidEnvironmentVariableError(
            "Environment variable '{}' is requesting family '{}' and label"
            " '{}', however this combination does not exist in the "
            "currently loaded manifests.  Full version map: {}".format(
                _DEFAULT_VERSION_ENVVAR,
                family,
                label,
                versioning.full_map()
            )
        )


def write_to_string(input_otio, target_schema_versions=None, indent=4):
    """
    Serializes an OpenTimelineIO object into a string

    Args:
        input_otio (OpenTimeline): An OpenTimeline object
        indent (int): number of spaces for each json indentation level. Use\
            -1 for no indentation or newlines.

    If target_schema_versions is None and the environment variable
    "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL" is set, will read a map out of
    that for downgrade target.  The variable should be of the form
    FAMILY:LABEL, for example "MYSTUDIO:JUNE2022".

    Returns:
        str: A json serialized string representation

    Raises:
        otio.exceptions.InvalidEnvironmentVariableError: if there is a problem
        with the default environment variable
        "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL".
    """

    if (
            target_schema_versions is None
            and _DEFAULT_VERSION_ENVVAR in os.environ
    ):
        target_schema_versions = _fetch_downgrade_map_from_env()

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
    "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL" is set, will read a map out of
    that for downgrade target.  The variable should be of the form
    FAMILY:LABEL, for example "MYSTUDIO:JUNE2022".

    Returns:
        bool: Write success

    Raises:
        ValueError: on write error
        otio.exceptions.InvalidEnvironmentVariableError: if there is a problem
        with the default environment variable
        "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL".
    """

    if (
        target_schema_versions is None
        and _DEFAULT_VERSION_ENVVAR in os.environ
    ):
        target_schema_versions = _fetch_downgrade_map_from_env()

    return core.serialize_json_to_file(
        input_otio,
        filepath,
        target_schema_versions,
        indent
    )
