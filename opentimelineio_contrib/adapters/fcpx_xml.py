#
# Copyright 2018 Pixar Animation Studios
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

"""OpenTimelineIO Final Cut Pro X XML Adapter. """
import os
import subprocess
import copy
from xml.etree import cElementTree
from fractions import Fraction
from datetime import date
from xml.dom import minidom

try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

import opentimelineio as otio

META_NAMESPACE = "fcpx_xml"

COMPOSABLE_ELEMENTS = ("video", "audio", "ref-clip", "asset-clip")

FRAMERATE_FRAMEDURATION = {23.98: "1001/24000s",
                           24: "25/600s",
                           25: "1/25s",
                           29.97: "1001/30000s",
                           30: "100/3000s",
                           50: "1/50s",
                           59.94: "1001/60000s",
                           60: "1/60s"}


def format_name(frame_rate, path):
    """
    Helper to get the formatName used in FCP X XML format elements. This
    uses ffprobe to get the frame size of the the clip at the provided path.

    Args:
        frame_rate (int): The frame rate of the clip at the provided path
        path (str): The path to the clip to probe

    Returns:
        str: The format name. If empty, then ffprobe couldn't find the item
    """

    path = path.replace("file://", "")
    path = unquote(path)
    if not os.path.exists(path):
        return ""

    try:
        frame_size = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=height,width",
                "-of",
                "csv=s=x:p=0",
                path
            ]
        )
    except (subprocess.CalledProcessError, OSError):
        frame_size = ""

    if not frame_size:
        return ""

    frame_size = frame_size.rstrip()

    if "1920" in frame_size:
        frame_size = "1080"

    if frame_size.endswith("1280"):
        frame_size = "720"

    return "FFVideoFormat{}p{}".format(frame_size, frame_rate)


def to_rational_time(rational_number, fps):
    """
    This converts a rational number value to an otio RationalTime object

    Args:
        rational_number (str): This is a rational number from an FCP X XML
        fps (int): The frame rate to use for calculating the rational time

    Returns:
        RationalTime: A RationalTime object
    """

    if rational_number == "0s" or rational_number is None:
        frames = 0
    else:
        parts = rational_number.split("/")
        if len(parts) > 1:
            frames = int(
                float(parts[0]) / float(parts[1].replace("s", "")) * float(fps)
            )
        else:
            frames = int(float(parts[0].replace("s", "")) * float(fps))

    return otio.opentime.RationalTime(frames, int(fps))


def from_rational_time(rational_time):
    """
    This converts a RationalTime object to a rational number as a string

    Args:
        rational_time (RationalTime): a rational time object

    Returns:
        str: A rational number as a string
    """

    if int(rational_time.value) == 0:
        return "0s"
    result = Fraction(
        float(rational_time.value) / float(rational_time.rate)
    ).limit_denominator()
    if str(result.denominator) == "1":
        return "{}s".format(result.numerator)
    return "{}/{}s".format(result.numerator, result.denominator)


class FcpxOtio(object):
    """
    This object is responsible for knowing how to convert an otio into an
    FCP X XML
    """

    def __init__(self, otio_timeline):
        self.otio_timeline = otio_timeline
        self.fcpx_xml = cElementTree.Element("fcpxml", version="1.8")
        self.resource_element = cElementTree.SubElement(
            self.fcpx_xml,
            "resources"
        )
        self.timelines = [
            timeline for timeline in self.otio_timeline.each_child(
                descended_from_type=otio.schema.Timeline
            )
        ]

        if len(self.timelines) > 1:
            self.event_resource = cElementTree.SubElement(
                self.fcpx_xml,
                "event",
                {"name": self.otio_timeline.name}
            )
        else:
            self.event_resource = self.fcpx_xml

        self.resource_count = 0

    def to_xml(self):
        """
        Convert an otio to an FCP X XML

        Returns:
            str: FCPX XML content
        """

        self._add_formats()
        self._add_compound_clips()

        for project in self.timelines:
            top_sequence = self._stack_to_sequence(project.tracks)

            project_element = cElementTree.Element(
                "project",
                {
                    "name": project.name,
                    "uid": project.metadata.get("fcpx", {}).get("uid", "")
                }
            )
            project_element.append(top_sequence)
            self.event_resource.append(project_element)

        if not self.timelines:
            for clip in self.otio_timeline.each_child(
                descended_from_type=otio.schema.Clip
            ):
                if not clip.parent():
                    self._add_asset(clip)

        child_parent_map = {c: p for p in self.fcpx_xml.iter() for c in p}

        for marker in [marker for marker in self.fcpx_xml.iter("marker")]:
            parent = child_parent_map.get(marker)
            marker_attribs = marker.attrib.copy()
            parent.remove(marker)
            cElementTree.SubElement(
                parent,
                "marker",
                marker_attribs
            )

        xml = cElementTree.tostring(
            self.fcpx_xml,
            encoding="UTF-8",
            method="xml"
        )
        dom = minidom.parseString(xml)
        pretty = dom.toprettyxml(indent="    ")
        return pretty.replace(
            '<?xml version="1.0" ?>',
            '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n'
        )

    def _stack_to_sequence(self, stack, compound_clip=False):
        lane_zero_clips = []
        format_element = self._format_by_frame_rate(stack.duration().rate)
        sequence_element = cElementTree.Element(
            "sequence",
            {
                "duration": self._calculate_rational_number(
                    stack.duration().value,
                    stack.duration().rate
                ),
                "format": str(format_element.get("id"))
            }
        )
        spine = cElementTree.SubElement(sequence_element, "spine")
        video_tracks = [
            t for t in stack
            if t.kind == otio.schema.TrackKind.Video
        ]
        audio_tracks = [
            t for t in stack
            if t.kind == otio.schema.TrackKind.Audio
        ]

        for idx, track in enumerate(video_tracks):
            lane_zero_clips = self._track_for_spine(
                track,
                idx,
                lane_zero_clips,
                spine,
                compound_clip
            )

        for idx, track in enumerate(audio_tracks):
            lane_id = -(idx + 1)
            lane_zero_clips = self._track_for_spine(
                track,
                lane_id,
                lane_zero_clips,
                spine,
                compound_clip
            )
        return sequence_element

    def _track_for_spine(
            self,
            track,
            lane_id,
            lane_zero_clips,
            spine,
            compound_clip):

        track_duration = 0
        for child in self._lanable_items(track.each_child()):
            if self._item_in_compound_clip(child) and not compound_clip:
                continue

            child_element = self._element_for_item(
                child,
                track_duration,
                lane_id
            )
            if not lane_id:
                spine.append(child_element)
                lane_zero_clips.append(
                    {
                        "range": int(track_duration + child.duration().value),
                        "item": child_element,
                        "otio_item": child
                    }
                )
            elif child.schema_name() != "Gap":
                parent = self._find_clip_at_duration(
                    lane_zero_clips,
                    track_duration
                )
                offset = self._offset_based_on_parent(
                    child,
                    child_element,
                    parent["otio_item"],
                    parent["item"]
                )

                child_element.set(
                    "offset",
                    from_rational_time(offset)
                )

                parent["item"].append(child_element)

            track_duration += int(child.duration().value)
        return lane_zero_clips

    def _offset_based_on_parent(
            self,
            child,
            child_element,
            parent,
            parent_element):

        parent_offset = to_rational_time(
            parent_element.get("offset"),
            parent.duration().rate
        )

        child_offset = to_rational_time(
            child_element.get("offset"),
            child.duration().rate
        )

        parent_start = to_rational_time(
            parent_element.get("start"),
            parent.duration().rate
        )
        return (child_offset - parent_offset) + parent_start

    def _item_in_compound_clip(self, item):
        stack_count = 0
        parent = item.parent()
        while parent is not None:
            if parent.schema_name() == "Stack":
                stack_count += 1
            parent = parent.parent()
        return stack_count > 1

    def _element_for_item(self, item, track_duration, lane):
        element = None
        duration = self._calculate_rational_number(
            item.duration().value,
            item.duration().rate
        )
        offset = self._calculate_offset(item.duration(), track_duration)
        if item.schema_name() == "Clip":
            asset_id = self._add_asset(item)

            element = cElementTree.Element(
                "clip",
                {
                    "name": item.name,
                    "offset": offset,
                    "duration": duration
                }
            )
            start = from_rational_time(item.source_range.start_time)
            if start != "0s":
                element.set("start", str(start))
            if item.parent().kind == otio.schema.TrackKind.Video:
                cElementTree.SubElement(
                    element,
                    "video",
                    {
                        "offset": "0s",
                        "ref": asset_id,
                        "duration": self._find_asset_duration(item)
                    }
                )
            else:
                gap_element = cElementTree.SubElement(
                    element,
                    "gap",
                    {
                        "name": "Gap",
                        "offset": "0s",
                        "duration": self._find_asset_duration(item)
                    }
                )
                audio = cElementTree.SubElement(
                    gap_element,
                    "audio",
                    {
                        "offset": "0s",
                        "ref": asset_id,
                        "duration": self._find_asset_duration(item)
                    }
                )
                if lane:
                    audio.set("lane", str(lane))

        if item.schema_name() == "Gap":
            element = cElementTree.Element(
                "gap",
                {
                    "name": "Gap",
                    "duration": duration,
                    "offset": offset,
                    "start": "3600s"
                }
            )
        if item.schema_name() == "Stack":
            asset_id = self._media_by_name(item.name).get("id")
            element = cElementTree.Element(
                "ref-clip",
                {
                    "name": item.name,
                    "duration": duration,
                    "offset": offset,
                    "start": from_rational_time(item.source_range.start_time),
                    "ref": str(asset_id)
                }
            )
            if item.parent().kind == otio.schema.TrackKind.Audio:
                element.set("srcEnable", "audio")

        if element is None:
            return None
        if lane:
            element.set("lane", str(lane))
        for marker in item.markers:
            marker_attribs = {
                "start": from_rational_time(marker.marked_range.start_time),
                "duration": from_rational_time(marker.marked_range.duration),
                "value": marker.name
            }
            marker_element = cElementTree.Element(
                "marker",
                marker_attribs
            )
            if marker.color == otio.schema.MarkerColor.RED:
                marker_element.set("completed", "0")
            if marker.color == otio.schema.MarkerColor.GREEN:
                marker_element.set("completed", "1")
            element.append(marker_element)
        return element

    def _lanable_items(self, items):
        return [
            item for item in items
            if item.schema_name() in ["Gap", "Stack", "Clip"]
        ]

    def _find_asset_duration(self, item):
        if (item.media_reference and
                not item.media_reference.is_missing_reference):
            return self._calculate_rational_number(
                item.media_reference.available_range.duration.value,
                item.media_reference.available_range.duration.rate
            )
        return self._calculate_rational_number(
            item.duration().value,
            item.duration().rate
        )

    def _find_asset_start(self, item):
        if (item.media_reference and
                not item.media_reference.is_missing_reference):
            return self._calculate_rational_number(
                item.media_reference.available_range.start_time.value,
                item.media_reference.available_range.start_time.rate
            )
        return self._calculate_rational_number(
            item.source_range.start_time.value,
            item.source_range.start_time.rate
        )

    def _calculate_offset(self, item_duration, track_duration):
        if int(track_duration) == 0:
            return "0s"
        return self._calculate_rational_number(
            track_duration,
            item_duration.rate
        )

    def _clip_format_name(self, clip):
        if not clip.media_reference:
            return ""

        if clip.media_reference.is_missing_reference:
            return ""

        return format_name(
            clip.duration().rate,
            clip.media_reference.target_url
        )

    def _add_format(self, clip):
        frame_duration = self._framerate_to_frame_duration(
            clip.duration().rate
        )
        format_element = self._format_by_frame_rate(clip.duration().rate)
        if format_element is None:
            cElementTree.SubElement(
                self.resource_element,
                "format",
                {
                    "id": self._resource_id_generator(),
                    "frameDuration": frame_duration,
                    "name": self._clip_format_name(clip)
                }
            )

    def _add_formats(self):
        for clip in self.otio_timeline.each_child(
            descended_from_type=otio.schema.Clip
        ):
            self._add_format(clip)
        # timelines = self.otio_timeline.each_child(
        #     descended_from_type=otio.schema.Timeline
        # )
        # for timeline in timelines:
        #     for track in timeline.video_tracks():
        #         for clip in track.each_clip():
        #             self._add_format(clip)

        #     for track in timeline.audio_tracks():
        #         for clip in track.each_clip():
        #             self._add_format(clip)

    def _add_asset(self, clip):
        self._add_format(clip)
        target_url = self._target_url_from_clip(clip)
        asset = self._asset_by_path(target_url)

        if asset is None:
            format_element = self._format_by_frame_rate(clip.duration().rate)
            resource_id = self._resource_id_generator()
            duration = self._find_asset_duration(clip)

            asset = cElementTree.SubElement(
                self.resource_element,
                "asset",
                {
                    "name": clip.name,
                    "src": target_url,
                    "format": format_element.get("id"),
                    "id": resource_id,
                    "duration": duration,
                    "start": self._find_asset_start(clip),
                    "hasAudio": "0",
                    "hasVideo": "0"
                }
            )
            cElementTree.SubElement(
                self.event_resource,
                "asset-clip",
                {
                    "name": clip.name,
                    "format": format_element.get("id"),
                    "ref": resource_id,
                    "duration": duration
                }
            )
        if not clip.parent():
            asset.set("hasAudio", "1")
            asset.set("hasVideo", "1")
            return asset.get("id")
        if clip.parent().kind == otio.schema.TrackKind.Audio:
            asset.set("hasAudio", "1")
        if clip.parent().kind == otio.schema.TrackKind.Video:
            asset.set("hasVideo", "1")
        return asset.get("id")

    def _add_compound_clip(self, item):
        media = self._media_by_name(item.name)
        if media is not None:
            return None

        resource_id = self._resource_id_generator()
        media_element = cElementTree.SubElement(
            self.resource_element,
            "media",
            {
                "name": self._compound_clip_name(item, resource_id),
                "id": resource_id
            }
        )
        if item.metadata.get("fcpx", {}).get("uid", False):
            media_element.set("uid", item.metadata.get("fcpx", {}).get("uid"))
        return (item, media_element)

    def _add_compound_clips(self):
        elements = [self._add_compound_clip(stack) for stack in self._stacks()]
        for compound_clip in elements:
            if compound_clip is None:
                continue
            element = compound_clip[1]
            item = compound_clip[0]

            element.append(self._stack_to_sequence(item, compound_clip=True))

    def _stacks(self):
        return self.otio_timeline.each_child(
            descended_from_type=otio.schema.Stack
        )

    def _resource_id_generator(self):
        self.resource_count += 1
        return "r{}".format(self.resource_count)

    def _event_name(self):
        if self.otio_timeline.name:
            return self.otio_timeline.name
        return date.strftime(date.today(), "%m-%e-%y")

    def _asset_by_path(self, path):
        return self.resource_element.find("./asset[@src='{}']".format(path))

    def _media_by_name(self, name):
        return self.resource_element.find("./media[@name='{}']".format(name))

    def _format_by_frame_rate(self, frame_rate):
        frame_duration = self._framerate_to_frame_duration(frame_rate)
        return self.resource_element.find(
            "./format[@frameDuration='{}']".format(frame_duration)
        )

    # --------------------
    # static methods
    # --------------------
    @staticmethod
    def _framerate_to_frame_duration(framerate):
        frame_duration = FRAMERATE_FRAMEDURATION.get(int(framerate), "")
        if not frame_duration:
            frame_duration = FRAMERATE_FRAMEDURATION.get(float(framerate), "")
        return frame_duration

    @staticmethod
    def _target_url_from_clip(clip):
        if (clip.media_reference and
                not clip.media_reference.is_missing_reference):
            return clip.media_reference.target_url
        return "file:///tmp/{}".format(clip.name)

    @staticmethod
    def _calculate_rational_number(duration, rate):
        if int(duration) == 0:
            return "0s"
        result = Fraction(float(duration) / float(rate)).limit_denominator()
        return "{}/{}s".format(result.numerator, result.denominator)

    @staticmethod
    def _find_clip_at_duration(clips, track_duration):
        for clip in clips:
            if clip["range"] > track_duration:
                return clip
        return clips[-1]

    @staticmethod
    def _compound_clip_name(compound_clip, resource_id):
        if compound_clip.name:
            return compound_clip.name
        return "compound_clip_{}".format(resource_id)


class FcpxXml(object):
    """
    This object is responsible for knowing how to convert an FCP X XML
    otio into an otio timeline
    """

    def __init__(self, xml_string):
        self.fcpx_xml = cElementTree.fromstring(xml_string)
        self.event_format_id = ""
        self.child_parent_map = {c: p for p in self.fcpx_xml.iter() for c in p}
        self.stack_list = []
        self.container = otio.schema.SerializableCollection()
        if self.fcpx_xml.find("./library/event"):
            self.container.name = self.fcpx_xml.find("./library/event").get(
                "name", ""
            )
        if self.fcpx_xml.find("./event"):
            self.container.name = self.fcpx_xml.find("./event").get("name", "")
        if self.fcpx_xml.find("./project"):
            self.container.name = self.fcpx_xml.find("./project").get(
                "name", ""
            )

    def to_otio(self):
        """
        Convert an FCP X XML to an otio

        Returns:
            OpenTimeline: An OpenTimeline Timeline object
        """
        timeline = None
        for project in self.fcpx_xml.findall(".//project"):
            timeline, stack_dictionary = self._create_stack_dictionary(project)
            self.stack_list.append(stack_dictionary)
            self.container.append(timeline)

        for media in self.fcpx_xml.findall(".//media"):
            compound, stack_dictionary = self._create_stack_dictionary(media)
            self.stack_list.append(stack_dictionary)
            if not timeline:
                self.container.append(compound)

        for sequence in self.fcpx_xml.findall(".//sequence"):
            self.event_format_id = sequence.get("format")
            for element in sequence.iter():
                if element.tag not in COMPOSABLE_ELEMENTS:
                    continue
                composable = self._build_composable(element)
                self._append_to_stacks(element, composable)

        for stack in self.stack_list:
            for lane in self._sorted_lanes(stack):
                track = self._lane_to_track(lane, stack)

                if stack["type"] == "project":
                    stack["stack"].tracks.append(track)

                if stack["type"] == "media":
                    stack["stack"].append(track)

        if not timeline:
            for element in self.fcpx_xml.iter():
                if element.tag == "ref-clip" or element.tag not in COMPOSABLE_ELEMENTS:
                    continue
                self.container.append(self._build_composable(element))

        return self.container

    def _lane_to_track(self, lane, stack):

        lane_items = self._sorted_items(lane, stack["otio_objects"])
        track = otio.schema.Track(name=lane, kind=self._track_type(lane_items))

        for item in lane_items:
            frame_diff = (int(item["offset"]) - track.duration().value)
            if frame_diff > 0:
                track.append(self._create_gap(0, frame_diff))
            track.append(item["otio_object"])
        return track

    def _build_composable(self, element):
        timing_clip = self._timing_clip(element)
        source_range = self._time_range(
            timing_clip,
            self._format_id_for_clip(element)
        )

        if element.tag != "ref-clip":
            otio_composable = otio.schema.Clip(
                name=timing_clip.get("name"),
                media_reference=self._reference_from_id(element.get("ref")),
                source_range=source_range
            )
        else:
            otio_composable = self._duplicate_stack(element, source_range)

        for marker in timing_clip.findall(".//marker"):
            otio_composable.markers.append(self._marker(marker))

        return otio_composable

    def _duplicate_stack(self, element, source_range):
        for stack in self.stack_list:
            if stack.get("id", "none") == element.get("ref"):
                duplicate_stack = copy.deepcopy(stack)

        duplicate_stack["stack"].source_range = source_range
        duplicate_stack["stack"].markers = []
        self.stack_list.append(duplicate_stack)
        return duplicate_stack["stack"]

    def _append_to_stacks(self, element, otio_composable):
        clip_offset, lane = self._offset_and_lane(element)
        parent = self._find_parent(element)
        for stack in self.stack_list:
            if stack.get("uid", "none") != parent.attrib.get("uid"):
                continue
            stack["otio_objects"].append(
                {
                    "type": element.tag,
                    "ref_id": element.get("ref"),
                    "offset": clip_offset.value,
                    "otio_object": otio_composable,
                    "track": lane,
                    "audio_only": self._audio_only(element)
                }
            )

    def _marker(self, element):
        if element.get("completed", None) and element.get("completed") == "1":
            color = otio.schema.MarkerColor.GREEN
        if element.get("completed", None) and element.get("completed") == "0":
            color = otio.schema.MarkerColor.RED
        if not element.get("completed", None):
            color = otio.schema.MarkerColor.PURPLE

        otio_marker = otio.schema.Marker(
            name=element.get("value", ""),
            marked_range=self._time_range(element, self.event_format_id),
            color=color
        )
        return otio_marker

    def _find_parent(self, element):
        parent = self.child_parent_map.get(element)
        if parent.tag in ("media", "project"):
            return parent
        return self._find_parent(parent)

    def _audio_only(self, element):
        if element.tag == "audio":
            return True
        if element.tag == "asset-clip":
            asset = self._asset_by_id(element.get("ref", None))
            if asset and asset.get("hasVideo", "0") == "0":
                return True
        if element.tag == "ref-clip":
            if element.get("srcEnable", "video") == "audio":
                return True
        return False

    def _create_gap(self, start_frame, number_of_frames):
        fps = self._format_frame_rate(self.event_format_id)
        source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(start_frame, fps),
            duration=otio.opentime.RationalTime(number_of_frames, fps)
        )
        return otio.schema.Gap(source_range=source_range)

    def _timing_clip(self, clip):
        while clip.tag not in ("clip", "asset-clip", "ref-clip"):
            clip = self.child_parent_map.get(clip)
        return clip

    def _offset_and_lane(self, clip):
        clip_format_id = self._format_id_for_clip(clip)
        clip = self._timing_clip(clip)
        parent = self.child_parent_map.get(clip)

        parent_format_id = self._format_id_for_clip(parent)

        if parent.tag == "spine" and parent.get("lane", None):
            lane = parent.get("lane")
            parent = self.child_parent_map.get(parent)
            spine = True
        else:
            lane = clip.get("lane", "0")
            spine = False

        clip_offset_frames = self._number_of_frames(
            clip.get("offset"),
            clip_format_id
        )

        if spine:
            parent_start_frames = 0
        else:
            parent_start_frames = self._number_of_frames(
                parent.get("start", None),
                parent_format_id
            )

        parent_offset_frames = self._number_of_frames(
            parent.get("offset", None),
            parent_format_id
        )

        clip_offset_frames = (
            (int(clip_offset_frames) - int(parent_start_frames)) +
            int(parent_offset_frames)
        )

        offset = otio.opentime.RationalTime(
            clip_offset_frames,
            self._format_frame_rate(clip_format_id)
        )

        return offset, lane

    def _format_id_for_clip(self, clip):
        if not clip.get("ref", None) or clip.tag == "gap":
            return self.event_format_id

        resource = self._asset_by_id(clip.get("ref"))

        if resource is None:
            resource = self._compound_clip_by_id(
                clip.get("ref")
            ).find("sequence")

        return resource.get("format", self.event_format_id)

    def _reference_from_id(self, asset_id):
        asset = self._asset_by_id(asset_id)
        if not asset.get("src", ""):
            return otio.schema.MissingReference()

        available_range = otio.opentime.TimeRange(
            start_time=to_rational_time(
                asset.get("start"),
                self._format_frame_rate(
                    asset.get("format", self.event_format_id)
                )
            ),
            duration=to_rational_time(
                asset.get("duration"),
                self._format_frame_rate(
                    asset.get("format", self.event_format_id)
                )
            )
        )
        return otio.schema.ExternalReference(
            target_url=asset.get("src"),
            available_range=available_range
        )

    # --------------------
    # time helpers
    # --------------------
    def _format_frame_duration(self, format_id):
        media_format = self._format_by_id(format_id)
        total, rate = media_format.get("frameDuration").split("/")
        rate = rate.replace("s", "")
        return total, rate

    def _format_frame_rate(self, format_id):
        fd_total, fd_rate = self._format_frame_duration(format_id)
        return int(float(fd_rate) / float(fd_total))

    def _number_of_frames(self, time_value, format_id):
        if time_value == "0s" or time_value is None:
            return 0
        fd_total, fd_rate = self._format_frame_duration(format_id)
        time_value = time_value.split("/")

        if len(time_value) > 1:
            time_value_a, time_value_b = time_value
            return int(
                (float(time_value_a) / float(time_value_b.replace("s", ""))) *
                (float(fd_rate) / float(fd_total))
            )

        return int(
            int(time_value[0].replace("s", "")) *
            (float(fd_rate) / float(fd_total))
        )

    def _time_range(self, element, format_id):
        return otio.opentime.TimeRange(
            start_time=to_rational_time(
                element.get("start", "0s"),
                self._format_frame_rate(format_id)
            ),
            duration=to_rational_time(
                element.get("duration"),
                self._format_frame_rate(format_id)
            )
        )
    # --------------------
    # search helpers
    # --------------------

    def _asset_by_id(self, asset_id):
        return self.fcpx_xml.find(
            "./resources/asset[@id='{}']".format(asset_id)
        )

    def _format_by_id(self, format_id):
        return self.fcpx_xml.find(
            "./resources/format[@id='{}']".format(format_id)
        )

    def _compound_clip_by_id(self, compound_id):
        return self.fcpx_xml.find(
            "./resources/media[@id='{}']".format(compound_id)
        )

    # --------------------
    # static methods
    # --------------------
    @staticmethod
    def _track_type(lane_items):
        audio_only_items = [l for l in lane_items if l["audio_only"]]
        if len(audio_only_items) == len(lane_items):
            return otio.schema.TrackKind.Audio
        return otio.schema.TrackKind.Video

    @staticmethod
    def _sorted_items(lane, otio_objects):
        lane_items = [item for item in otio_objects if item["track"] == lane]
        return sorted(lane_items, key=lambda k: k["offset"])

    @staticmethod
    def _sorted_lanes(stack):
        lanes = list(set([o.get("track") for o in stack.get("otio_objects")]))
        lanes.sort()
        return lanes

    @staticmethod
    def _create_stack_dictionary(element):
        if element.tag == "project":
            otio_object = otio.schema.Timeline(name=element.get("name", ""))
        if element.tag == "media":
            otio_object = otio.schema.Stack(name=element.get("name", ""))

        otio_object.metadata["fcpx"] = {"uid": element.get("uid")}
        stackable_dict = element.attrib.copy()
        # Need the duration here has the available_range
        stackable_dict.update(
            {
                "stack": otio_object,
                "otio_objects": [],
                "type": element.tag
            }
        )
        return otio_object, stackable_dict


# --------------------
# adapter requirements
# --------------------
def read_from_string(input_str):
    """
    Necessary read method for otio adapter

    Args:
        input_str (str): An FCP X XML string

    Returns:
        OpenTimeline: An OpenTimeline object
    """

    return FcpxXml(input_str).to_otio()


def write_to_string(input_otio):
    """
    Necessary write method for otio adapter

    Args:
        input_otio (OpenTimeline): An OpenTimeline object

    Returns:
        str: The string contents of an FCP X XML
    """

    return FcpxOtio(input_otio).to_xml()
