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
import unittest

from decimal import Decimal
from fractions import Fraction
from xml.etree import cElementTree
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


class GstStructure(object):
    """
    GstStructure parser with a "dictionary" like API.
    """
    UNESCAPE = re.compile(r'(?<!\\)\\(.)')
    INT_TYPES = "".join(
        ("int", "uint", "int8", "uint8", "int16",
         "uint16", "int32", "uint32", "int64", "uint64")
    )

    def __init__(self, text):
        self.text = text
        self.modified = False
        self.name, self.types, self.values = GstStructure._parse(text + ";")

    def __repr__(self):
        if not self.modified:
            return self.text

        res = self.name
        for key, value in self.values.items():
            value_type = self.types[key]
            res += ', %s=(%s)"%s"' % (key, value_type, self.escape(value))
        res += ';'

        return res

    def __getitem__(self, key):
        return self.values[key]

    def set(self, key, value_type, value):
        if self.types.get(key) == value_type and self.values.get(key) == value:
            return

        self.modified = True
        self.types[key] = value_type
        self.values[key] = value

    def get(self, key, default=None):
        return self.values.get(key, default)

    @staticmethod
    def _find_eos(s):
        # find next '"' without preceeding '\'
        line = 0
        while 1:  # faster than regexp for '[^\\]\"'
            p = s.index('"')
            line += p + 1
            if s[p - 1] != '\\':
                return line
            s = s[(p + 1):]
        return -1

    @staticmethod
    def escape(s):
        # XXX: The unicode type doesn't exist in Python 3 (all strings are unicode)
        # so we have to use type(u"") which works in both Python 2 and 3.
        if type(s) not in (str, type(u"")):
            return s
        return s.replace(" ", "\\ ")

    @staticmethod
    def _parse(s):
        in_string = s
        types = {}
        values = {}
        scan = True
        # parse id
        p = s.find(',')
        if p == -1:
            try:
                p = s.index(';')
            except ValueError:
                p = len(s)
            scan = False
        name = s[:p]
        # parse fields
        while scan:
            comma_space_it = p
            # skip 'name, ' / 'value, '
            while s[comma_space_it] in [' ', ',']:
                comma_space_it += 1
            s = s[comma_space_it:]
            p = s.index('=')
            k = s[:p]
            if not s[p + 1] == '(':
                raise ValueError("In %s position: %d" % (in_string, p))
            s = s[(p + 2):]  # skip 'key=('
            p = s.index(')')
            t = s[:p]
            s = s[(p + 1):]  # skip 'type)'

            if s[0] == '"':
                s = s[1:]  # skip '"'
                p = GstStructure._find_eos(s)
                if p == -1:
                    raise ValueError
                v = s[:(p - 1)]
                if s[p] == ';':
                    scan = False
                # unescape \., but not \\. (using a backref)
                # need a reverse for re.escape()
                v = v.replace('\\\\', '\\')
                v = GstStructure.UNESCAPE.sub(r'\1', v)
            else:
                p = s.find(',')
                if p == -1:
                    p = s.index(';')
                    scan = False
                v = s[:p]

            if t == 'structure':
                v = GstStructure(v)
            elif t == 'string' and len(v) and v[0] == '"':
                v = v[1:-1]
            elif t == 'boolean':
                v = (v == '1')
            elif t in GstStructure.INT_TYPES:
                v = int(v)
            types[k] = t
            values[k] = v

        return (name, types, values)


class GESTrackType:
    UNKNOWN = 1 << 0
    AUDIO = 1 << 1
    VIDEO = 1 << 2
    TEXT = 1 << 3
    CUSTOM = 1 << 4

    @staticmethod
    def to_otio_type(_type):
        if _type == GESTrackType.AUDIO:
            return otio.schema.TrackKind.Audio
        elif _type == GESTrackType.VIDEO:
            return otio.schema.TrackKind.Video

        raise GstParseError("Can't translate track type %s" % _type)


GST_CLOCK_TIME_NONE = 18446744073709551615
GST_SECOND = 1000000000


def to_gstclocktime(rational_time):
    """
    This converts a RationalTime object to a GstClockTime

    Args:
        rational_time (RationalTime): This is a RationalTime object

    Returns:
        int: A time in nanosecond
    """

    return int(rational_time.value_rescaled_to(1) * GST_SECOND)


def get_from_structure(xmlelement, fieldname, default=None, attribute="properties"):
    structure = GstStructure(xmlelement.get(attribute, attribute))
    return structure.get(fieldname, default)


class XGES:
    """
    This object is responsible for knowing how to convert an xGES
    project into an otio timeline
    """

    def __init__(self, xml_string):
        self.xges_xml = cElementTree.fromstring(xml_string)
        self.rate = 25

    def _set_rate_from_timeline(self, timeline):
        metas = GstStructure(timeline.attrib.get("metadatas", "metadatas"))
        framerate = metas.get("framerate")
        if framerate:
            rate = Fraction(framerate)
        else:
            video_track = timeline.find("./track[@track-type='4']")
            rate = None
            if video_track is not None:
                properties = GstStructure(
                    video_track.get("properties", "properties;"))
                restriction_caps = GstStructure(properties.get(
                    "restriction-caps", "restriction-caps"))
                rate = restriction_caps.get("framerate")

        if rate is None:
            return

        self.rate = float(Fraction(rate))
        if self.rate == int(self.rate):
            self.rate = int(self.rate)
        else:
            self.rate = float(round(Decimal(self.rate), 2))

    def to_rational_time(self, ns_timestamp):
        """
        This converts a GstClockTime value to an otio RationalTime object

        Args:
            ns_timestamp (int): This is a GstClockTime value (nanosecond absolute value)

        Returns:
            RationalTime: A RationalTime object
        """
        return otio.opentime.RationalTime(round(int(ns_timestamp) /
                                          (GST_SECOND / self.rate)), self.rate)

    def to_otio(self):
        """
        Convert an xges to an otio

        Returns:
            OpenTimeline: An OpenTimeline Timeline object
        """

        project = self.xges_xml.find("./project")
        metas = GstStructure(project.attrib.get("metadatas", "metadatas"))
        otio_project = otio.schema.SerializableCollection(
            name=metas.get('name'),
            metadata={
                META_NAMESPACE: {"metadatas": project.attrib.get(
                    "metadatas", "metadatas")}
            }
        )
        timeline = project.find("./timeline")
        self._set_rate_from_timeline(timeline)

        otio_timeline = otio.schema.Timeline(
            name=metas.get('name', "unnamed"),
            metadata={
                META_NAMESPACE: {
                    "metadatas": timeline.attrib.get("metadatas", "metadatas"),
                    "properties": timeline.attrib.get("properties", "properties")
                }
            }
        )

        all_names = set()
        self._add_layers(timeline, otio_timeline, all_names)
        otio_project.append(otio_timeline)

        return otio_project

    def _add_layers(self, timeline, otio_timeline, all_names):
        for layer in timeline.findall("./layer"):
            tracks = self._build_tracks_from_layer_clips(layer, all_names)
            otio_timeline.tracks.extend(tracks)

    def _get_clips_for_type(self, clips, track_type):
        if not clips:
            return False

        clips_for_type = []
        for clip in clips:
            if int(clip.attrib['track-types']) & track_type:
                clips_for_type.append(clip)

        return clips_for_type

    def _build_tracks_from_layer_clips(self, layer, all_names):
        all_clips = layer.findall('./clip')

        tracks = []
        for track_type in [GESTrackType.VIDEO, GESTrackType.AUDIO]:
            clips = self._get_clips_for_type(all_clips, track_type)
            if not clips:
                continue

            track = otio.schema.Track()
            track.kind = GESTrackType.to_otio_type(track_type)
            self._add_clips_in_track(clips, track, all_names)

            tracks.append(track)

        return tracks

    def _add_clips_in_track(self, clips, track, all_names):
        for clip in clips:
            otio_clip = self._create_otio_clip(clip, all_names)
            if otio_clip is None:
                continue

            clip_offset = self.to_rational_time(int(clip.attrib['start']))
            if clip_offset > track.duration():
                track.append(
                    self._create_otio_gap(
                        0,
                        (clip_offset - track.duration())
                    )
                )

            track.append(otio_clip)

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
        start = self.to_rational_time(clip.attrib["start"])
        end = start + self.to_rational_time(clip.attrib["duration"])
        cut_point = otio.opentime.RationalTime((end.value - start.value) /
                                               2, start.rate)

        return otio.schema.Transition(
            name=self._get_clip_name(clip, all_names),
            transition_type=TRANSITION_MAP.get(
                clip.attrib["asset-id"], otio.schema.TransitionTypes.Custom
            ),
            in_offset=cut_point,
            out_offset=cut_point,
        )

    def _create_otio_uri_clip(self, clip, all_names):
        source_range = otio.opentime.TimeRange(
            start_time=self.to_rational_time(clip.attrib["inpoint"]),
            duration=self.to_rational_time(clip.attrib["duration"]),
        )

        otio_clip = otio.schema.Clip(
            name=self._get_clip_name(clip, all_names),
            source_range=source_range,
            media_reference=self._reference_from_id(
                clip.get("asset-id"), clip.get("type-name")),
        )

        return otio_clip

    def _create_otio_clip(self, clip, all_names):
        otio_clip = None

        if clip.get("type-name") == "GESTransitionClip":
            otio_clip = self._create_otio_transition(clip, all_names)
        elif clip.get("type-name") == "GESUriClip":
            otio_clip = self._create_otio_uri_clip(clip, all_names)

        if otio_clip is None:
            print("Could not represent: %s" % clip.attrib)
            return None

        otio_clip.metadata[META_NAMESPACE] = {
            "properties": clip.get("properties", "properties;"),
            "metadatas": clip.get("metadatas", "metadatas;"),
        }

        return otio_clip

    def _create_otio_gap(self, start, duration):
        source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(start),
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
            duration = get_from_structure(asset, "duration", duration)

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
            if get_from_structure(clip, 'name') == name:
                return clip

        return None


class XGESOtio:

    def __init__(self, input_otio):
        self.container = input_otio
        self.rate = 25

    def _insert_new_sub_element(self, into_parent, tag, attrib=None, text=''):
        elem = cElementTree.SubElement(into_parent, tag, **attrib or {})
        elem.text = text
        return elem

    def _get_element_properties(self, element):
        return element.metadata.get(META_NAMESPACE, {}).get("properties", "properties;")

    def _get_element_metadatas(self, element):
        return element.metadata.get(META_NAMESPACE,
                                    {"GES": {}}).get("metadatas", "metadatas;")

    def _serialize_ressource(self, ressources, ressource, asset_type):
        if isinstance(ressource, otio.schema.MissingReference):
            return

        if ressources.find("./asset[@id='%s'][@extractable-type-name='%s']" % (
                ressource.target_url, asset_type)) is not None:
            return

        properties = GstStructure(self._get_element_properties(ressource))
        if properties.get('duration') is None:
            properties.set('duration', 'guin64',
                           to_gstclocktime(ressource.available_range.duration))

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
            round(int(offset) / (GST_SECOND / self.rate)),
            self.rate
        )
        start = rational_offset - otio_transition.in_offset
        end = rational_offset + otio_transition.out_offset

        return 0, to_gstclocktime(start), to_gstclocktime(end - start)

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
            inpoint = to_gstclocktime(otio_clip.source_range.start_time)
            duration = to_gstclocktime(otio_clip.source_range.duration)

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

        properties = otio_clip.metadata.get(
            META_NAMESPACE,
            {
                "properties": 'properties, name=(string)"%s"' % (
                    GstStructure.escape(otio_clip.name)
                )
            }).get("properties")
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
        audio_vals = (
            'properties',
            'restriction-caps=(string)audio/x-raw(ANY)',
            'framerate=(GstFraction)1',
            otio_timeline.duration().rate
        )

        properties = '%s, %s,%s/%s' % audio_vals
        self._insert_new_sub_element(
            timeline, 'track',
            attrib={
                "caps": "audio/x-raw(ANY)",
                "track-type": '2',
                'track-id': '0',
                'properties': properties
            }
        )

        video_vals = (
            'properties',
            'restriction-caps=(string)video/x-raw(ANY)',
            'framerate=(GstFraction)1',
            otio_timeline.duration().rate
        )

        properties = '%s, %s,%s/%s' % video_vals
        for otio_track in otio_timeline.tracks:
            if otio_track.kind == otio.schema.TrackKind.Video:
                self._insert_new_sub_element(
                    timeline, 'track',
                    attrib={
                        "caps": "video/x-raw(ANY)",
                        "track-type": '4',
                        'track-id': '1',
                        'properties': properties,
                    }
                )

                return

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

        return to_gstclocktime(otio_element.source_range.duration)

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
        metadatas.set(
            "framerate", "fraction", self._framerate_to_frame_duration(
                otio_timeline.duration().rate
            )
        )
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
        for layer_priority, otio_track in enumerate(otio_timeline.tracks):
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
        xges = cElementTree.Element('ges', version="0.4")

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
        string = cElementTree.tostring(xges, encoding="UTF-8")
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
# Some unit check for internal types
# --------------------

class XGESTests(unittest.TestCase):

    def test_gst_structure_parsing(self):
        struct = GstStructure('properties, name=(string)"%s";' % (
            GstStructure.escape("sc01 sh010_anim.mov"))
        )
        self.assertEqual(struct["name"], "sc01 sh010_anim.mov")

    def test_gst_structure_editing(self):
        struct = GstStructure('properties, name=(string)"%s";' % (
            GstStructure.escape("sc01 sh010_anim.mov"))
        )
        self.assertEqual(struct["name"], "sc01 sh010_anim.mov")

        struct.set("name", "string", "test")
        self.assertEqual(struct["name"], "test")
        self.assertEqual(str(struct), 'properties, name=(string)"test";')

    def test_empty_string(self):
        struct = GstStructure('properties, name=(string)"";')
        self.assertEqual(struct["name"], "")


if __name__ == '__main__':
    unittest.main()
