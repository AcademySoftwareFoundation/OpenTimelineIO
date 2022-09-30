# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OTIO to SVG Adapter
   Points in calculations are y-up.
   Points in SVG are y-down."""

# otio
import opentimelineio as otio
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# python
import math
import random

random_colors_used = []


class Color:
    def __init__(self, r=0.0, g=0.0, b=0.0, a=255.0):
        self.value = (r, g, b, a)

    def __getitem__(self, item):
        return self.value[item]

    @staticmethod
    def random_color():
        color = Color.__generate_new_color()
        random_colors_used.append(color)
        return color

    @staticmethod
    def __generate_new_color():
        max_distance = None
        best_color = None
        for _ in range(100):
            color = Color.__get_random_color()
            if len(random_colors_used) == 0:
                return color
            best_distance = min([Color.__color_distance(color, c)
                                 for c in random_colors_used])
            if not max_distance or best_distance > max_distance:
                max_distance = best_distance
                best_color = color
        return best_color

    @staticmethod
    def __get_random_color():
        return Color(random.random(), random.random(), random.random(), 1.0)

    @staticmethod
    def __color_distance(c1, c2):
        return sum([abs(x[0] - x[1]) for x in zip(c1.value, c2.value)])

    @property
    def r(self):
        return self.value[0]

    @property
    def g(self):
        return self.value[1]

    @property
    def b(self):
        return self.value[2]

    @property
    def a(self):
        return self.value[3]

    def svg_color(self):
        return 'rgb({:.8f},{:.8f},{:.8f})'.format(
            self.r * 255.0,
            self.g * 255.0,
            self.b * 255.0
        )


COLORS = {
    'transparent': Color(0, 0, 0, 0),
    'black': Color(0.0, 0.0, 0.0, 1.0),
    'white': Color(1.0, 1.0, 1.0, 1.0),
    'transluscent_white': Color(1.0, 1.0, 1.0, 0.7),
    'purple': Color(0.5, 0.0, 0.5, 1.0),
    'light_blue': Color(0.529, 0.808, 0.922, 1.0),
    'blue': Color(0.0, 0.0, 1.0, 1.0),
    'dark_blue': Color(0.0, 0.0, 0.54, 1.0),
    'green': Color(0.0, 0.5, 0.0, 1.0),
    'dark_green': Color(0.0, 0.39, 0.0, 1.0),
    'yellow': Color(1.0, 1.0, 0.0, 1.0),
    'gold': Color(1.0, 0.84, 0.0, 1.0),
    'orange': Color(1.0, 0.647, 0.0, 1.0),
    'red': Color(1.0, 0.0, 0.0, 1.0),
    'dark_red': Color(0.54, 0.0, 0.0, 1.0),
    'brown': Color(0.54, 0.27, 0.1, 1.0),
    'pink': Color(1.0, 0.75, 0.79, 1.0),
    'gray': Color(0.5, 0.5, 0.5, 1.0),
    'dark_gray': Color(0.66, 0.66, 0.66, 1.0),
    'dark_gray_transluscent': Color(0.66, 0.66, 0.66, 0.7843)
}


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def svg_point_string(self):
        return f"{self.x:.8f},{self.y:.8f}"


class Rect:
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


def convert_point_to_svg_coordinates(point, image_height):
    y = image_height - point.y
    return Point(point.x, y)


def convert_rect_to_svg_coordinates(rect, image_height):
    """Convert to SVG coordinate system (0,0 at top-left)"""
    normalized_rect = rect.normalized()
    normalized_rect.origin = convert_point_to_svg_coordinates(
        normalized_rect.origin, image_height)
    normalized_rect.height *= -1
    return normalized_rect.normalized()


class SVGWriter:

    def __init__(
        self,
        image_width=2406.0,
        image_height=1054.0,
        image_margin=20.0,
        arrow_margin=10.0,
        arrow_label_margin=5.0,
        font_size=15.0,
        font_family='sans-serif'
    ):
        self.image_width = image_width
        self.image_height = image_height
        self.image_margin = image_margin
        self.arrow_margin = arrow_margin
        self.arrow_label_margin = arrow_label_margin
        self.font_size = font_size
        self.text_margin = 0.5 * font_size
        self.font_family = font_family

        self.all_clips_data = []
        self.trackwise_clip_count = []
        self.tracks_duration = []
        self.track_transition_available = []
        self.max_total_duration = 0
        self.global_min_time = 0
        self.global_max_time = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.x_origin = 0
        self.clip_rect_height = 0
        self.vertical_drawing_index = -1
        self.svg_elem = Element(
            "svg",
            {
                "height": f"{self.image_height:.8f}",
                "width": f"{self.image_width:.8f}",
                "version": "4.0",
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
            }
        )

        # white background
        SubElement(self.svg_elem, "rect",
                   {
                       "width": "100%",
                       "height": "100%",
                       "fill": "white",
                   })

    def draw_rect(self, rect, stroke_width=2.0, stroke_color=COLORS['black']):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        SubElement(
            self.svg_elem,
            "rect",
            {
                "x": f"{svg_rect.origin.x:.8f}",
                "y": f"{svg_rect.origin.y:.8f}",
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "style": "fill:rgb(255,255,255);stroke-width:{:.8f};"
                "stroke:{};opacity:1;fill-opacity:0;".format(
                    stroke_width,
                    stroke_color.svg_color()
                )
            }
        )

    def draw_labeled_rect(self, rect, stroke_width=2.0,
                          stroke_color=COLORS['black'],
                          fill_color=COLORS['white'],
                          label='',
                          label_size=10.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        g_elem = SubElement(self.svg_elem, "g",
                            {
                                "transform": "translate({:.8f},{:.8f})".format(
                                    svg_rect.origin.x,
                                    svg_rect.origin.y)
                            })
        SubElement(
            g_elem,
            "rect",
            {
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "style": "fill:{};stroke-width:{:.8f};"
                "stroke:{};opacity:1;".format(
                    fill_color.svg_color(),
                    stroke_width,
                    stroke_color.svg_color()
                )
            }
        )
        sub_svg_elem = SubElement(g_elem, "svg",
                                  {
                                      "width": f"{svg_rect.width:.8f}",
                                      "height": f"{svg_rect.height:.8f}"
                                  })
        text_elem = SubElement(sub_svg_elem, "text",
                               {
                                   "x": "50%",
                                   "y": "50%",
                                   "font-size": f"{label_size:.8f}",
                                   "font-family": self.font_family,
                                   "style":
                                       "stroke:{};stroke-width:{:.8f};"
                                       "fill:{};opacity:{:.8f};".format(
                                           COLORS['black'].svg_color(),
                                           stroke_width / 4.0,
                                           COLORS['black'].svg_color(),
                                           COLORS['black'].a),
                                   "alignment-baseline": "middle",
                                   "text-anchor": "middle"})
        text_elem.text = label

    def draw_dashed_rect(
        self,
        rect,
        stroke_width=2.0,
        stroke_color=COLORS['black'],
        fill_color=COLORS['white']
    ):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        SubElement(
            self.svg_elem,
            "rect",
            {
                "x": f"{svg_rect.origin.x:.8f}",
                "y": f"{svg_rect.origin.y:.8f}",
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "stroke-dasharray": "5",
                "style": "fill:{};stroke-width:{:.8f};stroke:{};"
                "opacity:1;fill-opacity:{:.8f}".format(
                    fill_color.svg_color(),
                    stroke_width,
                    stroke_color.svg_color(),
                    fill_color.a
                )
            }
        )

    def draw_labeled_dashed_rect_with_border(self, rect, stroke_width=2.0,
                                             fill_color=COLORS['white'],
                                             border_color=COLORS['black'],
                                             label='',
                                             label_size=10.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        g_elem = SubElement(self.svg_elem, "g",
                            {
                                "transform": "translate({:.8f},{:.8f})".format(
                                    svg_rect.origin.x, svg_rect.origin.y)
                            })
        SubElement(
            g_elem,
            "rect",
            {
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "stroke-dasharray": "5",
                "style": "fill:{};stroke-width:{:.8f};"
                "stroke:{};opacity:{:.8f};".format(
                    fill_color.svg_color(),
                    stroke_width,
                    border_color.svg_color(),
                    fill_color.a
                )
            }
        )
        sub_svg_elem = SubElement(g_elem, "svg",
                                  {
                                      "width": f"{svg_rect.width:.8f}",
                                      "height": f"{svg_rect.height:.8f}"
                                  })
        text_elem = SubElement(
            sub_svg_elem,
            "text",
            {
                "x": "50%",
                "y": "50%",
                "font-size": f"{label_size:.8f}",
                "font-family": self.font_family,
                "style": "stroke:{};stroke-width:{:.8f};"
                "fill:{};opacity:{:.8f};".format(
                    COLORS['black'].svg_color(),
                    stroke_width / 4.0,
                    COLORS['black'].svg_color(),
                    COLORS['black'].a),
                "alignment-baseline": "middle",
                "text-anchor": "middle"
            }
        )
        text_elem.text = label

    def draw_solid_rect(self, rect, fill_color=COLORS['white']):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        SubElement(
            self.svg_elem,
            "rect",
            {
                "x": f"{svg_rect.origin.x:.8f}",
                "y": f"{svg_rect.origin.y:.8f}",
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "style": "fill:{};stroke-width:0;"
                "stroke:rgb(0,0,0);opacity:{:.8f};".format(
                    fill_color.svg_color(),
                    fill_color.a
                )
            }
        )

    def draw_solid_rect_with_border(self, rect, stroke_width=2.0,
                                    fill_color=COLORS['white'],
                                    border_color=COLORS['black']):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        SubElement(
            self.svg_elem,
            "rect",
            {
                "x": f"{svg_rect.origin.x:.8f}",
                "y": f"{svg_rect.origin.y:.8f}",
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "style": "fill:{};stroke-width:{:.8f};"
                "stroke:{};opacity:{:.8f};".format(
                    fill_color.svg_color(),
                    stroke_width,
                    border_color.svg_color(),
                    fill_color.a
                )
            }
        )

    def draw_labeled_solid_rect_with_border(self, rect, stroke_width=2.0,
                                            fill_color=COLORS['white'],
                                            border_color=COLORS['black'],
                                            label='',
                                            label_size=10.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        g_elem = SubElement(self.svg_elem, "g",
                            {
                                "transform": "translate({:.8f},{:.8f})".format(
                                    svg_rect.origin.x, svg_rect.origin.y)
                            })
        SubElement(
            g_elem,
            "rect",
            {
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}",
                "style": "fill:{};stroke-width:{:.8f};"
                "stroke:{};opacity:{:.8f};".format(
                    fill_color.svg_color(),
                    stroke_width,
                    border_color.svg_color(),
                    fill_color.a
                )
            }
        )
        sub_svg_elem = SubElement(
            g_elem,
            "svg",
            {
                "width": f"{svg_rect.width:.8f}",
                "height": f"{svg_rect.height:.8f}"
            }
        )
        text_elem = SubElement(
            sub_svg_elem,
            "text",
            {
                "x": "50%",
                "y": "50%",
                "font-size": f"{label_size:.8f}",
                "font-family": self.font_family,
                "style": "stroke:{};stroke-width:{:.8f};"
                "fill:{};opacity:{:.8f};".format(
                    COLORS['black'].svg_color(),
                    stroke_width / 4.0,
                    COLORS['black'].svg_color(),
                    COLORS['black'].a
                ),
                "alignment-baseline": "middle",
                "text-anchor": "middle"
            }
        )
        text_elem.text = label

    def draw_line(self, start_point, end_point, stroke_width,
                  stroke_color=COLORS['black'], is_dashed=False):
        point1 = convert_point_to_svg_coordinates(
            start_point,
            self.image_height
        )
        point2 = convert_point_to_svg_coordinates(end_point, self.image_height)
        style_str = "stroke-width:{:.8f};stroke:{}" \
                    ";opacity:{:.8f};" \
                    "stroke-linecap:butt;".format(stroke_width,
                                                  stroke_color.svg_color(),
                                                  stroke_color.a)
        if is_dashed:
            style_str = style_str + "stroke-dasharray:4 1"
        SubElement(self.svg_elem, "line",
                   {
                       "x1": f"{point1.x:.8f}",
                       "y1": f"{point1.y:.8f}",
                       "x2": f"{point2.x:.8f}",
                       "y2": f"{point2.y:.8f}",
                       "style": style_str
                   })

    def draw_arrow(self, start_point, end_point, stroke_width,
                   stroke_color=COLORS['black']):
        point1 = convert_point_to_svg_coordinates(
            start_point,
            self.image_height
        )
        point2 = convert_point_to_svg_coordinates(end_point, self.image_height)
        direction = Point(point2.x - point1.x, point2.y - point1.y)
        direction_magnitude = math.sqrt(direction.x * direction.x +
                                        direction.y * direction.y)
        inv_magnitude = 1.0 / direction_magnitude
        arrowhead_length = 9.0
        arrowhead_half_width = arrowhead_length * 0.5
        direction = Point(
            direction.x * inv_magnitude,
            direction.y * inv_magnitude
        )
        point2 = Point(point2.x - arrowhead_length * direction.x,
                       point2.y - arrowhead_length * direction.y)
        triangle_tip = Point(point2.x + arrowhead_length * direction.x,
                             point2.y + arrowhead_length * direction.y)
        perpendicular_dir = Point(-direction.y, direction.x)
        triangle_pt_1 = Point(
            point2.x + arrowhead_half_width * perpendicular_dir.x,
            point2.y + arrowhead_half_width * perpendicular_dir.y
        )
        triangle_pt_2 = Point(
            point2.x - arrowhead_half_width * perpendicular_dir.x,
            point2.y - arrowhead_half_width * perpendicular_dir.y
        )
        SubElement(
            self.svg_elem,
            "line",
            {
                "x1": f"{point1.x:.8f}",
                "y1": f"{point1.y:.8f}",
                "x2": f"{point2.x:.8f}",
                "y2": f"{point2.y:.8f}",
                "style": "stroke-width:{:.8f};stroke:{};opacity:{:.8f};"
                "stroke-linecap:butt;".format(
                    stroke_width,
                    stroke_color.svg_color(),
                    stroke_color.a
                )
            }
        )
        SubElement(
            self.svg_elem,
            "polygon",
            {
                "points": " ".join(
                    p.svg_point_string()
                    for p in [
                        triangle_tip,
                        triangle_pt_1,
                        triangle_pt_2
                    ]
                ),
                "style": f"fill:{stroke_color.svg_color()};"
            }
        )

    def draw_text(self, text, location,
                  text_size, color=COLORS['black'], stroke_width=1.0):
        location_svg = convert_point_to_svg_coordinates(
            location,
            self.image_height
        )
        text_elem = SubElement(
            self.svg_elem,
            "text",
            {
                "x": f"{location_svg.x:.8f}",
                "y": f"{location_svg.y:.8f}",
                "font-size": f"{text_size:.8f}",
                "font-family": self.font_family,
                "style": "stroke:{};stroke-width:{:.8f};"
                "fill:{};opacity:{:.8f};".format(
                    color.svg_color(),
                    stroke_width / 4.0,
                    color.svg_color(),
                    color.a
                )
            }
        )
        text_elem.text = text

    def get_image(self):
        xmlstr = tostring(
            self.svg_elem,
            encoding='utf-8',
            method='xml'
        ).decode('utf8')

        return minidom.parseString(xmlstr).toprettyxml(indent='  ')


class ClipData:

    def __init__(self, src_start=0.0, src_end=0.0, avlbl_start=0.0,
                 avlbl_end=0.0, avlbl_duration=0.0,
                 trim_start=0.0, trim_duration=0.0, clip_id=0,
                 transition_begin=None, transition_end=None):
        self.src_start = src_start
        self.src_end = src_end
        self.avlbl_start = avlbl_start
        self.avlbl_end = avlbl_end
        self.avlbl_duration = avlbl_duration
        self.trim_start = trim_start
        self.trim_duration = trim_duration
        self.clip_id = clip_id
        self.transition_begin = transition_begin
        self.transition_end = transition_end


def draw_item(otio_obj, svg_writer, extra_data=()):
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
        return WRITE_TYPE_MAP[type(otio_obj)](otio_obj, svg_writer, extra_data)


# Draw Timeline and calculate Clip and Gap data
def _draw_timeline(timeline, svg_writer, extra_data=()):
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
            avlbl_start = (
                track_duration - item.trimmed_range().start_time.value
            )
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
                avlbl_end = (
                    item.available_range().start_time.value
                    + item.available_range().duration.value
                    - item.trimmed_range().start_time.value
                    - item.trimmed_range().duration.value
                    + track_duration - 1
                )
                clip_count += 1
                avlbl_duration = item.available_range().duration.value
                clip_data = ClipData(src_start, src_end, avlbl_start,
                                     avlbl_end, avlbl_duration, trim_start,
                                     trim_duration,
                                     clip_count - 1)
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
        svg_writer.global_max_time = max(svg_writer.global_max_time, max_time)
        svg_writer.global_min_time = min(svg_writer.global_min_time, min_time)
        svg_writer.all_clips_data.append(current_track_clips_data)
        svg_writer.tracks_duration.append(track_duration)
        svg_writer.track_transition_available.append(
            current_track_has_transition
        )
        if current_track_has_transition:
            transition_track_count += 1
        # store track-wise clip count to draw arrows from stack to tracks
        if len(svg_writer.trackwise_clip_count) == 0:
            svg_writer.trackwise_clip_count.append(clip_count)
        else:
            svg_writer.trackwise_clip_count.append(
                clip_count - svg_writer.trackwise_clip_count[
                    len(svg_writer.trackwise_clip_count) - 1])
    # The scale in x direction is calculated considering margins on the
    # left and right side if the image
    svg_writer.scale_x = (
        (svg_writer.image_width - (2.0 * svg_writer.image_margin))
        / (svg_writer.global_max_time - svg_writer.global_min_time + 1.0)
    )
    svg_writer.x_origin = ((-svg_writer.global_min_time) * svg_writer.scale_x +
                           svg_writer.image_margin)
    track_count = len(svg_writer.tracks_duration)
    # The rect height is calculated considering the following:
    # Total space available:
    #   image height - top & bottom margin -
    #   space for two labels for the bottom-most rect
    # Number of total rects to fit the height of the drawing space:
    #   track_count * 2.0 = one for track rect and one for the sequence of
    #                       components on that track
    #   + 2.0 = timeline and stack rects
    #   clip_count = we need to draw a rect for a media reference per clip
    #   transition_track_count = we need one more row per the number of tracks
    #                            with transitions
    # NumberOfRects * 2.0 - 1.0 = to account for "one rect space" between all
    #                             the rects
    total_image_margin_space = 2.0 * svg_writer.image_margin
    bottom_label_space = 2.0 * svg_writer.font_size
    svg_total_draw_space = (
        svg_writer.image_height
        - total_image_margin_space
        - bottom_label_space
    )
    track_sequence_rect_count = track_count * 2.0
    timeline_stack_rect_count = 2.0
    rect_count = (track_sequence_rect_count + timeline_stack_rect_count +
                  clip_count + transition_track_count)
    total_slots = rect_count * 2.0 - 1.0
    svg_writer.clip_rect_height = svg_total_draw_space / total_slots

    # Draw Timeline
    svg_writer.vertical_drawing_index += 2
    timeline_origin = Point(svg_writer.x_origin,
                            svg_writer.image_height - svg_writer.image_margin -
                            svg_writer.vertical_drawing_index *
                            svg_writer.clip_rect_height)
    svg_writer.max_total_duration = max(svg_writer.tracks_duration)
    label_text_size = 0.4 * svg_writer.clip_rect_height
    svg_writer.draw_labeled_solid_rect_with_border(
        Rect(
            timeline_origin,
            svg_writer.max_total_duration * svg_writer.scale_x,
            svg_writer.clip_rect_height
        ),
        label="Timeline",
        label_size=label_text_size
    )
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(1, int(svg_writer.max_total_duration)):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x),
                         timeline_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(
            start_point=start_pt,
            end_point=end_pt,
            stroke_width=1.0,
            stroke_color=COLORS['black']
        )
    # Draw arrow from timeline to stack
    timeline_width = svg_writer.max_total_duration * svg_writer.scale_x
    arrow_start = Point(svg_writer.x_origin + timeline_width * 0.5,
                        timeline_origin.y - svg_writer.arrow_margin)
    arrow_end = Point(svg_writer.x_origin + timeline_width * 0.5,
                      timeline_origin.y - svg_writer.clip_rect_height +
                      svg_writer.arrow_margin)
    svg_writer.draw_arrow(start_point=arrow_start, end_point=arrow_end,
                          stroke_width=2.0, stroke_color=COLORS['black'])
    arrow_label_location = Point(arrow_start.x + svg_writer.arrow_label_margin,
                                 (arrow_start.y + arrow_end.y) * 0.5)
    svg_writer.draw_text('tracks', arrow_label_location, svg_writer.font_size)
    # Draw global_start_time info
    if timeline.global_start_time is None:
        start_time_text = r'global_start_time: {}'.format('None')
    else:
        start_time_text = r'global_start_time: {}'.format(
            repr(float(round(timeline.global_start_time.value, 1))))
    start_time_location = Point(timeline_origin.x + svg_writer.font_size,
                                timeline_origin.y - svg_writer.font_size)
    svg_writer.draw_text(
        start_time_text,
        start_time_location,
        svg_writer.font_size
    )

    # Draw stack
    draw_item(timeline.tracks, svg_writer,
              (svg_writer.x_origin, svg_writer.max_total_duration))


# Draw stack
def _draw_stack(stack, svg_writer, extra_data=()):
    stack_x_origin = extra_data[0]
    stack_duration = extra_data[1]
    svg_writer.vertical_drawing_index += 2
    stack_origin = Point(stack_x_origin,
                         svg_writer.image_height - svg_writer.image_margin -
                         svg_writer.vertical_drawing_index *
                         svg_writer.clip_rect_height)
    stack_text_size = 0.4 * svg_writer.clip_rect_height
    svg_writer.draw_labeled_solid_rect_with_border(
        Rect(stack_origin, stack_duration * svg_writer.scale_x,
             svg_writer.clip_rect_height),
        label="Stack", fill_color=COLORS['dark_gray_transluscent'],
        label_size=stack_text_size)
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(1, int(svg_writer.max_total_duration)):
        start_pt = Point(
            svg_writer.x_origin + (i * svg_writer.scale_x),
            stack_origin.y
        )
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(
            start_point=start_pt,
            end_point=end_pt,
            stroke_width=1.0,
            stroke_color=COLORS['black']
        )
    for i in range(0, len(svg_writer.tracks_duration)):
        draw_item(
            stack[i],
            svg_writer,
            (
                stack_x_origin,
                svg_writer.tracks_duration[i],
                svg_writer.all_clips_data[i],
                svg_writer.track_transition_available[i]
            )
        )
    # Draw arrows from stack to tracks
    #   arrow from stack to first track
    stack_width = stack_duration * svg_writer.scale_x
    arrow_start = Point(svg_writer.x_origin + stack_width * 0.5,
                        stack_origin.y - svg_writer.arrow_margin)
    arrow_end = Point(svg_writer.x_origin + stack_width * 0.5,
                      stack_origin.y - svg_writer.clip_rect_height +
                      svg_writer.arrow_margin)
    svg_writer.draw_arrow(start_point=arrow_start, end_point=arrow_end,
                          stroke_width=2.0,
                          stroke_color=COLORS['black'])
    end_arrow_offset = 1
    #   arrows from stack to rest of the tracks
    for i in range(1, len(svg_writer.trackwise_clip_count)):
        arrow_x_increment_per_track = 10.0
        end_arrow_offset += (
            svg_writer.trackwise_clip_count[i - 1] * 2.0 + 4.0
        )
        arrow_start = Point(
            (
                (i * arrow_x_increment_per_track)
                + svg_writer.x_origin
                + stack_width * 0.5
            ),
            stack_origin.y - svg_writer.arrow_margin
        )
        arrow_end = Point(
            (
                (i * arrow_x_increment_per_track)
                + svg_writer.x_origin
                + stack_width * 0.5
            ),
            stack_origin.y - (end_arrow_offset * svg_writer.clip_rect_height) +
            svg_writer.arrow_margin
        )
        svg_writer.draw_arrow(
            start_point=arrow_start,
            end_point=arrow_end,
            stroke_width=2.0,
            stroke_color=COLORS['black']
        )
    arrow_label_text = fr'children[{len(svg_writer.trackwise_clip_count)}]'
    arrow_label_location = Point(
        arrow_start.x + svg_writer.arrow_label_margin,
        stack_origin.y - svg_writer.clip_rect_height * 0.5
    )
    svg_writer.draw_text(
        arrow_label_text,
        arrow_label_location,
        svg_writer.font_size
    )
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
    trimmed_range_location = Point(
        stack_origin.x + svg_writer.font_size,
        stack_origin.y + svg_writer.clip_rect_height + svg_writer.text_margin
    )
    source_range_location = Point(stack_origin.x + svg_writer.font_size,
                                  stack_origin.y - svg_writer.font_size)
    svg_writer.draw_text(trimmed_range_text, trimmed_range_location,
                         svg_writer.font_size,
                         )
    svg_writer.draw_text(
        source_range_text,
        source_range_location,
        svg_writer.font_size
    )


def _draw_track(track, svg_writer, extra_data=()):
    svg_writer.vertical_drawing_index += 2
    track_x_origin = extra_data[0]
    track_duration = extra_data[1]
    clips_data = extra_data[2]
    track_has_transition = extra_data[3]
    track_origin = Point(track_x_origin,
                         svg_writer.image_height - svg_writer.image_margin -
                         svg_writer.vertical_drawing_index *
                         svg_writer.clip_rect_height)
    track_text_size = 0.4 * svg_writer.clip_rect_height
    track_text = track.name if track.name else 'Track'
    svg_writer.draw_labeled_solid_rect_with_border(
        Rect(track_origin, track_duration * svg_writer.scale_x,
             svg_writer.clip_rect_height),
        label=track_text, fill_color=COLORS['dark_gray_transluscent'],
        label_size=track_text_size)
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(1, int(track_duration)):
        start_pt = Point(
            svg_writer.x_origin + (i * svg_writer.scale_x),
            track_origin.y
        )
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(
            start_point=start_pt,
            end_point=end_pt,
            stroke_width=1.0,
            stroke_color=COLORS['black']
        )
    item_count = 0
    clip_count = 0
    transition_count = 0
    svg_writer.vertical_drawing_index += 2
    if track_has_transition:
        svg_writer.vertical_drawing_index += 2
    for item in track:
        if isinstance(item, otio.schema.Clip):
            clip_count += 1
            draw_item(item, svg_writer, (clips_data[item_count], clip_count))
            item_count += 1
        elif isinstance(item, otio.schema.Gap):
            draw_item(item, svg_writer, (clips_data[item_count],))
            item_count += 1
        elif isinstance(item, otio.schema.Transition):
            cut_x = svg_writer.x_origin + (clips_data[clip_count].src_start *
                                           svg_writer.scale_x)
            draw_item(item, svg_writer, (cut_x,))
            transition_count += 1
    svg_writer.vertical_drawing_index += (2 * clip_count)
    # Draw arrow from track to clips
    track_width = track_duration * svg_writer.scale_x
    arrow_start = Point(svg_writer.x_origin + track_width * 0.5,
                        track_origin.y - svg_writer.arrow_margin)
    arrow_end = Point(svg_writer.x_origin + track_width * 0.5,
                      track_origin.y - svg_writer.clip_rect_height +
                      svg_writer.arrow_margin)
    svg_writer.draw_arrow(start_point=arrow_start, end_point=arrow_end,
                          stroke_width=2.0,
                          stroke_color=COLORS['black'])
    arrow_label_text = fr'children[{item_count + transition_count}]'
    arrow_label_location = Point(
        arrow_start.x + svg_writer.arrow_label_margin,
        track_origin.y - svg_writer.clip_rect_height * 0.5
    )
    svg_writer.draw_text(
        arrow_label_text,
        arrow_label_location,
        svg_writer.font_size
    )
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
    trimmed_range_location = Point(
        track_origin.x + svg_writer.font_size,
        track_origin.y + svg_writer.clip_rect_height + svg_writer.text_margin
    )
    source_range_location = Point(track_origin.x + svg_writer.font_size,
                                  track_origin.y - svg_writer.font_size)
    svg_writer.draw_text(trimmed_range_text, trimmed_range_location,
                         svg_writer.font_size,
                         )
    svg_writer.draw_text(
        source_range_text,
        source_range_location,
        svg_writer.font_size
    )


def _draw_clip(clip, svg_writer, extra_data=()):
    clip_data = extra_data[0]
    clip_count = extra_data[1]
    clip_color = Color.random_color()
    clip_origin = Point(
        svg_writer.x_origin + (clip_data.src_start * svg_writer.scale_x),
        svg_writer.image_height - svg_writer.image_margin -
        svg_writer.vertical_drawing_index * svg_writer.clip_rect_height)
    clip_rect = Rect(clip_origin, clip_data.trim_duration * svg_writer.scale_x,
                     svg_writer.clip_rect_height)
    clip_text_size = 0.4 * svg_writer.clip_rect_height
    clip_text = fr'Clip-{clip_data.clip_id}' if len(
        clip.name) == 0 else clip.name
    svg_writer.draw_labeled_solid_rect_with_border(
        clip_rect,
        label=clip_text, fill_color=clip_color,
        label_size=clip_text_size)
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(int(clip_data.src_start), int(clip_data.src_end) + 1):
        start_pt = Point(
            svg_writer.x_origin + (i * svg_writer.scale_x), clip_origin.y
        )
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(
            start_point=start_pt,
            end_point=end_pt,
            stroke_width=1.0,
            stroke_color=COLORS['black']
        )
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
    trimmed_range_location = Point(clip_origin.x + svg_writer.font_size,
                                   clip_origin.y + svg_writer.clip_rect_height +
                                   svg_writer.text_margin)
    source_range_location = Point(clip_origin.x + svg_writer.font_size,
                                  clip_origin.y - svg_writer.font_size)
    svg_writer.draw_text(trimmed_range_text, trimmed_range_location,
                         svg_writer.font_size,
                         )
    svg_writer.draw_text(source_range_text, source_range_location, svg_writer.font_size)

    # Draw media reference
    trim_media_origin = Point(
        svg_writer.x_origin + (clip_data.src_start * svg_writer.scale_x),
        svg_writer.image_height - svg_writer.image_margin -
        (svg_writer.vertical_drawing_index + clip_count * 2) *
        svg_writer.clip_rect_height)
    media_origin = Point(
        svg_writer.x_origin + (clip_data.avlbl_start * svg_writer.scale_x),
        svg_writer.image_height - svg_writer.image_margin -
        (svg_writer.vertical_drawing_index + clip_count * 2) *
        svg_writer.clip_rect_height)
    svg_writer.draw_rect(
        Rect(media_origin, clip_data.avlbl_duration * svg_writer.scale_x,
             svg_writer.clip_rect_height))
    media_text_size = 0.4 * svg_writer.clip_rect_height
    media_text = fr'Media-{clip_data.clip_id}' if len(
        clip.media_reference.name) == 0 else clip.media_reference.name
    svg_writer.draw_labeled_solid_rect_with_border(
        Rect(trim_media_origin, clip_data.trim_duration * svg_writer.scale_x,
             svg_writer.clip_rect_height),
        label=media_text, fill_color=clip_color,
        label_size=media_text_size)
    for i in range(int(clip_data.avlbl_start),
                   int(clip_data.avlbl_end) + 1):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), media_origin.y)
        if start_pt.x < media_origin.x:
            continue
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                             stroke_color=COLORS['black'])
    # Draw media_reference info
    if clip.available_range() is None:
        available_range_text = r'available_range: {}'.format('None')
    else:
        available_range_text = r'available_range: {}, {}'.format(
            repr(float(round(clip.available_range().start_time.value, 1))),
            repr(float(round(clip.available_range().duration.value, 1))))
    available_range_location = Point(media_origin.x + svg_writer.font_size,
                                     media_origin.y - svg_writer.font_size)
    svg_writer.draw_text(available_range_text, available_range_location,
                         svg_writer.font_size,
                         )
    if hasattr(clip.media_reference, 'target_url'):
        if clip.media_reference.target_url is None:
            target_url_text = r'target_url: {}'.format('Media Unavailable')
        else:
            target_url_text = fr'target_url: {clip.media_reference.target_url}'
        target_url_location = Point(media_origin.x + svg_writer.font_size,
                                    media_origin.y - 2.0 * svg_writer.font_size)
        svg_writer.draw_text(target_url_text, target_url_location, svg_writer.font_size)
    # Draw arrow from clip to media reference
    clip_media_height_difference = (((clip_count - 1) * 2.0 + 1) *
                                    svg_writer.clip_rect_height)
    media_arrow_start = Point(
        clip_origin.x + (clip_data.trim_duration * svg_writer.scale_x) * 0.5,
        clip_origin.y - svg_writer.arrow_margin)
    media_arrow_end = Point(
        clip_origin.x + (clip_data.trim_duration * svg_writer.scale_x) * 0.5,
        clip_origin.y - clip_media_height_difference + svg_writer.arrow_margin)
    svg_writer.draw_arrow(start_point=media_arrow_start, end_point=media_arrow_end,
                          stroke_width=2.0, stroke_color=COLORS['black'])
    arrow_label_text = r'media_reference'
    arrow_label_location = Point(media_arrow_start.x + svg_writer.arrow_label_margin,
                                 media_arrow_start.y -
                                 svg_writer.clip_rect_height * 0.5)
    svg_writer.draw_text(arrow_label_text, arrow_label_location, svg_writer.font_size)
    # Draw media transition sections
    if clip_data.transition_end is not None:
        cut_x = clip_origin.x + clip_rect.width
        section_start_pt = Point(cut_x, media_origin.y)
        # Handle the case of transition ending at cut
        if clip_data.transition_end.out_offset.value == 0.0:
            media_transition_rect = Rect(section_start_pt,
                                         -clip_data.transition_end.in_offset.value *
                                         svg_writer.scale_x,
                                         svg_writer.clip_rect_height)
            marker_x = [clip_data.src_end,
                        clip_data.src_end - clip_data.transition_end.in_offset.value]
        else:
            media_transition_rect = Rect(section_start_pt,
                                         clip_data.transition_end.out_offset.value *
                                         svg_writer.scale_x,
                                         svg_writer.clip_rect_height)
            marker_x = [clip_data.src_end,
                        clip_data.src_end + clip_data.transition_end.out_offset.value]
        section_color = Color(clip_color[0], clip_color[1], clip_color[2], 0.5)
        svg_writer.draw_dashed_rect(media_transition_rect, fill_color=section_color)
        marker_x.sort()
        # Draw markers for transition sections
        for i in range(int(marker_x[0]),
                       int(marker_x[1]) + 1):
            start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x),
                             media_origin.y)
            if start_pt.x < media_transition_rect.min_x():
                continue
            end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
            svg_writer.draw_line(start_point=start_pt, end_point=end_pt,
                                 stroke_width=1.0,
                                 stroke_color=COLORS['black'])
    if clip_data.transition_begin is not None:
        cut_x = clip_origin.x
        section_start_pt = Point(cut_x, media_origin.y)
        # Handle the case of transition starting at cut
        if clip_data.transition_begin.in_offset.value == 0.0:
            media_transition_rect = Rect(section_start_pt,
                                         clip_data.transition_begin.out_offset.value *
                                         svg_writer.scale_x,
                                         svg_writer.clip_rect_height)
            marker_x = [clip_data.src_start,
                        clip_data.src_start +
                        clip_data.transition_begin.out_offset.value]
        else:
            media_transition_rect = Rect(section_start_pt,
                                         -clip_data.transition_begin.in_offset.value *
                                         svg_writer.scale_x,
                                         svg_writer.clip_rect_height)
            marker_x = [clip_data.src_start,
                        clip_data.src_start -
                        clip_data.transition_begin.out_offset.value]
        section_color = Color(clip_color[0], clip_color[1], clip_color[2], 0.5)
        svg_writer.draw_dashed_rect(media_transition_rect, fill_color=section_color)
        marker_x.sort()
        # Draw markers for transition sections
        for i in range(int(marker_x[0]),
                       int(marker_x[1]) + 1):
            start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x),
                             media_origin.y)
            if start_pt.x < media_transition_rect.min_x():
                continue
            end_pt = Point(start_pt.x, start_pt.y + 0.15 * svg_writer.clip_rect_height)
            svg_writer.draw_line(start_point=start_pt, end_point=end_pt,
                                 stroke_width=1.0,
                                 stroke_color=COLORS['black'])


def _draw_gap(gap, svg_writer, extra_data=()):
    gap_data = extra_data[0]
    gap_origin = Point(svg_writer.x_origin + (gap_data.src_start * svg_writer.scale_x),
                       svg_writer.image_height - svg_writer.image_margin -
                       svg_writer.vertical_drawing_index * svg_writer.clip_rect_height)
    gap_text_size = 0.4 * svg_writer.clip_rect_height
    gap_text = 'Gap'
    svg_writer.draw_labeled_dashed_rect_with_border(
        Rect(gap_origin, gap_data.trim_duration * svg_writer.scale_x,
             svg_writer.clip_rect_height),
        label=gap_text, label_size=gap_text_size)
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(int(gap_data.src_start), int(gap_data.src_end) + 1):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), gap_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
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
    trimmed_range_location = Point(gap_origin.x + svg_writer.font_size,
                                   gap_origin.y + svg_writer.clip_rect_height +
                                   svg_writer.text_margin)
    source_range_location = Point(gap_origin.x + svg_writer.font_size,
                                  gap_origin.y - svg_writer.font_size)
    svg_writer.draw_text(trimmed_range_text, trimmed_range_location,
                         svg_writer.font_size,
                         )
    svg_writer.draw_text(source_range_text, source_range_location, svg_writer.font_size)


def _draw_transition(transition, svg_writer, extra_data=()):
    cut_x = extra_data[0]
    transition_origin = Point(cut_x - (transition.in_offset.value * svg_writer.scale_x),
                              svg_writer.image_height - svg_writer.image_margin -
                              (svg_writer.vertical_drawing_index - 2) *
                              svg_writer.clip_rect_height)
    transition_rect = Rect(transition_origin,
                           (transition.in_offset.value + transition.out_offset.value) *
                           svg_writer.scale_x,
                           svg_writer.clip_rect_height)
    transition_name = 'Transition' if len(
        transition.name) == 0 else transition.name
    transition_name_size = 0.4 * svg_writer.clip_rect_height
    svg_writer.draw_labeled_rect(transition_rect, label=transition_name,
                                 label_size=transition_name_size)
    line_end = Point(transition_origin.x + transition_rect.width,
                     transition_origin.y + transition_rect.height)
    svg_writer.draw_line(transition_origin, line_end, stroke_width=1.0,
                         stroke_color=COLORS['black'])
    in_offset_location = Point(transition_origin.x + svg_writer.font_size,
                               transition_origin.y - svg_writer.font_size)
    out_offset_location = Point(transition_origin.x + svg_writer.font_size,
                                transition_origin.y - 2.0 * svg_writer.font_size)
    in_offset_text = r'in_offset: ' \
                     r'{}'.format(repr(float(round(transition.in_offset.value, 1))))
    out_offset_text = r'out_offset: ' \
                      r'{}'.format(repr(float(round(transition.out_offset.value, 1))))
    svg_writer.draw_text(in_offset_text, in_offset_location, svg_writer.font_size)
    svg_writer.draw_text(out_offset_text, out_offset_location, svg_writer.font_size)
    cut_location = Point(cut_x, transition_origin.y)
    cut_line_end = Point(cut_x,
                         svg_writer.image_height - svg_writer.image_margin -
                         svg_writer.vertical_drawing_index *
                         svg_writer.clip_rect_height)
    svg_writer.draw_line(cut_location, cut_line_end, stroke_width=1.0,
                         stroke_color=COLORS['black'])


def _draw_collection(collection, svg_writer, extra_data=()):
    pass


def convert_otio_to_svg(timeline, width, height):
    global random_colors_used

    svg_writer = SVGWriter(image_width=width, image_height=height,
                           font_family='sans-serif', image_margin=20.0, font_size=15.0,
                           arrow_label_margin=5.0)
    random_colors_used = []
    random.seed(100)
    draw_item(timeline, svg_writer, ())

    return svg_writer.get_image()


# --------------------
# adapter requirements
# --------------------

def write_to_string(input_otio, width=2406.0, height=1054.0):
    return convert_otio_to_svg(input_otio, width=width, height=height)
