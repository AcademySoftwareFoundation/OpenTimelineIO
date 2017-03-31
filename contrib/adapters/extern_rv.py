"""RV External Adapter component.

Because the rv adapter requires being run from within the RV py-interp to take
advantage of modules inside of RV, this script gets shelled out to from the
RV OTIO adapter.

Requires that you set the environment variables:
    OTIO_RV_PYTHON_LIB - should the be directory containing rvSession directory
    OTIO_RV_PYTHON_BIN - should the be the directory of the py-interp program
"""

# python
import sys
import os

# otio
import opentimelineio as otio

# rv import
sys.path += [os.path.join(os.environ["OTIO_RV_PYTHON_LIB"], "rvSession")]
import rvSession #noqa


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
        otio.schema.Sequence: _write_sequence,
        otio.schema.Clip: _write_item,
        otio.schema.Filler: _write_item,
        otio.schema.Transition: _write_transition,
    }

    if type(otio_obj) in WRITE_TYPE_MAP:
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, to_session)
    raise NoMappingForOtioTypeError(type(otio_obj))


def _write_dissolve(pre_item, in_dissolve, post_item, to_session):
    # [ AAAA | BBBB ]

    # [ AAAA |T| BBBB ]
    #      [--T--]   

    # encoded in otio:
    # [t0, A, t1, B, C, t2]

    # _expand_transition:
    #  1) add filler if necesary
    #  2) Copy A -> a_t0, A'
    # return tuple

    # implies:
    # [f0, t0, A, t1, B, C, t2, f1]

    # in rv:
    # [[f0, t0, A_t0],A',[A_t1, t1, B_t1],B', C', [C_t2, t2, f1]]

    # ratio = 1

    rv_trx = to_session.newNode( "CrossDissolve", str(in_dissolve.name))
    rv_trx.setProperty(
        "CrossDissolve",
        "",
        "parameters",
        "startFrame",
        rvSession.gto.FLOAT,
        0.0
    )
    rv_trx.setProperty (
        "CrossDissolve",
        "",
        "parameters",
        "numFrames",
        rvSession.gto.FLOAT,
        int((in_dissolve.in_offset + in_dissolve.out_offset).rescaled_to(
            pre_item.source_range.duration.rate
        ).value)
    )

    rv_trx.setProperty(
        "CrossDissolve",
        "",
        "output",
        "fps",
        rvSession.gto.FLOAT,
        pre_item.source_range.duration.rate
    )
    # rv_trx.setProperty(
    #     "CrossDissolve",
    #     "",
    #     "output",
    #     "autoSize",
    #     rvSession.gto.INT,
    #     1
    # )
    # rv_trx.setProperty(
    #     "CrossDissolve",
    #     "",
    #     "node",
    #     "active",
    #     rvSession.gto.INT,
    #     1
    # )


    # [ K' [k_t t j_t] j']

    # 1) J_t clip plays all the way to the end, not just the part that is in the 
    #    transition
    # 2) J_t clip is playing at 30 fps by doubling each 60 hz frame, not skiping
    pre_item_rv = write_otio(pre_item, to_session)
    rv_trx.addInput(pre_item_rv)

    post_item_rv = write_otio(post_item, to_session)

    node_to_insert = post_item_rv

    if (
        # @TODO: should use "is_missing_reference()"?
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
        # ratio = (
        #     pre_item.media_reference.available_range.start_time.rate
        #     / post_item.media_reference.available_range.start_time.rate
        # )

        # write a retime to make sure post_item is in the timebase of pre_item
        rt_node = to_session.newNode("Retime", "transition_retime")
        rt_node.setTargetFps(
            pre_item.media_reference.available_range.start_time.rate
        )
        # rt_node.setAScale(ratio)
        # rt_node.setVScale(ratio)

        # post_item.source_range.duration.rescaled_to(
        #     pre_item.source_range.duration
        # ) *= 1/ratio
        post_item_rv = write_otio(post_item, to_session)

        rt_node.addInput(post_item_rv)
        node_to_insert = rt_node


    # [ K t J ]

    # [ K' [K_t t J_t] J'] 

    rv_trx.addInput(node_to_insert)

    return rv_trx


def _write_transition(pre_item, in_trx, post_item, to_session):
    trx_map = {
        "dissolve" : _write_dissolve,
    }

    ttypename = in_trx.transition_type.lower()

    if ttypename not in trx_map:
        return

    return trx_map[ttypename](pre_item, in_trx, post_item, to_session)


def _write_stack(in_stack, to_session):
    new_stack = to_session.newNode("Stack", str(in_stack.name) or "tracks")

    for seq in in_stack:
        result = write_otio(seq, to_session)
        if result:
            new_stack.addInput(result)

    return new_stack


def _write_sequence(in_seq, to_session):
    new_seq = to_session.newNode("Sequence", str(in_seq.name) or "sequence")

    items_to_serialize = otio.utilities.sequence_with_expanded_transitions(in_seq)
    otio.adapters.write_to_file(items_to_serialize, "/var/tmp/debug.otio")


    for thing in items_to_serialize:
        if isinstance(thing, tuple):
            result = _write_transition(*thing, to_session=to_session)
        else:
            result = write_otio(thing, to_session)

        if result:
            new_seq.addInput(result)

    return new_seq


def _write_timeline(tl, to_session):
    result = write_otio(tl.tracks, to_session)
    return result


def _write_item(it, to_session):
    src = to_session.newNode("Source", str(it.name) or "clip")

    src.setProperty(
        "RVSourceGroup",
        "source",
        "attributes",
        "otio_metadata",
        rvSession.gto.STRING, str(it.metadata)
    )

    # the source range is the range of the media reference that is being cut in.
    # if the source range is not set, then fall back to the available_range,
    # which is all of the media that could possibly be cut in.  One or the
    # other must be provided, however, otherwise duration cannot be computed
    # correctly in the rest of OTIO.
    range_to_read = it.source_range
    if not range_to_read:
        range_to_read = it.media_reference.available_range

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
        range_to_read.end_time_exclusive().value_rescaled_to(
            range_to_read.duration
        )
    )
    src.setFPS(range_to_read.duration.rate)

    # if the media reference is not missing
    if (
        hasattr(it, "media_reference") and
        it.media_reference and
        isinstance(
            it.media_reference,
            otio.media_reference.External
        )
    ):
        src.setMedia([str(it.media_reference.target_url)])
    else:
        kind = "smptebars"
        if isinstance(it, otio.schema.Filler):
            kind = "blank"
        src.setMedia(
            [
                "{},start={},end={},fps={}.movieproc".format(
                    kind,
                    range_to_read.start_time.value,
                    range_to_read.end_time_exclusive().value,
                    range_to_read.duration.rate
                )
            ]
        )

    return src


if __name__ == "__main__":
    main()
