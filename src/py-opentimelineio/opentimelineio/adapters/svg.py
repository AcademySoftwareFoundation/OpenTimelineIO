# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OTIO to SVG Adapter
   Points in calculations are y-up.
   Points in SVG are y-down."""

# python
import math
from random import seed, random
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# otio
import opentimelineio as otio

AVAILABLE_RANGE_LABEL = "available_range: {}"
CHILDREN_LABEL = "children[{}]"
CLIP_LABEL = "Clip-{}"
GLOBAL_START_TIME_LABEL = "global_start_time: {}"
IN_OFFSET_LABEL = "in_offset: {}"
MEDIA_REFERENCE_LABEL = "media_reference"
OUT_OFFSET_LABEL = "out_offset: {}"
SOURCE_RANGE_LABEL = "source_range: {}"
TARGET_URL_LABEL = "target_url: {}"
TRIMMED_RANGE_LABEL = "trimmed_range() -> {}"
UNKNOWN_LABEL = "UNKNOWN"

RANDOM_COLORS_USED = []


class Color:
    """
    Object to represent RGBA Color values.
    """
    def __init__(self, r=0.0, g=0.0, b=0.0, a=255.0):
        self.value = (r, g, b, a)

    def __getitem__(self, item):
        return self.value[item]

    @staticmethod
    def random_color():
        """
        Generate a random color.
        :rtype: Color
        """
        color = Color.__generate_new_color()
        RANDOM_COLORS_USED.append(color)
        return color

    @staticmethod
    def __generate_new_color():
        max_distance = None
        best_color = None
        for _ in range(100):
            color = Color.__get_random_color()
            if len(RANDOM_COLORS_USED) == 0:
                return color
            best_distance = min([Color.__color_distance(color, c)
                                 for c in RANDOM_COLORS_USED])
            if not max_distance or best_distance > max_distance:
                max_distance = best_distance
                best_color = color
        return best_color

    @staticmethod
    def __get_random_color():
        return Color(random(), random(), random(), 1.0)

    @staticmethod
    def __color_distance(c1, c2):
        return sum([abs(x[0] - x[1]) for x in zip(c1.value, c2.value)])

    @property
    def r(self):
        """ Value for the Red Channel """
        return self.value[0]

    @property
    def g(self):
        """ Value for the Green Channel """
        return self.value[1]

    @property
    def b(self):
        """ Value for the Blue Channel """
        return self.value[2]

    @property
    def a(self):
        """ Value for the Alpha Channel """
        return self.value[3]

    def to_svg(self):
        """ Convert RGB values """
        return 'rgb({:.8f},{:.8f},{:.8f})'.format(self.r * 255.0,
                                                  self.g * 255.0,
                                                  self.b * 255.0)


COLORS = {
    'transparent': Color(0, 0, 0, 0),
    'black': Color(0.0, 0.0, 0.0, 1.0),
    'white': Color(1.0, 1.0, 1.0, 1.0),
    'translucent_white': Color(1.0, 1.0, 1.0, 0.7),
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
    'dark_gray_translucent': Color(0.66, 0.66, 0.66, 0.7843)
}


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def svg_point_string(self):
        return "{:.8f},{:.8f}".format(self.x, self.y)


class Rect(object):
    origin = Point(0, 0)
    width = 0.0
    height = 0.0

    def __init__(self, origin=Point(0, 0), width=0.0, height=0.0):
        self.origin = origin
        self.width = width
        self.height = height

    def normalized(self):
        width = self.width if self.width < 0 else 0
        height = self.height if self.height < 0 else 0
        normalized_origin = Point(self.origin.x + width,
                                  self.origin.y + height)
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
    return Point(point.x, image_height - point.y)


def convert_rect_to_svg_coordinates(rect, image_height):
    """Convert to SVG coordinate system (0,0 at top-left)"""
    normalized_rect = rect.normalized()
    normalized_rect.origin = convert_point_to_svg_coordinates(normalized_rect.origin,
                                                              image_height)
    normalized_rect.height *= -1
    return normalized_rect.normalized()


class SVGWriter:

    def __init__(self,
                 image_width=2406.0,
                 image_height=1054.0,
                 image_margin=20.0,
                 arrow_margin=10.0,
                 arrow_label_margin=5.0,
                 font_size=15.0,
                 font_family='sans-serif'):
        """
        Writes an SVG based

        :param float arrow_label_margin: Margin around arrow's label
        :param float arrow_margin: Margin around arrow
        :param str font_family: Family of font
        :param float font_size: Size of font
        :param float image_margin: Margin around image
        :param float image_height: Height of the image to write
        :param float image_width: Width of the image to write
        """
        self.arrow_label_margin = arrow_label_margin
        self.arrow_margin = arrow_margin
        self.font_family = font_family
        self.font_size = font_size
        self.image_height = image_height
        self.image_margin = image_margin
        self.image_width = image_width
        self.text_margin = 0.5 * font_size

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

        elem_attrs = {"height": self.image_height,
                      "width": self.image_width,
                      "version": "4.0",
                      "xmlns": "http://www.w3.org/2000/svg",
                      "xmlns:xlink": "http://www.w3.org/1999/xlink"}
        self.svg_elem = Element("svg", _map_to_element_attrs(elem_attrs))

        # white background
        white_bg_attrs = {"fill": "white", "height": "100%", "width": "100%"}
        SubElement(self.svg_elem, "rect", _map_to_element_attrs(white_bg_attrs))

    def draw_rect(self, rect, stroke_width=2.0, stroke_color=COLORS['black']):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        attrs = {"x": svg_rect.origin.x,
                 "y": svg_rect.origin.y,
                 "width": svg_rect.width,
                 "height": svg_rect.height,
                 "style": {"fill": COLORS['white'],
                           "stroke-width": stroke_width,
                           "stroke": stroke_color,
                           "opacity": "1",
                           "fill-opacity": "0"}}
        SubElement(self.svg_elem, "rect", _map_to_element_attrs(attrs))

    def draw_labeled_rect(self, rect, stroke_width=2.0,
                          stroke_color=COLORS['black'],
                          fill_color=COLORS['white'],
                          label='',
                          label_size=10.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        svg_xform_attrs = _transform_elem_attrs_from_rect(svg_rect)
        g_elem = SubElement(self.svg_elem, "g", svg_xform_attrs)

        elem_attrs = {"width": svg_rect.width,
                      "height": svg_rect.height,
                      "style": {"fill": fill_color,
                                "stroke-width": stroke_width,
                                "stroke": stroke_color,
                                "opacity": "1"}}
        SubElement(g_elem, "rect", _map_to_element_attrs(elem_attrs))

        sub_elem_attrs = {"width": svg_rect.width, "height": svg_rect.height}
        sub_svg_elem = SubElement(g_elem, "svg", _map_to_element_attrs(sub_elem_attrs))

        text_attrs = {"alignment-baseline": "middle",
                      "font-family": self.font_family,
                      "font-size": label_size,
                      "text-anchor": "middle",
                      "x": "50%",
                      "y": "50%",
                      "style": {"stroke": COLORS['black'],
                                "stroke-width": stroke_width / 4.0,
                                "fill": COLORS['black'],
                                "opacity": COLORS['black'].a}}
        text_elem = SubElement(sub_svg_elem, "text", text_attrs)
        text_elem.text = label

    def draw_dashed_rect(self,
                         rect,
                         stroke_width=2.0,
                         stroke_color=COLORS['black'],
                         fill_color=COLORS['white']):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)

        attrs = {"x": svg_rect.origin.x,
                 "y": svg_rect.origin.y,
                 "width": svg_rect.width,
                 "height": svg_rect.height,
                 "stroke-dasharray": "5",
                 "style": {"fill": fill_color,
                           "stroke-width": stroke_width,
                           "stroke": stroke_color,
                           "opacity": "1",
                           "fill-opacity": fill_color.a}}
        SubElement(self.svg_elem, "rect", attrs)

    def draw_labeled_dashed_rect_with_border(self,
                                             rect,
                                             stroke_width=2.0,
                                             fill_color=COLORS['white'],
                                             border_color=COLORS['black'],
                                             label='',
                                             label_size=10.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        svg_xform_attrs = _transform_elem_attrs_from_rect(svg_rect)
        g_elem = SubElement(self.svg_elem, "g", svg_xform_attrs)

        elem_attrs = {"width": svg_rect.width,
                      "height": svg_rect.height,
                      "style": {"fill": fill_color,
                                "opacity": fill_color.a,
                                "stroke": border_color,
                                "stroke-width": stroke_width}}
        SubElement(g_elem, "rect", _map_to_element_attrs(elem_attrs))

        sub_elem_attrs = {"width": svg_rect.width, "height": svg_rect.height}
        sub_svg_elem = SubElement(g_elem, "svg", _map_to_element_attrs(sub_elem_attrs))

        text_elem_attrs = {"alignment-baseline": "middle",
                           "font-family": self.font_family,
                           "font-size": label_size,
                           "text-anchor": "middle",
                           "x": "50%",
                           "y": "50%",
                           "style": {"fill": COLORS['black'],
                                     "opacity": COLORS['black'].a,
                                     "stroke": COLORS['black'],
                                     "stroke-width": stroke_width / 4.0}}
        text_elem = SubElement(sub_svg_elem,
                               "text",
                               _map_to_element_attrs(text_elem_attrs))
        text_elem.text = label

    def draw_solid_rect(self, rect, fill_color=COLORS["white"]):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)

        solid_attrs = {"height": svg_rect.height,
                       "width": svg_rect.width,
                       "x": svg_rect.origin.x,
                       "y": svg_rect.origin.y,
                       "style": {"fill": fill_color,
                                 "opacity": fill_color.a,
                                 "stroke": COLORS['black'],
                                 "stroke-width": "0"}}
        SubElement(self.svg_elem, "rect", _map_to_element_attrs(solid_attrs))

    def draw_solid_rect_with_border(self,
                                    rect,
                                    border_color=COLORS['black'],
                                    fill_color=COLORS['white'],
                                    stroke_width=2.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        attrs = {"height": svg_rect.height,
                 "width": svg_rect.width,
                 "x": svg_rect.origin.x,
                 "y": svg_rect.origin.y,
                 "style": {"fill": fill_color,
                           "opacity": fill_color.a,
                           "stroke": border_color,
                           "stroke-width": stroke_width}}
        SubElement(self.svg_elem, "rect", _map_to_element_attrs(attrs))

    def draw_labeled_solid_rect_with_border(self,
                                            rect,
                                            border_color=COLORS['black'],
                                            fill_color=COLORS['white'],
                                            label='',
                                            label_size=10.0,
                                            stroke_width=2.0):
        svg_rect = convert_rect_to_svg_coordinates(rect, self.image_height)
        svg_xform_attrs = _transform_elem_attrs_from_rect(svg_rect)
        g_elem = SubElement(self.svg_elem, "g", svg_xform_attrs)

        rect_attrs = {"height": svg_rect.height,
                      "width": svg_rect.width,
                      "style": {"fill": fill_color,
                                "opacity": fill_color.a,
                                "stroke": border_color,
                                "stroke-width": stroke_width}}
        SubElement(g_elem, "rect", _map_to_element_attrs(rect_attrs))

        sub_svg_elem = {"width": svg_rect.width, "height": svg_rect.height}
        sub_svg_elem = SubElement(g_elem, "svg", _map_to_element_attrs(sub_svg_elem))

        text_attrs = {"alignment-baseline": "middle",
                      "font-family": self.font_family,
                      "font-size": label_size,
                      "text-anchor": "middle",
                      "x": "50%",
                      "y": "50%",
                      "style": {"fill": COLORS['black'],
                                "opacity": COLORS['black'].a,
                                "stroke": COLORS['black'],
                                "stroke-width": stroke_width / 4.0}}
        text_elem = SubElement(sub_svg_elem, "text", _map_to_element_attrs(text_attrs))
        text_elem.text = label

    def draw_line(self,
                  start_point,
                  end_point,
                  stroke_width,
                  stroke_color=COLORS['black'],
                  is_dashed=False):
        point1 = convert_point_to_svg_coordinates(start_point, self.image_height)
        point2 = convert_point_to_svg_coordinates(end_point, self.image_height)
        style = {'stroke-width': stroke_width,
                 'stroke': stroke_color,
                 'opacity': stroke_color.a,
                 'stroke-linecap': 'butt'}
        if is_dashed:
            style.update({"stroke-dasharray": "4 1"})

        svg_elem_attrs = {"x1": point1.x,
                          "y1": point1.y,
                          "x2": point2.x,
                          "y2": point2.y,
                          "style": style}
        SubElement(self.svg_elem, "line", _map_to_element_attrs(svg_elem_attrs))

    def draw_arrow(self,
                   start_point,
                   end_point,
                   stroke_width,
                   stroke_color=COLORS['black']):
        point1 = convert_point_to_svg_coordinates(start_point, self.image_height)
        point2 = convert_point_to_svg_coordinates(end_point, self.image_height)

        direction = Point(point2.x - point1.x, point2.y - point1.y)
        direction_magnitude = math.sqrt(math.pow(direction.x, 2) +
                                        math.pow(direction.y, 2))

        inv_magnitude = 1.0 / direction_magnitude
        arrowhead_length = 9.0
        arrowhead_half_width = arrowhead_length * 0.5
        direction = Point(direction.x * inv_magnitude, direction.y * inv_magnitude)
        perpendicular_dir = Point(-direction.y, direction.x)

        point2 = Point(point2.x - arrowhead_length * direction.x,
                       point2.y - arrowhead_length * direction.y)

        triangle_tip = Point(point2.x + arrowhead_length * direction.x,
                             point2.y + arrowhead_length * direction.y)

        triangle_pt_1 = Point(point2.x + arrowhead_half_width * perpendicular_dir.x,
                              point2.y + arrowhead_half_width * perpendicular_dir.y)

        triangle_pt_2 = Point(point2.x - arrowhead_half_width * perpendicular_dir.x,
                              point2.y - arrowhead_half_width * perpendicular_dir.y)

        line_attrs = {"x1": point1.x,
                      "y1": point1.y,
                      "x2": point2.x,
                      "y2": point2.y,
                      "style": {"opacity": stroke_color.a,
                                "stroke": stroke_color,
                                "stroke-linecap": "butt",
                                "stroke-width": stroke_width}}
        SubElement(self.svg_elem, "line", _map_to_element_attrs(line_attrs))

        poly_attrs = {"points": [triangle_tip, triangle_pt_1, triangle_pt_2],
                      "style": {"fill": stroke_color}}
        SubElement(self.svg_elem, "polygon", _map_to_element_attrs(poly_attrs))

    def draw_text(self,
                  text,
                  location,
                  text_size,
                  color=COLORS['black'],
                  stroke_width=1.0):
        location_svg = convert_point_to_svg_coordinates(location, self.image_height)

        text_attrs = {"font-family": self.font_family,
                      "font-size": text_size,
                      "x": location_svg.x,
                      "y": location_svg.y,
                      "style": {"file": color,
                                "opacity": color.a,
                                "stroke": color,
                                "stroke-width": stroke_width / 4.0}}
        text_elem = SubElement(self.svg_elem, "text", _map_to_element_attrs(text_attrs))
        text_elem.text = text

    def get_image(self):
        # Python 3 produces a bytestring with the tostring() method, whereas Python 2
        # gives a str object. The try-except block below checks for this case.
        xmlstr = tostring(self.svg_elem, encoding='utf-8', method='xml')
        try:
            xmlstr = xmlstr.decode("utf8")
        except UnicodeDecodeError:
            pass
        return minidom.parseString(xmlstr).toprettyxml(indent='  ')


class ClipData(object):

    def __init__(self, src_start=0.0, src_end=0.0, available_start=0.0,
                 available_end=0.0, available_duration=0.0,
                 trim_start=0.0, trim_duration=0.0, target_url='', clip_id=0,
                 transition_begin=None, transition_end=None):
        self.src_start = src_start
        self.src_end = src_end
        self.available_start = available_start
        self.available_end = available_end
        self.available_duration = available_duration
        self.trim_start = trim_start
        self.trim_duration = trim_duration
        self.clip_id = clip_id
        self.transition_begin = transition_begin
        self.transition_end = transition_end
        self.target_url = target_url


def draw_item(otio_obj, svg_writer, extra_data=()):
    """
    Draws a shape based on the type of OTIO object
    """
    write_type_map = {
        otio.schema.Timeline: _draw_timeline,
        otio.schema.Stack: _draw_stack,
        otio.schema.Track: _draw_track,
        otio.schema.Clip: _draw_clip,
        otio.schema.Gap: _draw_gap,
        otio.schema.Transition: _draw_transition,
        otio.schema.SerializableCollection: _draw_collection,
    }
    if type(otio_obj) in write_type_map:
        return write_type_map[type(otio_obj)](otio_obj, svg_writer, extra_data)


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

            trim_start = item.trimmed_range().start_time.value
            trim_duration = item.trimmed_range().duration.value
            available_start = track_duration - trim_start
            available_end = 0.0

            # If the Item's media reference does not have an available_range
            # use the Item's source range
            if item.media_reference and item.media_reference.available_range:
                available_range = item.available_range()
            else:
                available_range = item.source_range

            src_start = track_duration
            src_end = track_duration - 1
            track_duration += trim_duration

            if isinstance(item, otio.schema.Clip):
                available_start += available_range.start_time.value

            min_time = min(min_time, available_start)

            if isinstance(item, otio.schema.Clip):
                clip_count += 1
                available_duration = available_range.duration.value
                available_end = (available_start + available_duration -
                                 trim_start - trim_duration + track_duration - 1)

                if item.media_reference and hasattr(item.media_reference, 'target_url'):
                    target_url = item.media_reference.target_url
                else:
                    target_url = UNKNOWN_LABEL

                clip_data = ClipData(src_start, src_end, available_start,
                                     available_end, available_duration, trim_start,
                                     trim_duration, target_url, clip_count - 1)
                if current_transition is not None:
                    clip_data.transition_begin = current_transition
                    current_transition = None
                current_track_clips_data.append(clip_data)

            elif isinstance(item, otio.schema.Gap):
                available_end = src_end
                available_duration = trim_duration
                current_transition = None
                clip_data = ClipData(src_start, src_end, available_start,
                                     available_end, available_duration, trim_start,
                                     trim_duration, "Gap", -1)
                current_track_clips_data.append(clip_data)
            max_time = max(max_time, available_end)

        svg_writer.global_max_time = max(svg_writer.global_max_time, max_time)
        svg_writer.global_min_time = min(svg_writer.global_min_time, min_time)

        svg_writer.all_clips_data.append(current_track_clips_data)
        svg_writer.tracks_duration.append(track_duration)

        svg_writer.track_transition_available.append(current_track_has_transition)
        if current_track_has_transition:
            transition_track_count += 1

        # store track-wise clip count to draw arrows from stack to tracks
        track_clip_count = len(svg_writer.trackwise_clip_count)
        if track_clip_count == 0:
            svg_writer.trackwise_clip_count.append(clip_count)
        else:
            svg_clip_count = svg_writer.trackwise_clip_count[track_clip_count - 1]
            svg_writer.trackwise_clip_count.append(clip_count - svg_clip_count)
    # The scale in x direction is calculated considering margins on the
    # left and right side if the image
    svg_writer.scale_x = (svg_writer.image_width - (2.0 * svg_writer.image_margin)) / \
                         (svg_writer.global_max_time - svg_writer.global_min_time + 1.0)
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
    #   transition_track_count = we need one more row per the number of tracks with
    #                            transitions
    # NumberOfRects * 2.0 - 1.0 = to account for "one rect space" between all the rects
    total_image_margin_space = 2.0 * svg_writer.image_margin
    bottom_label_space = 2.0 * svg_writer.font_size
    svg_total_draw_space = (svg_writer.image_height - total_image_margin_space -
                            bottom_label_space)
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

    rect = Rect(timeline_origin,
                svg_writer.max_total_duration * svg_writer.scale_x,
                svg_writer.clip_rect_height)
    svg_writer.draw_labeled_solid_rect_with_border(
        rect,
        label="Timeline",
        label_size=0.4 * svg_writer.clip_rect_height
    )
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(1, int(svg_writer.max_total_duration)):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x),
                         timeline_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                             stroke_color=COLORS['black'])

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
    start_time_location = Point(timeline_origin.x + svg_writer.font_size,
                                timeline_origin.y - svg_writer.font_size)
    svg_writer.draw_text(
        GLOBAL_START_TIME_LABEL.format(_range_to_repr(timeline.global_start_time)),
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

    rect = Rect(stack_origin,
                stack_duration * svg_writer.scale_x,
                svg_writer.clip_rect_height)
    svg_writer.draw_labeled_solid_rect_with_border(
        rect,
        label="Stack",
        fill_color=COLORS['dark_gray_translucent'],
        label_size=0.4 * svg_writer.clip_rect_height
    )

    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(1, int(svg_writer.max_total_duration)):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), stack_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                             stroke_color=COLORS['black'])

    for i in range(0, len(svg_writer.tracks_duration)):
        draw_item(stack[i], svg_writer, (stack_x_origin, svg_writer.tracks_duration[i],
                                         svg_writer.all_clips_data[i],
                                         svg_writer.track_transition_available[i]))
    # Draw arrows from stack to tracks
    #   arrow from stack to first track
    stack_width = stack_duration * svg_writer.scale_x
    arrow_start = Point(svg_writer.x_origin + stack_width * 0.5,
                        stack_origin.y - svg_writer.arrow_margin)
    arrow_end = Point(svg_writer.x_origin + stack_width * 0.5,
                      stack_origin.y - svg_writer.clip_rect_height +
                      svg_writer.arrow_margin)
    svg_writer.draw_arrow(start_point=arrow_start,
                          end_point=arrow_end,
                          stroke_width=2.0,
                          stroke_color=COLORS['black'])

    end_arrow_offset = 1
    #   arrows from stack to rest of the tracks
    for i in range(1, len(svg_writer.trackwise_clip_count)):
        arrow_x_increment_per_track = 10.0
        end_arrow_offset += (svg_writer.trackwise_clip_count[i - 1] * 2.0 + 4.0)
        arrow_start = Point(
            (i * arrow_x_increment_per_track) + svg_writer.x_origin + stack_width * 0.5,
            stack_origin.y - svg_writer.arrow_margin)
        arrow_end = Point(
            (i * arrow_x_increment_per_track) + svg_writer.x_origin + stack_width * 0.5,
            stack_origin.y - (end_arrow_offset * svg_writer.clip_rect_height) +
            svg_writer.arrow_margin)
        svg_writer.draw_arrow(start_point=arrow_start,
                              end_point=arrow_end,
                              stroke_width=2.0,
                              stroke_color=COLORS['black'])

    arrow_label_location = Point(arrow_start.x + svg_writer.arrow_label_margin,
                                 stack_origin.y - svg_writer.clip_rect_height * 0.5)
    svg_writer.draw_text(
        CHILDREN_LABEL.format(len(svg_writer.trackwise_clip_count)),
        arrow_label_location,
        svg_writer.font_size
    )

    # Draw range info
    trimmed_range_location = Point(stack_origin.x + svg_writer.font_size,
                                   stack_origin.y + svg_writer.clip_rect_height +
                                   svg_writer.text_margin)
    svg_writer.draw_text(
        TRIMMED_RANGE_LABEL.format(_range_to_repr(stack.trimmed_range())),
        trimmed_range_location,
        svg_writer.font_size
    )
    source_range_location = Point(stack_origin.x + svg_writer.font_size,
                                  stack_origin.y - svg_writer.font_size)
    svg_writer.draw_text(
        SOURCE_RANGE_LABEL.format(_range_to_repr(stack.source_range)),
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

    track_rect = Rect(track_origin,
                      track_duration * svg_writer.scale_x,
                      svg_writer.clip_rect_height)
    svg_writer.draw_labeled_solid_rect_with_border(
        rect=track_rect,
        label=track.name or "Track",
        fill_color=COLORS["dark_gray_translucent"],
        label_size=0.4 * svg_writer.clip_rect_height,
    )
    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(1, int(track_duration)):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), track_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt,
                             end_point=end_pt,
                             stroke_width=1.0,
                             stroke_color=COLORS['black'])
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
    svg_writer.draw_arrow(start_point=arrow_start,
                          end_point=arrow_end,
                          stroke_width=2.0,
                          stroke_color=COLORS['black'])
    arrow_label_text = CHILDREN_LABEL.format(item_count + transition_count)
    arrow_label_location = Point(arrow_start.x + svg_writer.arrow_label_margin,
                                 track_origin.y - svg_writer.clip_rect_height * 0.5)
    svg_writer.draw_text(arrow_label_text, arrow_label_location, svg_writer.font_size)

    # Draw range info
    trimmed_range_location = Point(
        track_origin.x + svg_writer.font_size,
        track_origin.y + svg_writer.clip_rect_height + svg_writer.text_margin,
    )
    svg_writer.draw_text(
        TRIMMED_RANGE_LABEL.format(_range_to_repr(track.trimmed_range())),
        trimmed_range_location,
        svg_writer.font_size
    )
    source_range_location = Point(
        track_origin.x + svg_writer.font_size, track_origin.y - svg_writer.font_size
    )
    svg_writer.draw_text(
        SOURCE_RANGE_LABEL.format(_range_to_repr(track.source_range)),
        source_range_location,
        svg_writer.font_size
    )


# Draw clip
def _draw_clip(clip, svg_writer, extra_data=()):
    clip_data = extra_data[0]
    clip_count = extra_data[1]
    clip_color = Color.random_color()
    clip_origin = Point(
        svg_writer.x_origin + (clip_data.src_start * svg_writer.scale_x),
        svg_writer.image_height - svg_writer.image_margin -
        svg_writer.vertical_drawing_index * svg_writer.clip_rect_height
    )
    clip_rect = Rect(clip_origin, clip_data.trim_duration * svg_writer.scale_x,
                     svg_writer.clip_rect_height)

    svg_writer.draw_labeled_solid_rect_with_border(
        clip_rect,
        label=clip.name or CLIP_LABEL.format(clip_data.clip_id),
        fill_color=clip_color,
        label_size=0.4 * svg_writer.clip_rect_height
    )

    time_marker_height = 0.15 * svg_writer.clip_rect_height

    for i in range(int(clip_data.src_start), int(clip_data.src_end) + 1):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), clip_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                             stroke_color=COLORS['black'])

    # Draw trimmed range info
    trimmed_range_location = Point(clip_origin.x + svg_writer.font_size,
                                   clip_origin.y + svg_writer.clip_rect_height +
                                   svg_writer.text_margin)
    svg_writer.draw_text(
        TRIMMED_RANGE_LABEL.format(_range_to_repr(clip.trimmed_range())),
        trimmed_range_location,
        svg_writer.font_size
    )

    # Draw source range info
    source_range_location = Point(clip_origin.x + svg_writer.font_size,
                                  clip_origin.y - svg_writer.font_size)
    svg_writer.draw_text(
        SOURCE_RANGE_LABEL.format(_range_to_repr(clip.source_range)),
        source_range_location,
        svg_writer.font_size
    )

    # Draw media reference
    trim_media_origin = Point(
        svg_writer.x_origin + (clip_data.src_start * svg_writer.scale_x),
        svg_writer.image_height - svg_writer.image_margin -
        (svg_writer.vertical_drawing_index + clip_count * 2) *
        svg_writer.clip_rect_height
    )
    media_origin = Point(
        svg_writer.x_origin + (clip_data.available_start * svg_writer.scale_x),
        svg_writer.image_height - svg_writer.image_margin -
        (svg_writer.vertical_drawing_index + clip_count * 2) *
        svg_writer.clip_rect_height
    )

    media_ref_rect = Rect(media_origin,
                          clip_data.available_duration * svg_writer.scale_x,
                          svg_writer.clip_rect_height)
    svg_writer.draw_rect(media_ref_rect)

    # Draw lableled rect
    lbl_media_rect = Rect(trim_media_origin,
                          clip_data.trim_duration * svg_writer.scale_x,
                          svg_writer.clip_rect_height)
    svg_writer.draw_labeled_solid_rect_with_border(
        lbl_media_rect,
        label=clip.media_reference.name or "Media-{}".format(clip_data.clip_id),
        fill_color=clip_color,
        label_size=0.4 * svg_writer.clip_rect_height
    )
    for i in range(int(clip_data.available_start), int(clip_data.available_end) + 1):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), media_origin.y)
        if start_pt.x < media_origin.x:
            continue
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt,
                             end_point=end_pt,
                             stroke_width=1.0,
                             stroke_color=COLORS['black'])

    # Draw media_reference info
    if clip.media_reference and clip.media_reference.available_range:
        str_available_range = _range_to_repr(clip.available_range())
    else:
        str_available_range = UNKNOWN_LABEL

    available_range_location = Point(media_origin.x + svg_writer.font_size,
                                     media_origin.y - svg_writer.font_size)
    svg_writer.draw_text(
        AVAILABLE_RANGE_LABEL.format(str_available_range),
        available_range_location,
        svg_writer.font_size
    )

    # Draw target_rul
    if clip.media_reference and hasattr(clip.media_reference, 'target_url'):
        target_url = clip.media_reference.target_url
    else:
        target_url = UNKNOWN_LABEL
    target_url_location = Point(media_origin.x + svg_writer.font_size,
                                media_origin.y - 2.0 * svg_writer.font_size)
    svg_writer.draw_text(
        TARGET_URL_LABEL.format(target_url),
        target_url_location,
        svg_writer.font_size
    )

    # Draw arrow from clip to media reference
    calc_clip_count = (clip_count - 1) * 2.0 + 1
    clip_media_height_difference = calc_clip_count * svg_writer.clip_rect_height
    media_arrow_x = clip_origin.x + (clip_data.trim_duration * svg_writer.scale_x) * 0.5

    media_arrow_start = Point(media_arrow_x, clip_origin.y - svg_writer.arrow_margin)
    media_arrow_end = Point(
        media_arrow_x,
        clip_origin.y - clip_media_height_difference + svg_writer.arrow_margin
    )
    svg_writer.draw_arrow(start_point=media_arrow_start, end_point=media_arrow_end,
                          stroke_width=2.0, stroke_color=COLORS['black'])

    arrow_lbl_height = Point(media_arrow_start.x + svg_writer.arrow_label_margin,
                             media_arrow_start.y - svg_writer.clip_rect_height * 0.5)
    svg_writer.draw_text(MEDIA_REFERENCE_LABEL, arrow_lbl_height, svg_writer.font_size)

    # Draw media transition sections
    if clip_data.transition_end is not None:
        cut_x = clip_origin.x + clip_rect.width
        section_start_pt = Point(cut_x, media_origin.y)
        # Handle the case of transition ending at cut
        if clip_data.transition_end.out_offset.value == 0.0:
            width = -clip_data.transition_end.in_offset.value * svg_writer.scale_x
            x_offset = clip_data.src_end - clip_data.transition_end.in_offset.value
        else:
            width = clip_data.transition_end.out_offset.value * svg_writer.scale_x
            x_offset = clip_data.src_end + clip_data.transition_end.out_offset.value

        media_trans_rect = Rect(section_start_pt, width, svg_writer.clip_rect_height)
        section_color = Color(clip_color[0], clip_color[1], clip_color[2], 0.5)
        svg_writer.draw_dashed_rect(media_trans_rect, fill_color=section_color)

        marker_x = [clip_data.src_end, x_offset]
        marker_x.sort()
        # Draw markers for transition sections
        for i in range(int(marker_x[0]), int(marker_x[1]) + 1):
            start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x),
                             media_origin.y)
            if start_pt.x < media_trans_rect.min_x():
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
            width = clip_data.transition_begin.out_offset.value * svg_writer.scale_x
            x_offset = clip_data.src_start + clip_data.transition_begin.out_offset.value
        else:
            width = -clip_data.transition_begin.in_offset.value * svg_writer.scale_x
            x_offset = clip_data.src_start - clip_data.transition_begin.out_offset.value

        media_trans_rect = Rect(section_start_pt, width, svg_writer.clip_rect_height)
        section_color = Color(clip_color[0], clip_color[1], clip_color[2], 0.5)
        svg_writer.draw_dashed_rect(media_trans_rect, fill_color=section_color)

        marker_x = [clip_data.src_start, x_offset]
        marker_x.sort()
        # Draw markers for transition sections
        for i in range(int(marker_x[0]), int(marker_x[1]) + 1):
            start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x),
                             media_origin.y)
            if start_pt.x < media_trans_rect.min_x():
                continue
            end_pt = Point(start_pt.x, start_pt.y + 0.15 * svg_writer.clip_rect_height)
            svg_writer.draw_line(start_point=start_pt, end_point=end_pt,
                                 stroke_width=1.0, stroke_color=COLORS['black'])


def _draw_gap(gap, svg_writer, extra_data=()):
    gap_data = extra_data[0]
    gap_origin = Point(svg_writer.x_origin + (gap_data.src_start * svg_writer.scale_x),
                       svg_writer.image_height - svg_writer.image_margin -
                       svg_writer.vertical_drawing_index * svg_writer.clip_rect_height)

    gap_rect = Rect(gap_origin,
                    gap_data.trim_duration * svg_writer.scale_x,
                    svg_writer.clip_rect_height)
    svg_writer.draw_labeled_dashed_rect_with_border(
        gap_rect,
        label='Gap',
        label_size=0.4 * svg_writer.clip_rect_height
    )

    time_marker_height = 0.15 * svg_writer.clip_rect_height
    for i in range(int(gap_data.src_start), int(gap_data.src_end) + 1):
        start_pt = Point(svg_writer.x_origin + (i * svg_writer.scale_x), gap_origin.y)
        end_pt = Point(start_pt.x, start_pt.y + time_marker_height)
        svg_writer.draw_line(start_point=start_pt, end_point=end_pt, stroke_width=1.0,
                             stroke_color=COLORS['black'])

    # Draw trimmed range info
    trimmed_range_location = Point(gap_origin.x + svg_writer.font_size,
                                   gap_origin.y + svg_writer.clip_rect_height +
                                   svg_writer.text_margin)
    svg_writer.draw_text(
        TRIMMED_RANGE_LABEL.format(_range_to_repr(gap.trimmed_range())),
        trimmed_range_location,
        svg_writer.font_size
    )

    # Draw source range info
    source_range_location = Point(gap_origin.x + svg_writer.font_size,
                                  gap_origin.y - svg_writer.font_size)
    svg_writer.draw_text(
        SOURCE_RANGE_LABEL.format(_range_to_repr(gap.source_range)),
        source_range_location,
        svg_writer.font_size
    )


def _draw_transition(transition, svg_writer, extra_data=()):
    cut_x = extra_data[0]
    in_offset = transition.in_offset.value
    out_offset = transition.out_offset.value

    transition_origin = Point(cut_x - (in_offset * svg_writer.scale_x),
                              svg_writer.image_height - svg_writer.image_margin -
                              (svg_writer.vertical_drawing_index - 2) *
                              svg_writer.clip_rect_height)
    transition_rect = Rect(transition_origin,
                           (in_offset + out_offset) * svg_writer.scale_x,
                           svg_writer.clip_rect_height)
    svg_writer.draw_labeled_rect(transition_rect,
                                 label=transition.name or "Transition",
                                 label_size=0.4 * svg_writer.clip_rect_height)
    line_end = Point(transition_origin.x + transition_rect.width,
                     transition_origin.y + transition_rect.height)
    svg_writer.draw_line(transition_origin, line_end, stroke_width=1.0,
                         stroke_color=COLORS['black'])
    in_offset_location = Point(transition_origin.x + svg_writer.font_size,
                               transition_origin.y - svg_writer.font_size)
    out_offset_location = Point(transition_origin.x + svg_writer.font_size,
                                transition_origin.y - 2.0 * svg_writer.font_size)

    svg_writer.draw_text(
        IN_OFFSET_LABEL.format(_float_to_repr(in_offset)),
        in_offset_location,
        svg_writer.font_size
    )
    svg_writer.draw_text(
        OUT_OFFSET_LABEL.format(_float_to_repr(out_offset)),
        out_offset_location,
        svg_writer.font_size
    )
    cut_location = Point(cut_x, transition_origin.y)
    cut_line_end = Point(cut_x,
                         svg_writer.image_height - svg_writer.image_margin -
                         svg_writer.vertical_drawing_index *
                         svg_writer.clip_rect_height)
    svg_writer.draw_line(cut_location,
                         cut_line_end,
                         stroke_width=1.0,
                         stroke_color=COLORS['black'])


def _draw_collection(collection, svg_writer, extra_data=()):
    pass


def _range_to_repr(time_range):
    """
    Converts a TimeRange's value to a repr for formatting in strings

    :param opentimelineio.opentime.TimeRange time_range: Time Range to process
    :return: Formatted string of a Time Range
    :rtype: str
    """

    if time_range is None:
        return UNKNOWN_LABEL

    start_time = _float_to_repr(time_range.start_time.value)
    duration = _float_to_repr(time_range.duration.value)
    return "{}, {}".format(start_time, duration)


def _float_to_repr(value):
    """
    Convert float to its repr for formatting in strings

    :param float value: Value to process
    :return: String representation of a float
    :rtype: str
    """
    return repr(float(round(value, 1)))


def _map_to_element_attrs(data):
    """
    Converts values within a dict to appropriate values for making XML Elements.

    :param dict data: Mapping of XML keys to simple and complex structs to be converted
    :rtype: dict
    """
    elem_attrs = {}
    for key, value in data.items():
        # Flatten dict to string
        if key == 'style' and isinstance(value, dict):
            items = []
            for k, v in value.items():
                items.append("{}:{}".format(k, _elem_attr_to_str(v)))
            value = ';'.join(items)

        # Flatten list to string
        elif key == 'points' and isinstance(value, (tuple, list)):
            value = " ".join([p.svg_point_string() for p in value])

        else:
            value = _elem_attr_to_str(value)

        elem_attrs[key] = value
    return elem_attrs


def _transform_elem_attrs_from_rect(rect):
    """
    Generate the XML Element transform attrs from a :class:`Rect`

    :param Rect rect:
    :rtype: dict
    """
    x_str = _elem_attr_to_str(rect.origin.x)
    y_str = _elem_attr_to_str(rect.origin.y)
    return {"transform": "translate({},{})".format(x_str, y_str)}


def _elem_attr_to_str(value):
    """
    Converts value to XML appropriate string

    :param any value: value to convert
    :rtype: str
    """
    if isinstance(value, float):
        value = "{:.8f}".format(value)
    elif isinstance(value, Color):
        value = value.to_svg()
    return value


# --------------------
# adapter requirements
# --------------------

def write_to_string(input_otio, width=2406.0, height=1054.0, image_margin=20.0,
                    font_family='sans-serif', font_size=5.0, arrow_label_margin=5.0):
    global RANDOM_COLORS_USED

    svg_writer = SVGWriter(image_width=width, image_height=height,
                           font_family=font_family, image_margin=image_margin,
                           font_size=font_size, arrow_label_margin=arrow_label_margin)
    RANDOM_COLORS_USED = []
    seed(100)
    draw_item(input_otio, svg_writer, ())

    return svg_writer.get_image()
