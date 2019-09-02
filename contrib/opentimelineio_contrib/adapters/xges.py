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
    def _get_from_properties(xmlelement, fieldname, default=None):
        structure = GstStructure(
            xmlelement.get("properties", "properties;"))
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
        metas = GstStructure(timeline.attrib.get("metadatas", "metadatas;"))
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
        metas = GstStructure(project.attrib.get("metadatas", "metadatas;"))
        otio_project = otio.schema.SerializableCollection(
            name=metas.get('name', ""),
            metadata={
                META_NAMESPACE: {"metadatas": project.attrib.get(
                    "metadatas", "metadatas")}
            }
        )
        timeline = project.find("./timeline")
        self._set_rate_from_timeline(timeline)

        otio_timeline = otio.schema.Timeline(
            name=metas.get('name') or "unnamed",
            metadata={
                META_NAMESPACE: {
                    "metadatas": timeline.attrib.get("metadatas", "metadatas;"),
                    "properties": timeline.attrib.get("properties", "properties;")
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
            return False

        clips_for_type = []
        for clip in clips:
            if int(clip.attrib['track-types']) & track_type:
                clips_for_type.append(clip)

        return clips_for_type

    def _tracks_from_layer_clips(self, layer, all_names):
        all_clips = layer.findall('./clip')
        tracks = []
        for track_type in [GESTrackType.VIDEO, GESTrackType.AUDIO]:
            clips = self._get_clips_for_type(all_clips, track_type)
            if not clips:
                continue

            track = otio.schema.Track()
            track.kind = GESTrackType.to_otio_type(track_type)
            self._add_clips_to_track(clips, track, all_names)

            tracks.append(track)
        return tracks

    def _add_clips_to_track(self, clips, track, all_names):
        for clip in clips:
            otio_composable = self._create_otio_composable_from_clip(
                clip, all_names)
            if otio_composable is None:
                continue

            clip_offset = self.to_rational_time(int(clip.attrib['start']))
            if clip_offset > track.duration():
                track.append(
                    self._create_otio_gap(
                        self.to_rational_time(0),
                        (clip_offset - track.duration())
                    )
                )

            track.append(otio_composable)
        return track

    def _get_clip_name(self, clip, all_names):
        i = 0
        tmpname = name = clip.get("name", GstStructure(
                                  clip.get("properties", "properties;")).get("name"))
        while True:
            if tmpname not in all_names:
                all_names.add(tmpname)
                return tmpname

            i += 1
            tmpname = name + '_%d' % i

    def _create_otio_transition(self, clip, all_names):
        start = self.to_rational_time(int(clip.attrib["start"]))
        end = start + self.to_rational_time(int(clip.attrib["duration"]))
        cut_point = otio.opentime.RationalTime(
            (end.value - start.value) / 2.0,
            start.rate
        )

        return otio.schema.Transition(
            name=self._get_clip_name(clip, all_names),
            transition_type=TRANSITION_MAP.get(
                clip.attrib["asset-id"], otio.schema.TransitionTypes.Custom
            ),
            in_offset=cut_point,
            out_offset=cut_point,
        )

    def _create_otio_clip(self, clip, all_names):
        source_range = otio.opentime.TimeRange(
            start_time=self.to_rational_time(int(clip.attrib["inpoint"])),
            duration=self.to_rational_time(int(clip.attrib["duration"])),
        )

        return otio.schema.Clip(
            name=self._get_clip_name(clip, all_names),
            source_range=source_range,
            media_reference=self._reference_from_id(
                clip.get("asset-id"), clip.get("type-name")),
        )

    def _create_otio_composable_from_clip(self, clip, all_names):
        otio_composable = None

        if clip.get("type-name") == "GESTransitionClip":
            otio_composable = self._create_otio_transition(clip, all_names)
        elif clip.get("type-name") == "GESUriClip":
            otio_composable = self._create_otio_clip(clip, all_names)

        if otio_composable is None:
            print("Could not represent: %s" % clip.attrib)
            return None

        otio_composable.metadata[META_NAMESPACE] = {
            "properties": clip.get("properties", "properties;"),
            "metadatas": clip.get("metadatas", "metadatas;"),
        }

        return otio_composable

    def _create_otio_gap(self, start, duration):
        source_range = otio.opentime.TimeRange(
            start_time=start,
            duration=duration
        )
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
            "properties": asset.get("properties"),
            "metadatas": asset.get("metadatas"),
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

    def __init__(self, input_otio):
        self.container = input_otio
        self.rate = 25.0

    @staticmethod
    def to_gstclocktime(rational_time):
        """
        This converts a RationalTime object to a GstClockTime

        Args:
            rational_time (RationalTime): This is a RationalTime object

        Returns:
            int: A time in nanosecond
        """
        return int(rational_time.value_rescaled_to(1) * GST_SECOND)

    def _insert_new_sub_element(self, into_parent, tag, attrib=None, text=''):
        elem = ElementTree.SubElement(into_parent, tag, **attrib or {})
        elem.text = text
        return elem

    def _get_element_properties(self, element):
        return element.metadata.get(META_NAMESPACE, {}).get("properties", "properties;")

    def _get_element_metadatas(self, element):
        return element.metadata.get(META_NAMESPACE, {}).get("metadatas", "metadatas;")

    def _serialize_ressource(self, ressources, ressource, asset_type):
        if isinstance(ressource, otio.schema.MissingReference):
            return

        if ressources.find("./asset[@id='%s'][@extractable-type-name='%s']" % (
                ressource.target_url, asset_type)) is not None:
            return

        properties = GstStructure(self._get_element_properties(ressource))
        if properties.get('duration') is None:
            properties.set(
                'duration', 'guint64',
                self.to_gstclocktime(ressource.available_range.duration))

        self._insert_new_sub_element(
            ressources, 'asset',
            attrib={
                "id": ressource.target_url,
                "extractable-type-name": 'GESUriClip',
                "properties": str(properties),
                "metadatas": self._get_element_metadatas(ressource),
            }
        )

    def _get_transition_times(self, offset, otio_transition):
        rational_offset = otio.opentime.RationalTime(
            (float(offset) * self.rate) / float(GST_SECOND),
            self.rate
        )
        start = rational_offset - otio_transition.in_offset
        end = rational_offset + otio_transition.out_offset

        return (
            0, self.to_gstclocktime(start),
            self.to_gstclocktime(end - start))

    def _serialize_clip(
            self,
            otio_track,
            layer,
            layer_priority,
            ressources,
            otio_clip,
            clip_id,
            offset
    ):

        # FIXME - Figure out a proper way to determine clip type!
        asset_id = "GESTitleClip"
        asset_type = "GESTitleClip"

        if isinstance(otio_clip, otio.schema.Transition):
            asset_type = "GESTransitionClip"
            asset_id = TRANSITION_MAP.get(otio_clip.transition_type, "crossfade")
            inpoint, offset, duration = self._get_transition_times(offset, otio_clip)
        else:
            inpoint = self.to_gstclocktime(otio_clip.source_range.start_time)
            duration = self.to_gstclocktime(otio_clip.source_range.duration)

            if not isinstance(otio_clip.media_reference, otio.schema.MissingReference):
                asset_id = otio_clip.media_reference.target_url
                asset_type = "GESUriClip"

            self._serialize_ressource(ressources, otio_clip.media_reference,
                                      asset_type)

        if otio_track.kind == otio.schema.TrackKind.Audio:
            track_types = GESTrackType.AUDIO
        elif otio_track.kind == otio.schema.TrackKind.Video:
            track_types = GESTrackType.VIDEO
        else:
            raise ValueError("Unhandled track type: %s" % otio_track.kind)

        properties = otio_clip.metadata.get(META_NAMESPACE, {}).get("properties")
        if properties is None:
            properties = str(GstStructure(
                "properties", {"name": ("string", str(otio_clip.name))}))
        return self._insert_new_sub_element(
            layer, 'clip',
            attrib={
                "id": str(clip_id),
                "properties": properties,
                "asset-id": str(asset_id),
                "type-name": str(asset_type),
                "track-types": str(track_types),
                "layer-priority": str(layer_priority),
                "start": str(offset),
                "rate": '0',
                "inpoint": str(inpoint),
                "duration": str(duration),
                "metadatas": self._get_element_metadatas(otio_clip),
            }
        )

    def _serialize_tracks(self, timeline, otio_timeline):
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
        for otio_track in otio_timeline.tracks:
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

    def _serialize_layer(self, timeline, layers, layer_priority):
        if layer_priority not in layers:
            layers[layer_priority] = self._insert_new_sub_element(
                timeline, 'layer',
                attrib={
                    "priority": str(layer_priority),
                }
            )

    def _serialize_timeline_element(self, timeline, layers, layer_priority,
                                    offset, otio_track, otio_element,
                                    ressources, all_clips):
        self._serialize_layer(timeline, layers, layer_priority)
        layer = layers[layer_priority]
        if isinstance(otio_element, (otio.schema.Clip, otio.schema.Transition)):
            element = self._serialize_clip(otio_track, layer, layer_priority,
                                           ressources, otio_element,
                                           str(len(all_clips)), offset)
            all_clips.add(element)
            if isinstance(otio_element, otio.schema.Transition):
                # Make next clip overlap
                return int(element.get("start")) - offset
        elif not isinstance(otio_element, otio.schema.Gap):
            print("FIXME: Add support for %s" % type(otio_element))
            return 0

        return self.to_gstclocktime(otio_element.source_range.duration)

    def _make_element_names_unique(self, all_names, otio_element):
        if isinstance(otio_element, otio.schema.Gap):
            return

        if not isinstance(otio_element, otio.schema.Track):
            i = 0
            name = otio_element.name
            while True:
                if name not in all_names:
                    otio_element.name = name
                    break

                i += 1
                name = otio_element.name + '_%d' % i
            all_names.add(otio_element.name)

        if isinstance(otio_element, (otio.schema.Stack, otio.schema.Track)):
            for sub_element in otio_element:
                self._make_element_names_unique(all_names, sub_element)

    def _make_timeline_elements_names_unique(self, otio_timeline):
        element_names = set()
        for track in otio_timeline.tracks:
            for element in track:
                self._make_element_names_unique(element_names, element)

    def _serialize_timeline(self, project, ressources, otio_timeline):
        metadatas = GstStructure(self._get_element_metadatas(otio_timeline))
        rate = self._framerate_to_frame_duration(
            otio_timeline.duration().rate)
        if rate:
            metadatas.set("framerate", "fraction", Fraction(rate))
        timeline = self._insert_new_sub_element(
            project, 'timeline',
            attrib={
                "properties": self._get_element_properties(otio_timeline),
                "metadatas": str(metadatas),
            }
        )
        self._serialize_tracks(timeline, otio_timeline)

        self._make_timeline_elements_names_unique(otio_timeline)

        all_clips = set()
        layers = {}

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

        all_tracks = []
        for i, otio_track in enumerate(video_tracks):
            all_tracks.append(otio_track)
            try:
                all_tracks.append(audio_tracks[i])
            except IndexError:
                pass

        if len(audio_tracks) > len(video_tracks):
            all_tracks.extend(audio_tracks[len(video_tracks):])

        for layer_priority, otio_track in enumerate(all_tracks):
            self._serialize_layer(timeline, layers, layer_priority)
            offset = 0
            for otio_element in otio_track:
                offset += self._serialize_timeline_element(
                    timeline, layers, layer_priority, offset,
                    otio_track, otio_element, ressources, all_clips,
                )

        for layer in layers.values():
            layer[:] = sorted(layer, key=lambda child: int(child.get("start")))

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

        metadatas = GstStructure(self._get_element_metadatas(self.container))
        if self.container.name is not None:
            metadatas.set("name", "string", self.container.name)
        if not isinstance(self.container, otio.schema.Timeline):
            project = self._insert_new_sub_element(
                xges, 'project',
                attrib={
                    "properties": self._get_element_properties(self.container),
                    "metadatas": str(metadatas),
                }
            )

            if len(self.container) > 1:
                print(
                    "WARNING: Only one timeline supported, using *only* the first one.")

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
        self.rate = otio_timeline.duration().rate
        self._serialize_timeline(project, ressources, otio_timeline)

        # with indentations.
        string = ElementTree.tostring(xges, encoding="UTF-8")
        dom = minidom.parseString(string)
        return dom.toprettyxml(indent='    ')


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
        a dictionary containing the fields data, where each entry is
        a two-entry tuple containing the type name and value.
        """
        otio.core.SerializableObject.__init__(self)
        if type(text) is not str:
            if isinstance(text, type(u"")):
                # TODO: remove once python2 has ended
                text = text.encode("utf8")
            else:
                raise TypeError("Expect a str type for the first argument")
        if fields is not None:
            if type(fields) is not dict:
                try:
                    fields = dict(fields)
                except (TypeError, ValueError):
                    raise TypeError(
                        "Expect a dict-like type for the second argument")
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

        properties and metadatas can either be GstStructures, strings,
        None, or dict-like objects.
        If it is a GstStructure, then the fields are passed to
        GstStructure() (the structure name is ignored).
        If it is a string, then the string is to be parsed by
        GstStructure().
        If it is None, then an empty GstStructure will be made.
        Otherwise, it will be passed as the fields for GstStructure.
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
        self.properties = self._get_structure(properties, "properties")
        self.metadatas = self._get_structure(metadatas, "metadatas")

    @staticmethod
    def _get_structure(struct, struct_name):
        if isinstance(struct, GstStructure):
            return GstStructure(struct_name, struct.fields)
        if type(struct) in (str, type(u"")):
            # TODO: only check if str once python2 has ended
            struct = GstStructure(struct)
            if struct.name != struct_name:
                raise ValueError(
                    "The given string contains the structure name '%s'"
                    ", but '%s' was expected"
                    % (struct.name, struct_name))
            return struct
        # assume a dict-like type that contains the fields
        return GstStructure(struct_name, struct)

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
