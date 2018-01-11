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

"""RV External Adapter component.

Because the rv adapter requires being run from within the RV py-interp to take
advantage of modules inside of RV, this script gets shelled out to from the
RV OTIO adapter.

Requires that you set the environment variables:
    OTIO_RV_PYTHON_LIB - should point at the parent directory of rvSession
    OTIO_RV_PYTHON_BIN - should point at py-interp from within rv
"""

# python
import sys
import os

# otio
import opentimelineio as otio

# rv import
sys.path += [os.path.join(os.environ["OTIO_RV_PYTHON_LIB"], "rvSession")]
import rvSession  # noqa


def main():
    """ entry point, should be called from the rv adapter in otio """

    session_file = rvSession.Session()

    output_fname = sys.argv[1]

    # read the input OTIO off stdin
    input_otio = otio.adapters.read_from_string(sys.stdin.read(), 'otio_json')

    result = write_otio(input_otio, session_file)
    session_file.setViewNode(result)
    session_file.write(output_fname)


# exception class @{
class NoMappingForOtioTypeError(otio.exceptions.OTIOError):
    pass
# @}


def write_otio(otio_obj, to_session):
    WRITE_TYPE_MAP = {
        otio.schema.Timeline: _write_timeline,
        otio.schema.Stack: _write_stack,
        otio.schema.Track: _write_track,
        otio.schema.Clip: _write_item,
        otio.schema.Gap: _write_item,
        otio.schema.Transition: _write_transition,
    }

    if type(otio_obj) in WRITE_TYPE_MAP:
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, to_session)

    raise NoMappingForOtioTypeError(
        str(type(otio_obj)) + " on object: {}".format(otio_obj)
    )


def _write_dissolve(pre_item, in_dissolve, post_item, to_session):
    rv_trx = to_session.newNode("CrossDissolve", str(in_dissolve.name))
    rv_trx.setProperty(
        "CrossDissolve",
        "",
        "parameters",
        "startFrame",
        rvSession.gto.FLOAT,
        1.0
    )
    rv_trx.setProperty(
        "CrossDissolve",
        "",
        "parameters",
        "numFrames",
        rvSession.gto.FLOAT,
        int(
            (in_dissolve.in_offset + in_dissolve.out_offset).rescaled_to(
                pre_item.trimmed_range().duration.rate
            ).value
        )
    )

    rv_trx.setProperty(
        "CrossDissolve",
        "",
        "output",
        "fps",
        rvSession.gto.FLOAT,
        pre_item.trimmed_range().duration.rate
    )

    pre_item_rv = write_otio(pre_item, to_session)
    rv_trx.addInput(pre_item_rv)

    post_item_rv = write_otio(post_item, to_session)

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
        rt_node = to_session.newNode("Retime", "transition_retime")
        rt_node.setTargetFps(
            pre_item.media_reference.available_range.start_time.rate
        )

        post_item_rv = write_otio(post_item, to_session)

        rt_node.addInput(post_item_rv)
        node_to_insert = rt_node

    rv_trx.addInput(node_to_insert)

    return rv_trx


def _write_transition(pre_item, in_trx, post_item, to_session):
    trx_map = {
        otio.schema.TransitionTypes.SMPTE_Dissolve: _write_dissolve,
    }

    if in_trx.transition_type not in trx_map:
        return

    return trx_map[in_trx.transition_type](
        pre_item,
        in_trx,
        post_item,
        to_session
    )


def _write_stack(in_stack, to_session):
    new_stack = to_session.newNode("Stack", str(in_stack.name) or "tracks")

    for seq in in_stack:
        result = write_otio(seq, to_session)
        if result:
            new_stack.addInput(result)

    return new_stack


def _write_track(in_seq, to_session):
    new_seq = to_session.newNode("Sequence", str(in_seq.name) or "track")

    items_to_serialize = otio.algorithms.track_with_expanded_transitions(
        in_seq
    )

    for thing in items_to_serialize:
        if isinstance(thing, tuple):
            result = _write_transition(*thing, to_session=to_session)
        elif thing.duration().value == 0:
            continue
        else:
            result = write_otio(thing, to_session)

        if result:
            new_seq.addInput(result)

    return new_seq


def _write_timeline(tl, to_session):
    result = write_otio(tl.tracks, to_session)
    return result


def _create_media_reference(mr, to_session):
    if hasattr(mr, "media_reference") and mr.media_reference:
        if isinstance(mr.media_reference, otio.schema.ExternalReference):
            to_session.setMedia([str(mr.media_reference.target_url)])
            return True
        elif isinstance(mr.media_reference, otio.schema.GeneratorReference):
            if mr.media_reference.generator_kind == "SMPTEBars":
                kind = "smptebars"
                to_session.setMedia(
                    [
                        "{},start={},end={},fps={}.movieproc".format(
                            kind,
                            mr.available_range().start_time.value,
                            mr.available_range().end_time_inclusive().value,
                            mr.available_range().duration.rate
                        )
                    ]
                )
                return True

    return False


def _write_item(it, to_session):
    src = to_session.newNode("Source", str(it.name) or "clip")

    src.setProperty(
        "RVSourceGroup",
        "source",
        "attributes",
        "otio_metadata",
        rvSession.gto.STRING, str(it.metadata)
    )

    range_to_read = it.trimmed_range()

    if not range_to_read:
        raise otio.exceptions.OTIOError(
            "No valid range on clip: {0}.".format(
                str(it)
            )
        )

    # because OTIO has no global concept of FPS, the rate of the duration is
    # used as the rate for the range of the source.
    # RationalTime.value_rescaled_to returns the time value of the object in
    # time rate of the argument.
    src.setCutIn(
        range_to_read.start_time.value_rescaled_to(
            range_to_read.duration
        )
    )
    src.setCutOut(
        range_to_read.end_time_inclusive().value_rescaled_to(
            range_to_read.duration
        )
    )
    src.setFPS(range_to_read.duration.rate)

    # if the media reference is missing
    if not _create_media_reference(it, src):
        kind = "smptebars"
        if isinstance(it, otio.schema.Gap):
            kind = "blank"
        src.setMedia(
            [
                "{},start={},end={},fps={}.movieproc".format(
                    kind,
                    range_to_read.start_time.value,
                    range_to_read.end_time_inclusive().value,
                    range_to_read.duration.rate
                )
            ]
        )

    return src


if __name__ == "__main__":
    main()
