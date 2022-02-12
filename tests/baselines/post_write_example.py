# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os

"""This file is here to support the test_adapter_plugin unittest.
If you want to learn how to write your own adapter plugin, please read:
https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html
"""


def hook_function(in_timeline, argument_map=None):
    filepath = argument_map.get('_filepath')
    argument_map.update({'filesize': os.path.getsize(filepath)})
    in_timeline.metadata.update(argument_map)

    return in_timeline
