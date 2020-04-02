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

"""OpenTimelineIO GStreamer Editing Services XML Adapter. """
import re
import warnings
import numbers
from fractions import Fraction
from xml.etree import ElementTree
from xml.dom import minidom
import itertools
import opentimelineio as otio

META_NAMESPACE = "XGES"


FRAMERATE_FRAMEDURATION = {23.98: "24000/1001",
                           24: "600/25",
                           25: "25/1",
                           29.97: "30000/1001",
                           30: "30/1",
                           50: "50/1",
                           59.94: "60000/1001",
                           60: "60/1"}


TRANSITION_MAP = {
    "crossfade": otio.schema.TransitionTypes.SMPTE_Dissolve
}
# Two way map
TRANSITION_MAP.update(dict([(v, k) for k, v in TRANSITION_MAP.items()]))


class XGESReadError(otio.exceptions.OTIOError):
    """An incorrectly formatted xges string"""


class UnhandledValueError(otio.exceptions.OTIOError):
    """Received value is not handled"""
    def __init__(self, name, value):
        otio.exceptions.OTIOError.__init__(
            self, "Unhandled value {!s} for {}.".format(value, name))


class InvalidValueError(otio.exceptions.OTIOError):
    """Received value is invalid"""
    def __init__(self, name, value, expect):
        otio.exceptions.OTIOError.__init__(
            self, "Invalid value {!s} for {}. Expect {}.".format(
                value, name, expect))


class UnhandledOtioError(otio.exceptions.OTIOError):
    """Received otio object is not handled"""
    def __init__(self, otio_obj):
        otio.exceptions.OTIOError.__init__(
            self, "Unhandled otio schema {}.".format(
                otio_obj.schema_name()))


def show_ignore(msg):
    """Tell user we found an error, but we are ignoring it."""
    warnings.warn(msg + ".\nIGNORING.", stacklevel=2)


def show_otio_not_supported(otio_obj, effect):
    """Tell user that we do not properly support an otio type"""
    warnings.warn(
        "The schema {} is not currently supported.\n{}.".format(
            otio_obj.schema_name(), effect),
        stacklevel=2)


class GESTrackType:
    UNKNOWN = 1 << 0
    AUDIO = 1 << 1
    VIDEO = 1 << 2
    TEXT = 1 << 3
    CUSTOM = 1 << 4
    ALL_TYPES = (UNKNOWN, AUDIO, VIDEO, TEXT, CUSTOM)

    @staticmethod
    def to_otio_kind(track_type):
        if track_type == GESTrackType.AUDIO:
            return otio.schema.TrackKind.Audio
        elif track_type == GESTrackType.VIDEO:
            return otio.schema.TrackKind.Video
        raise UnhandledValueError("track_type", track_type)

    @staticmethod
    def from_otio_kind(*otio_kinds):
        track_type = 0
        for kind in otio_kinds:
            if kind == otio.schema.TrackKind.Audio:
                track_type |= GESTrackType.AUDIO
            elif kind == otio.schema.TrackKind.Video:
                track_type |= GESTrackType.VIDEO
            else:
                raise UnhandledValueError("track kind", kind)
        return track_type


GST_SECOND = 1000000000


class XGES:
    """
    This object is responsible for converting an xGES project into an
    otio timeline.
    """

    def __init__(self, ges_obj):
        """
        ges_obj should be the root of the xges xml tree (called 'ges').
        If it is not an ElementTree.Element it will first be parsed as
        a string to ElementTree.
        """
        if not isinstance(ges_obj, ElementTree.Element):
            ges_obj = ElementTree.fromstring(ges_obj)
        if ges_obj.tag != "ges":
            raise XGESReadError(
                "The root element for the received xml is tagged as "
                "{} rather than the expected 'ges' for xges".format(
                    ges_obj.tag))
        self.ges_xml = ges_obj
        self.rate = 25.0

    @staticmethod
    def _findall(xmlelement, path):
        found = xmlelement.findall(path)
        if found is None:
            return []
        return found

    def _findonly(self, xmlelement, path, allow_none=False):
        found = self._findall(xmlelement, path)
        if allow_none and not found:
            return None
        if len(found) != 1:
            raise XGESReadError(
                "Found {:d} xml elements under the path {} when only "
                "one was expected.".format(len(found), path))
        return found[0]

    @staticmethod
    def _get_attrib(xmlelement, key, expect_type):
        val = xmlelement.get(key)
        if val is None:
            raise XGESReadError(
                "The xges {} element is missing the {} "
                "attribute.".format(xmlelement.tag, key))
        try:
            val = expect_type(val)
        except (ValueError, TypeError):
            raise XGESReadError(
                "The xges {} element '{}' attribute has the value {}, "
                "which is not of the expected {} type.".format(
                    xmlelement.tag, key, val, expect_type.__name__))
        return val

    @staticmethod
    def _get_structure(xmlelement, struct_name):
        read_props = xmlelement.get(struct_name, struct_name)
        try:
            return GstStructure(read_props)
        except ValueError as err:
            show_ignore(
                "The {} attribute of {} could not be read as a "
                "GstStructure:\n{!s}".format(
                    struct_name, xmlelement.tag, err))
        return GstStructure(struct_name)

    @classmethod
    def _get_properties(cls, xmlelement):
        return cls._get_structure(xmlelement, "properties")

    @classmethod
    def _get_metadatas(cls, xmlelement):
        return cls._get_structure(xmlelement, "metadatas")

    @staticmethod
    def _get_from_structure(structure, fieldname, expect_type, default):
        field = structure.fields.get(fieldname)
        if field is None:
            return default
        typ, val = field
        if typ != expect_type:
            show_ignore(
                "The field {} had the type {} rather than the expected "
                "type {}".format(fieldname, typ, expect_type))
            return default
        return val

    def _get_from_properties(
            self, xmlelement, fieldname, expect_type, default=None):
        structure = self._get_properties(xmlelement)
        return self._get_from_structure(
            structure, fieldname, expect_type, default)

    def _get_from_metadatas(
            self, xmlelement, fieldname, expect_type, default=None):
        structure = self._get_metadatas(xmlelement)
        return self._get_from_structure(
            structure, fieldname, expect_type, default)

    @staticmethod
    def _get_from_caps(caps, fieldname, structname=None, default=None):
        """
        Return the value for the first fieldname that matches.
        If structname is given, then only search in structures who's
        name matches
        """
        # restriction-caps is in general a *collection* of GstStructures
        # along with corresponding features in the format:
        #   "struct-name-nums(feature), "
        #   "field1=(type1)val1, field2=(type2)val2; "
        #   "struct-name-alphas(feature), "
        #   "fieldA=(typeA)valA, fieldB=(typeB)valB"
        # Note the lack of ';' for the last structure, and the
        # '(feature)' is optional.
        #
        # Also note that gst_caps_from_string will also accept:
        #   "struct-name(feature"
        # without the final ')', but this must be the end of the string,
        # which is why we have included (\)|$) at the end of
        # CAPS_NAME_FEATURES_REGEX, i.e. match a closing ')' or the end.
        if caps in ("ANY", "EMPTY", "NONE"):
            return default
        CAPS_NAME_FEATURES_REGEX = re.compile(
            GstStructure.ASCII_SPACES + GstStructure.NAME_FORMAT
            + r"(\([^)]*(\)|$))?" + GstStructure.END_FORMAT)
        while caps:
            match = CAPS_NAME_FEATURES_REGEX.match(caps)
            if match is None:
                raise XGESReadError(
                    "The structure name in the caps ({}) is not of "
                    "the correct format".format(caps))
            caps = caps[match.end("end"):]
            try:
                with warnings.catch_warnings():
                    # unknown types may raise a warning. This will
                    # usually be irrelevant since we are searching for
                    # a specific field
                    fields, caps = GstStructure._parse_fields(caps)
            except ValueError as err:
                show_ignore(
                    "Failed to read the fields in the caps ({}):\n\t"
                    "{!s}".format(caps, err))
                continue
            if structname is not None:
                if match.group("name") != structname:
                    continue
            # use below method rather than fields.get(fieldname) to
            # allow us to want any value back, including None
            for key in fields:
                if key == fieldname:
                    return fields[key][1]
        return default

    def _set_rate_from_timeline(self, timeline):
        video_track = timeline.find("./track[@track-type='4']")
        if video_track is None:
            return
        res_caps = self._get_from_properties(
            video_track, "restriction-caps", "string")
        if res_caps is None:
            return
        rate = self._get_from_caps(res_caps, "framerate")
        if rate is None:
            return
        try:
            rate = Fraction(rate)
        except (ValueError, TypeError):
            show_ignore("Read a framerate that is not a fraction")
        else:
            self.rate = float(rate)

    def to_rational_time(self, ns_timestamp):
        """
        This converts a GstClockTime value to an otio RationalTime object

        Args:
            ns_timestamp (int): This is a GstClockTime value (nanosecond absolute value)

        Returns:
            RationalTime: A RationalTime object
        """
        return otio.opentime.RationalTime(
            (float(ns_timestamp) * self.rate) / float(GST_SECOND),
            self.rate
        )

    def _add_to_otio_metadata(self, otio_obj, key, val):
        xges_dict = otio_obj.metadata.get(META_NAMESPACE)
        if xges_dict is None:
            otio_obj.metadata[META_NAMESPACE] = {}
            xges_dict = otio_obj.metadata[META_NAMESPACE]
        xges_dict[key] = val

    def _add_properties_and_metadatas_to_otio(
            self, otio_obj, element, sub_key=None):
        xges_dict = otio_obj.metadata.get(META_NAMESPACE)
        if xges_dict is None:
            otio_obj.metadata[META_NAMESPACE] = {}
            xges_dict = otio_obj.metadata[META_NAMESPACE]
        if sub_key is not None:
            xges_dict[sub_key] = {}
            xges_dict = xges_dict[sub_key]
        xges_dict["properties"] = self._get_properties(element)
        xges_dict["metadatas"] = self._get_metadatas(element)

    def to_otio(self):
        """
        Convert an xges to an otio

        Returns:
            OpenTimeline: An OpenTimeline Timeline object
        """
        otio_timeline = otio.schema.Timeline()
        project = self._fill_otio_stack_from_ges(otio_timeline.tracks)
        otio_timeline.name = self._get_from_metadatas(
            project, "name", "string", "")
        return otio_timeline

    def _fill_otio_stack_from_ges(self, otio_stack):
        project = self._findonly(self.ges_xml, "./project")
        timeline = self._findonly(project, "./timeline")
        self._set_rate_from_timeline(timeline)

        xges_tracks = self._findall(timeline, "./track")
        xges_tracks.sort(
            key=lambda trk: self._get_attrib(trk, "track-id", int))
        xges_tracks = [
            XgesTrack(
                self._get_attrib(trk, "caps", str),
                self._get_attrib(trk, "track-type", int),
                self._get_properties(trk),
                self._get_metadatas(trk))
            for trk in xges_tracks]

        self._add_properties_and_metadatas_to_otio(
            otio_stack, project, "project")
        self._add_properties_and_metadatas_to_otio(
            otio_stack, timeline, "timeline")
        self._add_to_otio_metadata(otio_stack, "tracks", xges_tracks)
        self._add_layers_to_stack(timeline, otio_stack)
        return project

    def _add_layers_to_stack(self, timeline, stack):
        sort_tracks = []
        for layer in self._findall(timeline, "./layer"):
            priority = self._get_attrib(layer, "priority", int)
            tracks = self._tracks_from_layer_clips(layer)
            for track in tracks:
                sort_tracks.append((track, priority))
        sort_tracks.sort(key=lambda ent: ent[1], reverse=True)
        # NOTE: smaller priority is later in the list
        for track in (ent[0] for ent in sort_tracks):
            stack.append(track)

    def _get_clips_for_type(self, clips, track_type):
        return [
            clip for clip in clips
            if self._get_attrib(clip, "track-types", int) & track_type]

    def _tracks_from_layer_clips(self, layer):
        all_clips = self._findall(layer, "./clip")
        tracks = []
        for track_type in [GESTrackType.VIDEO, GESTrackType.AUDIO]:
            clips = self._get_clips_for_type(all_clips, track_type)
            if not clips:
                continue
            otio_items, otio_transitions = \
                self._create_otio_composables_from_clips(clips)

            track = otio.schema.Track()
            track.kind = GESTrackType.to_otio_kind(track_type)
            self._add_otio_composables_to_track(
                track, otio_items, otio_transitions)

            tracks.append(track)
        return tracks

    def _create_otio_composables_from_clips(self, clips):
        otio_transitions = []
        otio_items = []
        for clip in clips:
            clip_type = self._get_attrib(clip, "type-name", str)
            start = self._get_attrib(clip, "start", int)
            inpoint = self._get_attrib(clip, "inpoint", int)
            duration = self._get_attrib(clip, "duration", int)
            otio_composable = None
            if clip_type == "GESTransitionClip":
                otio_composable = self._otio_transition_from_clip(clip)
            elif clip_type == "GESUriClip":
                otio_composable = self._otio_item_from_uri_clip(clip)
            else:
                # TODO: support other clip types
                # maybe represent a GESTitleClip as a gap, with the text
                # in the metadata?
                # or as a clip with a MissingReference?
                show_ignore(
                    "Could not represent {} clip type".format(clip_type))

            if isinstance(otio_composable, otio.schema.Transition):
                otio_transitions.append({
                    "transition": otio_composable,
                    "start": start, "duration": duration})
            elif isinstance(otio_composable, otio.core.Item):
                otio_items.append({
                    "item": otio_composable, "start": start,
                    "inpoint": inpoint, "duration": duration})
        return otio_items, otio_transitions

    @staticmethod
    def _item_gap(second, first):
        if second is None:
            return 0
        if first is None:
            return second["start"]
        return second["start"] - first["start"] - first["duration"]

    def _add_otio_composables_to_track(self, track, items, transitions):
        """
        Insert items and transitions into the track with correct
        timings.
        items argument should be an array of dicts, containing an otio
        item, and its start, inpoint and duration times in gstclocktimes
        (taken from the corresponding xges clip attributes).
        The source_range will be set before insertion into the track.
        transitions argument should be an array of dicts, containing an
        otio transition, and its start and duration times in
        gstclocktimes(taken from the corresponding xges transition clip
        attributes). The in_offset and out_offset will be set before
        insertion into the track.
        """
        # otio tracks do not allow items to overlap
        # in contrast an xges layer will let clips overlap, and their
        # overlap may have some corresponding transition associated with
        # it. Diagrammatically, we want to translate:
        #  _ _ _ _ _ _ ____________ _ _ _ _ _ _ ____________ _ _ _ _ _ _
        #             +            +           +            +
        # xges-clip-0 |            |xges-clip-1|        xges-clip-2
        #  _ _ _ _ _ _+____________+_ _ _ _ _ _+____________+_ _ _ _ _ _
        #             .------------.           .------------.
        #             :xges-trans-1:           :xges-trans-2:
        #             '------------'           '------------'
        # -----------> <----------------------------------->
        #   start       duration (on xges-clip-1)
        # -----------> <---------->
        #   start       duration (on xges-trans-1)
        # ------------------------------------> <---------->
        #   start                             duration (on xges-trans-2)
        #
        # . . . . ..........................................
        # . Not    :                                       :
        # . Avail. :   xges-asset for xges-clip-1          :
        # . . . . .:.......................................:
        #  <--------->
        #   inpoint (on xges-clip-1)
        #  <---------------------------------------------->
        #   duration (on xges-asset)
        #
        # to:
        #  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
        #                   +                         +
        # otio-clip-0       |       otio-clip-1       | otio-clip-2
        #  _ _ _ _ _ _ _ _ _+_ _ _ _ _ _ _ _ _ _ _ _ _+_ _ _ _ _ _ _ _ _
        #             .------------.           .------------.
        #             :otio-trans-1:           :otio-trans-2:
        #             '------------'           '------------'
        #              <---> <---->             <----> <--->
        #         .in_offset .out_offset    .in_offset .out_offset
        #
        # . . . . ..........................................
        # . Not    :                                       :
        # . Avail. :   otio-med-ref for otio-clip-1        :
        # . . . . .:.......................................:
        #  <---------------> <----------------------->
        # s_range.start_time  s_range.duration (on otio-clip-1)
        #  <------> <------------------------------------->
        # a_range.start_time   a_range.duration (on otio-med-ref)
        #
        # where:
        #   s_range = source_range
        #   a_range = available_range
        #
        # so:
        #   for otio-trans-1:
        #       .in_offset + .out_offset = xges-trans-1-duration
        #   for otio-clip-1:
        #       s_range.start_time = xges-clip-1-inpoint
        #                            + otio-trans-1.in_offset
        #       s_range.duration = xges-clip-1-duration
        #                          - otio-trans-1.in_offset
        #                          - otio-trans-2.out_offset
        #
        #
        # We also want to insert any otio-gaps when the first xges clip
        # does not start at zero, or if there is an implied gap between
        # xges clips
        items.sort(key=lambda ent: ent["start"])
        prev_otio_transition = None
        for item, prev_item, next_item in zip(
                items, [None] + items, items[1:] + [None]):
            otio_start = self.to_rational_time(item["inpoint"])
            otio_duration = self.to_rational_time(item["duration"])
            otio_transition = None
            pre_gap = self._item_gap(item, prev_item)
            post_gap = self._item_gap(next_item, item)
            if pre_gap < 0:
                # overlap: transition should have been
                # handled by the previous iteration
                otio_start += prev_otio_transition.in_offset
                otio_duration -= prev_otio_transition.in_offset
                # start is delayed until the otio transition's position
                # duration looses what start gains
            elif pre_gap > 0:
                track.append(self._create_otio_gap(pre_gap))

            if post_gap < 0:
                # overlap
                duration = -post_gap
                transition = [
                    t for t in transitions
                    if t["start"] == next_item["start"] and
                    t["duration"] == duration]
                if len(transition) == 1:
                    otio_transition = transition[0]["transition"]
                    transitions.remove(transition[0])
                    # remove transitions once they have been extracted
                elif len(transition) == 0:
                    # NOTE: this can happen if auto-transition is false
                    # for the xges timeline
                    otio_transition = self._default_otio_transition()
                else:
                    raise XGESReadError(
                        "Found {:d} {!s} transitions with start={:d} "
                        "and duration={:d} within a single layer".format(
                            len(transition), track.kind,
                            next_item["start"], duration))
                half = float(duration) / 2.0
                otio_transition.in_offset = self.to_rational_time(half)
                otio_transition.out_offset = self.to_rational_time(half)
                otio_duration -= otio_transition.out_offset
                # trim the end of the clip, which is where the otio
                # transition starts
            otio_item = item["item"]
            otio_item.source_range = otio.opentime.TimeRange(
                otio_start, otio_duration)
            track.append(otio_item)
            if otio_transition:
                track.append(otio_transition)
            prev_otio_transition = otio_transition
        if transitions:
            raise XGESReadError(
                "xges layer contains {:d} {!s} transitions that could "
                "not be associated with any clip overlap".format(
                    len(transitions), track.kind))

    def _get_name(self, element):
        name = self._get_from_properties(element, "name", "string")
        if not name:
            name = element.tag
        return name

    def _otio_transition_from_clip(self, clip):
        otio_transition = otio.schema.Transition(
            name=self._get_name(clip),
            transition_type=TRANSITION_MAP.get(
                clip.attrib["asset-id"],
                otio.schema.TransitionTypes.Custom))
        self._add_properties_and_metadatas_to_otio(otio_transition, clip)
        return otio_transition

    def _default_otio_transition(self):
        return otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve)

    def _otio_item_from_uri_clip(self, clip):
        asset_id = self._get_attrib(clip, "asset-id", str)
        sub_project_asset = self._asset_by_id(asset_id, "GESTimeline")
        if sub_project_asset is not None:
            # this clip refers to a sub project
            sub_ges = XGES(self._findonly(sub_project_asset, "./ges"))
            otio_stack = otio.schema.Stack()
            sub_ges._fill_otio_stack_from_ges(otio_stack)
            otio_stack.name = self._get_name(clip)
            self._add_properties_and_metadatas_to_otio(
                otio_stack, sub_project_asset, "sub-project-asset")
            # NOTE: we include asset-id in the metadata, so that two
            # stacks that refer to a single sub-project will not be
            # split into separate assets when converting from
            # xges->otio->xges
            self._add_to_otio_metadata(otio_stack, "asset-id", asset_id)
            uri_clip_asset = self._asset_by_id(asset_id, "GESUriClip")
            if uri_clip_asset is None:
                show_ignore(
                    "Did not find the expected GESUriClip asset with "
                    "the id {}".format(asset_id))
            else:
                self._add_properties_and_metadatas_to_otio(
                    otio_stack, uri_clip_asset, "uri-clip-asset")
            return otio_stack
        otio_clip = otio.schema.Clip(
            name=self._get_name(clip),
            media_reference=self._reference_from_id(asset_id))
        self._add_properties_and_metadatas_to_otio(otio_clip, clip)
        return otio_clip

    def _create_otio_gap(self, gst_duration):
        source_range = otio.opentime.TimeRange(
            self.to_rational_time(0),
            self.to_rational_time(gst_duration))
        return otio.schema.Gap(source_range=source_range)

    def _reference_from_id(self, asset_id):
        asset = self._asset_by_id(asset_id, "GESUriClip")
        if asset is None:
            show_ignore(
                "Did not find the expected GESUriClip asset with the "
                "id {}".format(asset_id))
            return otio.schema.MissingReference()

        duration = self._get_from_properties(
            asset, "duration", "guint64")

        if duration is None:
            available_range = None
        else:
            available_range = otio.opentime.TimeRange(
                start_time=self.to_rational_time(0),
                duration=self.to_rational_time(duration)
            )
        ref = otio.schema.ExternalReference(
            target_url=asset_id,
            available_range=available_range
        )
        self._add_properties_and_metadatas_to_otio(ref, asset)
        return ref

    # --------------------
    # search helpers
    # --------------------
    def _asset_by_id(self, asset_id, asset_type):
        return self._findonly(
            self.ges_xml,
            "./project/ressources/asset[@id='{}']"
            "[@extractable-type-name='{}']".format(
                asset_id, asset_type),
            allow_none=True
        )

    def _timeline_element_by_name(self, timeline, name):
        for clip in self._findall(timeline, "./layer/clip"):
            if self._get_from_properties(clip, "name", "string") == name:
                return clip

        return None


class XGESOtio:
    """
    This object is responsible for converting an otio timeline into an
    xGES project.
    """

    def __init__(self, input_otio=None):
        if input_otio is not None:
            self.timeline = input_otio.deepcopy()
        else:
            self.timeline = None
        self.all_names = set()

    @staticmethod
    def rat_to_gstclocktime(rat_time):
        """
        Convert an otio RationalTime to an int representing the time in
        nanoseconds.
        """
        return int(otio.opentime.to_seconds(rat_time) * GST_SECOND)

    @classmethod
    def range_to_gstclocktimes(cls, time_range):
        """
        Convert an otio TimeRange to a tuple of the start_time and
        duration as ints representing the times in nanoseconds.
        """
        return (cls.rat_to_gstclocktime(time_range.start_time),
                cls.rat_to_gstclocktime(time_range.duration))

    def _insert_new_sub_element(self, into_parent, tag, attrib=None, text=''):
        elem = ElementTree.SubElement(into_parent, tag, attrib or {})
        elem.text = text
        return elem

    def _get_from_otio_metadata(self, otio_obj, key, default=None):
        return otio_obj.metadata.get(META_NAMESPACE, {}).get(key, default)

    def _get_element_structure(self, otio_obj, struct_name, sub_key=None):
        if sub_key is not None:
            struct = self._get_from_otio_metadata(
                otio_obj, sub_key, {}).get(struct_name)
        else:
            struct = self._get_from_otio_metadata(otio_obj, struct_name)
        if struct is not None:
            return struct
        return GstStructure(struct_name + ";")

    def _get_element_properties(self, element, sub_key=None):
        return self._get_element_structure(element, "properties", sub_key)

    def _get_element_metadatas(self, element, sub_key=None):
        return self._get_element_structure(element, "metadatas", sub_key)

    def _asset_exists(self, asset_id, ressources, *extract_types):
        assets = ressources.findall("./asset")
        if asset_id is None or assets is None:
            return False
        for extract_type in extract_types:
            for asset in assets:
                if asset.get("extractable-type-name") == extract_type \
                        and asset.get("id") == asset_id:
                    return True
        return False

    def _serialize_stack_to_ressource(self, otio_stack, ressources):
        asset_id = self._get_from_otio_metadata(otio_stack, "asset-id")
        if self._asset_exists(asset_id, ressources, "GESTimeline"):
            return
        if asset_id is None:
            asset_id = "0"
            while self._asset_exists(
                    asset_id, ressources, "GESUriClip", "GESTimeline"):
                # NOTE: asset_id must be unique for both the
                # GESTimeline and GESUriClip extractable types
                asset_id += "0"
        asset = self._insert_new_sub_element(
            ressources, "asset",
            attrib={
                "id": asset_id,
                "extractable-type-name": "GESTimeline",
                "properties": str(self._get_element_properties(
                    otio_stack, "sub-project-asset")),
                "metadatas": str(self._get_element_metadatas(
                    otio_stack, "sub-project-asset")),
            }
        )
        sub_obj = XGESOtio()
        sub_ges = sub_obj._serialize_stack_to_ges(otio_stack)
        asset.append(sub_ges)
        self._insert_new_sub_element(
            ressources, "asset",
            attrib={
                "id": asset_id,
                "extractable-type-name": "GESUriClip",
                "properties": str(self._get_element_properties(
                    otio_stack, "uri-clip-asset")),
                "metadatas": str(self._get_element_metadatas(
                    otio_stack, "uri-clip-asset")),
            }
        )
        return asset_id

    def _serialize_external_reference_to_ressource(
            self, reference, ressources):
        asset_id = reference.target_url
        if self._asset_exists(asset_id, ressources, "GESUriClip"):
            return
        properties = self._get_element_properties(reference)
        if properties.get("duration") is None:
            a_range = reference.available_range
            if a_range is not None:
                properties.set(
                    "duration", "guint64",
                    sum(self.range_to_gstclocktimes(a_range)))
                # TODO: check that this is correct approach for when
                # start_time is not 0.
                # duration is the sum of the a_range start_time and
                # duration we ignore that frames before start_time are
                # not available
        self._insert_new_sub_element(
            ressources, "asset",
            attrib={
                "id": asset_id,
                "extractable-type-name": "GESUriClip",
                "properties": str(properties),
                "metadatas": str(self._get_element_metadatas(reference)),
            }
        )

    def _get_clip_times(
            self, otio_composable, prev_composable, next_composable,
            prev_otio_end):
        # see _add_otio_composables_to_track for the translation from
        # xges clips to otio clips. Here we reverse this by setting:
        #   for xges-trans-1:
        #       otio_end = prev_otio_end
        #       start    = prev_otio_end
        #                  - otio-trans-1.in_offset
        #       duration = otio-trans-1.in_offset
        #                  + otio-trans-1.out_offset
        #
        #   for xges-clip-1:
        #       otio_end = prev_otio_end
        #                  + otio-clip-1.s_range.duration
        #       start    = prev_otio_end
        #                  - otio-clip-1.in_offset
        #       duration = otio-clip-1.s_range.duration
        #                  + otio-trans-1.in_offset
        #                  + otio-trans-2.out_offset
        #       inpoint  = otio-clip-1.s_range.start_time
        #                  - otio-trans-1.in_offset
        if isinstance(otio_composable, otio.core.Item):
            otio_start_time, otio_duration = self.range_to_gstclocktimes(
                otio_composable.trimmed_range())
            otio_end = prev_otio_end + otio_duration
            start = prev_otio_end
            duration = otio_duration
            inpoint = otio_start_time
            if isinstance(prev_composable, otio.schema.Transition):
                in_offset = self.rat_to_gstclocktime(
                    prev_composable.in_offset)
                start -= in_offset
                duration += in_offset
                inpoint -= in_offset
            if isinstance(next_composable, otio.schema.Transition):
                duration += self.rat_to_gstclocktime(
                    next_composable.out_offset)
        elif isinstance(otio_composable, otio.schema.Transition):
            otio_end = prev_otio_end
            in_offset = self.rat_to_gstclocktime(
                otio_composable.in_offset)
            out_offset = self.rat_to_gstclocktime(
                otio_composable.out_offset)
            start = prev_otio_end - in_offset
            duration = in_offset + out_offset
            inpoint = 0
        else:
            # NOTE: core schemas only give Item and Transition as
            # composable types
            raise UnhandledOtioError(otio_composable)
        return start, duration, inpoint, otio_end

    def _serialize_composable_to_clip(
            self, otio_composable, prev_composable, next_composable,
            layer, layer_priority, track_types, ressources, clip_id,
            prev_otio_end):
        """
        Return the next clip_id and the time at which the next clip
        should start.
        """
        start, duration, inpoint, otio_end = self._get_clip_times(
            otio_composable, prev_composable, next_composable,
            prev_otio_end)

        asset_id = None
        asset_type = None
        if isinstance(otio_composable, otio.schema.Gap):
            pass
        elif isinstance(otio_composable, otio.schema.Transition):
            asset_type = "GESTransitionClip"
            # FIXME: get transition type from metadata if transition is
            # not supported by otio
            # currently, any Custom_Transition is being turned into a
            # crossfade
            asset_id = TRANSITION_MAP.get(
                otio_composable.transition_type, "crossfade")
        elif isinstance(otio_composable, otio.schema.Clip):
            ref = otio_composable.media_reference
            if ref is None or ref.is_missing_reference:
                pass  # treat as a gap
                # FIXME: properly handle missing reference
            elif isinstance(ref, otio.schema.ExternalReference):
                asset_id = ref.target_url
                asset_type = "GESUriClip"
                self._serialize_external_reference_to_ressource(
                    ref, ressources)
            elif isinstance(ref, otio.schema.MissingReference):
                pass  # shouldn't really happen
            elif isinstance(ref, otio.schema.GeneratorReference):
                # FIXME: insert a GESTestClip if possible once otio
                # supports GeneratorReferenceTypes
                show_otio_not_supported(
                    ref, "Treating as a gap")
            else:
                show_otio_not_supported(
                    ref, "Treating as a gap")
        elif isinstance(otio_composable, otio.schema.Stack):
            asset_id = self._serialize_stack_to_ressource(
                otio_composable, ressources)
            asset_type = "GESUriClip"
        else:
            show_otio_not_supported(otio_composable, "Treating as a gap")

        if asset_id is None:
            if isinstance(prev_composable, otio.schema.Transition) \
                    or isinstance(next_composable, otio.schema.Transition):
                # unassigned clip is preceded or followed by a transition
                # transitions in GES are only between two clips, so
                # we will insert an empty GESTitleClip to act as a
                # transparent clip, which emulates an otio gap
                asset_id = "GESTitleClip"
                asset_type = "GESTitleClip"
            # else gap is simply the absence of a clip
        if asset_id is None:
            # No clip is inserted, so return same clip_id
            return (clip_id, otio_end)

        properties = self._get_element_properties(otio_composable)
        if not properties.get("name"):
            properties.set(
                "name", "string", self._get_unique_name(otio_composable))
        self._insert_new_sub_element(
            layer, 'clip',
            attrib={
                "id": str(clip_id),
                "properties": str(properties),
                "asset-id": str(asset_id),
                "type-name": str(asset_type),
                "track-types": str(track_types),
                "layer-priority": str(layer_priority),
                "start": str(start),
                "rate": '0',
                "inpoint": str(inpoint),
                "duration": str(duration),
                "metadatas": str(self._get_element_metadatas(otio_composable)),
            }
        )
        return (clip_id + 1, otio_end)

    def _serialize_stack_to_tracks(self, otio_stack, timeline):
        xges_tracks = self._get_from_otio_metadata(otio_stack, "tracks")
        if xges_tracks is None:
            xges_tracks = []
            # FIXME: track_id is currently arbitrarily set.
            # Only the xges effects, source and bindings elements use
            # a track-id attribute, which are not yet supported anyway.
            track_types = self._get_stack_track_types(otio_stack)
            for track_type in [GESTrackType.VIDEO, GESTrackType.AUDIO]:
                if track_types & track_type:
                    xges_tracks.append(
                        XgesTrack.new_from_track_type(track_type))
        for track_id, xges_track in enumerate(xges_tracks):
            self._insert_new_sub_element(
                timeline, 'track',
                attrib={
                    "caps": xges_track.caps,
                    "track-type": str(xges_track.track_type),
                    "track-id": str(track_id),
                    "properties": str(xges_track.properties),
                    "metadatas": str(xges_track.metadatas)
                })

    def _serialize_track_to_layer(
            self, otio_track, timeline, layer_priority):
        return self._insert_new_sub_element(
            timeline, 'layer',
            attrib={"priority": str(layer_priority)})

    def _get_unique_name(self, named_otio):
        name = named_otio.name
        if not name:
            name = named_otio.schema_name()
        tmpname = name
        for i in itertools.count(start=1):
            if tmpname not in self.all_names:
                self.all_names.add(tmpname)
                return tmpname
            tmpname = name + "_{:d}".format(i)

    def _serialize_stack_to_project(
            self, otio_stack, ges, otio_timeline):
        metadatas = self._get_element_metadatas(otio_stack, "project")
        if not metadatas.get("name"):
            if otio_timeline is not None and otio_timeline.name:
                metadatas.set(
                    "name", "string", self._get_unique_name(otio_timeline))
            elif otio_stack.name:
                metadatas.set(
                    "name", "string", self._get_unique_name(otio_stack))
        return self._insert_new_sub_element(
            ges, "project",
            attrib={"metadatas": str(metadatas)})

    def _serialize_stack_to_timeline(self, otio_stack, project):
        return self._insert_new_sub_element(
            project, "timeline",
            attrib={
                "properties": str(self._get_element_properties(
                    otio_stack, "timeline")),
                "metadatas": str(self._get_element_metadatas(
                    otio_stack, "timeline")),
            })

    def _serialize_stack_to_ges(self, otio_stack, otio_timeline=None):
        ges = ElementTree.Element("ges", version="0.4")
        project = self._serialize_stack_to_project(
            otio_stack, ges, otio_timeline)
        ressources = self._insert_new_sub_element(project, "ressources")
        timeline = self._serialize_stack_to_timeline(otio_stack, project)
        self._serialize_stack_to_tracks(otio_stack, timeline)

        clip_id = 0
        for layer_priority, otio_track in enumerate(reversed(otio_stack)):
            # NOTE: stack orders tracks with later tracks having higher
            # priority, so we reverse the list for xges
            layer = self._serialize_track_to_layer(
                otio_track, timeline, layer_priority)
            # FIXME: should the start be effected by the global_start_time
            # on the otio timeline?
            otio_end = 0
            track_types = self._get_track_types(otio_track)
            for otio_composable in otio_track:
                neighbours = otio_track.neighbors_of(otio_composable)
                clip_id, otio_end = self._serialize_composable_to_clip(
                    otio_composable, neighbours[0], neighbours[1],
                    layer, layer_priority, track_types, ressources,
                    clip_id, otio_end)
        return ges

    def _remove_non_xges_metadata(self, otio_obj):
        keys = [k for k in otio_obj.metadata.keys()]
        for key in keys:
            if key != META_NAMESPACE:
                del otio_obj.metadata[key]

    @staticmethod
    def _add_track_types(otio_track, track_type):
        otio_track.metadata["track-types"] |= track_type

    @staticmethod
    def _set_track_types(otio_track, track_type):
        otio_track.metadata["track-types"] = track_type

    @staticmethod
    def _get_track_types(otio_track):
        return otio_track.metadata["track-types"]

    def _get_stack_track_types(self, otio_stack):
        track_types = 0
        for otio_track in otio_stack:
            track_types |= self._get_track_types(otio_track)
        return track_types

    def _init_track_types(self, otio_track):
        # May overwrite the metadata, but we have a deepcopy of the
        # original timeline and track-type is not otherwise used.
        self._set_track_types(
            otio_track, GESTrackType.from_otio_kind(otio_track.kind))

    def _merge_track_in_place(self, otio_track, merge):
        self._add_track_types(otio_track, self._get_track_types(merge))

    def _equal_track_modulo_kind(self, otio_track, compare):
        otio_track_types = self._get_track_types(otio_track)
        compare_track_types = self._get_track_types(compare)
        if otio_track_types & compare_track_types:
            # do not want to merge two tracks if they overlap in
            # their track types. Otherwise, we may "loose" a track
            # after merging
            return False
        tmp_kind = compare.kind
        compare.kind = otio_track.kind
        self._set_track_types(compare, otio_track_types)
        same = otio_track.is_equivalent_to(compare)
        compare.kind = tmp_kind
        self._set_track_types(compare, compare_track_types)
        return same

    def _merge_tracks_in_stack(self, otio_stack):
        index = len(otio_stack) - 1  # start with higher priority
        while index > 0:
            track = otio_stack[index]
            next_track = otio_stack[index - 1]
            if self._equal_track_modulo_kind(track, next_track):
                # want to merge if two tracks are the same, except their
                # track kind is *different*
                # merge down
                self._merge_track_in_place(next_track, track)
                del otio_stack[index]
                # next track will be the merged one, which allows
                # us to merge again. Currently this is redundant since
                # there are only two track kinds
            index -= 1

    def _pad_source_range_track(self, otio_stack):
        index = 0
        while index < len(otio_stack):
            # we are using this form of iteration to make transparent
            # that we may be editing the stack's content
            child = otio_stack[index]
            if isinstance(child, otio.schema.Track) and \
                    child.source_range is not None:
                # each track will correspond to a layer, but xges can
                # not trim a layer, so to account for the source_range,
                # we will place the layer below a clip by using
                # sub-projects.
                # i.e. we will insert above a track and stack, where the
                # stack takes the source_range instead
                new_track = otio.schema.Track(
                    name=child.name,
                    kind=child.kind)
                self._init_track_types(new_track)
                new_stack = otio.schema.Stack(
                    name=child.name,
                    source_range=child.source_range)
                child.source_range = None
                otio_stack[index] = new_track
                new_track.append(new_stack)
                new_stack.append(child)
            index += 1

    def _pad_double_track(self, otio_track):
        index = 0
        while index < len(otio_track):
            # we are using this form of iteration to make transparent
            # that we may be editing the track's content
            child = otio_track[index]
            if isinstance(child, otio.schema.Track):
                # have two tracks in a row, we expect tracks to be
                # below a stack, so we will insert a stack inbetween
                insert = otio.schema.Stack(name=child.name)
                otio_track[index] = insert
                insert.append(child)
            index += 1

    def _pad_non_track_children_of_stack(self, otio_stack):
        index = 0
        while index < len(otio_stack):
            # we are using this form of iteration to make transparent
            # that we may be editing the stack's content
            child = otio_stack[index]
            if not isinstance(child, otio.schema.Track):
                # we expect a stack to only contain tracks, so we will
                # insert a track inbetween
                insert = otio.schema.Track(name=child.name)
                if isinstance(child, otio.schema.Stack):
                    self._set_track_types(
                        insert, self._get_stack_track_types(child))
                else:
                    warnings.warn(
                        "Found an otio {} object directly under a "
                        "Stack.\nTreating as a Video and Audio source."
                        "".format(child.schema_name()))
                    self._set_track_types(
                        insert, GESTrackType.VIDEO | GESTrackType.AUDIO)
                otio_stack[index] = insert
                insert.append(child)
            index += 1

    def _perform_bottom_up(self, func, otio_composable, filter_type):
        """
        Perform the given function to all otio composables found below
        the given one. The given function should not change the number
        or order of siblings within the composable's parent, but it is
        ok to change the children of the received composable.
        """
        if isinstance(otio_composable, otio.core.Composition):
            for child in otio_composable:
                self._perform_bottom_up(func, child, filter_type)
        if isinstance(otio_composable, filter_type):
            func(otio_composable)

    def _prepare_timeline(self):
        if self.timeline.tracks.source_range is not None:
            # only xges clips can correctly handle a trimmed
            # source_range, so place this stack one layer down. Note
            # that a dummy track will soon be inserted between these
            # two stacks
            orig_stack = self.timeline.tracks.deepcopy()
            # seem to get an error if we don't copy the stack
            self.timeline.tracks = otio.schema.Stack()
            self.timeline.tracks.name = orig_stack.name
            self.timeline.tracks.append(orig_stack)
        # get rid of non-xges metadata. In particular, this will allow
        # two otio objects to look the same if they only differ by some
        # unused metadata
        self._perform_bottom_up(
            self._remove_non_xges_metadata,
            self.timeline.tracks, otio.core.SerializableObject)
        # this needs to be first, to give all tracks the required
        # metadata. Any tracks created after this must manually set
        # this metadata
        self._perform_bottom_up(
            self._init_track_types,
            self.timeline.tracks, otio.schema.Track)
        self._perform_bottom_up(
            self._pad_double_track,
            self.timeline.tracks, otio.schema.Track)
        self._perform_bottom_up(
            self._pad_non_track_children_of_stack,
            self.timeline.tracks, otio.schema.Stack)
        # the next operations must be after the previous ones, to ensure
        # that all stacks only contain tracks as items
        self._perform_bottom_up(
            self._pad_source_range_track,
            self.timeline.tracks, otio.schema.Stack)
        self._perform_bottom_up(
            self._merge_tracks_in_stack,
            self.timeline.tracks, otio.schema.Stack)

    def to_xges(self):
        self._prepare_timeline()
        ges = self._serialize_stack_to_ges(
            self.timeline.tracks, self.timeline)
        # with indentations.
        string = ElementTree.tostring(ges, encoding="UTF-8")
        dom = minidom.parseString(string)
        return dom.toprettyxml(indent='  ')


# --------------------
# adapter requirements
# --------------------
def read_from_string(input_str):
    """
    Necessary read method for otio adapter

    Args:
        input_str (str): A GStreamer Editing Services formated project

    Returns:
        OpenTimeline: An OpenTimeline object
    """

    return XGES(input_str).to_otio()


def write_to_string(input_otio):
    """
    Necessary write method for otio adapter

    Args:
        input_otio (OpenTimeline): An OpenTimeline object

    Returns:
        str: The string contents of an FCP X XML
    """

    return XGESOtio(input_otio).to_xges()


# --------------------
# schemas
# --------------------

@otio.core.register_type
class GstStructure(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema that acts as a named dictionary with
    typed entries, essentially mimicking the GstStructure of the
    GStreamer C library.

    In particular, this schema mimics the gst_structure_to_string and
    gst_structure_from_string C methods. As such, it can be used to
    read and write the properties and metadatas attributes found in
    xges elements.

    Note that the types are to correspond to GStreamer/GES GTypes,
    rather than python types.

    Current supported GTypes:
    GType         Associated    Accepted
                  Python type   aliases
    ======================================
    gint          int           int, i
    glong         int
    gint64        int
    guint         int           uint, u
    gulong        int
    guint64       int
    gfloat        float         float, f
    gdouble       float         double, d
    gboolean      bool          boolean,
                                bool, b
    string        str or None   str, s
    GstFraction   str or        fraction
                  Fraction

    Note that other types can be given: these must be given as strings
    and the user will be responsible for making sure they are already in
    a serialized form.
    """
    _serializable_label = "GstStructure.1"

    name = otio.core.serializable_field(
        "name", str, "The name of the structure")
    fields = otio.core.serializable_field(
        "fields", dict, "The fields of the structure, of the form:\n"
        "    {fielname: (type, value), ...}\n"
        "where 'fieldname' is a str that names the field, 'type' is "
        "a str that names the value type, and 'value' is the actual "
        "value. Note that the name of the type corresponds to the "
        "GType that would be used in the Gst/GES library, or some "
        "accepted alias, rather than the python type.")

    TYPE_ALIAS = {
        "i": "int",
        "gint": "int",
        "u": "uint",
        "guint": "uint",
        "f": "float",
        "gfloat": "float",
        "d": "double",
        "gdouble": "double",
        "b": "boolean",
        "bool": "boolean",
        "gboolean": "boolean",
        "GstFraction": "fraction",
        "str": "string",
        "s": "string"
    }
    INT_TYPES = ("int", "glong", "gint64")
    UINT_TYPES = ("uint", "gulong", "guint64")
    FLOAT_TYPES = ("float", "double")
    BOOLEAN_TYPES = ("boolean", )
    FRACTION_TYPES = ("fraction", )
    STRING_TYPES = ("string", )
    KNOWN_TYPES = INT_TYPES + UINT_TYPES + FLOAT_TYPES + BOOLEAN_TYPES \
        + FRACTION_TYPES + STRING_TYPES

    def __init__(self, text="Unnamed", fields=None):
        """
        Initialize the GstStructure.

        If only a single string is given it will be parsed to extract
        the full structure.

        If two arguments are given, the first will be interpreted as
        the name of the structure, and the second will be treated as
        either another GstStructure (who's field data is copied, but
        the name is ignored), a string to be parsed (the first
        argument will still be used as the name, and the name found in
        the parsed string will be ignored), or a dictionary containing
        the field data (where each entry is a two-entry tuple
        containing the type name and value).
        """
        otio.core.SerializableObject.__init__(self)
        if type(text) is not str:
            if isinstance(text, type(u"")):
                # TODO: remove once python2 has ended
                text = text.encode("utf8")
            else:
                raise TypeError("Expect a str type for the first argument")
        if isinstance(fields, (str, type(u""))):
            # TODO: replace with single str check once python2 has ended
            if type(fields) is not str:
                fields = fields.encode("utf8")
            self._check_name(text)
            self.name = text
            self.fields = self._parse(fields)[1]
        elif fields is not None:
            if isinstance(fields, GstStructure):
                fields = fields.fields
            if type(fields) is not dict:
                try:
                    fields = dict(fields)
                except (TypeError, ValueError):
                    raise TypeError(
                        "Expect a GstStructure, str, or dict-like type"
                        "for the second argument")
            self._check_name(text)
            self.name = text
            self.fields = {}
            for key in fields:
                entry = fields[key]
                if type(entry) is not tuple:
                    try:
                        entry = tuple(entry)
                    except (TypeError, ValueError):
                        raise TypeError(
                            "Expect dict to be filled with tuple-like "
                            "entries")
                if len(entry) != 2:
                    raise TypeError(
                        "Expect dict to be filled with 2-entry tuples")
                self.set(key, *entry)
        else:
            self.name, self.fields = self._parse(text)
            # NOTE: in python2 the str values in the returned fields are
            # converted to unicode when we make this assignment!!!!
            # this comes from being an otio serializable_field

    def __repr__(self):
        return "GstStructure({}, {})".format(
            repr(self.name), repr(self.fields))

    UNKNOWN_PREFIX = "[UNKNOWN]"

    @classmethod
    def _make_type_unknown(cls, _type):
        return cls.UNKNOWN_PREFIX + _type
        # note the sqaure brackets make the type break the TYPE_FORMAT

    @classmethod
    def _is_unknown_type(cls, _type):
        return _type[:len(cls.UNKNOWN_PREFIX)] == cls.UNKNOWN_PREFIX

    @classmethod
    def _get_unknown_type(cls, _type):
        return _type[len(cls.UNKNOWN_PREFIX):]

    def _fields_to_str(self):
        write = []
        for key in self.fields:
            _type, value = self.fields[key]
            key = self._check_key(key)
            if self._is_unknown_type(_type):
                _type = self._get_unknown_type(_type)
                _type = self._check_type(_type)
                value = self._check_unknown_typed_value(value)
            else:
                _type = self._check_type(_type)
                value = self.serialize_value(_type, value)
            write.append(", {}=({}){}".format(key, _type, value))
        return "".join(write)

    def __str__(self):
        """Emulates gst_structure_to_string"""
        name = self._check_name(self.name)
        return name + self._fields_to_str() + ";"

    def __getitem__(self, key):
        value = self.fields[key][1]
        # TODO: remove below once python2 has ended
        if not isinstance(value, str) and isinstance(value, type(u"")):
            # Only possible in python2
            return value.encode("utf8")
        return value

    @staticmethod
    def _shorten_str(in_string):
        MAX_LEN = 20
        if len(in_string) <= MAX_LEN:
            return in_string
        return in_string[:MAX_LEN] + "..."

    @classmethod
    def _string_val_err(cls, string_val, problem, prefix=""):
        raise ValueError(
            "Received string ({}{}) ".format(
                prefix, cls._shorten_str(string_val)) + problem)

    @staticmethod
    def _val_type_err(typ, val, expect):
        raise TypeError(
            "Received value ({!s}) is a {} rather than a {}, even "
            "though the {} type was given".format(
                val, type(val).__name__, expect, typ))

    @staticmethod
    def _val_prop_err(typ, val, wrong_prop):
        raise ValueError(
            "Received value ({!s}) is {}, even though the {} type "
            "was given".format(val, wrong_prop, typ))

    @staticmethod
    def _val_read_err(typ, val, extra=None):
        message = "Value ({!s}) is invalid for {} type".format(val, typ)
        if extra:
            message += ":\n{}".format(extra)
        raise ValueError(message)

    def set(self, key, _type, value):
        if self.fields.get(key) == (_type, value):
            return
        key = self._check_key(key)
        type_is_unknown = True
        if self._is_unknown_type(_type):
            # this can happen if the user is setting a GstStructure
            # using a preexisting GstStructure, the type will then
            # be passed and marked as unknown
            _type = self._get_unknown_type(_type)
            _type = self._check_type(_type)
        else:
            _type = self._check_type(_type)
            if _type in self.INT_TYPES:
                type_is_unknown = False
                # TODO: simply check for int once python2 has ended
                # currently in python2, can receive either an int or
                # a long
                if not isinstance(value, numbers.Integral):
                    self._val_type_err(_type, value, "int")
            elif _type in self.UINT_TYPES:
                type_is_unknown = False
                # TODO: simply check for int once python2 has ended
                # currently in python2, can receive either an int or
                # a long
                if not isinstance(value, numbers.Integral):
                    self._val_type_err(_type, value, "int")
                if value < 0:
                    self._val_prop_err(_type, value, "negative")
            elif _type in self.FLOAT_TYPES:
                type_is_unknown = False
                if type(value) is not float:
                    self._val_type_err(_type, value, "float")
            elif _type in self.BOOLEAN_TYPES:
                type_is_unknown = False
                if type(value) is not bool:
                    self._val_type_err(_type, value, "bool")
            elif _type in self.FRACTION_TYPES:
                type_is_unknown = False
                if type(value) is Fraction:
                    value = str(value)  # store internally as a str
                elif type(value) in (str, type(u"")):
                    # TODO: change to just str type once python2 has ended
                    try:
                        Fraction(value)
                    except ValueError:
                        self._val_prop_err(_type, value, "not a fraction")
                else:
                    self._val_type_err(_type, value, "Fraction or str")
            elif _type in self.STRING_TYPES:
                type_is_unknown = False
                if value is not None and \
                        type(value) not in (str, type(u"")):
                    # TODO: change to just str type once python2 has ended
                    self._val_type_err(_type, value, "str or None")
        if type_is_unknown:
            value = self._check_unknown_typed_value(value)
            warnings.warn(
                "The GstStructure type {} with the value ({}) is "
                "unknown. The value will be stored and serialized as "
                "given.".format(_type, value))
            _type = self._make_type_unknown(_type)
        self.fields[key] = (_type, value)
        # NOTE: in python2, otio will convert a str value to a unicode

    def get(self, key, default=None):
        """Return the raw value associated with key"""
        value = self.fields.get(key, (None, default))[1]
        # TODO: remove below once python2 has ended
        if not isinstance(value, str) and isinstance(value, type(u"")):
            # Only possible in python2
            return value.encode("utf8")
        return value

    ASCII_SPACES = r"(\\?[ \t\n\r\f\v])*"
    END_FORMAT = r"(?P<end>" + ASCII_SPACES + r")"
    NAME_FORMAT = r"(?P<name>[a-zA-Z][a-zA-Z0-9/_.:-]*)"
    # ^Format requirement for the name of a GstStructure
    SIMPLE_STRING = r"[a-zA-Z0-9_+/:.-]+"
    # see GST_ASCII_CHARS (below)
    KEY_FORMAT = r"(?P<key>" + SIMPLE_STRING + r")"
    # NOTE: GstStructure technically allows more general keys, but
    # these can break the parsing.
    TYPE_FORMAT = r"(?P<type>" + SIMPLE_STRING + r")"
    BASIC_VALUE_FORMAT = \
        r'(?P<value>("(\\.|[^"])*")|(' + SIMPLE_STRING + r'))'
    # consume simple string or a string between quotes. Second will
    # consume anything that is escaped, including a '"'
    # NOTE: \\. is used rather than \\" since:
    #   + '"start\"end;"'  should be captured as '"start\"end"' since
    #     the '"' is escaped.
    #   + '"start\\"end;"' should be captured as '"start\\"' since the
    #     '\' is escaped, not the '"'
    # In the fist case \\. will consume '\"', and in the second it will
    # consumer '\\', as desired. The second would not work with just \\"

    # TODO: remove the trailing '$' when python2 has ended and use
    # re's fullmatch rather than match (not available in python2)

    @staticmethod
    def _check_against_regex(check, regex, name):
        if type(check) is not str:
            # TODO: remove below once python2 has ended
            if isinstance(check, type(u"")):
                check = check.encode("utf8")
            else:
                raise TypeError(
                    "Expected '{}' to be str typed".format(name))
        # TODO: once python2 has ended, use 'fullmatch'
        if not regex.match(check):
            raise ValueError(
                "The {} ({}) is not of the correct format ({})".format(
                    name, check, regex.pattern))
        return check

    # TODO: once python2 has ended, we can drop the trailing $ and use
    # re.fullmatch in _check_against_regex
    NAME_REGEX = re.compile(NAME_FORMAT + "$")
    KEY_REGEX = re.compile(KEY_FORMAT + "$")
    TYPE_REGEX = re.compile(TYPE_FORMAT + "$")

    @classmethod
    def _check_name(cls, name):
        return cls._check_against_regex(name, cls.NAME_REGEX, "name")

    @classmethod
    def _check_key(cls, key):
        return cls._check_against_regex(key, cls.KEY_REGEX, "key")

    @classmethod
    def _check_type(cls, _type):
        _type = cls._check_against_regex(_type, cls.TYPE_REGEX, "type")
        return cls.TYPE_ALIAS.get(_type, _type)

    @classmethod
    def _check_unknown_typed_value(cls, value):
        if type(value) is not str:
            # TODO: remove below once python2 has ended
            if isinstance(value, type(u"")):
                value = value.encode("utf8")
            else:
                cls._val_type_err("unknown", value, "string")
        try:
            # see if the value could be successfully parsed in again
            ret_type, ret_val, _ = cls._parse_value(value, False)
        except ValueError as err:
            raise ValueError(
                "The unknown-typed value ({}) is not of a the "
                "expected serialized format:\n{!s}".format(value, err))
        else:
            if ret_type is not None:
                raise ValueError(
                    "The unknown-typed value ({}) starts with a type "
                    "specification. Only the serialized value should "
                    "be given".format(value))
            if ret_val != value:
                raise ValueError(
                    "The unknown-typed value ({}) is not the same as "
                    "its parsed value ({})".format(value, ret_val))
        return value

    PARSE_NAME_REGEX = re.compile(
        ASCII_SPACES + NAME_FORMAT + END_FORMAT)

    @classmethod
    def _parse_name(cls, read):
        match = cls.PARSE_NAME_REGEX.match(read)
        if match is None:
            cls._string_val_err(
                read, "does not start with a correct name")
        name = match.group("name")
        read = read[match.end("end"):]
        return name, read

    @classmethod
    def _parse_range_list_array(cls, read):
        start = read[0]
        end = {'[': ']', '{': '}', '<': '>'}.get(start)
        read = read[1:]
        values = [start, ' ']
        first = True
        while read[0] != end:
            if first:
                first = False
            else:
                if read[0] != ',':
                    cls._string_val_err(
                        read, "does not contain a comma "
                        "between listed items", "...")
                values.append(", ")
                read = read[1:]
            _type, value, read = cls._parse_value(read, False)
            if _type is not None:
                if cls._is_unknown_type(_type):
                    # remove unknown marker for serialization
                    _type = cls._get_unknown_type(_type)
                values.extend(('(', _type, ')'))
            values.append(value)
        read = read[1:]  # skip past 'end'
        match = cls.END_REGEX.match(read)  # skip whitespace
        read = read[match.end("end"):]
        # NOTE: we are ignoring the incorrect cases where a range
        # has 0, 1 or 4+ values! This is the users responsiblity.
        values.extend((' ', end))
        return "".join(values), read

    FIELD_START_REGEX = re.compile(
        ASCII_SPACES + KEY_FORMAT + ASCII_SPACES + r"=" + END_FORMAT)
    FIELD_TYPE_REGEX = re.compile(
        ASCII_SPACES + r"(\(" + ASCII_SPACES + TYPE_FORMAT
        + ASCII_SPACES + r"\))?" + END_FORMAT)
    FIELD_VALUE_REGEX = re.compile(
        ASCII_SPACES + BASIC_VALUE_FORMAT + END_FORMAT)
    END_REGEX = re.compile(END_FORMAT)

    @classmethod
    def _parse_value(cls, read, deserialize=True):
        match = cls.FIELD_TYPE_REGEX.match(read)
        # match shouldn't be None since the (TYPE_FORMAT) is optional
        # and the rest is just ASCII_SPACES
        _type = match.group("type")
        if _type is None and deserialize:
            # if deserialize is False, the (type) is optional
            cls._string_val_err(
                read, "does not contain a valid '(type)' format", "...")
        _type = cls.TYPE_ALIAS.get(_type, _type)
        type_is_unknown = True
        read = read[match.end("end"):]
        if read[0] in ('[', '{', '<'):
            # range/list/array types
            # this is an unknown type, even though _type itself may
            # be known. e.g. a list on integers will have _type as 'int'
            # but the corresponding value can not be deserialized as an
            # integer
            value, read = cls._parse_range_list_array(read)
            if deserialize:
                # prevent printing on subsequent calls if we find a
                # list within a list, etc.
                warnings.warn(
                    "GstStructure received a range/list/array of type "
                    "{}, which can not be deserialized. Storing the "
                    "value as {}.".format(_type, value))
        else:
            match = cls.FIELD_VALUE_REGEX.match(read)
            if match is None:
                cls._string_val_err(
                    read, "does not have a valid value format",
                    "...")
            read = read[match.end("end"):]
            value = match.group("value")
            if deserialize:
                if _type in cls.KNOWN_TYPES:
                    type_is_unknown = False
                    try:
                        value = cls.deserialize_value(_type, value)
                    except ValueError as err:
                        cls._string_val_err(
                            read, "contains an invalid typed value:\n"
                            "{!s}".format(err), "...")
                else:
                    warnings.warn(
                        "GstStructure found a type {} that is unknown. "
                        "The corresponding value ({}) will not be "
                        "deserialized and will be stored as given."
                        "".format(_type, value))
        if type_is_unknown and _type is not None:
            _type = cls._make_type_unknown(_type)
        return _type, value, read

    @classmethod
    def _parse_field(cls, read):
        match = cls.FIELD_START_REGEX.match(read)
        if match is None:
            cls._string_val_err(
                read, "does not have a valid 'key=...' format", "...")
        key = match.group("key")
        read = read[match.end("end"):]
        _type, value, read = cls._parse_value(read)
        return key, (_type, value), read

    @classmethod
    def _parse_fields(cls, read):
        fields = {}
        while read and read[0] != ';':
            if read[0] != ',':
                cls._string_val_err(
                    read, "does not separate fields with commas", "...")
            read = read[1:]
            key, entry, read = cls._parse_field(read)
            if entry is not None:
                fields[key] = entry
        if read:
            # read[0] == ';'
            read = read[1:]
        return fields, read

    @classmethod
    def _parse(cls, read):
        """Emulates gst_structure_from_string"""
        name, read = cls._parse_name(read)
        fields = cls._parse_fields(read)[0]
        # ignore returned end of string -^
        return (name, fields)

    @classmethod
    def deserialize_value(cls, _type, value):
        """Return the value as the corresponding type"""
        _type = cls.TYPE_ALIAS.get(_type, _type)
        if _type in cls.INT_TYPES or _type in cls.UINT_TYPES:
            try:
                value = int(value)
            except ValueError:
                cls._val_read_err(_type, value)
            if _type in cls.UINT_TYPES and value < 0:
                cls._val_read_err(_type, value)
        elif _type in cls.FLOAT_TYPES:
            try:
                value = float(value)
            except ValueError:
                cls._val_read_err(_type, value)
        elif _type in cls.BOOLEAN_TYPES:
            try:
                value = cls.deserialize_boolean(value)
            except ValueError:
                cls._val_read_err(_type, value)
        elif _type in cls.FRACTION_TYPES:
            try:
                value = str(Fraction(value))  # store internally as a str
            except ValueError:
                cls._val_read_err(_type, value)
        elif _type in cls.STRING_TYPES:
            try:
                value = cls.deserialize_string(value)
            except ValueError as err:
                cls._val_read_err(_type, value, err)
        else:
            raise ValueError(
                "The type {} is unknown, so the value ({}) can not "
                "be deserialized.".format(_type, value))
        return value

    @classmethod
    def serialize_value(cls, _type, value):
        """Serialize the typed value as a string"""
        _type = cls.TYPE_ALIAS.get(_type, _type)
        if _type in cls.INT_TYPES + cls.UINT_TYPES + cls.FLOAT_TYPES \
                + cls.FRACTION_TYPES:
            return str(value)
        if _type in cls.BOOLEAN_TYPES:
            if value:
                return "true"
            return "false"
        if _type in cls.STRING_TYPES:
            if value is not None and type(value) is not str:
                # TODO: remove once python2 has ended
                # will only happen in python2 when we have unicode
                value = value.encode("utf8")
            return cls.serialize_string(value)
        raise ValueError(
            "The type {} is unknown, so the value ({}) can not be "
            "serialized.".format(_type, str(value)))

    # see GST_ASCII_IS_STRING in gst_private.h
    GST_ASCII_CHARS = [
        ord(l) for l in "abcdefghijklmnopqrstuvwxyz"
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        "0123456789"
                        "_-+/:."
    ]
    LEADING_OCTAL_CHARS = [ord(l) for l in "0123"]
    OCTAL_CHARS = [ord(l) for l in "01234567"]

    @classmethod
    def serialize_string(cls, read):
        """
        Emulates gst_value_serialize_string.
        Accepts a bytes, str or None type.
        Returns a str type.
        """
        if read is None:
            return "NULL"
        if read == "NULL":
            return "\"NULL\""
        if type(read) is bytes:
            # NOTE: in python2 this will be True if read is a str type
            # in python3 it will not
            pass
        elif type(read) is str:
            read = read.encode()
        else:
            raise TypeError("Expect a None, str, or a bytes type")
        if not read:
            return '""'
        added_wrap = False
        ser_string_list = []
        for byte in bytearray(read):
            # For python3 we could have just called `byte in read`
            # For python2 we need the `bytearray(read)` cast to convert
            # the str type to int
            # TODO: simplify once python2 has ended
            if byte in cls.GST_ASCII_CHARS:
                ser_string_list.append(chr(byte))
            elif byte < 0x20 or byte >= 0x7f:
                ser_string_list.append("\\{:03o}".format(byte))
                added_wrap = True
            else:
                ser_string_list.append("\\" + chr(byte))
                added_wrap = True
        if added_wrap:
            ser_string_list.insert(0, '"')
            ser_string_list.append('"')
        return "".join(ser_string_list)

    @classmethod
    def deserialize_string(cls, read):
        """
        Emulates gst_value_deserialize_string.
        Accepts a str type.
        Returns a str or None type.
        """
        if not type(read) is str:
            raise TypeError("Expected a str type")
        if read == "NULL":
            return None
        if not read:
            return ""
        if read[0] != '"' and read[-1] != '"':
            return read

        if type(read) is bytes:
            # TODO: remove once python2 has ended
            read_array = bytearray(read)
        else:
            read_array = bytearray(read.encode())
        byte_list = []
        bytes_iter = iter(read_array)

        def next_byte():
            try:
                return next(bytes_iter)
            except StopIteration:
                cls._string_val_err(read, "end unexpectedly")

        byte = next_byte()
        if byte != ord('"'):
            cls._string_val_err(
                read, "does not start with '\"', but ends with '\"'")
        while True:
            byte = next_byte()
            if byte in cls.GST_ASCII_CHARS:
                byte_list.append(byte)
            elif byte == ord('"'):
                try:
                    next(bytes_iter)
                except StopIteration:
                    # expect there to be no more bytes
                    break
                cls._string_val_err(
                    read, "contains an un-escaped '\"' before the end")
            elif byte == ord('\\'):
                byte = next_byte()
                if byte in cls.LEADING_OCTAL_CHARS:
                    # could be the start of an octal
                    byte2 = next_byte()
                    byte3 = next_byte()
                    if byte2 in cls.OCTAL_CHARS and byte3 in cls.OCTAL_CHARS:
                        nums = [b - ord('0') for b in (byte, byte2, byte3)]
                        byte = (nums[0] << 6) + (nums[1] << 3) + nums[2]
                        byte_list.append(byte)
                    else:
                        cls._string_val_err(
                            read, "contains the start of an octal "
                            "sequence but not the end")
                else:
                    if byte == 0:
                        cls._string_val_err(
                            read, "contains a null byte after an escape")
                    byte_list.append(byte)
            else:
                cls._string_val_err(
                    read, "contains an unexpected un-escaped character")
        out_str = bytes(bytearray(byte_list))
        if type(out_str) is str:
            # TODO: remove once python2 has ended
            # and simplify above to only call bytes(byte_list)
            return out_str
        try:
            return out_str.decode()
        except (UnicodeError, ValueError):
            cls._string_val_err(
                read, "contains invalid utf-8 byte sequences")

    @staticmethod
    def deserialize_boolean(read):
        """Return a boolean"""
        if type(read) is bool:
            return read
        if type(read) is int and read in (0, 1):
            return bool(read)
        if read.lower() in ("true", "t", "yes", "1"):
            return True
        if read.lower() in ("false", "f", "no", "0"):
            return False
        raise ValueError("Unknown boolean value {!s}".format(read))


@otio.core.register_type
class XgesTrack(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema for storing a GESTrack.

    Not to be confused with OpenTimelineIO's schema.Track.
    """
    _serializable_label = "XgesTrack.1"

    caps = otio.core.serializable_field(
        "caps", str, "The GstCaps of the track")
    track_type = otio.core.serializable_field(
        "track-type", int, "The GESTrackType of the track")
    properties = otio.core.serializable_field(
        "properties", GstStructure, "The GObject properties of the track")
    metadatas = otio.core.serializable_field(
        "metadatas", GstStructure, "Metadata for the track")

    def __init__(
            self, caps="ANY", track_type=GESTrackType.UNKNOWN,
            properties=None, metadatas=None):
        """
        Initialize the XgesTrack.

        properties and metadatas are passed as the second argument to
        GstStructure.
        """
        otio.core.SerializableObject.__init__(self)
        if type(caps) is not str:
            if isinstance(caps, type(u"")):
                # TODO: remove once python2 has ended
                caps = caps.encode("utf8")
            else:
                raise TypeError("Expect a str type for the caps")
        self.caps = caps
        if type(track_type) is not int:
            raise TypeError("Expect an int type for the track_type")
        if track_type not in GESTrackType.ALL_TYPES:
            raise InvalidValueError(
                "track_type", track_type, "a GESTrackType")
        self.track_type = track_type
        self.properties = GstStructure("properties", properties)
        self.metadatas = GstStructure("metadatas", metadatas)

    def __repr__(self):
        return \
            "XgesTrack(caps={}, track_type={}, "\
            "properties={}, metadatas={})".format(
                repr(self.caps), repr(self.track_type),
                repr(self.properties), repr(self.metadatas))

    @classmethod
    def new_from_otio_track_kind(cls, kind):
        """Return a new default XgesTrack for the given track kind"""
        return cls.new_from_track_type(GESTrackType.from_otio_kind(kind))

    @classmethod
    def new_from_track_type(cls, track_type):
        """Return a new default XgesTrack for the given track type"""
        props = {}
        if track_type == GESTrackType.VIDEO:
            caps = "video/x-raw(ANY)"
            # TODO: remove restriction-caps property once the GES
            # library supports default, non-NULL restriction-caps for
            # GESVideoTrack (like GESAudioTrack).
            # For time being, framerate is needed for stability.
            props["restriction-caps"] = \
                ("string", "video/x-raw, framerate=(fraction)30/1")
        elif track_type == GESTrackType.AUDIO:
            caps = "audio/x-raw(ANY)"
        else:
            raise UnhandledValueError("track_type", track_type)
        props["mixing"] = ("boolean", True)
        return cls(caps, track_type, props)
