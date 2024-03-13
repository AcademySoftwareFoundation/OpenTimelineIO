# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""This file is here to support the test_adapter_plugin unittest.
If you want to learn how to write your own adapter plugin, please read:
https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html
"""


# `hook_function_argument_map` is only a required argument for adapters that implement
# custom hooks.
def read_from_file(filepath, suffix="", hook_function_argument_map=None):
    import opentimelineio as otio

    fake_tl = otio.schema.Timeline(name=filepath + str(suffix))
    fake_tl.tracks.append(otio.schema.Track())
    fake_tl.tracks[0].append(otio.schema.Clip(name=filepath + "_clip"))

    if (hook_function_argument_map and
            hook_function_argument_map.get("run_custom_hook", False)):
        return otio.hooks.run(hook="custom_adapter_hook", tl=fake_tl,
                              extra_args=hook_function_argument_map)

    return fake_tl


# `hook_function_argument_map` is only a required argument for adapters that implement
# custom hooks.
def read_from_string(input_str, suffix="", hook_function_argument_map=None):
    tl = read_from_file(input_str, suffix, hook_function_argument_map)
    return tl


# this is only required for adapters that implement custom hooks
def adapter_hook_names():
    return ["custom_adapter_hook"]


# in practice, these will be in separate plugins, but for simplicity in the
# unit tests, we put this in the same file as the example adapter.
def link_media_reference(in_clip, media_linker_argument_map):
    import opentimelineio as otio

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
