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
        self.event_resource = cElementTree.SubElement(
            cElementTree.SubElement(self.fcpx_xml, "library"),
            "event",
            {"name": self.otio_timeline.name}
        )
        self.format_dictionary = {}
        self.resource_dictionary = {}
        self.resource_count = 0

    def to_xml(self):
        """
        Convert an otio to an FCP X XML

        Returns:
            str: FCPX XML content
        """

        self._add_formats()
        self._add_compound_clips()

        projects = self.otio_timeline.each_child(
            descended_from_type=otio.schema.Timeline
        )
        for project in projects:
            top_sequence = self._stack_to_sequence(project.tracks)

            project_element = cElementTree.Element(
                "project",
                {"name": project.name}
            )
            project_element.append(top_sequence)
            self.event_resource.append(project_element)
        xml = cElementTree.tostring(
            self.fcpx_xml,
            encoding="UTF-8",
            method="xml"
        )
        dom = minidom.parseString(xml)
        return dom.toprettyxml(indent="    ")

    def _stack_to_sequence(self, stack, compound_clip=False):

        lane_zero_clips = []
        sequence_element = cElementTree.Element(
            "sequence",
            {
                "duration": self._calculate_rational_number(
                    stack.duration().value,
                    stack.duration().rate
                ),
                "format": str(
                    self.format_dictionary[str(stack.duration().rate)]
                )
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
                lane_id,
                track.kind
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

    def _element_for_item(self, item, track_duration, lane, kind):
        element_tag = ""
        item_dict = {
            "duration": self._calculate_rational_number(
                item.duration().value,
                item.duration().rate
            ),
            "offset": self._calculate_offset(item.duration(), track_duration)
        }

        if item.schema_name() == "Clip":
            asset_id = self._add_asset(item, kind)
            element_tag = "asset-clip"
            item_dict.update({
                "name": item.name,
                "ref": asset_id,
                "start": from_rational_time(item.source_range.start_time)
            })

        if item.schema_name() == "Gap":
            element_tag = "gap"
            item_dict.update({
                "name": "Gap",
                "start": from_rational_time(item.source_range.start_time)
            })

        if item.schema_name() == "Stack":
            asset_id = self.resource_dictionary[item.name]
            element_tag = "ref-clip"
            item_dict.update(
                {
                    "name": self._compound_clip_name(item, asset_id),
                    "ref": asset_id
                }
            )

        if lane:
            item_dict.update({"lane": str(lane)})

        if element_tag:
            return cElementTree.Element(element_tag, item_dict)
        return None

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
        if str(clip.duration().rate) in self.format_dictionary:
            return

        format_dict = {
            "id": self._resource_id_generator(),
            "frameDuration": self._framerate_to_frame_duration(
                clip.duration().rate
            ),
            "name": self._clip_format_name(clip)
        }

        cElementTree.SubElement(self.resource_element, "format", format_dict)
        self.format_dictionary[str(clip.duration().rate)] = format_dict["id"]

    def _add_formats(self):
        timelines = self.otio_timeline.each_child(
            descended_from_type=otio.schema.Timeline
        )
        for timeline in timelines:
            for track in timeline.video_tracks():
                for clip in track.each_clip():
                    self._add_format(clip)

            for track in timeline.audio_tracks():
                for clip in track.each_clip():
                    self._add_format(clip)

    def _add_asset(self, clip, kind):
        self._add_format(clip)
        target_url = self._target_url_from_clip(clip)
        if target_url not in self.resource_dictionary:
            resource_id = self._resource_id_generator()
            self.resource_dictionary[target_url] = resource_id
            format_id = str(self.format_dictionary[str(clip.duration().rate)])
            duration = self._find_asset_duration(clip)
            has_audio = "0"
            has_video = "0"
            if kind == otio.schema.TrackKind.Audio:
                has_audio = "1"
            if kind == otio.schema.TrackKind.Video:
                has_video = "1"

            cElementTree.SubElement(
                self.resource_element,
                "asset",
                {
                    "name": clip.name,
                    "src": target_url,
                    "format": format_id,
                    "id": resource_id,
                    "duration": duration,
                    "start": self._find_asset_start(clip),
                    "hasAudio": has_audio,
                    "hasVideo": has_video
                }
            )
            cElementTree.SubElement(
                self.event_resource,
                "asset-clip",
                {
                    "name": clip.name,
                    "format": format_id,
                    "ref": resource_id,
                    "duration": duration
                }
            )
            return resource_id

        return self.resource_dictionary[target_url]

    def _add_compound_clip(self, item):
        resource_id = self._resource_id_generator()
        self.resource_dictionary[item.name] = resource_id
        media_element = cElementTree.SubElement(
            self.resource_element,
            "media",
            {
                "name": self._compound_clip_name(item, resource_id),
                "id": resource_id
            }
        )
        media_element.append(self._stack_to_sequence(item, compound_clip=True))

    def _compound_clip_name(self, compound_clip, resource_id):
        if compound_clip.name:
            return compound_clip.name
        return "compound_clip_{}".format(resource_id)

    def _add_compound_clips(self):
        for stack in self._stacks():
            self._add_compound_clip(stack)

    def _stacks(self):
        return [
            item for item in self.otio_timeline.each_child()
            if item.schema_name() == "Stack"
        ]

    def _resource_id_generator(self):
        self.resource_count += 1
        return "r{}".format(self.resource_count)

    def _event_name(self):
        if self.otio_timeline.name:
            return self.otio_timeline.name
        return date.strftime(date.today(), "%m-%e-%y")

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


class FcpxXml(object):
    """
    This object is responsible for knowing how to convert an FCP X XML
    otio into an otio timeline
    """

    def __init__(self, xml_string):
        self.fcpx_xml = cElementTree.fromstring(xml_string)
        self.event_format_id = ""

    def to_otio(self):
        """
        Convert an FCP X XML to an otio

        Returns:
            OpenTimeline: An OpenTimeline Timeline object
        """

        event = self.fcpx_xml.find("./library/event")
        container = otio.schema.SerializableCollection(
            name=event.get("name", "")
        )
        projects = event.findall("./project")
        if not projects:
            raise ValueError("No top-level timelines found")

        for project in projects:
            sequence = project.find("./sequence")
            timeline = otio.schema.Timeline(name=project.get("name"))
            self.event_format_id = sequence.get("format")
            for track in self._stack_from_sequence(sequence):
                timeline.tracks.append(track)
            container.append(timeline)
        return container

    def _audio_only(self, clips):
        if not clips:
            return False

        for clip in clips:
            asset = self._asset_by_id(clip["item"].get("ref", None))

            if asset is None:
                return False

            if asset.get("hasVideo", "0") == "1":
                return False

        return True

    def _build_track_from_lane(self, lane, clips):
        track = otio.schema.Track(name=lane)

        if self._audio_only(clips):
            track.kind = otio.schema.TrackKind.Audio

        for clip in clips:
            otio_clip = self._create_otio_composable(clip["item"])
            clip_offset = self._clip_offset(clip["item"], clip["parent"])
            if clip_offset.value > track.duration().value:

                track.append(
                    self._create_otio_gap_with_frames(
                        0,
                        (clip_offset.value - track.duration().value)
                    )
                )

            track.append(otio_clip)
        return track

    def _create_otio_composable(self, composable):
        if composable.tag == "asset-clip":
            return self._create_otio_clip(composable)
        if composable.tag == "ref-clip":
            return self._stack_from_compund_clip(composable.get("ref"))
        if composable.tag == "gap":
            return self._create_otio_gap(
                composable.get("start"),
                composable.get("duration")
            )

    def _create_otio_clip(self, clip):
        asset = self._asset_by_id(clip.get("ref"))
        source_range = otio.opentime.TimeRange(
            start_time=to_rational_time(
                clip.get("start"),
                self._format_frame_rate(
                    asset.get("format", self.event_format_id)
                )
            ),
            duration=to_rational_time(
                clip.get("duration"),
                self._format_frame_rate(
                    asset.get("format", self.event_format_id)
                )
            )
        )

        return otio.schema.Clip(
            name=clip.get("name"),
            media_reference=self._reference_from_id(clip.get("ref")),
            source_range=source_range
        )

    def _create_otio_gap(self, start, duration):
        source_range = otio.opentime.TimeRange(
            start_time=to_rational_time(
                start,
                self._format_frame_rate(self.event_format_id)
            ),
            duration=to_rational_time(
                duration,
                self._format_frame_rate(self.event_format_id)
            )
        )
        return otio.schema.Gap(source_range=source_range)

    def _create_otio_gap_with_frames(self, start, duration):
        source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(
                start,
                self._format_frame_rate(self.event_format_id)
            ),
            duration=otio.opentime.RationalTime(
                duration,
                self._format_frame_rate(self.event_format_id)
            )
        )
        return otio.schema.Gap(source_range=source_range)

    def _items_by_lane(self, element):
        items = {}
        for item in list(element):
            items.setdefault(
                item.get("lane", "0"), []
            ).append({"item": item, "parent": element})
            subitems = self._items_by_lane(item)
            for k, v in subitems.items():
                items.setdefault(k, []).extend(v)
        return items

    def _stack_from_sequence(self, sequence):
        lanes = self._items_by_lane(sequence.find("spine"))
        tracks = []
        for lane in sorted(lanes.keys()):
            tracks.append(self._build_track_from_lane(lane, lanes[lane]))
        return tracks

    def _stack_from_compund_clip(self, compound_id):
        compound_clip_element = self._compound_clip_by_id(compound_id)
        stack = otio.schema.Stack(name=compound_clip_element.get("name", ""))
        stack.extend(
            self._stack_from_sequence(compound_clip_element.find("sequence"))
        )
        return stack

    def _clip_offset(self, clip, parent):

        if clip.tag == "gap":
            return to_rational_time(
                clip.get("offset"),
                self._format_frame_rate(self.event_format_id)
            )

        format_id = self._format_id_for_clip(clip)
        clip_offset_frames = self._number_of_frames(
            clip.get("offset"),
            self._format_id_for_clip(clip)
        )
        offset = to_rational_time(
            clip.get("offset"),
            self._format_frame_rate(format_id)
        )

        if parent and parent.get("start", ""):
            parent_format_id = self._format_id_for_clip(parent)
            parent_start_frames = self._number_of_frames(
                parent.get("start"),
                parent_format_id
            )
            parent_offset_frames = self._number_of_frames(
                parent.get("offset"),
                parent_format_id
            )
            clip_offset_frames = (
                (int(clip_offset_frames) - int(parent_start_frames)) +
                int(parent_offset_frames)
            )

            offset = otio.opentime.RationalTime(
                clip_offset_frames,
                self._format_frame_rate(format_id)
            )

        return offset

    def _format_id_for_clip(self, clip):
        if clip.tag == "gap":
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
