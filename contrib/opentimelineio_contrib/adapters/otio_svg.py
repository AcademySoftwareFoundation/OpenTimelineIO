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

"""OTIO to SVG Adapter"""

import opentimelineio as otio

from random import seed
from random import random

seed(50)


class Color:
    r = 0.0
    g = 0.0
    b = 0.0
    a = 0.0

    def __init__(self, r=0.0, g=0.0, b=0.0, a=0.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def random_color():
        return Color(random(), random(), random(), 1.0)


transparent = Color(0, 0, 0, 0)
black = Color(0.0, 0.0, 0.0, 1.0)
white = Color(1.0, 1.0, 1.0, 1.0)
transluscent_white = Color(1.0, 1.0, 1.0, 0.7)
purple = Color(0.5, 0.0, 0.5, 1.0)
light_blue = Color(0.529, 0.808, 0.922, 1.0)
blue = Color(0.0, 0.0, 1.0, 1.0)
dark_blue = Color(0.0, 0.0, 0.54, 1.0)
green = Color(0.0, 0.5, 0.0, 1.0)
dark_green = Color(0.0, 0.39, 0.0, 1.0)
yellow = Color(1.0, 1.0, 0.0, 1.0)
gold = Color(1.0, 0.84, 0.0, 1.0)
orange = Color(1.0, 0.647, 0.0, 1.0)
red = Color(1.0, 0.0, 0.0, 1.0)
dark_red = Color(0.54, 0.0, 0.0, 1.0)
brown = Color(0.54, 0.27, 0.1, 1.0)
pink = Color(1.0, 0.75, 0.79, 1.0)
gray = Color(0.5, 0.5, 0.5, 1.0)
dark_gray = Color(0.66, 0.66, 0.66, 1.0)


class Point:
    x = 0.0
    y = 0.0

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Rect:
    origin = Point()
    width = 0.0
    height = 0.0

    def __init__(self, origin=Point(), width=0.0, height=0.0):
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
        return self.origin.x + (self.width / 2)

    def mid_y(self):
        return self.origin.y + (self.height / 2)

    def max_x(self):
        norm = self.normalized()
        return norm.origin.x + norm.width

    def max_y(self):
        norm = self.normalized()
        return norm.origin.y + norm.height

    def contract(self, distance):
        self.origin.x += distance
        self.origin.y += distance
        self.width -= 2 * distance
        self.height -= 2 * distance


class SVGRenderer:
    LCARS_CHAR_SIZE_ARRAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 17, 26, 46, 63, 42, 105, 45, 20, 25, 25, 47, 39, 21, 34, 26, 36, 36, 28, 36, 36, 36,
                             36, 36, 36, 36, 36, 27, 27, 36, 35, 36, 35, 65, 42, 43, 42, 44, 35, 34, 43, 46, 25, 39, 40,
                             31, 59, 47, 43, 41, 43, 44, 39, 28, 44, 43, 65, 37, 39, 34, 37, 42, 37, 50, 37, 32, 43, 43,
                             39, 43, 40, 30, 42, 45, 23, 25, 39, 23, 67, 45, 41, 43, 42, 30, 40, 28, 45, 33, 52, 33, 36,
                             31, 39, 26, 39, 55]
    width = 1000.0
    height = 660.0
    font_family = "Roboto"
    lines = ['']

    def __init__(self, width=1000.0, height=660.0, font_family="Roboto"):
        self.width = width
        self.height = height
        self.font_family = font_family

    def convert_point_to_svg_coordinates(self, point=Point()):
        y = self.height - point.y
        return Point(point.x, y)

    def convert_rect_to_svg_coordinates(self, rect=Rect()):
        """Convert to SVG coordinate system (0,0 at top-left)"""
        normalized_rect = rect.normalized()
        normalized_rect.origin = self.convert_point_to_svg_coordinates(normalized_rect.origin)
        normalized_rect.height *= -1
        return normalized_rect.normalized()

    def svg_color_string(self, color):
        return 'rgb({},{},{})'.format(color.r * 255.0, color.g * 255.0, color.b * 255.0)

    def draw_rect(self, rect, stroke_width=2, stroke_color=black):
        converted_rect = self.convert_rect_to_svg_coordinates(rect)
        rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" style="fill:rgb(255,255,255);stroke-width:{};' \
                   r'stroke:{};opacity:1;fill-opacity:0;" />'.format(converted_rect.origin.x, converted_rect.origin.y,
                                                                     converted_rect.width, converted_rect.height,
                                                                     stroke_width, self.svg_color_string(stroke_color))
        self.lines.append(rect_str)

    def draw_solid_rect(self, rect, fill_color=white):
        converted_rect = self.convert_rect_to_svg_coordinates(rect)
        rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" style="fill:{};stroke-width:0;' \
                   r'stroke:rgb(0,0,0);opacity:{};" />'.format(converted_rect.origin.x, converted_rect.origin.y,
                                                               converted_rect.width, converted_rect.height,
                                                               self.svg_color_string(fill_color), fill_color.a)
        self.lines.append(rect_str)

    def draw_solid_rect_with_border(self, rect, stroke_width=2, fill_color=white, border_color=black):
        converted_rect = self.convert_rect_to_svg_coordinates(rect)
        rect_str = r'<rect x="{}" y="{}" width="{}" height="{}" style="fill:{};stroke-width:{};' \
                   r'stroke:{};opacity:{};" />'.format(converted_rect.origin.x, converted_rect.origin.y,
                                                       converted_rect.width, converted_rect.height,
                                                       self.svg_color_string(fill_color), stroke_width,
                                                       self.svg_color_string(border_color), fill_color.a)
        self.lines.append(rect_str)

    def draw_line(self, start_point, end_point, stroke_width, stroke_color=black, is_dashed=False):
        svg_start_point = self.convert_point_to_svg_coordinates(start_point)
        svg_end_point = self.convert_point_to_svg_coordinates(end_point)
        line = ''
        if is_dashed:
            line = r'<line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:{};stroke-width:{};opacity:{};' \
                   r'stroke-linecap:butt;stroke-dasharray:4 1" />'.format(svg_start_point.x, svg_start_point.y,
                                                                          svg_end_point.x, svg_end_point.y,
                                                                          self.svg_color_string(stroke_color),
                                                                          stroke_width, stroke_color.a)
        else:
            line = r'<line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:{};stroke-width:{};opacity:{};' \
                   r'stroke-linecap:butt;" />'.format(svg_start_point.x, svg_start_point.y,
                                                      svg_end_point.x, svg_end_point.y,
                                                      self.svg_color_string(stroke_color),
                                                      stroke_width, stroke_color.a)
        self.lines.append(line)

    def draw_text(self, text, location, text_size, color=black, stroke_width=1):
        location_svg = self.convert_point_to_svg_coordinates(location)
        text_str = r'<text font-size="{}" font-family="{}" x="{}" y="{}"' \
                   r' style="stroke:{};stroke-width:{};' \
                   r'fill:{};opacity:{};">{}</text>'.format(text_size, self.font_family, location_svg.x, location_svg.y,
                                                            self.svg_color_string(color), stroke_width / 4.0,
                                                            self.svg_color_string(color), color.a, text)
        self.lines.append(text_str)

    def get_text_layout_size(self, text='', text_size=10.0):
        width = 0.0
        for character in text:
            ascii_val = int(ord(character))
            width += self.LCARS_CHAR_SIZE_ARRAY[ascii_val] if ascii_val < 128 else 0
        scale_factor = text_size / 100.0
        return width * scale_factor + 25

    def save_image(self, file_path):
        header = r'<svg height="{}" width="{}" version="4.0" xmlns="http://www.w3.org/2000/svg"' \
                 r' xmlns:xlink= "http://www.w3.org/1999/xlink">'.format(self.height, self.width)
        background = r'<rect width="100%" height="100%" fill="white"/>'
        font = r'<defs><style>@import url("https://fonts.googleapis.com/css?family=\#(fontFamily)");</style></defs>'
        separator = '\n'
        image = header + '\n' + background + '\n' + font + '\n' + separator.join(self.lines) + '\n</svg>'
        svg_file = open(file_path, 'w')
        svg_file.write(image)
        svg_file.close()


class ClipData:
    src_start = 0.0
    src_end = 0.0
    available_start = 0.0
    available_end = 0.0
    available_duration = 0.0
    trim_start = 0.0
    trim_duration = 0.0
    target_url = ''
    clip_id = 0

    def __init__(self, src_start=0.0, src_end=0.0, available_start=0.0, available_end=0.0, available_duration=0.0,
                 trim_start=0.0, trim_duration=0.0, target_url='', clip_id=0):
        self.src_start = src_start
        self.src_end = src_end
        self.available_start = available_start
        self.available_end = available_end
        self.available_duration = available_duration
        self.trim_start = trim_start
        self.trim_duration = trim_duration
        self.target_url = target_url
        self.clip_id = clip_id


def convert_otio_to_svg(timeline, filepath):
    renderer = SVGRenderer(2406.0, 1054.0)
    image_margin = 10.0
    font_size = 15
    # renderer.draw_line(Point(0, 0), Point(1203, 527), 3, black)
    # renderer.draw_rect(Rect(Point(1203, 527), 1203, 527))
    # renderer.draw_solid_rect_with_border(Rect(Point(803, 351.33), 1203, 527), fill_color=green, border_color=black)
    # renderer.draw_text("Hello SVG!", location=Point(50, 500), text_size=20)
    total_duration = 0
    min_time = 0.0
    max_time = 0.0
    all_clips_data = []
    clip_count = -1
    for current_clip in timeline.tracks[0]:
        if isinstance(current_clip, otio.schema.Clip):
            available_start = total_duration - current_clip.source_range.start_time.value
            min_time = min(min_time, available_start)
            src_start = total_duration
            total_duration += current_clip.source_range.duration.value
            src_end = total_duration - 1
            available_end = (current_clip.media_reference.available_range.start_time.value +
                             current_clip.media_reference.available_range.duration.value -
                             current_clip.source_range.start_time.value -
                             current_clip.source_range.duration.value + total_duration - 1)
            max_time = max(max_time, available_end)
            trim_start = current_clip.source_range.start_time.value
            trim_duration = current_clip.source_range.duration.value
            available_duration = current_clip.media_reference.available_range.duration.value
            clip_count += 1
            clip_data = ClipData(src_start, src_end, available_start,
                                 available_end, available_duration, trim_start, trim_duration,
                                 current_clip.media_reference.target_url, clip_count)
            all_clips_data.append(clip_data)

    scale_x = (renderer.width - (2.0*image_margin))/(max_time - min_time + 1.0)
    x_origin = (-min_time)*scale_x

    clip_rect_height = (renderer.height - (2.0*image_margin) - (2.0*font_size))/((4.0 + len(all_clips_data))*2 - 1)

    # Draw Timeline
    timeline_origin = Point(x_origin, renderer.height-image_margin - clip_rect_height)
    renderer.draw_solid_rect_with_border(Rect(timeline_origin, total_duration*scale_x, clip_rect_height),
                                         fill_color=gray, border_color=black)
    label_text_size = 0.4*clip_rect_height
    timeline_text_width = renderer.get_text_layout_size("Timeline", label_text_size)
    timeline_text_location = Point(x_origin + (total_duration*scale_x)/2.0 - (timeline_text_width/2.0), timeline_origin.y + (clip_rect_height/2.0))
    renderer.draw_text(text="Timeline", location=timeline_text_location, text_size=label_text_size)
    arrow_margin = 10
    arrow_start = Point(x_origin + (total_duration*scale_x)/2.0,
                        timeline_origin.y - arrow_margin)
    arrow_end = Point(x_origin + (total_duration*scale_x)/2.0,
                      timeline_origin.y - clip_rect_height + arrow_margin)
    renderer.draw_line(start_point=arrow_start, end_point=arrow_end, stroke_width=2, stroke_color=black)
    for i in range(1, int(total_duration)):
        start_pt = Point(x_origin + (i*scale_x), timeline_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + 0.15*clip_rect_height)
        renderer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1, stroke_color=black)

    # Draw Stack
    stack_origin = Point(x_origin, renderer.height - image_margin - 3*clip_rect_height)
    renderer.draw_solid_rect_with_border(Rect(stack_origin, total_duration * scale_x, clip_rect_height),
                                         fill_color=gray, border_color=black)
    stack_text_size = label_text_size
    stack_text_width = renderer.get_text_layout_size("Stack", stack_text_size)
    stack_text_location = Point(x_origin + (total_duration * scale_x) / 2.0 - (stack_text_width / 2.0),
                                stack_origin.y + (clip_rect_height / 2.0))
    renderer.draw_text(text="Stack", location=stack_text_location, text_size=stack_text_size)
    arrow_start = Point(x_origin + (total_duration * scale_x) / 2.0,
                        stack_origin.y - arrow_margin)
    arrow_end = Point(x_origin + (total_duration * scale_x) / 2.0,
                      stack_origin.y - clip_rect_height + arrow_margin)
    renderer.draw_line(start_point=arrow_start, end_point=arrow_end, stroke_width=2, stroke_color=black)
    for i in range(1, int(total_duration)):
        start_pt = Point(x_origin + (i * scale_x), stack_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + 0.15 * clip_rect_height)
        renderer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1, stroke_color=black)

    # Draw Track
    track_origin = Point(x_origin, renderer.height - image_margin - 5 * clip_rect_height)
    renderer.draw_solid_rect_with_border(Rect(track_origin, total_duration * scale_x, clip_rect_height),
                                         fill_color=gray, border_color=black)
    track_text_size = label_text_size
    track_text_width = renderer.get_text_layout_size("Track", track_text_size)
    track_text_location = Point(x_origin + (total_duration * scale_x) / 2.0 - (stack_text_width / 2.0),
                                track_origin.y + (clip_rect_height / 2.0))
    renderer.draw_text(text="Track", location=track_text_location, text_size=track_text_size)
    arrow_start = Point(x_origin + (total_duration * scale_x) / 2.0,
                        track_origin.y - arrow_margin)
    arrow_end = Point(x_origin + (total_duration * scale_x) / 2.0,
                      track_origin.y - clip_rect_height + arrow_margin)
    renderer.draw_line(start_point=arrow_start, end_point=arrow_end, stroke_width=2, stroke_color=black)
    for i in range(1, int(total_duration)):
        start_pt = Point(x_origin + (i * scale_x), track_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + 0.15 * clip_rect_height)
        renderer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1, stroke_color=black)

    # Draw Clips
    for clip_data in all_clips_data:
        clip_color = Color.random_color()
        clip_origin = Point(x_origin + (clip_data.src_start*scale_x),
                            renderer.height - image_margin - 7 * clip_rect_height)
        renderer.draw_solid_rect_with_border(Rect(clip_origin, clip_data.trim_duration * scale_x, clip_rect_height),
                                             fill_color=clip_color, border_color=black)
        clip_text_size = label_text_size
        clip_text = 'Clip-' + str(clip_data.clip_id)
        clip_text_width = renderer.get_text_layout_size(clip_text, clip_text_size)
        clip_text_location = Point(clip_origin.x + (clip_data.trim_duration * scale_x) / 2.0 - (stack_text_width / 2.0),
                                   clip_origin.y + (clip_rect_height / 2.0))
        renderer.draw_text(text=clip_text, location=clip_text_location, text_size=clip_text_size)
        for i in range(int(clip_data.src_start), int(clip_data.src_end)+1):
            start_pt = Point(x_origin + (i * scale_x), clip_origin.y)
            end_pt = Point(start_pt.x, start_pt.y + 0.15 * clip_rect_height)
            renderer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1, stroke_color=black)
        # Draw media references

        selected_media_origin = Point(x_origin + (clip_data.src_start * scale_x),
                                      renderer.height - image_margin - (7 + (clip_data.clip_id+1)*2) * clip_rect_height)
        media_origin = Point(x_origin + (clip_data.available_start * scale_x),
                             renderer.height - image_margin - (7 + (clip_data.clip_id + 1) * 2) * clip_rect_height)
        renderer.draw_solid_rect(Rect(selected_media_origin, clip_data.trim_duration * scale_x, clip_rect_height),
                                 fill_color=clip_color)
        renderer.draw_rect(Rect(media_origin, clip_data.available_duration*scale_x, clip_rect_height))
        media_text_size = label_text_size
        media_text = 'Media-' + str(clip_data.clip_id)
        media_text_width = renderer.get_text_layout_size(media_text, media_text_size)
        media_text_location = Point(media_origin.x + (clip_data.available_duration * scale_x) / 2.0
                                    - (stack_text_width / 2.0),
                                    media_origin.y + (clip_rect_height / 2.0))
        renderer.draw_text(text=media_text, location=media_text_location, text_size=media_text_size)
        clip_media_height_difference = (clip_data.clip_id*2 + 1) * clip_rect_height
        media_arrow_start = Point(clip_origin.x + (clip_data.trim_duration * scale_x) / 2.0,
                                  clip_origin.y - arrow_margin)
        media_arrow_end = Point(clip_origin.x + (clip_data.trim_duration * scale_x) / 2.0,
                                clip_origin.y - clip_media_height_difference + arrow_margin)
        renderer.draw_line(start_point=media_arrow_start, end_point=media_arrow_end, stroke_width=2, stroke_color=black)
        for i in range(int(clip_data.available_start), int(clip_data.available_end) + 1):
            start_pt = Point(x_origin + (i * scale_x), media_origin.y)
            end_pt = Point(start_pt.x, start_pt.y + 0.15 * clip_rect_height)
            renderer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1, stroke_color=black)

    renderer.save_image(filepath)


# --------------------
# adapter requirements
# --------------------

def write_to_file(input_otio, filepath):
    timeline = otio.core.deserialize_json_from_file(input_otio)
    convert_otio_to_svg(timeline, filepath)
    return
