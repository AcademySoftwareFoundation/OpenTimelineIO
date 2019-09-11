#
# Copyright (C) 2019 Igalia S.L
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

from fractions import Fraction
from xml.etree import ElementTree
from xml.dom import minidom
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


class GstParseError(otio.exceptions.OTIOError):
    pass


class GESTrackType:
    UNKNOWN = 1 << 0
    AUDIO = 1 << 1
    VIDEO = 1 << 2
    TEXT = 1 << 3
    CUSTOM = 1 << 4
    MAX = UNKNOWN | AUDIO | VIDEO | TEXT | CUSTOM

    @staticmethod
    def to_otio_type(_type):
        if _type == GESTrackType.AUDIO:
            return otio.schema.TrackKind.Audio
        elif _type == GESTrackType.VIDEO:
            return otio.schema.TrackKind.Video

        raise GstParseError("Can't translate track type %s" % _type)


GST_CLOCK_TIME_NONE = 18446744073709551615
GST_SECOND = 1000000000


class XGES:
    """
    This object is responsible for knowing how to convert an xGES
    project into an otio timeline
    """

    def __init__(self, xml_string):
        self.xges_xml = ElementTree.fromstring(xml_string)
        self.rate = 25.0

    @staticmethod
    def _get_properties(xmlelement):
        return GstStructure(xmlelement.get("properties", "properties;"))

    @staticmethod
    def _get_metadatas(xmlelement):
        return GstStructure(xmlelement.get("metadatas", "metadatas;"))

    def _get_from_properties(self, xmlelement, fieldname, default=None):
        structure = self._get_properties(xmlelement)
        return structure.get(fieldname, default)

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
                raise GstParseError(
                    "The structure name in the caps (%s) is not of "
                    "the correct format" % (caps))
            caps = caps[match.end("end"):]
            try:
                fields, caps = GstStructure._parse_fields(caps)
            except ValueError as err:
                raise GstParseError(
                    "Failed to read the fields in the caps (%s):\n"
                    + str(err))
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
        metas = self._get_metadatas(timeline)
        rate = metas.get("framerate")
        if rate is None:
            video_track = timeline.find("./track[@track-type='4']")
            if video_track is not None:
                res_caps = self._get_from_properties(
                    video_track, "restriction-caps")
                rate = self._get_from_caps(res_caps, "framerate")
        if rate is None:
            return
        try:
            rate = Fraction(rate)
        except ValueError:
            print(
                "WARNING: read a framerate that is not a fraction. "
                "Ignoring")
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

    def to_otio(self):
        """
        Convert an xges to an otio

        Returns:
            OpenTimeline: An OpenTimeline Timeline object
        """

        project = self.xges_xml.find("./project")
        metas = self._get_metadatas(project)
        otio_project = otio.schema.SerializableCollection(
            name=metas.get('name', ""),
            metadata={
                META_NAMESPACE: {"metadatas": metas}
            }
        )
        timeline = project.find("./timeline")
        self._set_rate_from_timeline(timeline)

        otio_timeline = otio.schema.Timeline(
            name=metas.get('name') or "unnamed",
            metadata={
                META_NAMESPACE: {
                    "metadatas": self._get_metadatas(timeline),
                    "properties": self._get_properties(timeline)
                }
            }
        )
        all_names = set()
        self._add_layers_to_stack(
            timeline, otio_timeline.tracks, all_names)
        otio_project.append(otio_timeline)
        return otio_project

    def _add_layers_to_stack(self, timeline, stack, all_names):
        sort_tracks = []
        for layer in timeline.findall("./layer"):
            priority = layer.get("priority")
            tracks = self._tracks_from_layer_clips(layer, all_names)
            for track in tracks:
                sort_tracks.append((track, priority))
        sort_tracks.sort(key=lambda ent: ent[1], reverse=True)
        # NOTE: smaller priority is later in the list
        for track in (ent[0] for ent in sort_tracks):
            stack.append(track)

    def _get_clips_for_type(self, clips, track_type):
        if not clips:
            return []

        clips_for_type = []
        for clip in clips:
            if int(clip.attrib['track-types']) & track_type:
                clips_for_type.append(clip)

        return clips_for_type

    def _tracks_from_layer_clips(self, layer, all_names):
        all_clips = layer.findall('./clip')
        tracks = []
        # FIXME: should we be restricting to the track-types found in
        # the xges track elements. E.g., should we be building an extra
        # otio track for the uri clips that have track-types=6, when we
        # only have a single xges track that is track-type=2?
        for track_type in [GESTrackType.VIDEO, GESTrackType.AUDIO]:
            clips = self._get_clips_for_type(all_clips, track_type)
            if not clips:
                continue
            otio_items, otio_transitions = \
                self._create_otio_composables_from_clips(clips, all_names)

            track = otio.schema.Track()
            track.kind = GESTrackType.to_otio_type(track_type)
            self._add_otio_composables_to_track(
                track, otio_items, otio_transitions)

            tracks.append(track)
        return tracks

    def _create_otio_composables_from_clips(self, clips, all_names):
        otio_transitions = []
        otio_items = []
        for clip in clips:
            clip_type = clip.get("type-name")
            start = int(clip.get("start"))
            inpoint = int(clip.get("inpoint"))
            duration = int(clip.get("duration"))
            otio_composable = None
            if clip_type == "GESTransitionClip":
                otio_composable = self._otio_transition_from_clip(
                    clip, all_names)
            elif clip_type == "GESUriClip":
                otio_composable = self._otio_item_from_uri_clip(
                    clip, all_names)
            else:
                # TODO: support other clip types
                # maybe represent a GESTitleClip as a gap, with the text
                # in the metadata?
                # or as a clip with a MissingReference?
                print("Could not represent %s clip type" % (clip_type))

            if otio_composable:
                # TODO: use GstStructure for properties and metadatas,
                # TODO: allow metadata to be set by:
                #   _otio_transition_from_clip and
                #   _otio_item_from_uri_clip
                otio_composable.metadata[META_NAMESPACE] = {
                    "properties": self._get_properties(clip),
                    "metadatas": self._get_metadatas(clip)
                }

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
        item, and its start, inpoint and duration times (from the
        corresponding xges clip). The source_range will be set before
        insertion into the track.
        transitions argument should be an array of dicts, containing an
        otio transition, and its start and duration times (from the
        corresponding xges transition clip). The in_offset and
        out_offset will be set before insertion into the track.
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
                    raise GstParseError(
                        "Found more than one transition with start=%i "
                        " and duration=%i for the same track-kind "
                        "within a single layer"
                        % (next_item["start"], duration))
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
            raise GstParseError(
                "xges layer contained %i transitions that could not be "
                "associated with any clip overlap (for a given "
                "track-kind)" % (len(transitions)))

    def _get_clip_name(self, clip, all_names):
        i = 0
        tmpname = name = clip.get(
            "name", self._get_from_properties(clip, "name", ""))
        while True:
            if tmpname not in all_names:
                all_names.add(tmpname)
                return tmpname

            i += 1
            tmpname = name + '_%d' % i

    def _otio_transition_from_clip(self, clip, all_names):
        return otio.schema.Transition(
            name=self._get_clip_name(clip, all_names),
            transition_type=TRANSITION_MAP.get(
                clip.attrib["asset-id"],
                otio.schema.TransitionTypes.Custom))

    def _default_otio_transition(self):
        return otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve)

    def _otio_item_from_uri_clip(self, clip, all_names):
        # FIXME: check asset to see if extractable type is
        # a GESTimeline and/or a <xges> lives below it
        # then we want a stack, not a clip
        return otio.schema.Clip(
            name=self._get_clip_name(clip, all_names),
            media_reference=self._reference_from_id(
                clip.get("asset-id"), clip.get("type-name")))

    def _create_otio_gap(self, gst_duration):
        source_range = otio.opentime.TimeRange(
            self.to_rational_time(0),
            self.to_rational_time(gst_duration))
        return otio.schema.Gap(source_range=source_range)

    def _reference_from_id(self, asset_id, asset_type="GESUriClip"):
        asset = self._asset_by_id(asset_id, asset_type)
        if asset is None:
            return None
        if not asset.get("id", ""):
            return otio.schema.MissingReference()

        duration = GST_CLOCK_TIME_NONE
        if asset_type == "GESUriClip":
            tmp_dur = self._get_from_properties(asset, "duration", duration)
            if type(tmp_dur) is int:
                duration = tmp_dur
            else:
                print("WARNING: read a duration that is not an int")

        available_range = otio.opentime.TimeRange(
            start_time=self.to_rational_time(0),
            duration=self.to_rational_time(duration)
        )
        ref = otio.schema.ExternalReference(
            target_url=asset.get("id"),
            available_range=available_range
        )

        ref.metadata[META_NAMESPACE] = {
            "properties": self._get_properties(asset),
            "metadatas": self._get_metadatas(asset)
        }

        return ref

    # --------------------
    # search helpers
    # --------------------
    def _asset_by_id(self, asset_id, asset_type):
        return self.xges_xml.find(
            "./project/ressources/asset[@id='{}'][@extractable-type-name='{}']".format(
                asset_id, asset_type)
        )

    def _timeline_element_by_name(self, timeline, name):
        for clip in timeline.findall("./layer/clip"):
            if self._get_from_properties(clip, "name") == name:
                return clip

        return None


class XGESOtio:
    """
    This object is responsible for knowing how to convert an otio
    timeline into an xGES project
    """

    def __init__(self, input_otio):
        self.container = input_otio

    @staticmethod
    def to_gstclocktime(otio_time):
        """
        Convert an otio time into a GstClockTime. If a RationalTime is
        received, returns a single int representing the time in
        nanoseconds. If a TimeRange is received, returns a tuple of the
        start_time and duration as ints representing the times in
        nanoseconds.
        """
        if isinstance(otio_time, otio.opentime.RationalTime):
            return int(otio_time.value_rescaled_to(1) * GST_SECOND)
        if isinstance(otio_time, otio.opentime.TimeRange):
            return (
                int(otio_time.start_time.value_rescaled_to(1) * GST_SECOND),
                int(otio_time.duration.value_rescaled_to(1) * GST_SECOND))

    def _insert_new_sub_element(self, into_parent, tag, attrib=None, text=''):
        elem = ElementTree.SubElement(into_parent, tag, attrib or {})
        elem.text = text
        return elem

    def _get_element_structure(self, element, struct_name, sub_key=None):
        struct = None
        _dict = element.metadata.get(META_NAMESPACE)
        if _dict and sub_key is not None:
            _dict = _dict.get(sub_key)
        if _dict:
            struct = _dict.get(struct_name)
        if isinstance(struct, GstStructure):
            return struct
        elif struct is not None:
            print(
                "WARNING: ignoring the metadata found under \"%s\" "
                "since it is not a GstStructure as expected"
                % (struct_name))
        return GstStructure(struct_name + ";")

    def _get_element_properties(self, element, sub_key=None):
        return self._get_element_structure(element, "properties", sub_key)

    def _get_element_metadatas(self, element, sub_key=None):
        return self._get_element_structure(element, "metadatas", sub_key)

    def _serialize_external_reference_to_ressource(
            self, reference, ressources):
        # FIXME: target_url may contain special characters (e.g. quotes
        # or non-ascii utf8) this will need to be converted in the same
        # way as the GES library, otherwise the asset_id will not be
        # correctly loaded by GES.
        # We also need to make sure there aren't any un-escaped
        # apostrophes which will make the next search fail!
        if ressources.find(
                "./asset[@id='%s'][@extractable-type-name='GESUriClip']"
                % (reference.target_url)) is not None:
            return

        properties = self._get_element_properties(reference)
        if properties.get('duration') is None:
            a_range = reference.available_range
            if a_range is not None:
                properties.set(
                    "duration", "guint64",
                    sum(self.to_gstclocktime(a_range)))
                # TODO: check that this is correct approach for when
                # start_time is not 0.
                # duration is the sum of the a_range start_time and
                # duration we ignore that frames before start_time are
                # not available

        self._insert_new_sub_element(
            ressources, 'asset',
            attrib={
                "id": reference.target_url,
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
            otio_start_time, otio_duration = self.to_gstclocktime(
                otio_composable.trimmed_range())
            otio_end = prev_otio_end + otio_duration
            start = prev_otio_end
            duration = otio_duration
            inpoint = otio_start_time
            if isinstance(prev_composable, otio.schema.Transition):
                in_offset = self.to_gstclocktime(
                    prev_composable.in_offset)
                start -= in_offset
                duration += in_offset
                inpoint -= in_offset
            if isinstance(next_composable, otio.schema.Transition):
                duration += self.to_gstclocktime(
                    next_composable.out_offset)
        elif isinstance(otio_composable, otio.schema.Transition):
            otio_end = prev_otio_end
            in_offset = self.to_gstclocktime(otio_composable.in_offset)
            out_offset = self.to_gstclocktime(otio_composable.out_offset)
            start = prev_otio_end - in_offset
            duration = in_offset + out_offset
            inpoint = 0
        else:
            # NOTE: core schemas only give Item and Transition as
            # composable types
            raise TypeError(
                "Unhandled otio composable type: %s"
                % (type(otio_composable)))
        return start, duration, inpoint, otio_end

    def _serialize_composable_to_clip(
            self, otio_composable, prev_composable, next_composable,
            layer, layer_priority, otio_track_kind, ressources, clip_id,
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
                print(
                    "WARNING: GeneratorReference is not currently "
                    "supported. Treating clip as a gap.")
            else:
                print(
                    "WARNING: MediaReference schema %s is not currently "
                    "handled. Treating clip as a gap."
                    % (ref.schema_name()))
        else:
            # FIXME: add support for stacks
            # FIXME: add support for finding another Track:
            # treat as if it is a stack with no source_range, that only
            # contains the found track
            print(
                "WARNING: Otio schema %s is not currently supported "
                "within a track. Treating as a gap."
                % (otio_composable.schema_name()))

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

        if otio_track_kind == otio.schema.TrackKind.Audio:
            track_types = GESTrackType.AUDIO
        elif otio_track_kind == otio.schema.TrackKind.Video:
            track_types = GESTrackType.VIDEO
        else:
            raise ValueError("Unhandled track type: %s" % otio_track_kind)

        properties = self._get_element_properties(otio_composable)
        if not properties.get("name"):
            properties.set("name", "string", otio_composable.name)
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

    def _serialize_tracks(self, timeline, otio_stack):
        # TODO: check if XgesTrack exists in metadata
        # and use that instead if it exists.
        # Eventually want to store the XgesTrack in the metadata of
        # a schema.Stack (rather than a schema.Timeline, which this
        # function uses) once sub-projects/nested Stacks are supported

        # TODO: grab track_id from the index of the XgesTrack in a Stack
        # The correct track-id is only needed by xges effect, source
        # and binding elements, which we do not yet support anyway,
        # so any track-id will do for now
        track_id = 0
        found_track_kinds = []
        for otio_track in otio_stack:
            kind = otio_track.kind
            if kind not in found_track_kinds:
                found_track_kinds.append(kind)
                xges_track = XgesTrack.new_from_otio_track_kind(kind)
                self._insert_new_sub_element(
                    timeline, 'track',
                    attrib={
                        "caps": xges_track.caps,
                        "track-type": str(xges_track.track_type),
                        "track-id": str(track_id),
                        "properties": str(xges_track.properties),
                        "metadatas": str(xges_track.metadatas)
                    }
                )
                track_id += 1

    def _serialize_track_to_layer(
            self, otio_track, timeline, layer_priority):
        # FIXME: once substacks are supported, if a track has a
        # source_range that is *not* None, then, since GESLayers do not
        # support start/duration/inpoint we will want to create
        # a layer that has a single clip with an asset that is an xges
        # project with a single layer, we would want to return the
        # latter layer, but this would interfere with the used clip ids!
        return self._insert_new_sub_element(
            timeline, 'layer',
            attrib={"priority": str(layer_priority)})

    def _make_otio_names_unique(self, all_names, otio_composable):
        if isinstance(otio_composable, otio.schema.Gap):
            return

        if not isinstance(otio_composable, otio.schema.Track):
            i = 0
            # FIXME: name may be empty
            # Maybe choose starting name from type
            name = otio_composable.name
            while True:
                if name not in all_names:
                    # FIXME: shouldn't be editing the attributes of the
                    # the received timeline since the user may still
                    # want to keep a copy
                    otio_composable.name = name
                    break

                i += 1
                name = otio_composable.name + '_%d' % i
            all_names.add(otio_composable.name)

        if isinstance(otio_composable, otio.core.Composition):
            # FIXME: do we want to give unique names to elements within
            # a new Composition? Especially, if they are a stack (or
            # a track below another track) where they will live in a
            # subproject
            for sub_comp in otio_composable:
                self._make_otio_names_unique(all_names, sub_comp)

    def _make_stack_names_unique(self, otio_stack):
        all_names = set()
        for track in otio_stack:
            for otio_composable in track:
                self._make_otio_names_unique(
                    all_names, otio_composable)

    # TODO: change _serialize_timeline to _serialize_stack_to_project
    # replace otio_timeline.tracks with a stack, and get metadata
    # from the stack, not otio_timeline
    def _serialize_timeline(self, project, ressources, otio_timeline):
        metadatas = self._get_element_metadatas(otio_timeline)
        rate = self._framerate_to_frame_duration(
            otio_timeline.duration().rate)
        if rate:
            metadatas.set("framerate", "fraction", Fraction(rate))
        timeline = self._insert_new_sub_element(
            project, 'timeline',
            attrib={
                "properties": str(self._get_element_properties(otio_timeline)),
                "metadatas": str(metadatas),
            }
        )
        self._serialize_tracks(timeline, otio_timeline.tracks)

        self._make_stack_names_unique(otio_timeline.tracks)

        # FIXME: as part of supporting sub-stacks, take into account
        # that the top stack otio_timeline.tracks may have source_range
        # set to something other than None, in which case we will want
        # to create a single layer, with one UriClip that has a
        # subproject/xges asset which contains the actual top stack
        # information, which will allow us to set the start, inpoint,
        # and duration.
        # This is not necessary for stacks lower down since they are
        # automatically below an asset.

        # FIXME: as part of supporting sub-stacks, if a stack contains a
        # + track:
        #       do the same as now
        # + some other composable:
        #       treat as if it is a track with no source_range (?)
        #       that contains a single item that is the composable
        video_tracks = [
            t for t in otio_timeline.tracks
            if t.kind == otio.schema.TrackKind.Video and list(t)
        ]
        video_tracks.reverse()
        audio_tracks = [
            t for t in otio_timeline.tracks
            if t.kind == otio.schema.TrackKind.Audio and list(t)
        ]
        audio_tracks.reverse()

        # FIXME: why interlace the video and audio tracks?
        # e.g. what if we find in the stack, two audio tracks, followed
        # by one video, why should we order them in layers as:
        # video1, audio1, audio2? Especially when we have little
        # correspondence between the audio and video tracks.
        all_tracks = []
        for i, otio_track in enumerate(video_tracks):
            all_tracks.append(otio_track)
            try:
                all_tracks.append(audio_tracks[i])
            except IndexError:
                pass

        # FIXME: need a better way to sort tracks (see above)
        if len(audio_tracks) > len(video_tracks):
            all_tracks.extend(audio_tracks[len(video_tracks):])

        # FIXME: add a smart way to merge two tracks into one layer
        # if they are identical modulo the track-kind
        clip_id = 0
        for layer_priority, otio_track in enumerate(all_tracks):
            layer = self._serialize_track_to_layer(
                otio_track, timeline, layer_priority)
            # FIXME: should the start be effected by the global_start_time
            # on the otio timeline?
            otio_end = 0
            for otio_composable in otio_track:
                neighbours = otio_track.neighbors_of(otio_composable)
                clip_id, otio_end = self._serialize_composable_to_clip(
                    otio_composable, neighbours[0], neighbours[1],
                    layer, layer_priority, otio_track.kind, ressources,
                    clip_id, otio_end)

    # --------------------
    # static methods
    # --------------------
    @staticmethod
    def _framerate_to_frame_duration(framerate):
        frame_duration = FRAMERATE_FRAMEDURATION.get(int(framerate), "")
        if not frame_duration:
            frame_duration = FRAMERATE_FRAMEDURATION.get(float(framerate), "")
        return frame_duration

    def to_xges(self):
        xges = ElementTree.Element('ges', version="0.4")

        metadatas = self._get_element_metadatas(self.container)
        if self.container.name is not None:
            metadatas.set("name", "string", self.container.name)
        if not isinstance(self.container, otio.schema.Timeline):
            # FIXME: why would we expect something that isn't a Timeline?
            project = self._insert_new_sub_element(
                xges, 'project',
                attrib={
                    "properties": str(self._get_element_properties(self.container)),
                    "metadatas": str(metadatas),
                }
            )

            if len(self.container) > 1:
                print(
                    "WARNING: Only one timeline supported, using *only* the first one.")

            # FIXME: make sure this is actually a SerializableCollection
            otio_timeline = self.container[0]

        else:
            project = self._insert_new_sub_element(
                xges, 'project',
                attrib={
                    "metadatas": str(metadatas),
                }
            )
            otio_timeline = self.container

        ressources = self._insert_new_sub_element(project, 'ressources')
        self._serialize_timeline(project, ressources, otio_timeline)

        # with indentations.
        string = ElementTree.tostring(xges, encoding="UTF-8")
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

    INT_TYPES = ("int", "i", "gint", "glong", "gint64")
    UINT_TYPES = ("uint", "u", "guint", "gulong", "guint64")
    FLOAT_TYPES = ("float", "f", "gfloat", "double", "d", "gdouble")
    BOOLEAN_TYPES = ("boolean", "bool", "b", "gboolean")
    FRACTION_TYPES = ("fraction", "GstFraction")
    STRING_TYPES = ("string", "str", "s")

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

    def _fields_to_str(self):
        write = []
        for key in self.fields:
            entry = self.fields[key]
            write.append(
                ", %s=(%s)%s"
                % (key, entry[0], self.serialize_value(*entry)))
        return "".join(write)

    def __str__(self):
        """Emulates gst_structure_to_string"""
        self._check_name(self.name)
        return self.name + self._fields_to_str() + ";"

    def __getitem__(self, key):
        value = self.fields[key][1]
        # TODO: remove below once python2 has ended
        if not isinstance(value, str) and isinstance(value, type(u"")):
            # Only possible in python2
            return value.encode("utf8")
        return value

    @staticmethod
    def _unknown_type(_type):
        raise ValueError("The type (%s) is unknown" % (_type))

    @staticmethod
    def _shorten_str(in_string):
        MAX_LEN = 20
        if len(in_string) <= MAX_LEN:
            return in_string
        return in_string[:MAX_LEN] + "..."

    @classmethod
    def _string_val_err(cls, string_val, problem, prefix=""):
        raise ValueError(
            "Received string (%s%s) "
            % (prefix, cls._shorten_str(string_val)) + problem)

    @staticmethod
    def _val_type_err(typ, val, expect):
        raise TypeError(
            "Received value (%s) is not a %s even though the %s "
            "type was given" % (str(val), expect, typ))

    @staticmethod
    def _val_prop_err(typ, val, wrong_prop):
        raise ValueError(
            "Received value (%s) is %s even though the %s type "
            "was given" % (val, wrong_prop, typ))

    @staticmethod
    def _val_read_err(typ, val, extra=None):
        message = "Value (%s) is invalid for %s type" % (val, typ)
        if extra:
            message += ":\n" + str(extra)
        raise ValueError(message)

    def set(self, key, _type, value):
        if self.fields.get(key) == (_type, value):
            return
        if type(key) is not str:
            raise TypeError("Expected a str for the key argument")
        if type(_type) not in (str, type(u"")):
            # TODO: change to a simple check that the type is a str
            # once python2 has ended.
            # The current problem is that, in python2, otio will
            # convert _type from str to the unicode type on assignment
            # to the serializable_field 'fields'
            raise TypeError("Expected a str for the type argument")
        self._check_key(key)

        if _type in self.INT_TYPES:
            if type(value) is not int:
                self._val_type_err(_type, value, "int")
        elif _type in self.UINT_TYPES:
            if type(value) is not int:
                self._val_type_err(_type, value, "int")
            if value < 0:
                self._val_prop_err(_type, value, "negative")
        elif _type in self.FLOAT_TYPES:
            if type(value) is not float:
                self._val_type_err(_type, value, "float")
        elif _type in self.BOOLEAN_TYPES:
            if type(value) is not bool:
                self._val_type_err(_type, value, "bool")
        elif _type in self.FRACTION_TYPES:
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
            if value is not None and \
                    type(value) not in (str, type(u"")):
                # TODO: change to just str type once python2 has ended
                self._val_type_err(_type, value, "str or None")
        else:
            self._unknown_type(_type)
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
    SIMPLE_VALUE_FORMAT = r"(?P<value>" + SIMPLE_STRING + r")"
    QUOTED_VALUE_FORMAT = r'(?P<value>"(\\.|[^"])*")'
    # consume simple string or a string between quotes. Second will
    # consume anything that is escaped, including a '"'
    # NOTE: \\. is used rather than \\" since:
    #   + '"start\"end;"'  should be captured as '"start\"end"' since
    #     the '"' is escaped.
    #   + '"start\\"end;"' should be captured as '"start\\"' since the
    #     '\' is escaped, not the '"'
    # In the fist case \\. will consume '\"', and in the second it will
    # consumer '\\', as desired. The second would not work with just \\"

    @classmethod
    def _check_name(cls, name):
        if "fullmatch" in dir(re):
            # Not available in python2
            if not re.fullmatch(cls.NAME_FORMAT, name):
                raise ValueError(
                    "The name (%s) is not of the correct format" % (name))
        else:
            # TODO: remove once python2 has ended
            if not re.match(cls.NAME_FORMAT + "$", name):
                raise ValueError(
                    "The name (%s) is not of the correct format" % (name))

    @classmethod
    def _check_key(cls, key):
        if "fullmatch" in dir(re):
            if not re.fullmatch(cls.KEY_FORMAT, key):
                raise ValueError(
                    "The key (%s) is not of the correct format" % (key))
        else:
            # TODO: remove once python2 has ended
            if not re.match(cls.KEY_FORMAT + "$", key):
                raise ValueError(
                    "The key (%s) is not of the correct format" % (key))

    NAME_REGEX = re.compile(ASCII_SPACES + NAME_FORMAT + END_FORMAT)

    @classmethod
    def _parse_name(cls, read):
        match = cls.NAME_REGEX.match(read)
        if match is None:
            cls._string_val_err(
                read, "does not start with a correct name")
        name = match.group("name")
        read = read[match.end("end"):]
        return name, read

    FIELD_START = ASCII_SPACES + KEY_FORMAT + ASCII_SPACES + r"=" \
        + ASCII_SPACES + r"\(" + ASCII_SPACES + TYPE_FORMAT \
        + ASCII_SPACES + r"\)" + ASCII_SPACES
    SIMPLE_FIELD_REGEX = re.compile(
        FIELD_START + SIMPLE_VALUE_FORMAT + END_FORMAT)
    QUOTED_FIELD_REGEX = re.compile(
        FIELD_START + QUOTED_VALUE_FORMAT + END_FORMAT)

    @classmethod
    def _parse_field(cls, read):
        match = cls.SIMPLE_FIELD_REGEX.match(read)
        if match is None:
            match = cls.QUOTED_FIELD_REGEX.match(read)
            if match is None:
                cls._string_val_err(
                    read,
                    "does not have a valid 'key=(type)value' format", "...")
        key = match.group("key")
        _type = match.group("type")
        value = match.group("value")
        try:
            value = cls.deserialize_value(_type, value)
        except ValueError as err:
            cls._string_val_err(
                read,
                "contains an invalid typed value:\n" + str(err), "...")
        read = read[match.end("end"):]
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
        if _type in cls.INT_TYPES or _type in cls.UINT_TYPES:
            if type(value) is float and int(value) != value:
                cls._val_read_err(_type, value)
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
            cls._unknown_type(_type)
        return value

    @classmethod
    def serialize_value(cls, _type, value):
        """Serialize the typed value as a string"""
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
        cls._unkown_type(_type)

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
                ser_string_list.append("\\%03o" % (byte))
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
        raise ValueError("Unknown boolean value %s" % str(read))


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
        if track_type < 0 or track_type > GESTrackType.MAX:
            raise ValueError(
                "Expect the track_type to be a non-negative int "
                "< %i" % (GESTrackType.MAX))
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
        props = {}
        if kind == otio.schema.TrackKind.Video:
            caps = "video/x-raw(ANY)"
            track_type = GESTrackType.VIDEO
            # TODO: remove restriction-caps property once the GES
            # library supports default, non-NULL restriction-caps for
            # GESVideoTrack (like GESAudioTrack).
            # For time being, framerate is needed for stability.
            props["restriction-caps"] = \
                ("string", "video/x-raw, framerate=(fraction)30/1")
        elif kind == otio.schema.TrackKind.Audio:
            caps = "audio/x-raw(ANY)"
            track_type = GESTrackType.AUDIO
        else:
            raise ValueError("Received unknown otio.schema.TrackKind")
        props["mixing"] = ("boolean", True)
        return cls(caps, track_type, props)
