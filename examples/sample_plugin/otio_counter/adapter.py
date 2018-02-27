import opentimelineio as otio


def write_to_string(input_otio):
    return '{}'.format(len(input_otio.tracks))


def read_from_string(input_str):
    t = otio.schema.Timeline()

    for i in range(int(input_str)):
        t.tracks.append(otio.schema.Track())

    return t
