# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""This file is here to support the test_adapter_plugin unittest, specifically adapters
that implement their own hooks.
If you want to learn how to write your own adapter plugin, please read:
https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html
"""


def hook_function(in_timeline, argument_map=None):
    in_timeline.metadata["custom_hook"] = dict(argument_map)
    return in_timeline
