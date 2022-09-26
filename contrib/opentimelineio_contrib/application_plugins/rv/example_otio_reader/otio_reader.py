# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

# This code has been taken from opentimelineio's exten_rv rv adapter
# and converted to work interactively in RV.
#
# TODO: We would like to move this back into opentimelineio's rv adapter
# such that we can use this both interactively as well as standalone
#

from rv import commands
from rv import extra_commands

import opentimelineio as otio
from contextlib import contextmanager


@contextmanager
def set_context(context, **kwargs):
    old_context = context.copy()
    context.update(**kwargs)

    try:
        yield
    finally:
        context.clear()
        context.update(old_context)


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


def create_rv_node_from_otio(otio_obj, context=None):
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
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, context)

    raise NoMappingForOtioTypeError(
        str(type(otio_obj)) + f" on object: {otio_obj}"
    )


def _create_dissolve(pre_item, in_dissolve, post_item, context=None):
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

    pre_item_rv = create_rv_node_from_otio(pre_item, context)

    post_item_rv = create_rv_node_from_otio(post_item, context)

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

        post_item_rv = create_rv_node_from_otio(post_item, context)

        rt_node.addInput(post_item_rv)
        node_to_insert = rt_node

    commands.setNodeInputs(rv_trx, [pre_item_rv, node_to_insert])
    _add_metadata_to_node(in_dissolve, rv_trx)
    return rv_trx


def _create_transition(pre_item, in_trx, post_item, context=None):
    trx_map = {
        otio.schema.TransitionTypes.SMPTE_Dissolve: _create_dissolve,
    }

    if in_trx.transition_type not in trx_map:
        return

    return trx_map[in_trx.transition_type](
        pre_item,
        in_trx,
        post_item,
        context
    )


def _create_stack(in_stack, context=None):
    new_stack = commands.newNode("RVStackGroup", in_stack.name or "tracks")
    extra_commands.setUIName(new_stack, str(in_stack.name or "tracks"))

    new_inputs = []
    for seq in in_stack:
        result = create_rv_node_from_otio(seq, context)
        if result:
            new_inputs.append(result)

    commands.setNodeInputs(new_stack, new_inputs)
    _add_metadata_to_node(in_stack, new_stack)
    return new_stack


def _create_track(in_seq, context=None):
    context = context or {}

    new_seq = commands.newNode("RVSequenceGroup", str(in_seq.name or "track"))
    extra_commands.setUIName(new_seq, str(in_seq.name or "track"))

    items_to_serialize = otio.algorithms.track_with_expanded_transitions(
        in_seq
    )

    with set_context(context, track_kind=in_seq.kind):
        new_inputs = []
        for thing in items_to_serialize:
            if isinstance(thing, tuple):
                result = _create_transition(*thing, context=context)
            elif thing.duration().value == 0:
                continue
            else:
                result = create_rv_node_from_otio(thing, context)

            if result:
                new_inputs.append(result)

        commands.setNodeInputs(new_seq, new_inputs)
        _add_metadata_to_node(in_seq, new_seq)

    return new_seq


def _get_global_transform(tl):
    # since there's no global scale in otio, use the first source with
    # bounds as the global bounds
    def find_display_bounds(tl):
        for clip in tl.clip_if():
            try:
                bounds = clip.media_reference.available_image_bounds
                if bounds:
                    return bounds
            except AttributeError:
                continue
        return None

    bounds = find_display_bounds(tl)
    if bounds is None:
        return {}

    translate = bounds.center()
    scale = bounds.max - bounds.min

    # RV's global coordinate system has a width and height of 1 where the
    # width will be scaled to the image aspect ratio.  So scale globally by
    # height. The source width will later be scaled to aspect ratio.
    global_scale = otio.schema.V2d(1.0 / scale.y, 1.0 / scale.y)

    return {
        'global_scale': global_scale,
        'global_translate': translate * global_scale,
    }


def _create_timeline(tl, context=None):
    context = context or {}

    with set_context(
        context,
        **_get_global_transform(tl)
    ):
        return create_rv_node_from_otio(tl.tracks, context)


def _create_collection(collection, context=None):
    results = []
    for item in collection:
        result = create_rv_node_from_otio(item, context)
        if result:
            results.append(result)

    if results:
        return results[0]


def _create_media_reference(item, context=None):
    context = context or {}
    if hasattr(item, "media_reference") and item.media_reference:
        if isinstance(item.media_reference, otio.schema.ExternalReference):
            media = [str(item.media_reference.target_url)]
            if context.get('track_kind') == otio.schema.TrackKind.Audio:
                # Create blank video media to accompany audio for valid source
                blank = _create_movieproc(item.available_range())
                # Appending blank to media promotes name of audio file in RV
                media.append(blank)

            return media
        elif isinstance(item.media_reference,
                        otio.schema.ImageSequenceReference):
            frame_sub = "%0{n}d".format(
                n=item.media_reference.frame_zero_padding
            )

            media = [
                str(item.media_reference.abstract_target_url(symbol=frame_sub))
            ]

            return media
        elif isinstance(item.media_reference, otio.schema.GeneratorReference):
            if item.media_reference.generator_kind == "SMPTEBars":
                kind = "smptebars"
                return [_create_movieproc(item.available_range(), kind)]

    return None


def _create_item(it, context=None):
    context = context or {}
    range_to_read = it.trimmed_range()

    if not range_to_read:
        raise otio.exceptions.OTIOError(
            "No valid range on clip: {}.".format(
                str(it)
            )
        )

    new_media = _create_media_reference(it, context)
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
        print(f'ERROR: {e}')
        error_media = _create_movieproc(range_to_read, 'smptebars')
        src = commands.addSourceVerbose([error_media])

    src_group = commands.nodeGroup(src)

    extra_commands.setUIName(src_group, str(it.name or "clip"))

    # Add otio metadata to this group and the source
    _add_metadata_to_node(it, src_group)
    if hasattr(it, "media_reference") and it.media_reference:
        _add_metadata_to_node(it.media_reference, src)

    in_frame = out_frame = None
    if hasattr(it, "media_reference") and it.media_reference:
        if isinstance(it.media_reference, otio.schema.ImageSequenceReference):
            in_frame, out_frame = \
                it.media_reference.frame_range_for_time_range(
                    range_to_read
                )

        _add_source_bounds(it.media_reference, src, context)

    if not in_frame and not out_frame:
        # because OTIO has no global concept of FPS, the rate of the duration
        # is used as the rate for the range of the source.
        in_frame = otio.opentime.to_frames(
            range_to_read.start_time,
            rate=range_to_read.duration.rate
        )
        out_frame = otio.opentime.to_frames(
            range_to_read.end_time_inclusive(),
            rate=range_to_read.duration.rate
        )

    commands.setIntProperty(src + ".cut.in", [in_frame])
    commands.setIntProperty(src + ".cut.out", [out_frame])

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


def _add_source_bounds(media_ref, src, context):
    bounds = media_ref.available_image_bounds
    if not bounds:
        return

    global_scale = context.get('global_scale')
    global_translate = context.get('global_translate')
    if global_scale is None or global_translate is None:
        return

    # A width of 1.0 in RV means draw to the aspect ratio, so scale the
    # width by the inverse of the aspect ratio
    #
    media_info = commands.sourceMediaInfo(src)
    height = media_info['height']
    aspect_ratio = 1.0 if height == 0 else media_info['width'] / height

    translate = bounds.center() * global_scale - global_translate
    scale = (bounds.max - bounds.min) * global_scale

    transform_node = extra_commands.associatedNode('RVTransform2D', src)

    commands.setFloatProperty(
        f"{transform_node}.transform.scale",
        [scale.x / aspect_ratio, scale.y]
    )
    commands.setFloatProperty(
        f"{transform_node}.transform.translate",
        [translate.x, translate.y]
    )

    # write the bounds global_scale and global_translate to the node so we can
    # preserve the original values if we round-trip
    commands.newProperty(
        f"{transform_node}.otio.global_scale",
        commands.FloatType,
        2
    )
    commands.newProperty(
        f"{transform_node}.otio.global_translate",
        commands.FloatType,
        2
    )
    commands.setFloatProperty(
        f"{transform_node}.otio.global_scale",
        [global_scale.x, global_scale.y],
        True
    )
    commands.setFloatProperty(
        f"{transform_node}.otio.global_translate",
        [global_translate.x, global_translate.y],
        True
    )


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
