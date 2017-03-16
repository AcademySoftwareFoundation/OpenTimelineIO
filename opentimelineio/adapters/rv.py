"""RvSession Adapter"""

import rvSession

import opentimelineio as otio


class NoMappingForOtioTypeError(Exception): pass


def write_otio(otio_obj, to_session):
    if type(otio_obj) in WRITE_TYPE_MAP:
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, to_session)
    raise NoMappingForOtioTypeError(type(otio_obj))

def _write_stack(in_stack, to_session):
    new_stack = to_session.newNode("Stack", str(in_stack.name) or "tracks")

    for seq in in_stack:
        result = write_otio(seq, to_session)
        new_stack.addInput(result)

    return new_stack

def _write_sequence(in_seq, to_session):
    new_seq = to_session.newNode("Sequence", str(in_seq.name) or "sequence")

    for seq in in_seq:
        result = write_otio(seq, to_session)
        new_seq.addInput(result)

    return new_seq

def _write_timeline(tl, to_session):
    result = write_otio(tl.tracks, to_session)
    return result

def write_to_file(input_otio, filepath):
    session_file = rvSession.Session()
    write_otio(input_otio, session_file)
    session_file.write(filepath)

def _write_item(it, to_session):
    src = to_session.newNode("Source", str(it.name) or "clip")

    # if the media reference is not missing
    if (
        it.media_reference and
        isinstance(
            it.media_reference,
            otio.media_reference.External
        )
    ):
        # @TODO: conform/resolve?
        # @TODO: instancing?
        src.setMedia([str(it.media_reference.target_url.replace("file://",''))])

    if it.source_range:
        range_to_read = it.source_range
    else:
        range_to_read = it.available_range

    if not range_to_read:
        raise Exception(
            "No valid range on clip: {0}.".format(
                str(it)
            )
        )

    src.setCutIn(
        range_to_read.start_time.value_rescaled_to(
            range_to_read.duration
        )
    )
    src.setCutOut(
        range_to_read.end_time().value_rescaled_to(
            range_to_read.duration
        )
    )
    src.setFPS(range_to_read.duration.rate)

    return src


WRITE_TYPE_MAP = {
    otio.schema.Timeline: _write_timeline,
    otio.schema.Stack: _write_stack,
    otio.schema.Sequence: _write_sequence,
    otio.schema.Clip: _write_item,
    otio.schema.Filler: _write_item,
}
