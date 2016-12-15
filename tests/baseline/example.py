"example adapter"

import opentimelineio as otio


def read_from_file(path):
    return otio.schema.Timeline(name=path)
