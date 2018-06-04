# MIT License
#
# Copyright (c) 2018 Daniel Flehner Heen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# allcopies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""OpenTimelineIO Media Lovin' Toolkit (MLT) XML Adapter
Highly influenced by the fcp_xml adapter

mltxml ref:
    https://www.mltframework.org/docs/mltxml/
XML DTD:
    https://github.com/mltframework/mlt/blob/master/src/modules/xml/mlt-xml.dtd
"""

from xml.etree import cElementTree
from xml.dom import minidom

import opentimelineio as otio


def _build_track(stack, timeline_range, br_map):
    track_e = cElementTree.Element('sequence')
    _insert_new_sub_element(track_e, 'name', text=stack.name)
    _insert_new_sub_element(
        track_e, 'duration',
        text='{:.0f}'.format(timeline_range.duration.value)
    )
    track_e.append(_build_rate(timeline_range.start_time))
    track_rate = timeline_range.start_time.rate

    media_e = _insert_new_sub_element(track_e, 'media')
    video_e = _insert_new_sub_element(media_e, 'video')
    audio_e = _insert_new_sub_element(media_e, 'audio')

    for track in stack:
        if track.kind == otio.schema.TrackKind.Video:
            video_e.append(_build_top_level_track(track, track_rate, br_map))
        elif track.kind == otio.schema.TrackKind.Audio:
            audio_e.append(_build_top_level_track(track, track_rate, br_map))

    for marker in stack.markers:
        track_e.append(_build_marker(marker))

    return track_e


def _insert_new_sub_element(into_parent, tag, attrib=None, text=''):
    elem = cElementTree.SubElement(into_parent, tag, **attrib or {})
    elem.text = text
    return elem


def _make_pretty_string(tree_e):
    # Snatched from fcp_xml.py
    # most of the parsing in this adapter is done with cElementTree because it
    # is simpler and faster. However, the string representation it returns is
    # far from elegant. Therefor we feed it through minidom to provide an xml
    # with indentations.
    string = cElementTree.tostring(tree_e, encoding="UTF-8", method="xml")
    dom = minidom.parseString(string)
    return dom.toprettyxml(indent='    ')


def read_from_string(input_str):
    pass


def write_from_string(input_otio):
    root_e = cElementTree.Element('mlt', title=input_otio.name)
    tractor_e = _insert_new_sub_element(root_e, 'tractor', id='tractor0')

    #br_map = collections.defaultdict(dict)
    #_populate_backreference_map(input_otio, br_map)

    if isinstance(input_otio, otio.schema.Timeline):
        timeline_range = otio.opentime.TimeRange(
            start_time=input_otio.global_start_time,
            duration=input_otio.duration()
        )
        tractor_e.append(
            _build_track(input_otio.tracks, timeline_range, br_map)
        )
    #elif isinstance(input_otio, otio.schema.SerializableCollection):
        #children_e.extend(
            #_build_collection(input_otio, br_map)
        #)

    return _make_pretty_string(tree_e)
