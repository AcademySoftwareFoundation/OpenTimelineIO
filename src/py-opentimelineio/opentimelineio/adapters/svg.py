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

"""OTIO to SVG Adapter
   Points in calculations are y-up.
   Points in SVG are y-down."""

# otio
import opentimelineio as otio

# python
import math
from random import seed
from random import random
from collections import namedtuple

COLORS = {
    'transparent': (0, 0, 0, 0),
    'black': (0.0, 0.0, 0.0, 255.0),
    'white': (255.0, 255.0, 255.0, 255.0),
    'transluscent_white': (255.0, 255.0, 255.0, 178.5),
    'purple': (127.5, 0.0, 127.5, 255.0),
    'light_blue': (134.895, 206.04, 235.11, 255.0),
    'blue': (0.0, 0.0, 255.0, 255.0),
    'dark_blue': (0.0, 0.0, 137.7, 255.0),
    'green': (0.0, 127.5, 0.0, 255.0),
    'dark_green': (0.0, 99.45, 0.0, 255.0),
    'yellow': (255.0, 255.0, 0.0, 255.0),
    'gold': (255.0, 214.2, 0.0, 255.0),
    'orange': (255.0, 164.985, 0.0, 255.0),
    'red': (255.0, 0.0, 0.0, 255.0),
    'dark_red': (137.7, 0.0, 0.0, 255.0),
    'brown': (137.7, 68.85, 25.5, 255.0),
    'pink': (255.0, 191.25, 201.45, 255.0),
    'gray': (127.5, 127.5, 127.5, 255.0),
    'dark_gray': (168.3, 168.3, 168.3, 255.0),
    'dark_gray_transluscent': (168.3, 168.3, 168.3, 200.0)
}

random_colors_used = []


def get_random_color():
    return [random(), random(), random()]


def color_distance(c1, c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])


def generate_new_color(existing_colors):
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color()
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color


def random_color():
    color = generate_new_color(random_colors_used)
    random_colors_used.append(color)
    return color[0] * 255.0, color[1] * 255.0, color[2] * 255.0, 255.0


Point = namedtuple('Point', ['x', 'y'])


class Rect(object):
    origin = Point(0, 0)
    width = 0.0
    height = 0.0

    def __init__(self, origin=Point(0, 0), width=0.0, height=0.0):
        self.origin = origin
        self.width = width
        self.height = height

    def normalized(self):
        normalized_origin = Point(
            self.origin.x + (self.width if self.width < 0 else 0),
            self.origin.y + (self.height if self.height < 0 else 0),
        )
        normalized_width = abs(self.width)
        normalized_height = abs(self.height)
        return Rect(normalized_origin, normalized_width, normalized_height)

    def min_x(self):
        return self.normalized().origin.x

    def min_y(self):
        return self.normalized().origin.y

    def mid_x(self):
        return self.origin.x + (self.width * 0.5)

    def mid_y(self):
        return self.origin.y + (self.height * 0.5)

    def max_x(self):
        norm = self.normalized()
        return norm.origin.x + norm.width

    def max_y(self):
        norm = self.normalized()
        return norm.origin.y + norm.height

    def contract(self, distance):
        self.origin.x += distance
        self.origin.y += distance
        self.width -= 2.0 * distance
        self.height -= 2.0 * distance


image_width = 1000.0
image_height = 660.0
font_family = "Roboto"
lines = ['']


def convert_point_to_svg_coordinates(point=Point(0, 0)):
    y = image_height - point.y
    return Point(point.x, y)


def convert_rect_to_svg_coordinates(rect=Rect()):
    """Convert to SVG coordinate system (0,0 at top-left)"""
    normalized_rect = rect.normalized()
    normalized_rect.origin = convert_point_to_svg_coordinates(
        normalized_rect.origin)
    normalized_rect.height *= -1
    return normalized_rect.normalized()


def svg_color(color):
    return 'rgb({},{},{})'.format(repr(color[0]), repr(color[1]), repr(color[2]))


def draw_rect(rect, stroke_width=2.0, stroke_color=COLORS['black']):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" ' \
               r'style="fill:rgb(255,255,255);stroke-width:{};' \
               r'stroke:{};opacity:1;' \
               r'fill-opacity:0;" />'.format(repr(svg_rect.origin.x),
                                             repr(svg_rect.origin.y),
                                             repr(svg_rect.width),
                                             repr(svg_rect.height),
                                             repr(stroke_width),
                                             svg_color(
                                                 stroke_color))
    lines.append(rect_str)


def draw_labeled_rect(rect, stroke_width=2.0,
                      stroke_color=COLORS['black'],
                      fill_color=COLORS['white'],
                      label='',
                      label_size=10.0):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    text_str = r'<text font-size="{}" font-family="{}" x="50%" y="50%"' \
               r' style="stroke:{};stroke-width:{};' \
               r'fill:{};opacity:{};" alignment-baseline="middle"' \
               r' text-anchor="middle">{}</text>'.format(repr(label_size),
                                                         font_family,
                                                         svg_color(COLORS['black']),
                                                         repr(stroke_width / 4.0),
                                                         svg_color(COLORS['black']),
                                                         repr(COLORS['black'][3]),
                                                         label)
    rect_str = r'<g transform="translate({},{})">' \
               r'   <rect width="{}" height="{}"' \
               r'    style="fill:{};stroke-width:{};stroke:{};opacity:1;"/>' \
               r'   <svg width="{}" height="{}">'.format(repr(svg_rect.origin.x),
                                                         repr(svg_rect.origin.y),
                                                         repr(svg_rect.width),
                                                         repr(svg_rect.height),
                                                         svg_color(fill_color),
                                                         repr(stroke_width),
                                                         svg_color(stroke_color),
                                                         repr(svg_rect.width),
                                                         repr(svg_rect.height)) \
               + text_str + \
               r'   </svg>' \
               r'</g>'
    lines.append(rect_str)


def draw_dashed_rect(rect, stroke_width=2.0, stroke_color=COLORS['black'],
                     fill_color=COLORS['white']):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" ' \
               r'stroke-dasharray="5" ' \
               r'style="fill:{};stroke-width:{};' \
               r'stroke:{};opacity:1;' \
               r'fill-opacity:{};" />'.format(repr(svg_rect.origin.x),
                                              repr(svg_rect.origin.y),
                                              repr(svg_rect.width),
                                              repr(svg_rect.height),
                                              svg_color(fill_color),
                                              repr(stroke_width),
                                              svg_color(
                                                  stroke_color),
                                              repr(fill_color[3] / 255.0))
    lines.append(rect_str)


def draw_labeled_dashed_rect_with_border(rect, stroke_width=2.0,
                                         fill_color=COLORS['white'],
                                         border_color=COLORS['black'],
                                         label='',
                                         label_size=10.0):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    text_str = r'<text font-size="{}" font-family="{}" x="50%" y="50%"' \
               r' style="stroke:{};stroke-width:{};' \
               r'fill:{};opacity:{};" alignment-baseline="middle"' \
               r' text-anchor="middle">{}</text>'.format(repr(label_size),
                                                         font_family,
                                                         svg_color(COLORS['black']),
                                                         repr(stroke_width / 4.0),
                                                         svg_color(COLORS['black']),
                                                         repr(COLORS['black'][3]),
                                                         label)
    rect_str = r'<g transform="translate({},{})">' \
               r'   <rect width="{}" height="{}"' \
               r'    stroke-dasharray="5" ' \
               r'    style="fill:{};stroke-width:{};stroke:{};opacity:{};"/>' \
               r'   <svg width="{}" height="{}">'.format(repr(svg_rect.origin.x),
                                                         repr(svg_rect.origin.y),
                                                         repr(svg_rect.width),
                                                         repr(svg_rect.height),
                                                         svg_color(fill_color),
                                                         repr(stroke_width),
                                                         svg_color(border_color),
                                                         repr(fill_color[3] / 255.0),
                                                         repr(svg_rect.width),
                                                         repr(svg_rect.height)) \
               + text_str + \
               r'   </svg>' \
               r'</g>'
    lines.append(rect_str)


def draw_solid_rect(rect, fill_color=COLORS['white']):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" ' \
               r'style="fill:{};stroke-width:0;' \
               r'stroke:rgb(0,0,0);opacity:{};" />'.format(repr(svg_rect.origin.x),
                                                           repr(svg_rect.origin.y),
                                                           repr(svg_rect.width),
                                                           repr(svg_rect.height),
                                                           svg_color(fill_color),
                                                           repr(fill_color[3] / 255.0))
    lines.append(rect_str)


def draw_solid_rect_with_border(rect, stroke_width=2.0,
                                fill_color=COLORS['white'],
                                border_color=COLORS['black']):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" ' \
               r'style="fill:{};stroke-width:{};' \
               r'stroke:{};opacity:{};" />'.format(repr(svg_rect.origin.x),
                                                   repr(svg_rect.origin.y),
                                                   repr(svg_rect.width),
                                                   repr(svg_rect.height),
                                                   svg_color(fill_color),
                                                   repr(stroke_width),
                                                   svg_color(border_color),
                                                   repr(fill_color[3] / 255.0))
    lines.append(rect_str)


def draw_labeled_solid_rect_with_border(rect, stroke_width=2.0,
                                        fill_color=COLORS['white'],
                                        border_color=COLORS['black'],
                                        label='',
                                        label_size=10.0):
    svg_rect = convert_rect_to_svg_coordinates(rect)
    text_str = r'<text font-size="{}" font-family="{}" x="50%" y="50%"' \
               r' style="stroke:{};stroke-width:{};' \
               r'fill:{};opacity:{};" alignment-baseline="middle"' \
               r' text-anchor="middle">{}</text>'.format(repr(label_size),
                                                         font_family,
                                                         svg_color(COLORS['black']),
                                                         repr(stroke_width / 4.0),
                                                         svg_color(COLORS['black']),
                                                         repr(COLORS['black'][3]),
                                                         label)
    rect_str = r'<g transform="translate({},{})">' \
               r'   <rect width="{}" height="{}"' \
               r'    style="fill:{};stroke-width:{};stroke:{};opacity:{};"/>' \
               r'   <svg width="{}" height="{}">'.format(repr(svg_rect.origin.x),
                                                         repr(svg_rect.origin.y),
                                                         repr(svg_rect.width),
                                                         repr(svg_rect.height),
                                                         svg_color(fill_color),
                                                         repr(stroke_width),
                                                         svg_color(border_color),
                                                         repr(fill_color[3] / 255.0),
                                                         repr(svg_rect.width),
                                                         repr(svg_rect.height)) \
               + text_str + \
               r'   </svg>' \
               r'</g>'
    lines.append(rect_str)


def draw_line(start_point, end_point, stroke_width,
              stroke_color=COLORS['black'], is_dashed=False):
    point1 = convert_point_to_svg_coordinates(start_point)
    point2 = convert_point_to_svg_coordinates(end_point)
    if is_dashed:
        line = r'<line x1="{}" y1="{}" x2="{}" y2="{}" ' \
               r'style="stroke:{};stroke-width:{};opacity:{};' \
               r'stroke-linecap:butt;' \
               r'stroke-dasharray:4 1" />'.format(repr(point1.x),
                                                  repr(point1.y),
                                                  repr(point2.x),
                                                  repr(point2.y),
                                                  svg_color(stroke_color),
                                                  repr(stroke_width),
                                                  repr(stroke_color[3]))
    else:
        line = r'<line x1="{}" y1="{}" x2="{}" y2="{}" ' \
               r'style="stroke:{};stroke-width:{};opacity:{};' \
               r'stroke-linecap:butt;" />'.format(repr(point1.x),
                                                  repr(point1.y),
                                                  repr(point2.x), repr(point2.y),
                                                  svg_color(stroke_color),
                                                  repr(stroke_width),
                                                  repr(stroke_color[3]))
    lines.append(line)


def draw_arrow(start_point, end_point, stroke_width, stroke_color=COLORS['black']):
    point1 = convert_point_to_svg_coordinates(start_point)
    point2 = convert_point_to_svg_coordinates(end_point)
    direction = Point(point2.x - point1.x, point2.y - point1.y)
    direction_magnitude = math.sqrt(direction.x * direction.x +
                                    direction.y * direction.y)
    inv_magnitude = 1.0 / direction_magnitude
    arrowhead_length = 9.0
    arrowhead_half_width = arrowhead_length * 0.5
    direction = Point(direction.x * inv_magnitude, direction.y * inv_magnitude)
    point2 = Point(point2.x - arrowhead_length * direction.x,
                   point2.y - arrowhead_length * direction.y)
    triangle_tip = Point(point2.x + arrowhead_length * direction.x,
                         point2.y + arrowhead_length * direction.y)
    perpendicular_dir = Point(-direction.y, direction.x)
    triangle_pt_1 = Point(point2.x + arrowhead_half_width * perpendicular_dir.x,
                          point2.y + arrowhead_half_width * perpendicular_dir.y)
    triangle_pt_2 = Point(point2.x - arrowhead_half_width * perpendicular_dir.x,
                          point2.y - arrowhead_half_width * perpendicular_dir.y)
    line = r'<line x1="{}" y1="{}" x2="{}" y2="{}" ' \
           r'style="stroke:{};stroke-width:{};opacity:{};' \
           r'stroke-linecap:butt;" />'.format(repr(point1.x),
                                              repr(point1.y),
                                              repr(point2.x),
                                              repr(point2.y),
                                              svg_color(stroke_color),
                                              repr(stroke_width),
                                              repr(stroke_color[3]))
    triangle = r'<polygon points="{},{} {},{} {},{}" ' \
               r'style="fill:{};" />'.format(repr(triangle_tip.x),
                                             repr(triangle_tip.y),
                                             repr(triangle_pt_1.x),
                                             repr(triangle_pt_1.y),
                                             repr(triangle_pt_2.x),
                                             repr(triangle_pt_2.y),
                                             svg_color(stroke_color))
    lines.append(line)
    lines.append(triangle)


def draw_text(text, location,
              text_size, color=COLORS['black'], stroke_width=1.0):
    location_svg = convert_point_to_svg_coordinates(location)
    text_str = r'<text font-size="{}" font-family="{}" x="{}" y="{}"' \
               r' style="stroke:{};stroke-width:{};' \
               r'fill:{};opacity:{};">{}</text>'.format(repr(text_size),
                                                        font_family,
                                                        repr(location_svg.x),
                                                        repr(location_svg.y),
                                                        svg_color(color),
                                                        repr(stroke_width / 4.0),
                                                        svg_color(color),
                                                        repr(color[3]),
                                                        text)
    lines.append(text_str)


def get_image():
    header = r'<svg height="{}" width="{}" version="4.0"' \
             r' xmlns="http://www.w3.org/2000/svg"' \
             r' xmlns:xlink= "http://www.w3.org/1999/xlink">'.format(image_height,
                                                                     image_width)
    background = r'<rect width="100%" height="100%" fill="white"/>'
    font = r'<defs><style>@import url("https://fonts.googleapis.com/css?' \
           r'family={}");</style></defs>'.format(font_family)
    separator = '\n'
    image = header + '\n' + background + '\n' + font + '\n' + separator.join(
        lines) + '\n</svg>'
    return image


class ClipData(object):

    def __init__(self, src_start=0.0, src_end=0.0, avlbl_start=0.0,
                 avlbl_end=0.0, avlbl_duration=0.0,
                 trim_start=0.0, trim_duration=0.0, target_url='', clip_id=0,
                 transition_begin=None, transition_end=None):
        self.src_start = src_start
        self.src_end = src_end
        self.avlbl_start = avlbl_start
        self.avlbl_end = avlbl_end
        self.avlbl_duration = avlbl_duration
        self.trim_start = trim_start
        self.trim_duration = trim_duration
        self.target_url = target_url
        self.clip_id = clip_id
        self.transition_begin = transition_begin
        self.transition_end = transition_end


all_clips_data = []
trackwise_clip_count = []
tracks_duration = []
track_transition_available = []
max_total_duration = 0
global_min_time = 0
global_max_time = 0
scale_x = 1.0
scale_y = 1.0
x_origin = 0
image_margin = 20.0
arrow_margin = 10.0
font_size = 15
text_margin = 0.5 * font_size
clip_rect_height = 0
vertical_drawing_index = -1
arrow_label_margin = 5.0


def draw_item(otio_obj, extra_data=()):
    WRITE_TYPE_MAP = {
        otio.schema.Timeline: _draw_timeline,
        otio.schema.Stack: _draw_stack,
        otio.schema.Track: _draw_track,
        otio.schema.Clip: _draw_clip,
        otio.schema.Gap: _draw_gap,
        otio.schema.Transition: _draw_transition,
        otio.schema.SerializableCollection: _draw_collection,
    }

    if type(otio_obj) in WRITE_TYPE_MAP:
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, extra_data)


# Draw Timeline and calculate Clip and Gap data
def _draw_timeline(timeline, extra_data=()):
    global global_max_time
    global global_min_time
    global max_total_duration
    global scale_x
    global scale_y
    global x_origin
    global clip_rect_height
    global vertical_drawing_index
    global trackwise_clip_count
    global arrow_label_margin
    clip_count = 0
    transition_track_count = 0
    for track in timeline.tracks:
        if len(track) == 0:
            continue
        current_track_clips_data = []
        current_track_has_transition = False
        current_transition = None
        track_duration = 0
        min_time = 0
        max_time = 0
        for item in track:
            if isinstance(item, otio.schema.Transition):
                current_track_has_transition = True
                current_transition = item
                current_track_clips_data[-1].transition_end = item
                continue
            avlbl_start = track_duration - item.trimmed_range().start_time.value
            if isinstance(item, otio.schema.Clip):
                avlbl_start += item.available_range().start_time.value
            min_time = min(min_time, avlbl_start)
            src_start = track_duration
            track_duration += item.trimmed_range().duration.value
            src_end = track_duration - 1
            avlbl_end = 0.0
            trim_start = item.trimmed_range().start_time.value
            trim_duration = item.trimmed_range().duration.value
            if isinstance(item, otio.schema.Clip):
                avlbl_end = (item.available_range().start_time.value +
                             item.available_range().duration.value -
                             item.trimmed_range().start_time.value -
                             item.trimmed_range().duration.value + track_duration - 1)
                clip_count += 1
                avlbl_duration = item.available_range().duration.value
                clip_data = ClipData(src_start, src_end, avlbl_start,
                                     avlbl_end, avlbl_duration, trim_start,
                                     trim_duration,
                                     item.media_reference.target_url, clip_count - 1)
                if current_transition is not None:
                    clip_data.transition_begin = current_transition
                    current_transition = None
                current_track_clips_data.append(clip_data)
            elif isinstance(item, otio.schema.Gap):
                avlbl_end = src_end
                avlbl_duration = trim_duration
                current_transition = None
                clip_data = ClipData(src_start, src_end, avlbl_start,
                                     avlbl_end, avlbl_duration, trim_start,
                                     trim_duration,
                                     "Gap", -1)
                current_track_clips_data.append(clip_data)
            max_time = max(max_time, avlbl_end)
        global_max_time = max(global_max_time, max_time)
        global_min_time = min(global_min_time, min_time)
        all_clips_data.append(current_track_clips_data)
        tracks_duration.append(track_duration)
        track_transition_available.append(current_track_has_transition)
        if current_track_has_transition:
            transition_track_count += 1
        # store track-wise clip count to draw arrows from stack to tracks
        if len(trackwise_clip_count) == 0:
            trackwise_clip_count.append(clip_count)
        else:
            trackwise_clip_count.append(
                clip_count - trackwise_clip_count[len(trackwise_clip_count) - 1])
    # The scale in x direction is calculated considering margins on the
    # left and right side if the image
    scale_x = (image_width - (2.0 * image_margin)) / \
              (global_max_time - global_min_time + 1.0)
    x_origin = (-global_min_time) * scale_x + image_margin
    track_count = len(tracks_duration)
    # The rect height is calculated considering the following:
    # Total space available:
    #   image height - top & bottom margin -
    #   space for two labels for the bottom-most rect
    # Number of total rects to fit the height of the drawing space:
    #   track_count * 2.0 = one for track rect and one for the sequence of
    #                       components on that track
    #   + 2.0 = timeline and stack rects
    #   clip_count = we need to draw a rect for a media reference per clip
    #   transition_track_count = we need one more row per the number of tracks with
    #                            transitions
    # NumberOfRects * 2.0 - 1.0 = to account for "one rect space" between all the rects
    if transition_track_count == 0:
        clip_rect_height = (image_height - (2.0 * image_margin) - (2.0 * font_size)) / \
                           (((track_count * 2.0) + 2.0 + clip_count) * 2.0 - 1.0)
    else:
        clip_rect_height = (image_height - (2.0 * image_margin) -
                            (2.0 * font_size)) / \
                           (((track_count * 2.0) + 2.0 + clip_count +
                             transition_track_count) * 2.0 - 1.0)

    # Draw Timeline
    vertical_drawing_index += 2
    timeline_origin = Point(x_origin,
                            image_height - image_margin -
                            vertical_drawing_index * clip_rect_height)
    max_total_duration = max(tracks_duration)
    label_text_size = 0.4 * clip_rect_height
    draw_labeled_solid_rect_with_border(
        Rect(timeline_origin, max_total_duration * scale_x, clip_rect_height),
        label="Timeline", label_size=label_text_size)
    time_marker_height = 0.15 * clip_rect_height
    for i in range(1, int(max_total_duration)):
        start_pt = Point(x_origin + (i * scale_x), timeline_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                  stroke_color=COLORS['black'])
    # Draw arrow from timeline to stack
    timeline_width = max_total_duration * scale_x
    arrow_start = Point(x_origin + timeline_width * 0.5,
                        timeline_origin.y - arrow_margin)
    arrow_end = Point(x_origin + timeline_width * 0.5,
                      timeline_origin.y - clip_rect_height + arrow_margin)
    draw_arrow(start_point=arrow_start, end_point=arrow_end, stroke_width=2.0,
               stroke_color=COLORS['black'])
    arrow_label_location = Point(arrow_start.x + arrow_label_margin,
                                 (arrow_start.y + arrow_end.y) * 0.5)
    draw_text('tracks', arrow_label_location, font_size)
    # Draw global_start_time info
    if timeline.global_start_time is None:
        start_time_text = r'global_start_time: {}'.format('None')
    else:
        start_time_text = r'global_start_time: {}'.format(
            repr(float(round(timeline.global_start_time.value, 1))))
    start_time_location = Point(timeline_origin.x + font_size,
                                timeline_origin.y - font_size)
    draw_text(start_time_text, start_time_location, font_size)

    # Draw stack
    draw_item(timeline.tracks, (x_origin, max_total_duration))


# Draw stack
def _draw_stack(stack, extra_data=()):
    global vertical_drawing_index
    global clip_rect_height
    global scale_x
    global scale_y
    global trackwise_clip_count
    global text_margin
    global arrow_label_margin
    stack_x_origin = extra_data[0]
    stack_duration = extra_data[1]
    vertical_drawing_index += 2
    stack_origin = Point(stack_x_origin,
                         image_height - image_margin -
                         vertical_drawing_index * clip_rect_height)
    stack_text_size = 0.4 * clip_rect_height
    draw_labeled_solid_rect_with_border(
        Rect(stack_origin, stack_duration * scale_x, clip_rect_height),
        label="Stack", fill_color=COLORS['dark_gray_transluscent'],
        label_size=stack_text_size)
    time_marker_height = 0.15 * clip_rect_height
    for i in range(1, int(max_total_duration)):
        start_pt = Point(x_origin + (i * scale_x), stack_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                  stroke_color=COLORS['black'])
    for i in range(0, len(tracks_duration)):
        draw_item(stack[i], (stack_x_origin, tracks_duration[i], all_clips_data[i],
                             track_transition_available[i]))
    # Draw arrows from stack to tracks
    #   arrow from stack to first track
    stack_width = stack_duration * scale_x
    arrow_start = Point(x_origin + stack_width * 0.5,
                        stack_origin.y - arrow_margin)
    arrow_end = Point(x_origin + stack_width * 0.5,
                      stack_origin.y - clip_rect_height + arrow_margin)
    draw_arrow(start_point=arrow_start, end_point=arrow_end, stroke_width=2.0,
               stroke_color=COLORS['black'])
    end_arrow_offset = 1
    #   arrows from stack to rest of the tracks
    for i in range(1, len(trackwise_clip_count)):
        arrow_x_increment_per_track = 10.0
        end_arrow_offset += (trackwise_clip_count[i - 1] * 2.0 + 4.0)
        arrow_start = Point(
            (i * arrow_x_increment_per_track) + x_origin + stack_width * 0.5,
            stack_origin.y - arrow_margin)
        arrow_end = Point(
            (i * arrow_x_increment_per_track) + x_origin + stack_width * 0.5,
            stack_origin.y - (end_arrow_offset * clip_rect_height) +
            arrow_margin)
        draw_arrow(start_point=arrow_start, end_point=arrow_end, stroke_width=2.0,
                   stroke_color=COLORS['black'])
    arrow_label_text = r'children[{}]'.format(len(trackwise_clip_count))
    arrow_label_location = Point(arrow_start.x + arrow_label_margin,
                                 stack_origin.y - clip_rect_height * 0.5)
    draw_text(arrow_label_text, arrow_label_location, font_size)
    # Draw range info
    if stack.trimmed_range() is None:
        trimmed_range_text = r'trimmed_range() -> {}'.format('None')
    else:
        trimmed_range_text = r'trimmed_range() -> {}, {}'.format(
            repr(float(round(stack.trimmed_range().start_time.value, 1))),
            repr(float(round(stack.trimmed_range().duration.value, 1))))
    if stack.source_range is None:
        source_range_text = r'source_range: {}'.format('None')
    else:
        source_range_text = r'source_range: {}, {}'.format(
            repr(float(round(stack.source_range.start_time.value, 1))),
            repr(float(round(stack.source_range.duration.value, 1))))
    trimmed_range_location = Point(stack_origin.x + font_size,
                                   stack_origin.y + clip_rect_height + text_margin)
    source_range_location = Point(stack_origin.x + font_size,
                                  stack_origin.y - font_size)
    draw_text(trimmed_range_text, trimmed_range_location, font_size)
    draw_text(source_range_text, source_range_location, font_size)


def _draw_track(track, extra_data=()):
    global vertical_drawing_index
    global text_margin
    global arrow_label_margin
    vertical_drawing_index += 2
    track_x_origin = extra_data[0]
    track_duration = extra_data[1]
    clips_data = extra_data[2]
    track_has_transition = extra_data[3]
    track_origin = Point(track_x_origin,
                         image_height - image_margin -
                         vertical_drawing_index * clip_rect_height)
    track_text_size = 0.4 * clip_rect_height
    track_text = 'Track' if len(track.name) == 0 else track.name
    draw_labeled_solid_rect_with_border(
        Rect(track_origin, track_duration * scale_x, clip_rect_height),
        label=track_text, fill_color=COLORS['dark_gray_transluscent'],
        label_size=track_text_size)
    time_marker_height = 0.15 * clip_rect_height
    for i in range(1, int(track_duration)):
        start_pt = Point(x_origin + (i * scale_x), track_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                  stroke_color=COLORS['black'])
    item_count = 0
    clip_count = 0
    transition_count = 0
    vertical_drawing_index += 2
    if track_has_transition:
        vertical_drawing_index += 2
    for item in track:
        if isinstance(item, otio.schema.Clip):
            clip_count += 1
            draw_item(item, (clips_data[item_count], clip_count))
            item_count += 1
        elif isinstance(item, otio.schema.Gap):
            draw_item(item, (clips_data[item_count],))
            item_count += 1
        elif isinstance(item, otio.schema.Transition):
            cut_x = x_origin + (clips_data[item_count].src_start * scale_x)
            draw_item(item, (cut_x,))
            transition_count += 1
    vertical_drawing_index += (2 * clip_count)
    # Draw arrow from track to clips
    track_width = track_duration * scale_x
    arrow_start = Point(x_origin + track_width * 0.5,
                        track_origin.y - arrow_margin)
    arrow_end = Point(x_origin + track_width * 0.5,
                      track_origin.y - clip_rect_height + arrow_margin)
    draw_arrow(start_point=arrow_start, end_point=arrow_end, stroke_width=2.0,
               stroke_color=COLORS['black'])
    arrow_label_text = r'children[{}]'.format(item_count + transition_count)
    arrow_label_location = Point(arrow_start.x + arrow_label_margin,
                                 track_origin.y - clip_rect_height * 0.5)
    draw_text(arrow_label_text, arrow_label_location, font_size)
    # Draw range info
    if track.trimmed_range() is None:
        trimmed_range_text = r'trimmed_range() -> {}'.format('None')
    else:
        trimmed_range_text = r'trimmed_range() -> {}, {}'.format(
            repr(float(round(track.trimmed_range().start_time.value, 1))),
            repr(float(round(track.trimmed_range().duration.value, 1))))
    if track.source_range is None:
        source_range_text = r'source_range: {}'.format('None')
    else:
        source_range_text = r'source_range: {}, {}'.format(
            repr(float(round(track.source_range.start_time.value, 1))),
            repr(float(round(track.source_range.duration.value, 1))))
    trimmed_range_location = Point(track_origin.x + font_size,
                                   track_origin.y + clip_rect_height + text_margin)
    source_range_location = Point(track_origin.x + font_size,
                                  track_origin.y - font_size)
    draw_text(trimmed_range_text, trimmed_range_location, font_size)
    draw_text(source_range_text, source_range_location, font_size)


# Draw clip
def _draw_clip(clip, extra_data=()):
    global x_origin
    global image_height
    global image_margin
    global clip_rect_height
    global vertical_drawing_index
    global text_margin
    global arrow_label_margin
    clip_data = extra_data[0]
    clip_count = extra_data[1]
    clip_color = random_color()
    clip_origin = Point(x_origin + (clip_data.src_start * scale_x),
                        image_height - image_margin -
                        vertical_drawing_index * clip_rect_height)
    clip_rect = Rect(clip_origin, clip_data.trim_duration * scale_x, clip_rect_height)
    clip_text_size = 0.4 * clip_rect_height
    clip_text = r'Clip-{}'.format(clip_data.clip_id) if len(
        clip.name) == 0 else clip.name
    draw_labeled_solid_rect_with_border(
        clip_rect,
        label=clip_text, fill_color=clip_color,
        label_size=clip_text_size)
    time_marker_height = 0.15 * clip_rect_height
    for i in range(int(clip_data.src_start), int(clip_data.src_end) + 1):
        start_pt = Point(x_origin + (i * scale_x), clip_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                  stroke_color=COLORS['black'])
    # Draw range info
    if clip.trimmed_range() is None:
        trimmed_range_text = r'trimmed_range() -> {}'.format('None')
    else:
        trimmed_range_text = r'trimmed_range() -> {}, {}'.format(
            repr(float(round(clip.trimmed_range().start_time.value, 1))),
            repr(float(round(clip.trimmed_range().duration.value, 1))))
    if clip.source_range is None:
        source_range_text = r'source_range: {}'.format('None')
    else:
        source_range_text = r'source_range: {}, {}'.format(
            repr(float(round(clip.source_range.start_time.value, 1))),
            repr(float(round(clip.source_range.duration.value, 1))))
    trimmed_range_location = Point(clip_origin.x + font_size,
                                   clip_origin.y + clip_rect_height + text_margin)
    source_range_location = Point(clip_origin.x + font_size,
                                  clip_origin.y - font_size)
    draw_text(trimmed_range_text, trimmed_range_location, font_size)
    draw_text(source_range_text, source_range_location, font_size)

    # Draw media reference
    trim_media_origin = Point(x_origin + (clip_data.src_start * scale_x),
                              image_height - image_margin -
                              (vertical_drawing_index + clip_count * 2) *
                              clip_rect_height)
    media_origin = Point(x_origin + (clip_data.avlbl_start * scale_x),
                         image_height - image_margin -
                         (vertical_drawing_index + clip_count * 2) * clip_rect_height)
    draw_rect(Rect(media_origin, clip_data.avlbl_duration * scale_x,
                   clip_rect_height))
    media_text_size = 0.4 * clip_rect_height
    media_text = r'Media-{}'.format(clip_data.clip_id) if len(
        clip.media_reference.name) == 0 else clip.media_reference.name
    draw_labeled_solid_rect_with_border(
        Rect(trim_media_origin, clip_data.trim_duration * scale_x, clip_rect_height),
        label=media_text, fill_color=clip_color,
        label_size=media_text_size)
    for i in range(int(clip_data.avlbl_start),
                   int(clip_data.avlbl_end) + 1):
        start_pt = Point(x_origin + (i * scale_x), media_origin.y)
        if start_pt.x < media_origin.x:
            continue
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                  stroke_color=COLORS['black'])
    # Draw media_reference info
    if clip.available_range() is None:
        available_range_text = r'available_range: {}'.format('None')
    else:
        available_range_text = r'available_range: {}, {}'.format(
            repr(float(round(clip.available_range().start_time.value, 1))),
            repr(float(round(clip.available_range().duration.value, 1))))
    if clip.media_reference.target_url is None:
        target_url_text = r'target_url: {}'.format('Media Unavailable')
    else:
        target_url_text = r'target_url: {}'.format(clip.media_reference.target_url)
    available_range_text = available_range_text
    available_range_location = Point(media_origin.x + font_size,
                                     media_origin.y - font_size)
    target_url_location = Point(media_origin.x + font_size,
                                media_origin.y - 2.0 * font_size)
    draw_text(available_range_text, available_range_location, font_size)
    draw_text(target_url_text, target_url_location, font_size)
    # Draw arrow from clip to media reference
    clip_media_height_difference = ((clip_count - 1) * 2.0 + 1) * clip_rect_height
    media_arrow_start = Point(
        clip_origin.x + (clip_data.trim_duration * scale_x) * 0.5,
        clip_origin.y - arrow_margin)
    media_arrow_end = Point(
        clip_origin.x + (clip_data.trim_duration * scale_x) * 0.5,
        clip_origin.y - clip_media_height_difference + arrow_margin)
    draw_arrow(start_point=media_arrow_start, end_point=media_arrow_end,
               stroke_width=2.0, stroke_color=COLORS['black'])
    arrow_label_text = r'media_reference'
    arrow_label_location = Point(media_arrow_start.x + arrow_label_margin,
                                 media_arrow_start.y -
                                 clip_rect_height * 0.5)
    draw_text(arrow_label_text, arrow_label_location, font_size)
    # Draw media transition sections
    if clip_data.transition_end is not None:
        cut_x = clip_origin.x + clip_rect.width
        section_start_pt = Point(cut_x, media_origin.y)
        # Handle the case of transition ending at cut
        if clip_data.transition_end.out_offset.value == 0.0:
            media_transition_rect = Rect(section_start_pt,
                                         -clip_data.transition_end.in_offset.value *
                                         scale_x,
                                         clip_rect_height)
            marker_x = [clip_data.src_end,
                        clip_data.src_end - clip_data.transition_end.in_offset.value]
        else:
            media_transition_rect = Rect(section_start_pt,
                                         clip_data.transition_end.out_offset.value *
                                         scale_x,
                                         clip_rect_height)
            marker_x = [clip_data.src_end,
                        clip_data.src_end + clip_data.transition_end.out_offset.value]
        section_color = clip_color[0], clip_color[1], clip_color[2], 127.5
        draw_dashed_rect(media_transition_rect, fill_color=section_color)
        marker_x.sort()
        # Draw markers for transition sections
        for i in range(int(marker_x[0]),
                       int(marker_x[1]) + 1):
            start_pt = Point(x_origin + (i * scale_x), media_origin.y)
            if start_pt.x < media_transition_rect.min_x():
                continue
            end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
            draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                      stroke_color=COLORS['black'])
    if clip_data.transition_begin is not None:
        cut_x = clip_origin.x
        section_start_pt = Point(cut_x, media_origin.y)
        # Handle the case of transition starting at cut
        if clip_data.transition_begin.in_offset.value == 0.0:
            media_transition_rect = Rect(section_start_pt,
                                         clip_data.transition_begin.out_offset.value *
                                         scale_x,
                                         clip_rect_height)
            marker_x = [clip_data.src_start,
                        clip_data.src_start +
                        clip_data.transition_begin.out_offset.value]
        else:
            media_transition_rect = Rect(section_start_pt,
                                         -clip_data.transition_begin.in_offset.value *
                                         scale_x,
                                         clip_rect_height)
            marker_x = [clip_data.src_start,
                        clip_data.src_start -
                        clip_data.transition_begin.out_offset.value]
        section_color = clip_color[0], clip_color[1], clip_color[2], 127.5
        draw_dashed_rect(media_transition_rect, fill_color=section_color)
        marker_x.sort()
        # Draw markers for transition sections
        for i in range(int(marker_x[0]),
                       int(marker_x[1]) + 1):
            start_pt = Point(x_origin + (i * scale_x), media_origin.y)
            if start_pt.x < media_transition_rect.min_x():
                continue
            end_pt = Point(start_pt.x, start_pt.y + 0.15 * clip_rect_height)
            draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                      stroke_color=COLORS['black'])


def _draw_gap(gap, extra_data=()):
    global x_origin
    global image_height
    global image_margin
    global clip_rect_height
    global vertical_drawing_index
    global text_margin
    gap_data = extra_data[0]
    gap_origin = Point(x_origin + (gap_data.src_start * scale_x),
                       image_height - image_margin -
                       vertical_drawing_index * clip_rect_height)
    gap_text_size = 0.4 * clip_rect_height
    gap_text = 'Gap'
    draw_labeled_dashed_rect_with_border(
        Rect(gap_origin, gap_data.trim_duration * scale_x, clip_rect_height),
        label=gap_text, label_size=gap_text_size)
    time_marker_height = 0.15 * clip_rect_height
    for i in range(int(gap_data.src_start), int(gap_data.src_end) + 1):
        start_pt = Point(x_origin + (i * scale_x), gap_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                  stroke_color=COLORS['black'])
    # Draw range info
    if gap.trimmed_range() is None:
        trimmed_range_text = r'trimmed_range() -> {}'.format('None')
    else:
        trimmed_range_text = r'trimmed_range() -> {}, {}'.format(
            repr(float(round(gap.trimmed_range().start_time.value, 1))),
            repr(float(round(gap.trimmed_range().duration.value, 1))))
    if gap.source_range is None:
        source_range_text = r'source_range: {}'.format('None')
    else:
        source_range_text = r'source_range: {}, {}'.format(
            repr(float(round(gap.source_range.start_time.value, 1))),
            repr(float(round(gap.source_range.duration.value, 1))))
    trimmed_range_location = Point(gap_origin.x + font_size,
                                   gap_origin.y + clip_rect_height + text_margin)
    source_range_location = Point(gap_origin.x + font_size,
                                  gap_origin.y - font_size)
    draw_text(trimmed_range_text, trimmed_range_location, font_size)
    draw_text(source_range_text, source_range_location, font_size)


def _draw_transition(transition, extra_data=()):
    global x_origin
    global image_height
    global image_margin
    global clip_rect_height
    global vertical_drawing_index
    cut_x = extra_data[0]
    transition_origin = Point(cut_x - (transition.in_offset.value * scale_x),
                              image_height - image_margin -
                              (vertical_drawing_index - 2) * clip_rect_height)
    transition_rect = Rect(transition_origin,
                           (transition.in_offset.value + transition.out_offset.value) *
                           scale_x,
                           clip_rect_height)
    transition_name = 'Transition' if len(
        transition.name) == 0 else transition.name
    transition_name_size = 0.4 * clip_rect_height
    draw_labeled_rect(transition_rect, label=transition_name,
                      label_size=transition_name_size)
    line_end = Point(transition_origin.x + transition_rect.width,
                     transition_origin.y + transition_rect.height)
    draw_line(transition_origin, line_end, stroke_width=1.0,
              stroke_color=COLORS['black'])
    in_offset_location = Point(transition_origin.x + font_size,
                               transition_origin.y - font_size)
    out_offset_location = Point(transition_origin.x + font_size,
                                transition_origin.y - 2.0 * font_size)
    in_offset_text = r'in_offset: ' \
                     r'{}'.format(repr(float(round(transition.in_offset.value, 1))))
    out_offset_text = r'out_offset: ' \
                      r'{}'.format(repr(float(round(transition.out_offset.value, 1))))
    draw_text(in_offset_text, in_offset_location, font_size)
    draw_text(out_offset_text, out_offset_location, font_size)
    cut_location = Point(cut_x, transition_origin.y)
    cut_line_end = Point(cut_x,
                         image_height - image_margin -
                         vertical_drawing_index * clip_rect_height)
    draw_line(cut_location, cut_line_end, stroke_width=1.0,
              stroke_color=COLORS['black'])


def _draw_collection(collection, extra_data=()):
    pass


def convert_otio_to_svg(timeline, width, height):
    global image_width
    global image_height
    global font_family
    global lines
    global all_clips_data
    global trackwise_clip_count
    global tracks_duration
    global random_colors_used
    global track_transition_available
    global max_total_duration
    global global_min_time
    global global_max_time
    global scale_x
    global scale_y
    global x_origin
    global image_margin
    global font_size
    global text_margin
    global clip_rect_height
    global vertical_drawing_index
    global arrow_label_margin

    image_width = width
    image_height = height
    font_family = "Pattaya"
    lines = ['']
    all_clips_data = []
    trackwise_clip_count = []
    tracks_duration = []
    random_colors_used = []
    track_transition_available = []
    max_total_duration = 0
    global_min_time = 0
    global_max_time = 0
    scale_x = 1.0
    scale_y = 1.0
    x_origin = 0
    image_margin = 20.0
    font_size = 15
    text_margin = 0.5 * font_size
    clip_rect_height = 0
    vertical_drawing_index = -1
    arrow_label_margin = 5.0
    seed(100)
    draw_item(timeline, ())

    return get_image()


# --------------------
# adapter requirements
# --------------------

def write_to_string(input_otio, width=2406.0, height=1054.0):
    return convert_otio_to_svg(input_otio, width=width, height=height)
