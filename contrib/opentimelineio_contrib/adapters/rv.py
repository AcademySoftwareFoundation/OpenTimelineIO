# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""RvSession Adapter harness"""

import subprocess
import os
import copy
import json

import opentimelineio as otio


# exception class @{
class NoMappingForOtioTypeError(otio.exceptions.OTIOError):
    pass
# @}


def write_to_file(input_otio, filepath):
    if "OTIO_RV_PYTHON_BIN" not in os.environ:
        raise RuntimeError(
            "'OTIO_RV_PYTHON_BIN' not set, please set this to path to "
            "py-interp within the RV installation."
        )

    if "OTIO_RV_PYTHON_LIB" not in os.environ:
        raise RuntimeError(
            "'OTIO_RV_PYTHON_LIB' not set, please set this to path to python "
            "directory within the RV installation."
        )

    # the adapter generates a simple JSON blob that gets turned into calls into
    # the RV API.
    simplified_data = generate_simplified_json(input_otio)

    base_environment = copy.deepcopy(os.environ)

    base_environment['PYTHONPATH'] = (
        os.pathsep.join(
            [
                # ensure that the rv adapter is on the pythonpath
                os.path.dirname(__file__),
            ]
        )
    )

    proc = subprocess.Popen(
        [
            base_environment["OTIO_RV_PYTHON_BIN"],
            '-m',
            'extern_rv',
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=base_environment
    )

    # for debugging
    # with open("/var/tmp/test.json", 'w') as fo:
    #     fo.write(json.dumps(simplified_data, sort_keys=True, indent=4))

    # If the subprocess fails before writing to stdin is complete, python will
    # throw a IOError exception.  If it fails after writing to stdin, there
    # won't be an exception.  Either way, the return code will be non-0 so the
    # rest of the code should catch the error case and print the (presumably)
    # helpful message from the subprocess.
    try:
        proc.stdin.write(json.dumps(simplified_data).encode())
    except OSError:
        pass

    out, err = proc.communicate()
    out = out.decode()
    err = err.decode()

    if out.strip():
        print(f"stdout: {out}")
    if err.strip():
        print(f"stderr: {err}")

    if proc.returncode:
        raise RuntimeError(
            "ERROR: extern_rv (called through the rv session file adapter) "
            "failed. stderr output: " + err
        )


# real entry point for translator
def generate_simplified_json(input_otio):
    session_json = {
        "nodes": [],
    }

    write_otio(input_otio, session_json)

    return session_json


def write_otio(otio_obj, to_session, track_kind=None):
    WRITE_TYPE_MAP = {
        otio.schema.Timeline: _write_timeline,
        otio.schema.Stack: _write_stack,
        otio.schema.Track: _write_track,
        otio.schema.Clip: _write_item,
        otio.schema.Gap: _write_item,
        otio.schema.Transition: _write_transition,
        otio.schema.SerializableCollection: _write_collection,
    }

    if type(otio_obj) in WRITE_TYPE_MAP:
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, to_session, track_kind)

    raise NoMappingForOtioTypeError(
        str(type(otio_obj)) + f" on object: {otio_obj}"
    )


def _add_node(to_session, kind, name=""):
    new_node = {
        "kind": kind,
        "name": name,
        "properties": [],
        "inputs": [],
        "commands": [],
        "node_index": len(to_session['nodes']),
    }
    to_session['nodes'].append(new_node)
    return new_node


def _add_input(to_node, input_node):
    to_node["inputs"].append(input_node["node_index"])


def _add_property(to_node, args):
    to_node['properties'].append(args)


def _add_command(to_node, command_name, args):
    to_node["commands"].append((command_name, args))


def _write_dissolve(pre_item, in_dissolve, post_item, to_session, track_kind=None):
    new_trx = _add_node(to_session, "CrossDissolve", str(in_dissolve.name))

    rate = pre_item.trimmed_range().duration.rate
    _add_property(
        new_trx, [
            "CrossDissolve",
            "",
            "parameters",
            "startFrame",
            "rvSession.gto.FLOAT",
            1.0
        ]
    )
    _add_property(
        new_trx,
        [
            "CrossDissolve",
            "",
            "parameters",
            "numFrames",
            "rvSession.gto.FLOAT",
            int(
                (
                    in_dissolve.in_offset
                    + in_dissolve.out_offset
                ).rescaled_to(rate).value
            )
        ]
    )
    _add_property(
        new_trx,
        [
            "CrossDissolve",
            "",
            "output",
            "fps",
            "rvSession.gto.FLOAT",
            rate
        ]
    )

    pre_item_rv = write_otio(pre_item, to_session, track_kind)
    _add_input(new_trx, pre_item_rv)

    post_item_rv = write_otio(post_item, to_session, track_kind)
    node_to_insert = post_item_rv

    if (
            hasattr(pre_item, "media_reference")
            and pre_item.media_reference
            and pre_item.media_reference.available_range
            and hasattr(post_item, "media_reference")
            and post_item.media_reference
            and post_item.media_reference.available_range
            and (
                post_item.media_reference.available_range.start_time.rate !=
                pre_item.media_reference.available_range.start_time.rate
            )
    ):
        # write a retime to make sure post_item is in the timebase of pre_item
        rt_node = _add_node(to_session, "Retime", "transition_retime")
        _add_command(
            rt_node,
            "setTargetFps",
            pre_item.media_reference.available_range.start_time.rate
        )

        post_item_rv = write_otio(post_item, to_session, track_kind)

        _add_input(rt_node, post_item_rv)
        node_to_insert = rt_node

    _add_input(new_trx, node_to_insert)

    return new_trx


def _write_transition(
        pre_item,
        in_trx,
        post_item,
        to_session,
        track_kind=None
):
    trx_map = {
        otio.schema.TransitionTypes.SMPTE_Dissolve: _write_dissolve,
    }

    if in_trx.transition_type not in trx_map:
        return

    return trx_map[in_trx.transition_type](
        pre_item,
        in_trx,
        post_item,
        to_session,
        track_kind
    )


def _write_stack(in_stack, to_session, track_kind=None):
    new_stack = _add_node(to_session, "Stack", str(in_stack.name) or "tracks")

    for seq in in_stack:
        result = write_otio(seq, to_session, track_kind)
        if result:
            _add_input(new_stack, result)

    return new_stack


def _write_track(in_seq, to_session, _=None):
    new_seq = _add_node(to_session, "Sequence", str(in_seq.name) or "track")

    items_to_serialize = otio.algorithms.track_with_expanded_transitions(
        in_seq
    )

    track_kind = in_seq.kind

    for thing in items_to_serialize:
        if isinstance(thing, tuple):
            result = _write_transition(
                *thing,
                to_session=to_session,
                track_kind=track_kind
            )
        elif thing.duration().value == 0:
            continue
        else:
            result = write_otio(thing, to_session, track_kind)

        if result:
            _add_input(new_seq, result)

    return new_seq


def _write_timeline(tl, to_session, _=None):
    result = write_otio(tl.tracks, to_session)
    return result


def _write_collection(collection, to_session, track_kind=None):
    results = []
    for item in collection:
        result = write_otio(item, to_session, track_kind)
        if result:
            results.append(result)

    if results:
        return results[0]


def _create_media_reference(item, src, track_kind=None):
    if hasattr(item, "media_reference") and item.media_reference:
        if isinstance(item.media_reference, otio.schema.ExternalReference):
            media = [str(item.media_reference.target_url)]

            if track_kind == otio.schema.TrackKind.Audio:
                # Create blank video media to accompany audio for valid source
                blank = "{},start={},end={},fps={}.movieproc".format(
                    "blank",
                    item.available_range().start_time.value,
                    item.available_range().end_time_inclusive().value,
                    item.available_range().duration.rate
                )
                # Inserting blank media here forces all content to only
                # produce audio. We do it twice in case we look at this in
                # stereo
                media = [blank, blank] + media

            _add_command(src, "setMedia", media)
            return True

        elif isinstance(item.media_reference, otio.schema.ImageSequenceReference):
            frame_sub = "%0{n}d".format(
                n=item.media_reference.frame_zero_padding
            )

            media = [
                str(item.media_reference.abstract_target_url(symbol=frame_sub))
            ]

            _add_command(src, "setMedia", media)

            return True

        elif isinstance(item.media_reference, otio.schema.GeneratorReference):
            if item.media_reference.generator_kind == "SMPTEBars":
                kind = "smptebars"
                _add_command(
                    src,
                    "setMedia",
                    [
                        "{},start={},end={},fps={}.movieproc".format(
                            kind,
                            item.available_range().start_time.value,
                            item.available_range().end_time_inclusive().value,
                            item.available_range().duration.rate
                        )
                    ]
                )
                return True

    return False


def _write_item(it, to_session, track_kind=None):
    new_item = _add_node(to_session, "Source", str(it.name) or "clip")

    if it.metadata:

        _add_property(
            new_item,

            # arguments to property
            [
                "RVSourceGroup",
                "source",
                "otio",
                "metadata",
                "rvSession.gto.STRING",
                # Serialize to a string as it seems gto has issues with unicode
                str(otio.core.serialize_json_to_string(it.metadata, indent=-1))
            ]
        )

    range_to_read = it.trimmed_range()

    if not range_to_read:
        raise otio.exceptions.OTIOError(
            "No valid range on clip: {}.".format(
                str(it)
            )
        )

    in_frame = out_frame = None
    if hasattr(it, "media_reference") and it.media_reference:
        if isinstance(it.media_reference, otio.schema.ImageSequenceReference):
            in_frame, out_frame = it.media_reference.frame_range_for_time_range(
                range_to_read
            )

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

    _add_command(new_item, "setCutIn", in_frame)
    _add_command(new_item, "setCutOut", out_frame)
    _add_command(new_item, "setFPS", range_to_read.duration.rate)

    # if the media reference is missing
    if not _create_media_reference(it, new_item, track_kind):
        kind = "smptebars"
        if isinstance(it, otio.schema.Gap):
            kind = "blank"
        _add_command(
            new_item,
            "setMedia",
            [
                "{},start={},end={},fps={}.movieproc".format(
                    kind,
                    range_to_read.start_time.value,
                    range_to_read.end_time_inclusive().value,
                    range_to_read.duration.rate
                )
            ]
        )

    return new_item
