# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OpenTimelineIO Final Cut Pro X XML Adapter. """
import os
import subprocess
from xml.etree import cElementTree
from xml.dom import minidom
from fractions import Fraction
from datetime import date
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
        ).decode("utf-8")
    except (subprocess.CalledProcessError, OSError):
        frame_size = ""

    if not frame_size:
        return ""

    frame_size = frame_size.rstrip()

    if "1920" in frame_size:
        frame_size = "1080"

    if frame_size.endswith("1280"):
        frame_size = "720"

    return f"FFVideoFormat{frame_size}p{frame_rate}"


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
        return f"{result.numerator}s"
    return f"{result.numerator}/{result.denominator}s"


class FcpxOtio:
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
        if self.otio_timeline.schema_name() == "Timeline":
            self.timelines = [self.otio_timeline]
        else:
            self.timelines = list(
                self.otio_timeline.children_if(
                    descended_from_type=otio.schema.Timeline
                )
            )

        if len(self.timelines) > 1:
            self.event_resource = cElementTree.SubElement(
                self.fcpx_xml,
                "event",
                {"name": self._event_name()}
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
            for clip in self._clips():
                if not clip.parent():
                    self._add_asset(clip)

            for stack in self._stacks():
                ref_element = self._element_for_item(
                    stack,
                    None,
                    ref_only=True,
                    compound=True
                )
                self.event_resource.append(ref_element)
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
        format_element = self._find_or_create_format_from(stack)
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
            self._track_for_spine(track, idx, spine, compound_clip)

        for idx, track in enumerate(audio_tracks):
            lane_id = -(idx + 1)
            self._track_for_spine(track, lane_id, spine, compound_clip)
        return sequence_element

    def _track_for_spine(self, track, lane_id, spine, compound):
        for child in self._lanable_items(track.children_if()):
            if self._item_in_compound_clip(child) and not compound:
                continue
            child_element = self._element_for_item(
                child,
                lane_id,
                compound=compound
            )
            if not lane_id:
                spine.append(child_element)
                continue
            if child.schema_name() == "Gap":
                continue

            parent_element = self._find_parent_element(
                spine,
                track.trimmed_range_of_child(child).start_time,
                self._find_or_create_format_from(track).get("id")
            )
            offset = self._offset_based_on_parent(
                child_element,
                parent_element,
                self._find_or_create_format_from(track).get("id")
            )
            child_element.set(
                "offset",
                from_rational_time(offset)
            )

            parent_element.append(child_element)
        return []

    def _find_parent_element(self, spine, trimmed_range, format_id):
        for item in spine.iter():
            if item.tag not in ("clip", "asset-clip", "gap", "ref-clip"):
                continue
            if item.get("lane") is not None:
                continue
            if item.tag == "gap" and item.find("./audio") is not None:
                continue
            offset = to_rational_time(
                item.get("offset"),
                self._frame_rate_from_element(item, format_id)
            )
            duration = to_rational_time(
                item.get("duration"),
                self._frame_rate_from_element(item, format_id)
            )
            total_time = offset + duration
            if offset > trimmed_range:
                continue
            if total_time > trimmed_range:
                return item
        return None

    def _offset_based_on_parent(self, child, parent, default_format_id):
        parent_offset = to_rational_time(
            parent.get("offset"),
            self._frame_rate_from_element(parent, default_format_id)
        )
        child_offset = to_rational_time(
            child.get("offset"),
            self._frame_rate_from_element(child, default_format_id)
        )

        parent_start = to_rational_time(
            parent.get("start"),
            self._frame_rate_from_element(parent, default_format_id)
        )
        return (child_offset - parent_offset) + parent_start

    def _frame_rate_from_element(self, element, default_format_id):
        if element.tag == "gap":
            format_id = default_format_id

        if element.tag == "ref-clip":
            media_element = self._media_by_id(element.get("ref"))
            asset = media_element.find("./sequence")
            format_id = asset.get("format")

        if element.tag == "clip":
            if element.find("./gap") is not None:
                asset_id = element.find("./gap").find("./audio").get("ref")
            else:
                asset_id = element.find("./video").get("ref")
            asset = self._asset_by_id(asset_id)
            format_id = asset.get("format")

        if element.tag == "asset-clip":
            asset = self._asset_by_id(element.get("ref"))
            format_id = asset.get("format")

        format_element = self.resource_element.find(
            f"./format[@id='{format_id}']"
        )
        total, rate = format_element.get("frameDuration").split("/")
        rate = rate.replace("s", "")
        return int(float(rate) / float(total))

    def _element_for_item(self, item, lane, ref_only=False, compound=False):
        element = None
        duration = self._calculate_rational_number(
            item.duration().value,
            item.duration().rate
        )
        if item.schema_name() == "Clip":
            asset_id = self._add_asset(item, compound_only=compound)
            element = self._element_for_clip(item, asset_id, duration, lane)

        if item.schema_name() == "Gap":
            element = self._element_for_gap(item, duration)

        if item.schema_name() == "Stack":
            element = self._element_for_stack(item, duration, ref_only)

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

    def _element_for_clip(self, item, asset_id, duration, lane):
        element = cElementTree.Element(
            "clip",
            {
                "name": item.name,
                "offset": from_rational_time(
                    item.trimmed_range_in_parent().start_time
                ),
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
        return element

    def _element_for_gap(self, item, duration):
        element = cElementTree.Element(
            "gap",
            {
                "name": "Gap",
                "duration": duration,
                "offset": from_rational_time(
                    item.trimmed_range_in_parent().start_time
                ),
                "start": "3600s"
            }
        )
        return element

    def _element_for_stack(self, item, duration, ref_only):
        media_element = self._add_compound_clip(item)
        asset_id = media_element.get("id")
        element = cElementTree.Element(
            "ref-clip",
            {
                "name": item.name,
                "duration": duration,
                "ref": str(asset_id)
            }
        )
        if not ref_only:
            element.set(
                "offset",
                from_rational_time(
                    item.trimmed_range_in_parent().start_time
                )
            )
            element.set(
                "start",
                from_rational_time(item.source_range.start_time)
            )
        if item.parent() and item.parent().kind == otio.schema.TrackKind.Audio:
            element.set("srcEnable", "audio")
        return element

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

    def _clip_format_name(self, clip):
        if clip.schema_name() in ("Stack", "Track"):
            return ""
        if not clip.media_reference:
            return ""

        if clip.media_reference.is_missing_reference:
            return ""

        return format_name(
            clip.duration().rate,
            clip.media_reference.target_url
        )

    def _find_or_create_format_from(self, clip):
        frame_duration = self._framerate_to_frame_duration(
            clip.duration().rate
        )
        format_element = self._format_by_frame_rate(clip.duration().rate)
        if format_element is None:
            format_element = cElementTree.SubElement(
                self.resource_element,
                "format",
                {
                    "id": self._resource_id_generator(),
                    "frameDuration": frame_duration,
                    "name": self._clip_format_name(clip)
                }
            )
        if format_element.get("name", "") == "":
            format_element.set("name", self._clip_format_name(clip))
        return format_element

    def _add_asset(self, clip, compound_only=False):
        format_element = self._find_or_create_format_from(clip)
        asset = self._create_asset_element(clip, format_element)

        if not compound_only and not self._asset_clip_by_name(clip.name):
            self._create_asset_clip_element(
                clip,
                format_element,
                asset.get("id")
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

    def _create_asset_clip_element(self, clip, format_element, resource_id):
        duration = self._find_asset_duration(clip)
        a_clip = cElementTree.SubElement(
            self.event_resource,
            "asset-clip",
            {
                "name": clip.name,
                "format": format_element.get("id"),
                "ref": resource_id,
                "duration": duration
            }
        )
        if clip.media_reference and not clip.media_reference.is_missing_reference:
            fcpx_metadata = clip.media_reference.metadata.get("fcpx", {})
            note_element = self._create_note_element(
                fcpx_metadata.get("note", None)
            )
            keyword_elements = self._create_keyword_elements(
                fcpx_metadata.get("keywords", [])
            )
            metadata_element = self._create_metadata_elements(
                fcpx_metadata.get("metadata", None)
            )

            if note_element is not None:
                a_clip.append(note_element)
            if keyword_elements:
                for keyword_element in keyword_elements:
                    a_clip.append(keyword_element)
            if metadata_element is not None:
                a_clip.append(metadata_element)

    def _create_asset_element(self, clip, format_element):
        target_url = self._target_url_from_clip(clip)
        asset = self._asset_by_path(target_url)
        if asset is not None:
            return asset

        asset = cElementTree.SubElement(
            self.resource_element,
            "asset",
            {
                "name": clip.name,
                "src": target_url,
                "format": format_element.get("id"),
                "id": self._resource_id_generator(),
                "duration": self._find_asset_duration(clip),
                "start": self._find_asset_start(clip),
                "hasAudio": "0",
                "hasVideo": "0"
            }
        )
        return asset

    def _add_compound_clip(self, item):
        media_element = self._media_by_name(item.name)
        if media_element is not None:
            return media_element
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
        media_element.append(self._stack_to_sequence(item, compound_clip=True))
        return media_element

    def _stacks(self):
        return self.otio_timeline.children_if(
            descended_from_type=otio.schema.Stack
        )

    def _clips(self):
        return self.otio_timeline.children_if(
            descended_from_type=otio.schema.Clip
        )

    def _resource_id_generator(self):
        self.resource_count += 1
        return f"r{self.resource_count}"

    def _event_name(self):
        if self.otio_timeline.name:
            return self.otio_timeline.name
        return date.strftime(date.today(), "%m-%e-%y")

    def _asset_by_path(self, path):
        return self.resource_element.find(f"./asset[@src='{path}']")

    def _asset_by_id(self, asset_id):
        return self.resource_element.find(f"./asset[@id='{asset_id}']")

    def _media_by_name(self, name):
        return self.resource_element.find(f"./media[@name='{name}']")

    def _media_by_id(self, media_id):
        return self.resource_element.find(f"./media[@id='{media_id}']")

    def _format_by_frame_rate(self, frame_rate):
        frame_duration = self._framerate_to_frame_duration(frame_rate)
        return self.resource_element.find(
            f"./format[@frameDuration='{frame_duration}']"
        )

    def _asset_clip_by_name(self, name):
        return self.event_resource.find(
            f"./asset-clip[@name='{name}']"
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
        return f"file:///tmp/{clip.name}"

    @staticmethod
    def _calculate_rational_number(duration, rate):
        if int(duration) == 0:
            return "0s"
        result = Fraction(float(duration) / float(rate)).limit_denominator()
        return f"{result.numerator}/{result.denominator}s"

    @staticmethod
    def _compound_clip_name(compound_clip, resource_id):
        if compound_clip.name:
            return compound_clip.name
        return f"compound_clip_{resource_id}"

    @staticmethod
    def _item_in_compound_clip(item):
        stack_count = 0
        parent = item.parent()
        while parent is not None:
            if parent.schema_name() == "Stack":
                stack_count += 1
            parent = parent.parent()
        return stack_count > 1

    @staticmethod
    def _create_metadata_elements(metadata):
        if metadata is None:
            return None
        metadata_element = cElementTree.Element(
            "metadata"
        )
        for metadata_dict in metadata:
            cElementTree.SubElement(
                metadata_element,
                "md",
                {
                    "key": list(metadata_dict.keys())[0],
                    "value": list(metadata_dict.values())[0]
                }
            )
        return metadata_element

    @staticmethod
    def _create_keyword_elements(keywords):
        keyword_elements = []
        for keyword_dict in keywords:
            keyword_elements.append(
                cElementTree.Element(
                    "keyword",
                    dict(keyword_dict)
                )
            )
        return keyword_elements

    @staticmethod
    def _create_note_element(note):
        if not note:
            return None
        note_element = cElementTree.Element(
            "note"
        )
        note_element.text = note
        return note_element


class FcpxXml:
    """
    This object is responsible for knowing how to convert an FCP X XML
    otio into an otio timeline
    """

    def __init__(self, xml_string):
        self.fcpx_xml = cElementTree.fromstring(xml_string)
        self.child_parent_map = {c: p for p in self.fcpx_xml.iter() for c in p}

    def to_otio(self):
        """
        Convert an FCP X XML to an otio

        Returns:
            OpenTimeline: An OpenTimeline Timeline object
        """

        if self.fcpx_xml.find("./library") is not None:
            return self._from_library()
        if self.fcpx_xml.find("./event") is not None:
            return self._from_event(self.fcpx_xml.find("./event"))
        if self.fcpx_xml.find("./project") is not None:
            return self._from_project(self.fcpx_xml.find("./project"))
        if ((self.fcpx_xml.find("./asset-clip") is not None) or
                (self.fcpx_xml.find("./ref-clip") is not None)):
            return self._from_clips()

    def _from_library(self):
        # We are just grabbing the first even in the project for now
        return self._from_event(self.fcpx_xml.find("./library/event"))

    def _from_event(self, event_element):
        container = otio.schema.SerializableCollection(
            name=event_element.get("name")
        )
        for project in event_element.findall("./project"):
            container.append(self._from_project(project))
        return container

    def _from_project(self, project_element):
        timeline = otio.schema.Timeline(name=project_element.get("name", ""))
        timeline.tracks = self._squence_to_stack(
            project_element.find("./sequence", {})
        )
        return timeline

    def _from_clips(self):
        container = otio.schema.SerializableCollection()
        if self.fcpx_xml.find("./asset-clip") is not None:
            for asset_clip in self.fcpx_xml.findall("./asset-clip"):
                container.append(
                    self._build_composable(
                        asset_clip,
                        asset_clip.get("format")
                    )
                )

        if self.fcpx_xml.find("./ref-clip") is not None:
            for ref_clip in self.fcpx_xml.findall("./ref-clip"):
                container.append(
                    self._build_composable(
                        ref_clip,
                        "r1"
                    )
                )
        return container

    def _squence_to_stack(self, sequence_element, name="", source_range=None):
        timeline_items = []
        lanes = []
        stack = otio.schema.Stack(name=name, source_range=source_range)
        for element in sequence_element.iter():
            if element.tag not in COMPOSABLE_ELEMENTS:
                continue
            composable = self._build_composable(
                element,
                sequence_element.get("format")
            )

            offset, lane = self._offset_and_lane(
                element,
                sequence_element.get("format")
            )

            timeline_items.append(
                {
                    "track": lane,
                    "offset": offset,
                    "composable": composable,
                    "audio_only": self._audio_only(element)
                }
            )

            lanes.append(lane)
        sorted_lanes = list(set(lanes))
        sorted_lanes.sort()
        for lane in sorted_lanes:
            sorted_items = self._sorted_items(lane, timeline_items)
            track = otio.schema.Track(
                name=lane,
                kind=self._track_type(sorted_items)
            )

            for item in sorted_items:
                frame_diff = (
                    int(item["offset"].value) - track.duration().value
                )
                if frame_diff > 0:
                    track.append(
                        self._create_gap(
                            0,
                            frame_diff,
                            sequence_element.get("format")
                        )
                    )
                track.append(item["composable"])
            stack.append(track)
        return stack

    def _build_composable(self, element, default_format):
        timing_clip = self._timing_clip(element)
        source_range = self._time_range(
            timing_clip,
            self._format_id_for_clip(element, default_format)
        )

        if element.tag != "ref-clip":
            otio_composable = otio.schema.Clip(
                name=timing_clip.get("name"),
                media_reference=self._reference_from_id(
                    element.get("ref"),
                    default_format
                ),
                source_range=source_range
            )
        else:
            media_element = self._compound_clip_by_id(element.get("ref"))
            otio_composable = self._squence_to_stack(
                media_element.find("./sequence"),
                name=media_element.get("name"),
                source_range=source_range
            )

        for marker in timing_clip.findall(".//marker"):
            otio_composable.markers.append(
                self._marker(marker, default_format)
            )

        return otio_composable

    def _marker(self, element, default_format):
        if element.get("completed", None) and element.get("completed") == "1":
            color = otio.schema.MarkerColor.GREEN
        if element.get("completed", None) and element.get("completed") == "0":
            color = otio.schema.MarkerColor.RED
        if not element.get("completed", None):
            color = otio.schema.MarkerColor.PURPLE

        otio_marker = otio.schema.Marker(
            name=element.get("value", ""),
            marked_range=self._time_range(element, default_format),
            color=color
        )
        return otio_marker

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

    def _create_gap(self, start_frame, number_of_frames, defualt_format):
        fps = self._format_frame_rate(defualt_format)
        source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(start_frame, fps),
            duration=otio.opentime.RationalTime(number_of_frames, fps)
        )
        return otio.schema.Gap(source_range=source_range)

    def _timing_clip(self, clip):
        while clip.tag not in ("clip", "asset-clip", "ref-clip"):
            clip = self.child_parent_map.get(clip)
        return clip

    def _offset_and_lane(self, clip, default_format):
        clip_format_id = self._format_id_for_clip(clip, default_format)
        clip = self._timing_clip(clip)
        parent = self.child_parent_map.get(clip)

        parent_format_id = self._format_id_for_clip(parent, default_format)

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

    def _format_id_for_clip(self, clip, default_format):
        if not clip.get("ref", None) or clip.tag == "gap":
            return default_format

        resource = self._asset_by_id(clip.get("ref"))

        if resource is None:
            resource = self._compound_clip_by_id(
                clip.get("ref")
            ).find("sequence")

        return resource.get("format", default_format)

    def _reference_from_id(self, asset_id, default_format):
        asset = self._asset_by_id(asset_id)
        if not asset.get("src", ""):
            return otio.schema.MissingReference()

        available_range = otio.opentime.TimeRange(
            start_time=to_rational_time(
                asset.get("start"),
                self._format_frame_rate(
                    asset.get("format", default_format)
                )
            ),
            duration=to_rational_time(
                asset.get("duration"),
                self._format_frame_rate(
                    asset.get("format", default_format)
                )
            )
        )
        asset_clip = self._assetclip_by_ref(asset_id)
        metadata = {}
        if asset_clip:
            metadata = self._create_metadta(asset_clip)
        return otio.schema.ExternalReference(
            target_url=asset.get("src"),
            available_range=available_range,
            metadata={"fcpx": metadata}
        )

    def _create_metadta(self, item):
        metadata = {}
        for element in item.iter():
            if element.tag == "md":
                metadata.setdefault("metadata", []).append(
                    {element.attrib.get("key"): element.attrib.get("value")}
                )
                # metadata.update(
                #     {element.attrib.get("key"): element.attrib.get("value")}
                # )
            if element.tag == "note":
                metadata.update({"note": element.text})
            if element.tag == "keyword":
                metadata.setdefault("keywords", []).append(element.attrib)
        return metadata

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
            f"./resources/asset[@id='{asset_id}']"
        )

    def _assetclip_by_ref(self, asset_id):
        event = self.fcpx_xml.find("./event")
        if event is None:
            return self.fcpx_xml.find(f"./asset-clip[@ref='{asset_id}']")
        else:
            return event.find(f"./asset-clip[@ref='{asset_id}']")

    def _format_by_id(self, format_id):
        return self.fcpx_xml.find(
            f"./resources/format[@id='{format_id}']"
        )

    def _compound_clip_by_id(self, compound_id):
        return self.fcpx_xml.find(
            f"./resources/media[@id='{compound_id}']"
        )

    # --------------------
    # static methods
    # --------------------
    @staticmethod
    def _track_type(lane_items):
        audio_only_items = [item for item in lane_items if item["audio_only"]]
        if len(audio_only_items) == len(lane_items):
            return otio.schema.TrackKind.Audio
        return otio.schema.TrackKind.Video

    @staticmethod
    def _sorted_items(lane, otio_objects):
        lane_items = [item for item in otio_objects if item["track"] == lane]
        return sorted(lane_items, key=lambda k: k["offset"])


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
