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

"""Internal implementation details of OpenTimelineIO."""

# flake8: noqa

from . import (
    serializable_object,
)
from .serializable_object import (
    SerializableObject,
    serializable_field,
    deprecated_field,
)
from .composable import (
    Composable
)
from .item import (
    Item
)
from . import composition
from .composition import (
    Composition,
)
from . import type_registry
from .type_registry import (
    register_type,
    upgrade_function_for,
    schema_name_from_label,
    schema_version_from_label,
    instance_from_schema,
)
from .json_serializer import (
    serialize_json_to_string,
    serialize_json_to_file,
    deserialize_json_from_string,
    deserialize_json_from_file,
)
from .media_reference import (
    MediaReference,
)
