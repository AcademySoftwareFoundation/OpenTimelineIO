"""
This file is here to support the test_adapter_plugin unittest.
If you want to learn how to write your own adapter plugin, please read:
https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter
"""

import opentimelineio as otio

def read_from_file(path):
    return otio.schema.Timeline(name=path)
