# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""This file is here to support the test_adapter_plugin unittest.
If you want to learn how to write your own adapter plugin, please read:
https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html
"""

import opentimelineio as otio


def read_from_file(filepath, suffix=""):
    fake_tl = otio.schema.Timeline(name=filepath + str(suffix))
    fake_tl.tracks.append(otio.schema.Track())
    fake_tl.tracks[0].append(otio.schema.Clip(name=filepath + "_clip"))
    return fake_tl


def read_from_string(input_str, suffix=""):
    return read_from_file(input_str, suffix)


# in practice, these will be in separate plugins, but for simplicity in the
# unit tests, we put this in the same file as the example adapter.
def link_media_reference(in_clip, media_linker_argument_map):
    d = {'from_test_linker': True}
    d.update(media_linker_argument_map)
    return otio.schema.MissingReference(
        name=in_clip.name + "_tweaked",
        metadata=d
    )


# same thing for this hookscript
def hook_function(in_timeline, argument_map=None):
    in_timeline.name = "hook ran and did stuff"
    in_timeline.metadata.update(argument_map)
    return in_timeline
