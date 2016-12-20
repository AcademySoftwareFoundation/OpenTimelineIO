"""
This adapter lets you read and write native .otio files
"""

import json

from .. import (
    exceptions,
    opentime,
    core
)


def read_from_file(filepath):
    return _deserialize_from_file(filepath)


def read_from_string(input_str):
    return _deserialize_from_string(input_str)


def write_to_string(input_otio):
    return _serialize_to_string(input_otio)


def write_to_file(input_otio, filepath):
    return _serialize_to_file(input_otio, filepath)

# @TODO: Implement out of process plugins that hand around JSON
# @TODO: Handle file version drifting


class _SerializeableObjectEncoder(json.JSONEncoder):

    """ Encoder for the SerializeableObject OTIO Class and its descendents. """

    def default(self, obj):
        for typename, encfn in _ENCODER_MAP.items():
            if isinstance(obj, typename):
                return encfn(obj)

        return json.JSONEncoder.default(self, obj)


def _serialize_to_string(root, sort_keys=True, indent=4):
    """
    Serialize a tree of SerializeableObject to JSON.  Returns a JSON string.
    """

    return _SerializeableObjectEncoder(
        sort_keys=sort_keys,
        indent=indent
    ).encode(root)


def _serialize_to_file(root, to_file):
    """
    Serialize a tree of SerializeableObject to JSON.

    Writes the result to the given file path.
    """

    content = _serialize_to_string(root)

    with open(to_file, 'w') as file_contents:
        file_contents.write(content)

# @{ Encoders


def _encoded_serializeable_object(input_otio):
    if not input_otio._serializeable_label:
        raise exceptions.InvalidSerializeableLabelError(
            input_otio._serializeable_label
        )
    result = {
        "OTIO_SCHEMA": input_otio._serializeable_label,
    }
    result.update(input_otio.data)
    return result


def _encoded_time(input_otio):
    return {
        "OTIO_SCHEMA": "RationalTime.1",
        'value': input_otio.value,
        'rate': input_otio.rate
    }


def _encoded_time_range(input_otio):
    return {
        "OTIO_SCHEMA": "TimeRange.1",
        'start_time': _encoded_time(input_otio.start_time),
        'duration': _encoded_time(input_otio.duration)
    }


def _encoded_transform(input_otio):
    return {
        "OTIO_SCHEMA": "TimeTransform.1",
        'offset': _encoded_time(input_otio.offset),
        'scale': input_otio.scale,
        'rate': input_otio.rate
    }
# @}


# Map of functions for encoding OTIO objects to JSON.
_ENCODER_MAP = {
    opentime.RationalTime: _encoded_time,
    opentime.TimeRange: _encoded_time_range,
    opentime.TimeTransform: _encoded_transform,
    core.SerializeableObject: _encoded_serializeable_object,
}

# @{ Decoders


def _decoded_time(input_otio):
    return opentime.RationalTime(
        input_otio['value'],
        input_otio['rate']
    )


def _decoded_time_range(input_otio):
    return opentime.TimeRange(
        input_otio['start_time'],
        input_otio['duration']
    )


def _decoded_transform(input_otio):
    return opentime.TimeTransform(
        input_otio['offset'],
        input_otio['scale']
    )
# @}


# Map of explicit decoder functions to schema labels (for opentime)
# because opentime is implemented with no knowledge of OTIO, it doesn't use the
# same pattern as SerializeableObject.
_DECODER_FUNCTION_MAP = {
    'RationalTime.1': _decoded_time,
    'TimeRange.1': _decoded_time_range,
    'TimeTransform.1': _decoded_transform,
}


def _as_otio(dct):
    """ Specialized JSON decoder for OTIO base Objects.  """

    if "OTIO_SCHEMA" in dct:
        schema_label = dct["OTIO_SCHEMA"]

        if schema_label in _DECODER_FUNCTION_MAP:
            return _DECODER_FUNCTION_MAP[schema_label](dct)

        schema_name = core.schema_name_from_label(schema_label)
        schema_version = core.schema_version_from_label(schema_label)
        del dct["OTIO_SCHEMA"]

        return core.instance_from_schema(schema_name, schema_version, dct)

    return dct


def _deserialize_from_string(otio_string):
    """ Deserialize a string containing JSON to OTIO objects. """

    json_data = json.loads(otio_string, object_hook=_as_otio)

    if json_data is {}:
        raise exceptions.CouldNotReadFileError

    return json_data


def _deserialize_from_file(otio_filepath):
    """ Deserialize the file at otio_filepath containing JSON to OTIO.  """

    with open(otio_filepath, 'r') as file_contents:
        result = _deserialize_from_string(file_contents.read())
        result._json_path = otio_filepath
        return result
