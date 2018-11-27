#
# Copyright 2017 Pixar Animation Studios
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

"""Serializer for SerializableObjects to JSON

Used for the otio_json adapter as well as for plugins and manifests.
"""

import json

from . import (
    SerializableObject,
    type_registry,
)

from .unknown_schema import UnknownSchema

from .. import (
    exceptions,
    opentime,
)


# @TODO: Handle file version drifting


class _SerializableObjectEncoder(json.JSONEncoder):

    """ Encoder for the SerializableObject OTIO Class and its descendents. """

    def default(self, obj):
        for typename, encfn in _ENCODER_LIST:
            if isinstance(obj, typename):
                return encfn(obj)

        return json.JSONEncoder.default(self, obj)


def serialize_json_to_string(root, indent=4):
    """Serialize a tree of SerializableObject to JSON.

    Returns a JSON string.
    """

    return _SerializableObjectEncoder(
        sort_keys=True,
        indent=indent
    ).encode(root)


def serialize_json_to_file(root, to_file):
    """
    Serialize a tree of SerializableObject to JSON.

    Writes the result to the given file path.
    """

    content = serialize_json_to_string(root)

    with open(to_file, 'w') as file_contents:
        file_contents.write(content)

# @{ Encoders


def _encoded_serializable_object(input_otio):
    if not input_otio._serializable_label:
        raise exceptions.InvalidSerializableLabelError(
            input_otio._serializable_label
        )
    result = {
        "OTIO_SCHEMA": input_otio._serializable_label,
    }
    result.update(input_otio._data)
    return result


def _encoded_unknown_schema_object(input_otio):
    orig_label = input_otio.data.get(UnknownSchema._original_label)
    if not orig_label:
        raise exceptions.InvalidSerializableLabelError(
            orig_label
        )
    # result is just a dict, not a SerializableObject
    result = {}
    result.update(input_otio.data)
    result["OTIO_SCHEMA"] = orig_label  # override the UnknownSchema label
    del result[UnknownSchema._original_label]
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


# Ordered list of functions for encoding OTIO objects to JSON.
# More particular cases should precede more general cases.
_ENCODER_LIST = [
    (opentime.RationalTime, _encoded_time),
    (opentime.TimeRange, _encoded_time_range),
    (opentime.TimeTransform, _encoded_transform),
    (UnknownSchema, _encoded_unknown_schema_object),
    (SerializableObject, _encoded_serializable_object)
]

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
# same pattern as SerializableObject.
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

        schema_name = type_registry.schema_name_from_label(schema_label)
        schema_version = type_registry.schema_version_from_label(schema_label)
        del dct["OTIO_SCHEMA"]

        return type_registry.instance_from_schema(
            schema_name,
            schema_version,
            dct
        )

    return dct


def deserialize_json_from_string(otio_string):
    """ Deserialize a string containing JSON to OTIO objects. """

    return json.loads(otio_string, object_hook=_as_otio)


def deserialize_json_from_file(otio_filepath):
    """ Deserialize the file at otio_filepath containing JSON to OTIO.  """

    with open(otio_filepath, 'r') as file_contents:
        result = deserialize_json_from_string(file_contents.read())
        result._json_path = otio_filepath
        return result
