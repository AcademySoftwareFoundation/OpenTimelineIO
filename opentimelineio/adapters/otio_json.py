""" This adapter lets you read and write native .otio files """

from .. import (
    core
)

def read_from_file(filepath):
    return core.deserialize_json_from_file(filepath)


def read_from_string(input_str):
    return core.deserialize_json_from_string(input_str)


def write_to_string(input_otio):
    return core.serialize_json_to_string(input_otio)


def write_to_file(input_otio, filepath):
    return core.serialize_json_to_file(input_otio, filepath)

# @TODO: Implement out of process plugins that hand around JSON
