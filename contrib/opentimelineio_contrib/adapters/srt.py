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
from html.parser import HTMLParser
from queue import LifoQueue
import opentimelineio as otio
import io


class SRTStyleParser(HTMLParser):
    class StyleState:

        def __init__(self):
            self.italics = False
            self.bold = False
            self.underline = False
            self.strikethrough = False
            self.font_size = '10'
            self.font_color = 'BLACK'
            self.font_face = ''

        def clear_state(self):
            self.italics = False
            self.bold = False
            self.underline = False
            self.strikethrough = False
            self.font_size = ''
            self.font_color = 'BLACK'
            self.font_face = ''

        def set_font_size(self, value):
            self.font_size = value

        def set_font_face(self, value):
            self.font_face = value

        def set_font_color(self, value):
            self.font_color = value

        def __repr__(self):
            return 'StyleState(' \
                   'italics=' + str(self.italics) + \
                   ',bold=' + str(self.bold) + \
                   ',underline=' + str(self.underline) + \
                   ',strikethrough=' + str(self.strikethrough) + \
                   ',fontSize=' + str(self.font_size) + \
                   ',fontColor=' + str(self.font_color) + \
                   ',fontFace=' + str(self.font_face) + \
                   ')'

    def __init__(self):
        super().__init__()
        self.tagStack = LifoQueue()
        self.styleState = self.StyleState()
        self.dataState = ""
        self.dataList = []
        self.TAG_FUNCTION_MAP = {
            'b': self._process_bold_tag,
            'u': self._process_underline_tag,
            'i': self._process_italics_tag,
            's': self._process_strikethrough_tag,
            'font': self._process_font_tag
        }

    def _process_tag(self, tag_attrs_tuple):
        if tag_attrs_tuple[0] in self.TAG_FUNCTION_MAP:
            self.TAG_FUNCTION_MAP[tag_attrs_tuple[0]](tag_attrs_tuple[1])

    def _process_bold_tag(self, tag_attrs):
        self.styleState.bold = True

    def _process_underline_tag(self, tag_attrs):
        self.styleState.underline = True

    def _process_italics_tag(self, tag_attrs):
        self.styleState.italics = True

    def _process_strikethrough_tag(self, tag_attrs):
        self.styleState.strikethrough = True

    def _process_font_tag(self, tag_attrs):
        FONT_ATTR_MAP = {
            'color': self.styleState.set_font_color,
            'face': self.styleState.set_font_face,
            'size': self.styleState.set_font_size,
        }
        for attribute, value in tag_attrs:
            if attribute in FONT_ATTR_MAP:
                FONT_ATTR_MAP[attribute](value)

    def parse_srt(self, srt_string):
        self.styleState.clear_state()
        self.feed(srt_string)
        return self.dataList

    def handle_starttag(self, tag, attrs):
        attr_list = []
        for attr in attrs:
            attr_list.append(attr)
        self.tagStack.put((tag, attr_list))

    def handle_endtag(self, tag):
        topTag = self.tagStack.get()
        if topTag[0] != tag:
            raise Exception('Invalid HTML')
        self._process_tag(topTag)
        if self.tagStack.empty():
            self.dataList.append((self.dataState, self.styleState))
            self.styleState = self.StyleState()
            self.dataState = ''

    def handle_data(self, data):
        if self.tagStack.empty():
            self.dataList.append((data, None))
        else:
            self.dataState = data

    def error(self, message):
        pass


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

    style_id_count = 0
    styles_map = {}
    style_parser = SRTStyleParser()
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
        subtitle_text = ''
        for text in sub[2:]:
            subtitle_text = subtitle_text + text

        if len(subtitle_text.strip()) == 0:
            subtitle_text = '\n'
        subtitle_data = style_parser.parse_srt(subtitle_text)
        tt = otio.schema.TimedText(in_time=start_time, out_time=end_time)
        for data in subtitle_data:
            style_id = ''
            if data[1] is not None:
                style_id_count += 1
                style = otio.schema.TimedTextStyle(style_id='style' + str(style_id_count),
                                                   text_color=data[1].font_color,
                                                   text_size=float(data[1].font_size),
                                                   text_bold=data[1].bold,
                                                   text_italics=data[1].italics,
                                                   text_underline=data[1].underline,
                                                   font_family=data[1].font_face)
                style_id = str(style_id_count)
                styles_map[style_id] = style
            tt.add_text(text=data[0], styleID=style_id)
        timed_texts.append(tt)
    subtitles = otio.schema.Subtitles(timed_texts=timed_texts)
    track = otio.schema.Track(name="Subtitles Track")
    timeline = otio.schema.Timeline("SRT Timeline", tracks=[track])
    timeline.metadata['styles'] = styles_map
    timeline.tracks[0].append(subtitles)
    return timeline
