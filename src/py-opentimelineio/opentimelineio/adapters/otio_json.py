# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""This adapter lets you read and write native .otio files"""

from .. import (
    core
)


# @TODO: Implement out of process plugins that hand around JSON


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


def write_to_string(input_otio, downgrade_version_manifest=None, indent=4):
    """
    Serializes an OpenTimelineIO object into a string

    Args:
        input_otio (OpenTimeline): An OpenTimeline object
        indent (int): number of spaces for each json indentation level. Use\
            -1 for no indentation or newlines.

    Returns:
        str: A json serialized string representation
    """
    return core.serialize_json_to_string(
            input_otio,
            downgrade_version_manifest or {},
            indent
    )


def write_to_file(
        input_otio,
        filepath,
        downgrade_version_manifest=None,
        indent=4
):
    """
    Serializes an OpenTimelineIO object into a file

    Args:

        input_otio (OpenTimeline): An OpenTimeline object
        filepath (str): The name of an otio file to write to
        indent (int): number of spaces for each json indentation level.\
            Use -1 for no indentation or newlines.

    Returns:
        bool: Write success

    Raises:
        ValueError: on write error
    """
    return core.serialize_json_to_file(input_otio, filepath, indent)
