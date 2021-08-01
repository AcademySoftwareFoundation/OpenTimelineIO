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

from itertools import groupby
import opentimelineio as otio
import io


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
    text = ''
    for caption in timed_text.texts:
        text = text + caption
    timed_text_str = in_time_str + ' --> ' + out_time_str + '\n' + text
    return timed_text_str


def write_to_string(input_otio):
    if not isinstance(input_otio, otio.schema.Subtitles):
        raise ValueError('Object not of type Subtitles!')

    str_string = ''
    block_count = 0

    for timed_text in input_otio.timed_texts:
        block_count += 1
        str_string = str_string + str(block_count) + '\n' + timed_text_to_srt_block(
            timed_text) + '\n'

    return str_string.strip()


def read_from_file(filepath):
    with io.open(filepath) as f:
        subs = [list(g) for b, g in groupby(f, lambda x: bool(x.strip())) if b]

    timed_texts = []

    for sub in subs:
        timestamps = sub[1].strip()
        timestamps_data = timestamps.split()
        start_time_str = timestamps_data[0].strip().replace(',', '.')
        end_time_str = timestamps_data[2].strip().replace(',', '.')
        start_time = otio.opentime.from_time_string(start_time_str, 24)
        end_time = otio.opentime.from_time_string(end_time_str, 24)
        xpos1 = None
        ypos1 = None
        xpos2 = None
        ypos2 = None
        if (len(timestamps_data) == 7):
            xpos1 = float(timestamps_data[3][3:])
            xpos2 = float(timestamps_data[4][3:])
            ypos1 = float(timestamps_data[5][3:])
            ypos2 = float(timestamps_data[6][3:])
        content = ''
        for text in sub[2:]:
            content = content + text

        if len(content.strip()) == 0:
            content = '\n'
        tt = otio.schema.TimedText(in_time=start_time, out_time=end_time)
        tt.add_text(text=content)
        timed_texts.append(tt)
    return otio.schema.Subtitles(timed_texts=timed_texts)
