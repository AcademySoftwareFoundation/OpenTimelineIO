# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

# flake8: noqa

"""User facing classes."""

from .. _otio import (
    AudioMixMatrix,
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
    IndexStreamAddress,
    StreamChannelIndexStreamAddress,
    Marker,
    MissingReference,
    SerializableCollection,
    Stack,
    StreamAddress,
    StreamInfo,
    StreamMapper,
    StreamSelector,
    StringStreamAddress,
    Timeline,
    Track,
    Transition,
    V2d,
)

MarkerColor = Marker.Color
StreamIdentifier = StreamInfo.Identifier
TrackKind = Track.Kind
TransitionTypes = Transition.Type
NeighborGapPolicy = Track.NeighborGapPolicy

from . schemadef import (
    SchemaDef
)

from . import (
    audio_mix_matrix,
    box2d,
    clip,
    effect,
    external_reference,
    generator_reference,
    image_sequence_reference,
    index_stream_address,
    stream_channel_index_stream_address,
    marker,
    serializable_collection,
    stream_address,
    stream_info,
    stream_mapper,
    stream_selector,
    string_stream_address,
    timeline,
    transition,
    v2d,
)

def timeline_from_clips(clips):
    """Convenience for making a single track timeline from a list of clips."""

    trck = Track(children=clips)
    return Timeline(tracks=[trck])

__all__ = [
    'AudioMixMatrix',
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
    'IndexStreamAddress',
    'StreamChannelIndexStreamAddress',
    'Marker',
    'MissingReference',
    'SerializableCollection',
    'SchemaDef',
    'Stack',
    'StreamAddress',
    'StreamIdentifier',
    'StreamInfo',
    'StreamMapper',
    'StreamSelector',
    'StringStreamAddress',
    'Timeline',
    'Transition',
    'timeline_from_clips',
    'V2d',
    'Track',
]
