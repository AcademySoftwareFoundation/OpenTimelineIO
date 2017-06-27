"""
This file is here to support the test_adapter_plugin unittest.
If you want to learn how to write your own adapter plugin, please read:
https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
"""

import opentimelineio as otio


def read_from_file(filepath):
    fake_tl = otio.schema.Timeline(name=filepath)
    fake_tl.tracks.append(otio.schema.Sequence())
    fake_tl.tracks[0].append(otio.schema.Clip(name=filepath + "_clip"))
    return fake_tl


def read_from_string(input_str):
    return read_from_file(input_str)


def link_media_reference(in_clip, media_linker_argument_map):
    d = {'from_test_linker': True}
    d.update(media_linker_argument_map)
    return otio.media_reference.MissingReference(
        name=in_clip.name + "_tweaked",
        metadata=d
    )
