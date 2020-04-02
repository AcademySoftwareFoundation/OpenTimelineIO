#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

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
