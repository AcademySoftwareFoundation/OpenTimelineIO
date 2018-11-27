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

# flake8: noqa

"""User facing classes."""

from .missing_reference import (
    MissingReference
)
from .external_reference import (
    ExternalReference
)
from .clip import (
    Clip,
)
from .track import (
    Track,
    TrackKind,
    NeighborGapPolicy,
)
from .stack import (
    Stack,
)
from .timeline import (
    Timeline,
    timeline_from_clips,
)
from .marker import (
    Marker,
    MarkerColor,
)
from .gap import (
    Gap,
)
from .effect import (
    Effect,
    TimeEffect,
    LinearTimeWarp,
    FreezeFrame,
)
from .transition import (
    Transition,
    TransitionTypes,
)
from .serializable_collection import (
    SerializableCollection
)
from .generator_reference import (
    GeneratorReference
)
from .schemadef import (
    SchemaDef
)
