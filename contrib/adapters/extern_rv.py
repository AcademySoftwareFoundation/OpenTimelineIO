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

    write_otio(input_otio, session_file)
    session_file.write(output_fname)


# exception class @{
class NoMappingForOtioTypeError(Exception):
    pass
# @}


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


def _write_item(it, to_session):
    src = to_session.newNode("Source", str(it.name) or "clip")

    src.setProperty(
        "RVSourceGroup",
        "source",
        "attributes",
        "otio_metadata",
        rvSession.gto.STRING, str(it.metadata)
    )

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

    # if the media reference is not missing
    if (
        it.media_reference and
        isinstance(
            it.media_reference,
            otio.media_reference.External
        )
    ):
        src.setMedia([str(it.media_reference.target_url)])
    else:
        # otherwise set color bars so its obviously missing.
        src.setMedia(
            [
                "smptebars,start={},end={},fps={}.movieproc".format(
                    range_to_read.start_time.value,
                    range_to_read.end_time().value,
                    range_to_read.duration.rate
                )
            ]
        )

    return src


WRITE_TYPE_MAP = {
    otio.schema.Timeline: _write_timeline,
    otio.schema.Stack: _write_stack,
    otio.schema.Sequence: _write_sequence,
    otio.schema.Clip: _write_item,
    otio.schema.Filler: _write_item,
}


if __name__ == "__main__":
    main()
