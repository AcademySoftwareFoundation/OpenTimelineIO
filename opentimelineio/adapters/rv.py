"""RvSession Adapter"""

import rvSession

import opentimelineio as otio


def write_to_file(input_otio, filepath):
    """ create an rvsession file from the input_otio """
    session_file = rvSession.Session()

    # stack
    tracks = session_file.newNode("Stack", "tracks")

    for seq in input_otio.tracks:
        rv_seq = session_file.newNode("Sequence", seq.name or "sequence")
        tracks.addInput(rv_seq)

        for source in seq:
            src = session_file.newNode("Source", source.name or "clip")
            # if the media reference is not missing
            if (
                source.media_reference and
                not isinstance(
                    source.media_reference,
                    otio.media_reference.External
                )
            ):
                # @TODO: conform/resolve?
                # @TODO: instancing?
                src.setMedia([source.media_reference.target_url])

            if source.source_range:
                range_to_read = source.source_range
            else:
                range_to_read = source.available_range

            if not range_to_read:
                raise Exception(
                    "No valid range on clip: {0}.".format(
                        str(source)
                    )
                )

            src.setCutIn(range_to_read.start_time)
            src.setCutOut(range_to_read.end_time())
            src.setFPS(range_to_read.duration.rate)
            rv_seq.addInput(src)

    session_file.write(filepath)
    print input_otio, filepath
