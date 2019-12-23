#
# Copyright 2019 Pixar Animation Studios
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

import opentimelineio as otio


__doc__ = """OTIO Adapter for reading/writing VLC PLS files"""


def write_to_string(input_otio):
    result = "[playlist]"

    if not isinstance(input_otio, otio.schema.Timeline):
        raise otio.exceptions.NotSupportedError(
            "The PLS/VLC adapter only supports single track timelines.  Got an"
            " object of type: '{}'".format(type(input_otio))
        )

    if len(input_otio.video_tracks()) > 1:
        raise otio.exceptions.NotSupportedError(
            "The PLS/VLC adapter only supports single track timelines.  Got a"
            " timeline with '{}' tracks.".format(len(input_otio.video_tracks()))
        )

    for i, clip in enumerate(input_otio.video_tracks()[0]):
        try:
            reference = clip.media_reference.target_url
        except AttributeError:
            raise otio.exceptions.NotSupportedError(
                "The PLS/VLC adapter only supports single track timelines with"
                " clips that have external reference media references.  Got a "
                "media reference of kind: '{}'.".format(
                    type(clip.media_reference)
                )
            )

        result += "\nFile{}={}".format(i + 1, reference)

    result += "\n"

    return result
