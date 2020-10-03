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

"""SRT Adapter harness"""

from .. import adapters

import opentimelineio as otio


def timed_text_to_srt_block(timed_text):
    in_time_str = otio.opentime.to_time_string(timed_text.in_time)
    out_time_str = otio.opentime.to_time_string(timed_text.out_time)
    in_time_str_decimal_index = in_time_str.rfind('.')
    out_time_str_decimal_index = out_time_str.rfind('.')
    in_time_ms = in_time_str[in_time_str_decimal_index + 1:]
    out_time_ms = out_time_str[out_time_str_decimal_index + 1:]
    in_time_str = in_time_str[0:in_time_str_decimal_index] + ',{:0<3}'.format(
        in_time_ms[:3])
    out_time_str = out_time_str[0:out_time_str_decimal_index] + ',{:0<3}'.format(
        out_time_ms[:3])
    timed_text_str = in_time_str + ' --> ' + out_time_str + '\n' + timed_text.text + '\n'
    return timed_text_str


def write_to_string(input_otio):
    if (not isinstance(input_otio, otio.schema.Subtitles)):
        raise ValueError('Object not of type Subtitles!')

    str_string = ''
    block_count = 0

    for timed_text in input_otio.timed_texts:
        block_count += 1
        str_string = str_string + str(block_count) + '\n' + timed_text_to_srt_block(
            timed_text) + '\n'

    return str_string
