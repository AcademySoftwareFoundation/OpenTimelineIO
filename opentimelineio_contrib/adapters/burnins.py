#
# Copyright 2017 Pixar Animation Studios
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
"""FFMPEG Burnins Adapter"""
import os
import sys


def build_burnins(input_otio):
    """
    Generates the burnin objects for each clip within the otio container

    :param input_otio: OTIO container
    :rtype: [ffmpeg_burnins.Burnins(), ...]
    """

    if os.path.dirname(__file__) not in sys.path:
        sys.path.append(os.path.dirname(__file__))

    import ffmpeg_burnins
    key = 'burnins'

    burnins = []
    for clip in input_otio.each_clip():

        # per clip burnin data
        burnin_data = clip.media_reference.metadata.get(key)
        if not burnin_data:
            # otherwise default to global burnin
            burnin_data = input_otio.metadata.get(key)

        if not burnin_data:
            continue

        media = clip.media_reference.target_url
        if media.startswith('file://'):
            media = media[7:]
        streams = burnin_data.get('streams')
        burnins.append(ffmpeg_burnins.Burnins(media,
                                              streams=streams))
        burnins[-1].otio_media = media
        burnins[-1].otio_overwrite = burnin_data.get('overwrite')
        burnins[-1].otio_args = burnin_data.get('args')

        for burnin in burnin_data.get('burnins', []):
            align = burnin.pop('align')
            function = burnin.pop('function')
            if function == 'text':
                text = burnin.pop('text')
                options = ffmpeg_burnins.TextOptions()
                options.update(burnin)
                burnins[-1].add_text(text, align, options=options)
            elif function == 'frame_number':
                options = ffmpeg_burnins.FrameNumberOptions()
                options.update(burnin)
                burnins[-1].add_frame_numbers(align, options=options)
            elif function == 'timecode':
                options = ffmpeg_burnins.TimeCodeOptions()
                options.update(burnin)
                burnins[-1].add_timecode(align, options=options)
            else:
                raise RuntimeError("Unknown function '%s'" % function)

    return burnins


def write_to_file(input_otio, filepath):
    """required OTIO function hook"""

    for burnin in build_burnins(input_otio):
        burnin.render(os.path.join(filepath, burnin.otio_media),
                      args=burnin.otio_args,
                      overwrite=burnin.otio_overwrite)
