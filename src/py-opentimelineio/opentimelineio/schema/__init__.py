# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

# flake8: noqa

"""User facing classes."""

from .. _otio import (
    Box2d,
    Clip,
    Effect,
    TimeEffect,
    LinearTimeWarp,
    ExternalReference,
    FreezeFrame,
    Gap,
    GeneratorReference,
    ImageSequenceReference,
    Marker,
    MissingReference,
    SerializableCollection,
    Stack,
    Timeline,
    Track,
    Transition,
    V2d,
)

MarkerColor = Marker.Color
TrackKind = Track.Kind
TransitionTypes = Transition.Type
NeighborGapPolicy = Track.NeighborGapPolicy

from . schemadef import (
    SchemaDef
)

from . import (
    box2d,
    clip,
    effect,
    external_reference,
    generator_reference,
    image_sequence_reference,
    marker,
    serializable_collection,
    timeline,
    transition,
    v2d,
)

track.TrackKind = TrackKind

def timeline_from_clips(clips):
    """Convenience for making a single track timeline from a list of clips."""

    trck = Track(children=clips)
    return Timeline(tracks=[trck])

__all__ = [
    'Box2d',
    'Clip',
    'Effect',
    'TimeEffect',
    'LinearTimeWarp',
    'ExternalReference',
    'FreezeFrame',
    'Gap',
    'GeneratorReference',
    'ImageSequenceReference',
    'Marker',
    'MissingReference',
    'SerializableCollection',
    'Stack',
    'Timeline',
    'Transition',
    'SchemaDef',
    'timeline_from_clips',
    'V2d'
]
