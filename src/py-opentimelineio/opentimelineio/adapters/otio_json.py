#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

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


def write_to_string(input_otio, indent=4):
    """
    Serializes an OpenTimelineIO object into a string

    Args:
        input_otio (OpenTimeline): An OpenTimeline object
        indent (int): number of spaces for each json indentation level. Use
            -1 for no indentation or newlines.

    Returns:
        str: A json serialized string representation
    """
    return core.serialize_json_to_string(input_otio, indent)


def write_to_file(input_otio, filepath, indent=4):
    """
    Serializes an OpenTimelineIO object into a file

    Args:
        input_otio (OpenTimeline): An OpenTimeline object
        filepath (str): The name of an otio file to write to
        indent (int): number of spaces for each json indentation level. Use
            -1 for no indentation or newlines.

    Returns:
        bool: Write success

    Raises:
        ValueError: on write error
    """
    return core.serialize_json_to_file(input_otio, filepath, indent)
