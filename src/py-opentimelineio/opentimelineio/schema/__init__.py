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

# flake8: noqa

"""User facing classes."""

from .. _otio import (
    Clip,
    Effect,
    TimeEffect,
    LinearTimeWarp,
    ExternalReference,
    FreezeFrame,
    Gap,
    GeneratorReference,
    Marker,
    MissingReference,
    SerializableCollection,
    Stack,
    Timeline,
    Track,
    Transition
)

MarkerColor = Marker.Color
TrackKind = Track.Kind
TransitionTypes = Transition.Type
NeighborGapPolicy = Track.NeighborGapPolicy

from . schemadef import (
    SchemaDef
)

from . import (
    clip, effect, external_reference,
    generator_reference, marker,
    serializable_collection,
    stack, timeline, track,
    transition
)

track.TrackKind = TrackKind

def timeline_from_clips(clips):
    """Convenience for making a single track timeline from a list of clips."""

    trck = Track(children=clips)
    return Timeline(tracks=[trck])
