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

# This code has been taken from opentimelineio's exten_rv rv adapter
# and converted to work interactively in RV.
#
# TODO: We would like to move this back into opentimelineio's rv adapter
# such that we can use this both interactively as well as standalone
#

from rv import commands
from rv import extra_commands

import opentimelineio as otio


class NoMappingForOtioTypeError(otio.exceptions.OTIOError):
    pass


def read_otio_file(otio_file):
    """
    Main entry point to expand a given otio (or file otio can read)
    into the current RV session.

    Returns the top level node created that represents this otio
    timeline.
    """
    input_otio = otio.adapters.read_from_file(otio_file)

    return create_rv_node_from_otio(input_otio)


def create_rv_node_from_otio(otio_obj, track_kind=None):
    WRITE_TYPE_MAP = {
        otio.schema.Timeline: _create_timeline,
        otio.schema.Stack: _create_stack,
        otio.schema.Track: _create_track,
        otio.schema.Clip: _create_item,
        otio.schema.Gap: _create_item,
        otio.schema.Transition: _create_transition,
        otio.schema.SerializableCollection: _create_collection,
    }

    if type(otio_obj) in WRITE_TYPE_MAP:
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, track_kind)

    raise NoMappingForOtioTypeError(
        str(type(otio_obj)) + " on object: {}".format(otio_obj)
    )


def _create_dissolve(pre_item, in_dissolve, post_item, track_kind=None):
    rv_trx = commands.newNode("CrossDissolve", in_dissolve.name or "dissolve")
    extra_commands.setUIName(rv_trx, str(in_dissolve.name or "dissolve"))

    commands.setFloatProperty(rv_trx + ".parameters.startFrame", [1.0], True)

    num_frames = (in_dissolve.in_offset + in_dissolve.out_offset).rescaled_to(
        pre_item.trimmed_range().duration.rate
    ).value

    commands.setFloatProperty(rv_trx + ".parameters.numFrames",
                              [float(num_frames)],
                              True)

    commands.setFloatProperty(rv_trx + ".output.fps",
                              [float(pre_item.trimmed_range().duration.rate)],
                              True)

    pre_item_rv = create_rv_node_from_otio(pre_item, track_kind)

    post_item_rv = create_rv_node_from_otio(post_item, track_kind)

    node_to_insert = post_item_rv

    if (
        hasattr(pre_item, "media_reference") and
        pre_item.media_reference and
        pre_item.media_reference.available_range and
        hasattr(post_item, "media_reference") and
        post_item.media_reference and
        post_item.media_reference.available_range and
        (
            post_item.media_reference.available_range.start_time.rate !=
            pre_item.media_reference.available_range.start_time.rate
        )
    ):
        # write a retime to make sure post_item is in the timebase of pre_item
        rt_node = commands.newNode("Retime", "transition_retime")
        rt_node.setTargetFps(
            pre_item.media_reference.available_range.start_time.rate
        )

        post_item_rv = create_rv_node_from_otio(post_item, track_kind)

        rt_node.addInput(post_item_rv)
        node_to_insert = rt_node

    commands.setNodeInputs(rv_trx, [pre_item_rv, node_to_insert])
    _add_metadata_to_node(in_dissolve, rv_trx)
    return rv_trx


def _create_transition(pre_item, in_trx, post_item, track_kind=None):
    trx_map = {
        otio.schema.TransitionTypes.SMPTE_Dissolve: _create_dissolve,
    }

    if in_trx.transition_type not in trx_map:
        return

    return trx_map[in_trx.transition_type](
        pre_item,
        in_trx,
        post_item,
        track_kind
    )


def _create_stack(in_stack, track_kind=None):
    new_stack = commands.newNode("RVStackGroup", in_stack.name or "tracks")
    extra_commands.setUIName(new_stack, str(in_stack.name or "tracks"))

    new_inputs = []
    for seq in in_stack:
        result = create_rv_node_from_otio(seq, track_kind)
        if result:
            new_inputs.append(result)

    commands.setNodeInputs(new_stack, new_inputs)
    _add_metadata_to_node(in_stack, new_stack)
    return new_stack


def _create_track(in_seq, _=None):
    new_seq = commands.newNode("RVSequenceGroup", str(in_seq.name or "track"))
    extra_commands.setUIName(new_seq, str(in_seq.name or "track"))

    items_to_serialize = otio.algorithms.track_with_expanded_transitions(
        in_seq
    )

    track_kind = in_seq.kind

    new_inputs = []
    for thing in items_to_serialize:
        if isinstance(thing, tuple):
            result = _create_transition(*thing, track_kind=track_kind)
        elif thing.duration().value == 0:
            continue
        else:
            result = create_rv_node_from_otio(thing, track_kind)

        if result:
            new_inputs.append(result)

    commands.setNodeInputs(new_seq, new_inputs)
    _add_metadata_to_node(in_seq, new_seq)
    return new_seq


def _create_timeline(tl, _=None):
    return create_rv_node_from_otio(tl.tracks)


def _create_collection(collection, track_kind=None):
    results = []
    for item in collection:
        result = create_rv_node_from_otio(item, track_kind)
        if result:
            results.append(result)

    if results:
        return results[0]


def _create_media_reference(item, track_kind=None):
    if hasattr(item, "media_reference") and item.media_reference:
        if isinstance(item.media_reference, otio.schema.ExternalReference):
            media = [str(item.media_reference.target_url)]
            if track_kind == otio.schema.TrackKind.Audio:
                # Create blank video media to accompany audio for valid source
                blank = _create_movieproc(item.available_range())
                # Appending blank to media promotes name of audio file in RV
                media.append(blank)

            return media
        elif isinstance(item.media_reference, otio.schema.GeneratorReference):
            if item.media_reference.generator_kind == "SMPTEBars":
                kind = "smptebars"
                return [_create_movieproc(item.available_range(), kind)]

    return None


def _create_item(it, track_kind=None):
    range_to_read = it.trimmed_range()

    if not range_to_read:
        raise otio.exceptions.OTIOError(
            "No valid range on clip: {0}.".format(
                str(it)
            )
        )

    new_media = _create_media_reference(it, track_kind)
    if not new_media:
        kind = "smptebars"
        if isinstance(it, otio.schema.Gap):
            kind = "blank"
        new_media = [_create_movieproc(range_to_read, kind)]

    try:
        src = commands.addSourceVerbose(new_media)
    except Exception as e:
        # Perhaps the media was missing, if so, lets load an error
        # source
        print('ERROR: {}'.format(e))
        error_media = _create_movieproc(range_to_read, 'smptebars')
        src = commands.addSourceVerbose([error_media])

    src_group = commands.nodeGroup(src)

    extra_commands.setUIName(src_group, str(it.name or "clip"))

    # Add otio metadata to this group and the source
    _add_metadata_to_node(it, src_group)
    if hasattr(it, "media_reference") and it.media_reference:
        _add_metadata_to_node(it.media_reference, src)

    # because OTIO has no global concept of FPS, the rate of the duration is
    # used as the rate for the range of the source.
    # RationalTime.value_rescaled_to returns the time value of the object in
    # time rate of the argument.
    cut_in = range_to_read.start_time.value_rescaled_to(
        range_to_read.duration
    )
    commands.setIntProperty(src + ".cut.in", [int(cut_in)])

    cut_out = range_to_read.end_time_inclusive().value_rescaled_to(
        range_to_read.duration
    )
    commands.setIntProperty(src + ".cut.out", [int(cut_out)])

    commands.setFloatProperty(src + ".group.fps",
                              [float(range_to_read.duration.rate)])

    return src_group


def _create_movieproc(time_range, kind="blank"):
    movieproc = "{},start={},end={},fps={}.movieproc".format(
        kind,
        time_range.start_time.value,
        time_range.end_time_inclusive().value,
        time_range.duration.rate
    )
    return movieproc


def _add_metadata_to_node(item, rv_node):
    """
    Add metadata from otio "item" to rv_node
    """
    if item.metadata:
        otio_metadata_property = rv_node + ".otio.metadata"
        otio_metadata = otio.core.serialize_json_to_string(item.metadata,
                                                           indent=-1)
        commands.newProperty(otio_metadata_property, commands.StringType, 1)
        commands.setStringProperty(otio_metadata_property,
                                   [otio_metadata],
                                   True)
