# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OpenTimelineIO GStreamer Editing Services XML Adapter."""
import re
import os
import warnings
import numbers
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.parse import parse_qs

from fractions import Fraction
from xml.etree import ElementTree
from xml.dom import minidom
import itertools
import colorsys
import opentimelineio as otio

META_NAMESPACE = "XGES"

_TRANSITION_MAP = {
    "crossfade": otio.schema.TransitionTypes.SMPTE_Dissolve
}
# Two way map
_TRANSITION_MAP.update({v: k for k, v in _TRANSITION_MAP.items()})


class XGESReadError(otio.exceptions.OTIOError):
    """An incorrectly formatted xges string."""


class UnhandledValueError(otio.exceptions.OTIOError):
    """Received value is not handled."""
    def __init__(self, name, value):
        otio.exceptions.OTIOError.__init__(
            self, f"Unhandled value {value!r} for {name}.")


class InvalidValueError(otio.exceptions.OTIOError):
    """Received value is invalid."""
    def __init__(self, name, value, expect):
        otio.exceptions.OTIOError.__init__(
            self, "Invalid value {!r} for {}. Expect {}.".format(
                value, name, expect))


class DeserializeError(otio.exceptions.OTIOError):
    """Receive an incorrectly serialized value."""
    MAX_LEN = 20

    def __init__(self, read, reason):
        if len(read) > self.MAX_LEN:
            read = read[:self.MAX_LEN] + "..."
        otio.exceptions.OTIOError.__init__(
            self, "Could not deserialize the string ({}) because it {}."
            "".format(read, reason))


class UnhandledOtioError(otio.exceptions.OTIOError):
    """Received otio object is not handled."""
    def __init__(self, otio_obj):
        otio.exceptions.OTIOError.__init__(
            self, "Unhandled otio schema {}.".format(
                otio_obj.schema_name()))


def _show_ignore(msg):
    """Tell user we found an error with 'msg', but we are ignoring it."""
    warnings.warn(msg + ".\nIGNORING.", stacklevel=2)


def _show_otio_not_supported(otio_obj, effect):
    """
    Tell user that we do not properly support an otio type for 'otio_obj'.
    'effect' is a message to the user about what will happen instead.
    """
    warnings.warn(
        "The schema {} is not currently supported.\n{}.".format(
            otio_obj.schema_name(), effect),
        stacklevel=2)


def _wrong_type_for_arg(val, expect_type_name, arg_name):
    """
    Raise exception in response to the 'arg_name' argument being given the
    value 'val', when we expected it to be of the type corresponding to
    'expect_type_name'.
    """
    raise TypeError(
        "Expect a {} type for the '{}' argument. Received a {} type."
        "".format(expect_type_name, arg_name, type(val).__name__))


def _force_gst_structure_name(struct, struct_name, owner=""):
    """
    If the GstStructure 'struct' does not have the given 'struct_name',
    change its name to match with a warning.
    'owner' is used for the message to tell the user which object the
    structure belongs to.
    """
    if struct.name != struct_name:
        if owner:
            start = f"{owner}'s"
        else:
            start = "The"
        warnings.warn(
            "{} structure name is \"{}\" rather than the expected \"{}\"."
            "\nOverwriting with the expected name.".format(
                start, struct.name, struct_name))
        struct.name = struct_name


# TODO: remove unicode_to_str once python2 has ended:
def unicode_to_str(value):
    """If python2, returns unicode as a utf8 str"""
    if type(value) is not str and isinstance(value, str):
        value = value.encode("utf8")
    return value


class GESTrackType:
    """
    Class for storing the GESTrackType types, and converting them to
    the otio.schema.TrackKind.
    """

    UNKNOWN = 1 << 0
    AUDIO = 1 << 1
    VIDEO = 1 << 2
    TEXT = 1 << 3
    CUSTOM = 1 << 4
    OTIO_TYPES = (VIDEO, AUDIO)
    NON_OTIO_TYPES = (UNKNOWN, TEXT, CUSTOM)
    ALL_TYPES = OTIO_TYPES + NON_OTIO_TYPES

    @staticmethod
    def to_otio_kind(track_type):
        """
        Convert from GESTrackType 'track_type' to otio.schema.TrackKind.
        """
        if track_type == GESTrackType.AUDIO:
            return otio.schema.TrackKind.Audio
        elif track_type == GESTrackType.VIDEO:
            return otio.schema.TrackKind.Video
        raise UnhandledValueError("track_type", track_type)

    @staticmethod
    def from_otio_kind(*otio_kinds):
        """
        Convert the list of otio.schema.TrackKind 'otio_kinds' to an
        GESTrackType.
        """
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
    Class for converting an xges string, which stores GES projects, to an
    otio.schema.Timeline.
    """
    # The xml elements found in the given xges are converted as:
    #
    # + A <ges>, its <project>, its <timeline> and its <track>s are
    #   converted to an otio.schema.Stack.
    # + A GESMarker on the <timeline> is converted to an
    #   otio.schema.Marker.
    # + A <layer> is converted to otio.schema.Track, one for each track
    #   type found.
    # + A <clip> + <asset> is converted to an otio.schema.Composable, one
    #   for each track type found:
    #   + A GESUriClip becomes an otio.schema.Clip with an
    #     otio.schema.ExternalReference.
    #   + A GESUriClip that references a sub-project instead becomes an
    #     otio.schema.Stack of the sub-project.
    #   + A GESTransitionClip becomes an otio.schema.Transition.
    # + An <effect> on a uriclip is converted to an otio.schema.Effect.
    # + An <asset> is wrapped
    #
    # TODO: Some parts of the xges are not converted.
    # <clip> types to support:
    # + GESTestClip, probably to a otio.schema.Clip with an
    #   otio.schema.GeneratorReference
    # + GESTitleClip, maybe to a otio.schema.Clip with an
    #   otio.schema.MissingReference?
    # + GESOverlayClip, difficult to convert since otio.schema.Clips can
    #   not overlap generically. Maybe use a separate otio.schema.Track?
    # + GESBaseEffectClip, same difficulty.
    #
    # Also, for <clip>, we're missing
    # + <source>, which contains <binding> elements that describe the
    #   property bindings.
    #
    # For <project>, we're missing:
    # + <encoding-profile>, not vital.
    #
    # For <asset>, we're missing:
    # + <stream-info>.
    #
    # For <timeline>, we're missing:
    # + <groups>, and its children <group> elements.
    #
    # For <effect>, we're missing:
    # + <binding>, same as the missing <clip> <binding>

    def __init__(self, ges_obj):
        """
        'ges_obj' should be the root of the xges xml tree (called "ges").
        If it is not an ElementTree, it will first be parsed as a string
        to ElementTree.
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
        """
        Return a list of all child xml elements found under 'xmlelement'
        at 'path'.
        """
        found = xmlelement.findall(path)
        if found is None:
            return []
        return found

    @classmethod
    def _findonly(cls, xmlelement, path, allow_none=False):
        """
        Find exactly one child xml element found under 'xmlelement' at
        'path' and return it. If we find multiple, we raise an error. If
        'allow_none' is False, we also error when we find no element,
        otherwise we can return None.
        """
        found = cls._findall(xmlelement, path)
        if allow_none and not found:
            return None
        if len(found) != 1:
            raise XGESReadError(
                "Found {:d} xml elements under the path {} when only "
                "one was expected.".format(len(found), path))
        return found[0]

    @staticmethod
    def _get_attrib(xmlelement, key, expect_type):
        """
        Get the xml attribute at 'key', try to convert it to the python
        'expect_type', and return it. Otherwise, raise an error.
        """
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
    def _get_structure(xmlelement, attrib_name, struct_name=None):
        """
        Try to find the GstStructure with the name 'struct_name' under
        the 'attrib_name' attribute of 'xmlelement'. If we can not do so
        we return an empty structure with the same name. If no
        'struct_name' is given, we use the 'attrib_name'.
        """
        if struct_name is None:
            struct_name = attrib_name
        read_struct = xmlelement.get(attrib_name, struct_name + ";")
        try:
            struct = GstStructure.new_from_str(read_struct)
        except DeserializeError as err:
            _show_ignore(
                "The {} attribute of {} could not be read as a "
                "GstStructure:\n{!s}".format(
                    struct_name, xmlelement.tag, err))
            return GstStructure(struct_name)
        _force_gst_structure_name(struct, struct_name, xmlelement.tag)
        return struct

    @classmethod
    def _get_properties(cls, xmlelement):
        """Get the properties GstStructure from an xges 'xmlelement'."""
        return cls._get_structure(xmlelement, "properties")

    @classmethod
    def _get_metadatas(cls, xmlelement):
        """Get the metadatas GstStructure from an xges 'xmlelement'."""
        return cls._get_structure(xmlelement, "metadatas")

    @classmethod
    def _get_children_properties(cls, xmlelement):
        """
        Get the children-properties GstStructure from an xges
        'xmlelement'.
        """
        return cls._get_structure(
            xmlelement, "children-properties", "properties")

    @classmethod
    def _get_from_properties(
            cls, xmlelement, fieldname, expect_type, default=None):
        """
        Try to get the property under 'fieldname' of the 'expect_type'
        type name from the properties GstStructure of an xges element.
        Otherwise return 'default'.
        """
        structure = cls._get_properties(xmlelement)
        return structure.get_typed(fieldname, expect_type, default)

    @classmethod
    def _get_from_metadatas(
            cls, xmlelement, fieldname, expect_type, default=None):
        """
        Try to get the metadata under 'fieldname' of the 'expect_type'
        type name from the metadatas GstStructure of an xges element.
        Otherwise return 'default'.
        """
        structure = cls._get_metadatas(xmlelement)
        return structure.get_typed(fieldname, expect_type, default)

    @staticmethod
    def _get_from_caps(caps, fieldname, structname=None, default=None):
        """
        Extract a GstCaps from the 'caps' string and search it for the
        first GstStructure (optionally, with the 'structname' name) with
        the 'fieldname' field, and return its value. Otherwise, return
        'default'.
        """
        try:
            with warnings.catch_warnings():
                # unknown types may raise a warning. This will
                # usually be irrelevant since we are searching for
                # a specific field
                caps = GstCaps.new_from_str(caps)
        except DeserializeError as err:
            _show_ignore(
                "Failed to read the fields in the caps ({}):\n\t"
                "{!s}".format(caps, err))
        else:
            for struct in caps:
                if structname is not None:
                    if struct.name != structname:
                        continue
                # use below method rather than fields.get(fieldname) to
                # allow us to want any value back, including None
                for key in struct.fields:
                    if key == fieldname:
                        return struct[key]
        return default

    def _set_rate_from_timeline(self, timeline):
        """
        Set the rate of 'self' to the rate found in the video track
        element of the xges 'timeline'.
        """
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
            _show_ignore("Read a framerate that is not a fraction")
        else:
            self.rate = float(rate)

    def _to_rational_time(self, ns_timestamp):
        """
        Converts the GstClockTime 'ns_timestamp' (nanoseconds as an int)
        to an otio.opentime.RationalTime object.
        """
        return otio.opentime.RationalTime(
            (float(ns_timestamp) * self.rate) / float(GST_SECOND),
            self.rate
        )

    @staticmethod
    def _add_to_otio_metadata(otio_obj, key, val, parent_key=None):
        """
        Add the data 'val' to the metadata of 'otio_obj' under 'key'.
        If 'parent_key' is given, it is instead added to the
        sub-dictionary found under 'parent_key'.
        The needed dictionaries are automatically created.
        """
        xges_dict = otio_obj.metadata.get(META_NAMESPACE)
        if xges_dict is None:
            otio_obj.metadata[META_NAMESPACE] = {}
            xges_dict = otio_obj.metadata[META_NAMESPACE]
        if parent_key is None:
            _dict = xges_dict
        else:
            sub_dict = xges_dict.get(parent_key)
            if sub_dict is None:
                xges_dict[parent_key] = {}
                sub_dict = xges_dict[parent_key]
            _dict = sub_dict
        _dict[key] = val

    @classmethod
    def _add_properties_and_metadatas_to_otio(
            cls, otio_obj, element, parent_key=None):
        """
        Add the properties and metadatas attributes of the xges 'element'
        to the metadata of 'otio_obj', as GstStructures. Optionally under
        the 'parent_key'.
        """
        cls._add_to_otio_metadata(
            otio_obj, "properties",
            cls._get_properties(element), parent_key)
        cls._add_to_otio_metadata(
            otio_obj, "metadatas",
            cls._get_metadatas(element), parent_key)

    @classmethod
    def _add_children_properties_to_otio(
            cls, otio_obj, element, parent_key=None):
        """
        Add the children-properties attribute of the xges 'element' to the
        metadata of 'otio_obj', as GstStructures. Optionally under the
        'parent_key'.
        """
        cls._add_to_otio_metadata(
            otio_obj, "children-properties",
            cls._get_children_properties(element), parent_key)

    def to_otio(self):
        """
        Convert the xges given to 'self' to an otio.schema.Timeline
        object, and returns it.
        """
        otio_timeline = otio.schema.Timeline()
        project = self._fill_otio_stack_from_ges(otio_timeline.tracks)
        otio_timeline.name = self._get_from_metadatas(
            project, "name", "string", "")
        return otio_timeline

    def _fill_otio_stack_from_ges(self, otio_stack):
        """
        Converts the top <ges> element given to 'self' into an
        otio.schema.Stack by setting the metadata of the given
        'otio_stack', and filling it with otio.schema.Tracks.
        Returns the <project> element found under <ges>.
        """
        project = self._findonly(self.ges_xml, "./project")
        timeline = self._findonly(project, "./timeline")
        self._set_rate_from_timeline(timeline)
        self._add_timeline_markers_to_otio_stack(timeline, otio_stack)

        tracks = self._findall(timeline, "./track")
        tracks.sort(
            key=lambda trk: self._get_attrib(trk, "track-id", int))
        xges_tracks = []
        for track in tracks:
            try:
                caps = GstCaps.new_from_str(
                    self._get_attrib(track, "caps", str))
            except DeserializeError as err:
                _show_ignore(
                    "Could not deserialize the caps attribute for "
                    "track {:d}:\n{!s}".format(
                        self._get_attrib(track, "track-id", int), err))
            else:
                xges_tracks.append(
                    XgesTrack(
                        caps,
                        self._get_attrib(track, "track-type", int),
                        self._get_properties(track),
                        self._get_metadatas(track)))

        self._add_properties_and_metadatas_to_otio(
            otio_stack, project, "project")
        self._add_properties_and_metadatas_to_otio(
            otio_stack, timeline, "timeline")
        self._add_to_otio_metadata(otio_stack, "tracks", xges_tracks)
        self._add_layers_to_otio_stack(timeline, otio_stack)
        return project

    def _add_timeline_markers_to_otio_stack(
            self, timeline, otio_stack):
        """
        Add the markers found in the GESMarkerlList metadata of the xges
        'timeline' to 'otio_stack' as otio.schema.Markers.
        """
        metadatas = self._get_metadatas(timeline)
        for marker_list in metadatas.values_of_type("GESMarkerList"):
            for marker in marker_list:
                if marker.is_colored():
                    otio_stack.markers.append(
                        self._otio_marker_from_ges_marker(marker))

    def _otio_marker_from_ges_marker(self, ges_marker):
        """Convert the GESMarker 'ges_marker' to an otio.schema.Marker."""
        with warnings.catch_warnings():
            # don't worry about not being string typed
            name = ges_marker.metadatas.get_typed("comment", "string", "")
        marked_range = otio.opentime.TimeRange(
            self._to_rational_time(ges_marker.position),
            self._to_rational_time(0))
        return otio.schema.Marker(
            name=name, color=ges_marker.get_nearest_otio_color(),
            marked_range=marked_range)

    def _add_layers_to_otio_stack(self, timeline, otio_stack):
        """
        Add the <layer> elements under the xges 'timeline' to 'otio_stack'
        as otio.schema.Tracks.
        """
        sort_otio_tracks = []
        for layer in self._findall(timeline, "./layer"):
            priority = self._get_attrib(layer, "priority", int)
            for otio_track in self._otio_tracks_from_layer_clips(layer):
                sort_otio_tracks.append((otio_track, priority))
        sort_otio_tracks.sort(key=lambda ent: ent[1], reverse=True)
        # NOTE: smaller priority is later in the list
        for otio_track in (ent[0] for ent in sort_otio_tracks):
            otio_stack.append(otio_track)

    def _otio_tracks_from_layer_clips(self, layer):
        """
        Convert the xges 'layer' into otio.schema.Tracks, one for each
        otio.schema.TrackKind.
        """
        otio_tracks = []
        for track_type in GESTrackType.OTIO_TYPES:
            otio_items, otio_transitions = \
                self._create_otio_composables_from_layer_clips(
                    layer, track_type)
            if not otio_items and not otio_transitions:
                continue
            otio_track = otio.schema.Track()
            otio_track.kind = GESTrackType.to_otio_kind(track_type)
            self._add_otio_composables_to_otio_track(
                otio_track, otio_items, otio_transitions)
            self._add_properties_and_metadatas_to_otio(otio_track, layer)
            otio_tracks.append(otio_track)
        for track_type in GESTrackType.NON_OTIO_TYPES:
            layer_clips = self._layer_clips_for_track_type(
                layer, track_type)
            if layer_clips:
                _show_ignore(
                    "The xges layer of priority {:d} contains clips "
                    "{!s} of the unhandled track type {:d}".format(
                        self._get_attrib(layer, "priority", int),
                        [self._get_name(clip) for clip in layer_clips],
                        track_type))
        return otio_tracks

    @classmethod
    def _layer_clips_for_track_type(cls, layer, track_type):
        """
        Return the <clip> elements found under the xges 'layer' whose
        "track-types" overlaps with track_type.
        """
        return [
            clip for clip in cls._findall(layer, "./clip")
            if cls._get_attrib(clip, "track-types", int) & track_type]

    @classmethod
    def _clip_effects_for_track_type(cls, clip, track_type):
        """
        Return the <effect> elements found under the xges 'clip' whose
        "track-type" matches 'track_type'.
        """
        return [
            effect for effect in cls._findall(clip, "./effect")
            if cls._get_attrib(effect, "track-type", int) & track_type]
        # NOTE: the attribute is 'track-type', not 'track-types'

    def _create_otio_composables_from_layer_clips(
            self, layer, track_type):
        """
        For all the <clip> elements found in the xges 'layer' that overlap
        the given 'track_type', attempt to create an
        otio.schema.Composable.

        Note that the created composables do not have their timing set.
        Instead, the timing information of the <clip> is stored in a
        dictionary alongside the composable.

        Returns a list of otio item dictionaries, and a list of otio
        transition dictionaries.
        Within the item dictionary:
            "item" points to the actual otio.schema.Item,
            "start", "duration" and "inpoint" give the corresponding
            <clip> attributes.
        Within the transition dictionary:
            "transition" points to the actual otio.schema.Transition,
            "start" and "duration" give the corresponding <clip>
            attributes.
        """
        otio_transitions = []
        otio_items = []
        for clip in self._layer_clips_for_track_type(layer, track_type):
            clip_type = self._get_attrib(clip, "type-name", str)
            start = self._get_attrib(clip, "start", int)
            inpoint = self._get_attrib(clip, "inpoint", int)
            duration = self._get_attrib(clip, "duration", int)
            otio_composable = None
            name = self._get_name(clip)
            if clip_type == "GESTransitionClip":
                otio_composable = self._otio_transition_from_clip(clip)
            elif clip_type == "GESUriClip":
                otio_composable = self._otio_item_from_uri_clip(clip)
            else:
                # TODO: support other clip types
                # maybe represent a GESTitleClip as a gap, with the text
                # in the metadata?
                # or as a clip with a MissingReference?
                _show_ignore(
                    "The xges clip {} is of an unsupported {} type"
                    "".format(name, clip_type))
                continue
            otio_composable.name = name
            self._add_properties_and_metadatas_to_otio(
                otio_composable, clip, "clip")
            self._add_clip_effects_to_otio_composable(
                otio_composable, clip, track_type)
            if isinstance(otio_composable, otio.schema.Transition):
                otio_transitions.append({
                    "transition": otio_composable,
                    "start": start, "duration": duration})
            elif isinstance(otio_composable, otio.core.Item):
                otio_items.append({
                    "item": otio_composable, "start": start,
                    "inpoint": inpoint, "duration": duration})
        return otio_items, otio_transitions

    def _add_clip_effects_to_otio_composable(
            self, otio_composable, clip, track_type):
        """
        Add the <effect> elements found under the xges 'clip' of the
        given 'track_type' to the 'otio_composable'.
        """
        clip_effects = self._clip_effects_for_track_type(
            clip, track_type)
        if not isinstance(otio_composable, otio.core.Item):
            if clip_effects:
                _show_ignore(
                    "The effects {!s} found under the xges clip {} can "
                    "not be represented".format(
                        [self._get_attrib(effect, "asset-id", str)
                         for effect in clip_effects],
                        self._get_name(clip)))
            return
        for effect in clip_effects:
            effect_type = self._get_attrib(effect, "type-name", str)
            if effect_type == "GESEffect":
                otio_composable.effects.append(
                    self._otio_effect_from_effect(effect))
            else:
                _show_ignore(
                    "The {} effect under the xges clip {} is of an "
                    "unsupported {} type".format(
                        self._get_attrib(effect, "asset-id", str),
                        self._get_name(clip), effect_type))

    def _otio_effect_from_effect(self, effect):
        """Convert the xges 'effect' into an otio.schema.Effect."""
        bin_desc = self._get_attrib(effect, "asset-id", str)
        # TODO: a smart way to convert the bin description into a standard
        # effect name that is recognised by other adapters
        # e.g. a bin description can also contain parameter values, such
        # as "agingtv scratch-lines=20"
        otio_effect = otio.schema.Effect(effect_name=bin_desc)
        self._add_to_otio_metadata(
            otio_effect, "bin-description", bin_desc)
        self._add_properties_and_metadatas_to_otio(otio_effect, effect)
        self._add_children_properties_to_otio(otio_effect, effect)
        return otio_effect

    @staticmethod
    def _item_gap(second, first):
        """
        Calculate the time gap between the start time of 'second' and the
        end time of 'first', each of which are item dictionaries as
        returned by _create_otio_composables_from_layer_clips.
        If 'first' is None, we return the gap between the start of the
        timeline and the start of 'second'.
        If 'second' is None, we return 0 to indicate no gap.
        """
        if second is None:
            return 0
        if first is None:
            return second["start"]
        return second["start"] - first["start"] - first["duration"]

    def _add_otio_composables_to_otio_track(
            self, otio_track, items, transitions):
        """
        Insert 'items' and 'transitions' into 'otio_track' with correct
        timings.

        'items' and 'transitions' should be a list of dictionaries, as
        returned by _create_otio_composables_from_layer_clips.

        Specifically, the item dictionaries should contain an un-parented
        otio.schema.Item under the "item" key, and GstClockTimes under the
        "start", "duration" and "inpoint" keys, corresponding to the times
        found under the corresponding xges <clip>.
        This method should set the correct source_range for the item
        before inserting it into 'otio_track'.

        The transitions dictionaries should contain an un-parented
        otio.schema.Transition under the "transition" key, and
        GstClockTimes under the "start" and "duration" keys, corresponding
        to the times found under the corresponding xges <clip>.
        Whenever an overlap of non-transition <clip>s is detected, the
        transition that matches the overlap will be searched for in
        'transitions', removed from the list, and the corresponding otio
        transition will be inserted in 'otio_track' with the correct
        timings.
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
            otio_start = self._to_rational_time(item["inpoint"])
            otio_duration = self._to_rational_time(item["duration"])
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
                otio_track.append(self._create_otio_gap(pre_gap))

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
                            len(transition), otio_track.kind,
                            next_item["start"], duration))
                half = float(duration) / 2.0
                otio_transition.in_offset = self._to_rational_time(half)
                otio_transition.out_offset = self._to_rational_time(half)
                otio_duration -= otio_transition.out_offset
                # trim the end of the clip, which is where the otio
                # transition starts
            otio_item = item["item"]
            otio_item.source_range = otio.opentime.TimeRange(
                otio_start, otio_duration)
            otio_track.append(otio_item)
            if otio_transition:
                otio_track.append(otio_transition)
            prev_otio_transition = otio_transition
        if transitions:
            raise XGESReadError(
                "xges layer contains {:d} {!s} transitions that could "
                "not be associated with any clip overlap".format(
                    len(transitions), otio_track.kind))

    @classmethod
    def _get_name(cls, element):
        """
        Get the "name" of the xges 'element' found in its properties, or
        return a generic name if none is found.
        """
        name = cls._get_from_properties(element, "name", "string")
        if not name:
            name = element.tag
        return name

    def _otio_transition_from_clip(self, clip):
        """
        Convert the xges transition 'clip' into an otio.schema.Transition.
        Note that the timing of the object is not set.
        """
        return otio.schema.Transition(
            transition_type=_TRANSITION_MAP.get(
                self._get_attrib(clip, "asset-id", str),
                otio.schema.TransitionTypes.Custom))

    @staticmethod
    def _default_otio_transition():
        """
        Create a default otio.schema.Transition.
        Note that the timing of the object is not set.
        """
        return otio.schema.Transition(
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve)

    def _otio_item_from_uri_clip(self, clip):
        """
        Convert the xges uri 'clip' into an otio.schema.Item.
        Note that the timing of the object is not set.

        If 'clip' is found to reference a sub-project, this will return
        an otio.schema.Stack of the sub-project, also converted from the
        found <ges> element.
        Otherwise, an otio.schema.Clip with an
        otio.schema.ExternalReference is returned.
        """
        asset_id = self._get_attrib(clip, "asset-id", str)
        sub_project_asset = self._asset_by_id(asset_id, "GESTimeline")
        if sub_project_asset is not None:
            # this clip refers to a sub project
            otio_item = otio.schema.Stack()
            sub_ges = XGES(self._findonly(sub_project_asset, "./ges"))
            sub_ges._fill_otio_stack_from_ges(otio_item)
            self._add_properties_and_metadatas_to_otio(
                otio_item, sub_project_asset, "sub-project-asset")
            # NOTE: we include asset-id in the metadata, so that two
            # stacks that refer to a single sub-project will not be
            # split into separate assets when converting from
            # xges->otio->xges
            self._add_to_otio_metadata(otio_item, "asset-id", asset_id)
            uri_clip_asset = self._asset_by_id(asset_id, "GESUriClip")
            if uri_clip_asset is None:
                _show_ignore(
                    "Did not find the expected GESUriClip asset with "
                    "the id {}".format(asset_id))
            else:
                self._add_properties_and_metadatas_to_otio(
                    otio_item, uri_clip_asset, "uri-clip-asset")
        else:
            otio_item = otio.schema.Clip(
                media_reference=self._otio_reference_from_id(asset_id))
        return otio_item

    def _create_otio_gap(self, gst_duration):
        """
        Create a new otio.schema.Gap with the given GstClockTime
        'gst_duration' duration.
        """
        source_range = otio.opentime.TimeRange(
            self._to_rational_time(0),
            self._to_rational_time(gst_duration))
        return otio.schema.Gap(source_range=source_range)

    def _otio_image_sequence_from_url(self, ref_url):

        # TODO: Add support for missing policy
        params = {}
        fname, ext = os.path.splitext(unquote(os.path.basename(ref_url.path)))
        index_format = re.findall(r"%\d+d", fname)
        if index_format:
            params["frame_zero_padding"] = int(index_format[-1][2:-1])
            fname = fname[0:-len(index_format[-1])]

        url_params = parse_qs(ref_url.query)
        if "framerate" in url_params:
            rate = params["rate"] = float(Fraction(url_params["framerate"][-1]))
            if "start-index" in url_params and "stop-index" in url_params:
                start = int(url_params["start-index"][-1])
                stop = int(url_params["stop-index"][-1])
                params["available_range"] = otio.opentime.TimeRange(
                    otio.opentime.RationalTime(int(start), rate),
                    otio.opentime.RationalTime(int(stop - start), rate),
                )
        else:
            rate = params["rate"] = float(30)

        return otio.schema.ImageSequenceReference(
            "file://" + os.path.dirname(ref_url.path),
            fname, ext, **params)

    def _otio_reference_from_id(self, asset_id):
        """
        Create a new otio.schema.Reference from the given 'asset_id'
        of an xges <clip>.
        """
        asset = self._asset_by_id(asset_id, "GESUriClip")
        if asset is None:
            _show_ignore(
                "Did not find the expected GESUriClip asset with the "
                "id {}".format(asset_id))
            return otio.schema.MissingReference()

        duration = self._get_from_properties(
            asset, "duration", "guint64")

        if duration is None:
            available_range = None
        else:
            available_range = otio.opentime.TimeRange(
                start_time=self._to_rational_time(0),
                duration=self._to_rational_time(duration)
            )

        ref_url = urlparse(asset_id)
        if ref_url.scheme == "imagesequence":
            otio_ref = self._otio_image_sequence_from_url(ref_url)
        else:
            otio_ref = otio.schema.ExternalReference(
                target_url=asset_id,
                available_range=available_range
            )
        self._add_properties_and_metadatas_to_otio(otio_ref, asset)
        return otio_ref

    def _asset_by_id(self, asset_id, asset_type):
        """
        Return the single xges <asset> element with "id"=='asset_id' and
        "extractable-type-name"=='asset_type.
        """
        return self._findonly(
            self.ges_xml,
            "./project/ressources/asset[@id='{}']"
            "[@extractable-type-name='{}']".format(
                asset_id, asset_type),
            allow_none=True
        )


class XGESOtio:
    """
    Class for converting an otio.schema.Timeline into an xges string.
    """
    # The otio objects found in the given timeline are converted as:
    #
    # + A Stack is converted to a a <ges>, its <project>, its <timeline>
    #   and its <track>s. If the Stack is found underneath a Track, we
    #   also create a uri <clip> that references the <project> as an
    #   <asset>.
    # + A Track is converted to a <layer>.
    # + A Clip with an ExternalReference is converted to a uri <clip> and
    #   an <asset>.
    # + A Transition is converted to a transition <clip>.
    # + An Effect on a Clip or Stack is converted to <effect>s under the
    #   corresponding <clip>.
    # + An Effect on a Track is converted to an effect <clip> that covers
    #   the <layer>.
    # + A Marker is converted to a GESMarker for the <timeline>.
    #
    # TODO: Some parts of otio are not supported:
    # + Clips with MissingReference or GeneratorReference references.
    #   The latter could probably be converted to a test <clip>.
    # + The global_start_time on a Timeline is ignored.
    # + TimeEffects are not converted into <effect>s or effect <clip>s.
    # + We don't support a non-zero start time for uri files in xges,
    #   unlike MediaReference.
    # + We don't have a good way to convert Effects into xges effects.
    #   Currently we just copy the names.
    # + We don't support TimeEffects. Need to wait until xges supports
    #   this.
    # + We don't support converting Transition transition_types into xges
    #   transition types. Currently they all become the default transition
    #   type.

    def __init__(self, input_otio=None):
        """
        Initialise with the otio.schema.Timeline 'input_otio'.
        """
        if input_otio is not None:
            # copy the timeline so that we can freely change it
            self.timeline = input_otio.deepcopy()
        else:
            self.timeline = None
        self.all_names = set()
        # map track types to a track id
        self.track_id_for_type = {}
        # map from a sub-<ges> element to an asset id
        self.sub_projects = {}

    @staticmethod
    def _rat_to_gstclocktime(rat_time):
        """
        Convert an otio.opentime.RationalTime to a GstClockTime
        (nanoseconds as an int).
        """
        return int(otio.opentime.to_seconds(rat_time) * GST_SECOND)

    @classmethod
    def _range_to_gstclocktimes(cls, time_range):
        """
        Convert an otio.opentime.TimeRange to a tuple of the start_time
        and duration as GstClockTimes.
        """
        return (cls._rat_to_gstclocktime(time_range.start_time),
                cls._rat_to_gstclocktime(time_range.duration))

    @staticmethod
    def _insert_new_sub_element(into_parent, tag, attrib=None):
        """
        Create a new 'tag' xml element as a child of 'into_parent' with
        the given 'attrib' attributes, and returns it.
        """
        return ElementTree.SubElement(into_parent, tag, attrib or {})

    @classmethod
    def _add_properties_and_metadatas_to_element(
            cls, element, otio_obj, parent_key=None,
            properties=None, metadatas=None):
        """
        Add the xges GstStructures "properties" and "metadatas" found in
        the metadata of 'otio_obj', optionally looking under 'parent_key',
        to the corresponding attributes of the xges 'element'.
        If 'properties' or 'metadatas' are given, these will be used
        instead of the ones found.
        """
        element.attrib["properties"] = str(
            properties or
            cls._get_element_properties(otio_obj, parent_key))
        element.attrib["metadatas"] = str(
            metadatas or
            cls._get_element_metadatas(otio_obj, parent_key))

    @classmethod
    def _add_children_properties_to_element(
            cls, element, otio_obj, parent_key=None,
            children_properties=None):
        """
        Add the xges GstStructure "children-properties" found in the
        metadata of 'otio_obj', optionally looking under 'parent_key', to
        the corresponding attributes of the xges 'element'.
        If 'children-properties' is given, this will be used instead of
        the one found.
        """
        element.attrib["children-properties"] = str(
            children_properties or
            cls._get_element_children_properties(otio_obj, parent_key))

    @staticmethod
    def _get_from_otio_metadata(
            otio_obj, key, parent_key=None, default=None):
        """
        Fetch some xges data stored under 'key' from the metadata of
        'otio_obj'. If 'parent_key' is given, we fetch the data from the
        dictionary under 'parent_key' in the metadata of 'otio_obj'. If
        nothing was found, 'default' is returned instead.
        This is used to find data that was added to 'otio_obj' using
        XGES._add_to_otio_metadata.
        """
        _dict = otio_obj.metadata.get(META_NAMESPACE, {})
        if parent_key is not None:
            _dict = _dict.get(parent_key, {})
        return _dict.get(key, default)

    @classmethod
    def _get_element_structure(
            cls, otio_obj, key, struct_name, parent_key=None):
        """
        Fetch a GstStructure under 'key' from the metadata of 'otio_obj',
        optionally looking under 'parent_key'.
        If the structure can not be found, a new empty structure with the
        name 'struct_name' is created and returned instead.
        This method will ensure that the returned GstStructure will have
        the name 'struct_name'.
        """
        struct = cls._get_from_otio_metadata(
            otio_obj, key, parent_key, GstStructure(struct_name))
        _force_gst_structure_name(struct, struct_name, "{} {}".format(
            type(otio_obj).__name__, otio_obj.name))
        return struct

    @classmethod
    def _get_element_properties(cls, otio_obj, parent_key=None):
        """
        Fetch the "properties" GstStructure under from the metadata of
        'otio_obj', optionally looking under 'parent_key'.
        If the structure is not found, an empty one is returned instead.
        """
        return cls._get_element_structure(
            otio_obj, "properties", "properties", parent_key)

    @classmethod
    def _get_element_metadatas(cls, otio_obj, parent_key=None):
        """
        Fetch the "metdatas" GstStructure under from the metadata of
        'otio_obj', optionally looking under 'parent_key'.
        If the structure is not found, an empty one is returned instead.
        """
        return cls._get_element_structure(
            otio_obj, "metadatas", "metadatas", parent_key)

    @classmethod
    def _get_element_children_properties(cls, otio_obj, parent_key=None):
        """
        Fetch the "children-properties" GstStructure under from the
        metadata of 'otio_obj', optionally looking under 'parent_key'.
        If the structure is not found, an empty one is returned instead.
        """
        return cls._get_element_structure(
            otio_obj, "children-properties", "properties", parent_key)

    @staticmethod
    def _set_structure_value(struct, field, _type, value):
        """
        For the given GstStructure 'struct', set the value under 'field'
        to 'value' with the given type name '_type'.
        If the type name is different from the current type name for
        'field', the value is still set, but we also issue a warning.
        """
        if field in struct.fields:
            current_type = struct.get_type_name(field)
            if current_type != _type:
                # the type changing is unexpected
                warnings.warn(
                    "The structure {} has a {} typed value {!s} under {}."
                    "\nOverwriting with the {} typed value {!s}".format(
                        struct.name, current_type,
                        struct.get_value(field), field, _type, value))
        struct.set(field, _type, value)

    @staticmethod
    def _asset_exists(asset_id, ressources, *extract_types):
        """
        Test whether we have already created the xges <asset> under the
        xges 'ressources' with id 'asset_id', and matching one of the
        'extract_types'.
        """
        assets = ressources.findall("./asset")
        if asset_id is None or assets is None:
            return False
        for extract_type in extract_types:
            for asset in assets:
                if asset.get("extractable-type-name") == extract_type \
                        and asset.get("id") == asset_id:
                    return True
        return False

    @classmethod
    def _xges_element_equal(cls, first_el, second_el):
        """Test if 'first_el' is equal to 'second_el'."""
        # start with most likely failures
        if first_el.attrib != second_el.attrib:
            return False
        if len(first_el) != len(second_el):
            return False
        if first_el.tag != second_el.tag:
            return False
        # zip should be safe for comparison since we've already checked
        # for equal length
        for first_child, second_child in zip(first_el, second_el):
            if not cls._xges_element_equal(first_child, second_child):
                return False
        if first_el.text != second_el.text:
            return False
        if first_el.tail != second_el.tail:
            return False
        return True

    def _serialize_stack_to_ressource(self, otio_stack, ressources):
        """
        Use 'otio_stack' to create a new xges <asset> under the xges
        'ressources' corresponding to a sub-project. If the asset already
        exists, it is not created. In either case, returns the asset id
        for the corresponding <asset>.
        """
        sub_obj = XGESOtio()
        sub_ges = sub_obj._serialize_stack_to_ges(otio_stack)
        for existing_sub_ges in self.sub_projects:
            if self._xges_element_equal(existing_sub_ges, sub_ges):
                # Already have the sub project as an asset, so return its
                # asset id
                return self.sub_projects[existing_sub_ges]
        asset_id = self._get_from_otio_metadata(otio_stack, "asset-id")
        if not asset_id:
            asset_id = otio_stack.name or "sub-project"
        orig_asset_id = asset_id
        for i in itertools.count(start=1):
            if not self._asset_exists(
                    asset_id, ressources, "GESUriClip", "GESTimeline"):
                # NOTE: asset_id must be unique for both the
                # GESTimeline and GESUriClip extractable types
                break
            asset_id = orig_asset_id + f"_{i:d}"
        # create a timeline asset
        asset = self._insert_new_sub_element(
            ressources, "asset", attrib={
                "id": asset_id, "extractable-type-name": "GESTimeline"})
        self._add_properties_and_metadatas_to_element(
            asset, otio_stack, "sub-project-asset")
        asset.append(sub_ges)
        self.sub_projects[sub_ges] = asset_id

        # also create a uri asset for the clip
        uri_asset = self._insert_new_sub_element(
            ressources, "asset", attrib={
                "id": asset_id, "extractable-type-name": "GESUriClip"})
        self._add_properties_and_metadatas_to_element(
            uri_asset, otio_stack, "uri-clip-asset")
        return asset_id

    def _serialize_external_reference_to_ressource(
            self, reference, ressources):
        """
        Use the the otio.schema.ExternalReference 'reference' to create
        a new xges <asset> under the xges 'ressources' corresponding to a
        uri clip asset. If the asset already exists, it is not created.
        """
        if isinstance(reference, otio.schema.ImageSequenceReference):
            base_url = urlparse(reference.target_url_base)
            asset_id = "imagesequence:" + base_url.path
            if not base_url.path.endswith("/"):
                asset_id += "/"
            asset_id += quote(
                reference.name_prefix + "%0"
                + str(reference.frame_zero_padding)
                + "d" + reference.name_suffix)

            params = []
            if reference.rate:
                rate = reference.rate.as_integer_ratio()
                params.append("rate=%i/%i" % (rate[0], rate[1]))

            if reference.available_range:
                params.append(
                    "start-index=%i" %
                    int(reference.available_range.start_time.value))
                params.append(
                    "stop-index=%i" % (
                        reference.available_range.start_time.value
                        + reference.available_range.duration.value))

            if params:
                asset_id += '?'
                asset_id += '&'.join(params)
        else:
            asset_id = reference.target_url
        if self._asset_exists(asset_id, ressources, "GESUriClip"):
            return asset_id
        properties = self._get_element_properties(reference)
        if properties.get_typed("duration", "guint64") is None:
            a_range = reference.available_range
            if a_range is not None:
                self._set_structure_value(
                    properties, "duration", "guint64",
                    sum(self._range_to_gstclocktimes(a_range)))
                # TODO: check that this is correct approach for when
                # start_time is not 0.
                # duration is the sum of the a_range start_time and
                # duration we ignore that frames before start_time are
                # not available
        asset = self._insert_new_sub_element(
            ressources, "asset", attrib={
                "id": asset_id, "extractable-type-name": "GESUriClip"})
        self._add_properties_and_metadatas_to_element(
            asset, reference, properties=properties)
        return asset_id

    @classmethod
    def _get_effect_bin_desc(cls, otio_effect):
        """
        Get the xges effect bin-description property from 'otio_effect'.
        """
        bin_desc = cls._get_from_otio_metadata(
            otio_effect, "bin-description")
        if bin_desc is None:
            # TODO: have a smart way to convert an effect name into a bin
            # description
            warnings.warn(
                "Did not find a GESEffect bin-description for the {0} "
                "effect. Using \"{0}\" as the bin-description."
                "".format(otio_effect.effect_name))
            bin_desc = otio_effect.effect_name
        return bin_desc

    def _serialize_item_effect(
            self, otio_effect, clip, clip_id, track_type):
        """
        Convert 'otio_effect' into a 'track_type' xges <effect> under the
        xges 'clip' with the given 'clip_id'.
        """
        if isinstance(otio_effect, otio.schema.TimeEffect):
            _show_otio_not_supported(otio_effect, "Ignoring")
            return
        track_id = self.track_id_for_type.get(track_type)
        if track_id is None:
            _show_ignore(
                "Could not get the required track-id for the {} effect "
                "because no xges track with the track-type {:d} exists"
                "".format(otio_effect.effect_name, track_type))
            return
        effect = self._insert_new_sub_element(
            clip, "effect", attrib={
                "asset-id": str(self._get_effect_bin_desc(otio_effect)),
                "clip-id": str(clip_id),
                "type-name": "GESEffect",
                "track-type": str(track_type),
                "track-id": str(track_id)
            }
        )
        self._add_properties_and_metadatas_to_element(effect, otio_effect)
        self._add_children_properties_to_element(effect, otio_effect)

    def _serialize_item_effects(
            self, otio_item, clip, clip_id, track_types):
        """
        Place all the effects found on 'otio_item' that overlap
        'track_types' under the xges 'clip' with the given 'clip_id'.
        """
        for track_type in (
                t for t in GESTrackType.ALL_TYPES if t & track_types):
            for otio_effect in otio_item.effects:
                self._serialize_item_effect(
                    otio_effect, clip, clip_id, track_type)

    def _serialize_track_effect_to_effect_clip(
            self, otio_effect, layer, layer_priority, start, duration,
            track_types, clip_id):
        """
        Convert the effect 'otio_effect' found on an otio.schema.Track
        into a GESEffectClip xges <clip> under the xges 'layer' with the
        given 'layer_priority'. 'start', 'duration', 'clip_id' and
        'track-types' will be used for the corresponding attributes of the
        <clip>.
        """
        if isinstance(otio_effect, otio.schema.TimeEffect):
            _show_otio_not_supported(otio_effect, "Ignoring")
            return
        self._insert_new_sub_element(
            layer, "clip", attrib={
                "id": str(clip_id),
                "asset-id": str(self._get_effect_bin_desc(otio_effect)),
                "type-name": "GESEffectClip",
                "track-types": str(track_types),
                "layer-priority": str(layer_priority),
                "start": str(start),
                "rate": '0',
                "inpoint": "0",
                "duration": str(duration),
                "properties": "properties;",
                "metadatas": "metadatas;"
            }
        )
        # TODO: add properties and metadatas if we support converting
        # GESEffectClips to otio track effects

    def _get_properties_with_unique_name(
            self, named_otio, parent_key=None):
        """
        Find the xges "properties" GstStructure found in the metadata of
        'named_otio', optionally under 'parent_key'. If the "name"
        property is not found or not unique for the project, it is
        modified to make it so. Then the structure is returned.
        """
        properties = self._get_element_properties(named_otio, parent_key)
        name = properties.get_typed("name", "string")
        if not name:
            name = named_otio.name or named_otio.schema_name()
        tmpname = name
        for i in itertools.count(start=1):
            if tmpname not in self.all_names:
                break
            tmpname = name + f"_{i:d}"
        self.all_names.add(tmpname)
        self._set_structure_value(properties, "name", "string", tmpname)
        return properties

    def _get_clip_times(
            self, otio_composable, prev_composable, next_composable,
            prev_otio_end):
        """
        Convert the timing of 'otio_composable' into an xges <clip>
        times, using the previous object in the parent otio.schema.Track
        'prev_composable', the next object in the track 'next_composable',
        and the end time of 'prev_composable' in GstClockTime
        'prev_otio_end', as references. 'next_composable' and
        'prev_composable' may be None when no such sibling exists.
        'prev_otio_end' should be the 'otio_end' that was returned from
        this method for 'prev_composable', or the initial time of the
        xges <timeline>.

        Returns the "start", "duration" and "inpoint" attributes for the
        <clip>, as well as the end time of 'otio_composable', all in
        the coordinates of the xges <timeline> and in GstClockTimes.
        """
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
            otio_start_time, otio_duration = self._range_to_gstclocktimes(
                otio_composable.trimmed_range())
            otio_end = prev_otio_end + otio_duration
            start = prev_otio_end
            duration = otio_duration
            inpoint = otio_start_time
            if isinstance(prev_composable, otio.schema.Transition):
                in_offset = self._rat_to_gstclocktime(
                    prev_composable.in_offset)
                start -= in_offset
                duration += in_offset
                inpoint -= in_offset
            if isinstance(next_composable, otio.schema.Transition):
                duration += self._rat_to_gstclocktime(
                    next_composable.out_offset)
        elif isinstance(otio_composable, otio.schema.Transition):
            otio_end = prev_otio_end
            in_offset = self._rat_to_gstclocktime(
                otio_composable.in_offset)
            out_offset = self._rat_to_gstclocktime(
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
        Convert 'otio_composable' into an xges <clip> with the id
        'clip_id', under the xges 'layer' with 'layer_priority'. The
        previous object in the parent otio.schema.Track
        'prev_composable', the next object in the track 'next_composable',
        and the end time of 'prev_composable' in GstClockTime
        'prev_otio_end', are used as references. Any xges <asset>
        elements needed for the <clip> are placed under the xges
        'ressources'.

        'next_composable' and 'prev_composable' may be None when no such
        sibling exists. 'prev_otio_end' should be the 'otio_end' that was
        returned from this method for 'prev_composable', or the initial
        time of the xges <timeline>. 'clip_id' should be the 'clip_id'
        that was returned from this method for 'prev_composable', or 0
        for the first clip.

        Note that a new clip may not be created for some otio types, such
        as otio.schema.Gaps, but the timings will be updated to accomodate
        them.

        Returns the 'clip_id' for the next clip, and the end time of
        'otio_composable' in the coordinates of the xges <timeline> in
        GstClockTime.
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
            asset_id = _TRANSITION_MAP.get(
                otio_composable.transition_type, "crossfade")
        elif isinstance(otio_composable, otio.schema.Clip):
            ref = otio_composable.media_reference
            if ref is None or ref.is_missing_reference:
                pass  # treat as a gap
                # FIXME: properly handle missing reference
            elif isinstance(ref,
                            (otio.schema.ExternalReference,
                             otio.schema.ImageSequenceReference)):
                asset_type = "GESUriClip"
                asset_id = self._serialize_external_reference_to_ressource(
                    ref, ressources)
            elif isinstance(ref, otio.schema.MissingReference):
                pass  # shouldn't really happen
            elif isinstance(ref, otio.schema.GeneratorReference):
                # FIXME: insert a GESTestClip if possible once otio
                # supports GeneratorReferenceTypes
                _show_otio_not_supported(
                    ref, "Treating as a gap")
            else:
                _show_otio_not_supported(
                    ref, "Treating as a gap")
        elif isinstance(otio_composable, otio.schema.Stack):
            asset_id = self._serialize_stack_to_ressource(
                otio_composable, ressources)
            asset_type = "GESUriClip"
        else:
            _show_otio_not_supported(otio_composable, "Treating as a gap")

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

        clip = self._insert_new_sub_element(
            layer, "clip", attrib={
                "id": str(clip_id),
                "asset-id": str(asset_id),
                "type-name": str(asset_type),
                "track-types": str(track_types),
                "layer-priority": str(layer_priority),
                "start": str(start),
                "rate": '0',
                "inpoint": str(inpoint),
                "duration": str(duration),
            }
        )
        self._add_properties_and_metadatas_to_element(
            clip, otio_composable, "clip",
            properties=self._get_properties_with_unique_name(
                otio_composable, "clip"))
        if isinstance(otio_composable, otio.core.Item):
            self._serialize_item_effects(
                otio_composable, clip, clip_id, track_types)
        return (clip_id + 1, otio_end)

    def _serialize_stack_to_tracks(self, otio_stack, timeline):
        """
        Create the xges <track> elements for the xges 'timeline' using
        'otio_stack'.
        """
        xges_tracks = self._get_from_otio_metadata(otio_stack, "tracks")
        if xges_tracks is None:
            xges_tracks = []
            # FIXME: track_id is currently arbitrarily set.
            # Only the xges effects, source and bindings elements use
            # a track-id attribute, which are not yet supported anyway.
            track_types = self._get_stack_track_types(otio_stack)
            for track_type in GESTrackType.OTIO_TYPES:
                if track_types & track_type:
                    xges_tracks.append(
                        XgesTrack.new_from_track_type(track_type))
        for track_id, xges_track in enumerate(xges_tracks):
            track_type = xges_track.track_type
            self._insert_new_sub_element(
                timeline, "track",
                attrib={
                    "caps": str(xges_track.caps),
                    "track-type": str(track_type),
                    "track-id": str(track_id),
                    "properties": str(xges_track.properties),
                    "metadatas": str(xges_track.metadatas)
                })
            if track_type in self.track_id_for_type:
                warnings.warn(
                    "More than one XgesTrack was found with the same "
                    "track type {0:d}.\nAll xges elements with "
                    "track-type={0:d} (such as effects) will use "
                    "track-id={1:d}.".format(
                        track_type, self.track_id_for_type[track_type]))
            else:
                self.track_id_for_type[track_type] = track_id

    def _serialize_track_to_layer(
            self, otio_track, timeline, layer_priority):
        """
        Convert 'otio_track' into an xges <layer> for the xges 'timeline'
        with the given 'layer_priority'. The layer is not yet filled with
        clips.
        """
        layer = self._insert_new_sub_element(
            timeline, "layer",
            attrib={"priority": str(layer_priority)})
        self._add_properties_and_metadatas_to_element(layer, otio_track)
        return layer

    def _serialize_stack_to_project(
            self, otio_stack, ges, otio_timeline):
        """
        Convert 'otio_stack' into an xges <project> for the xges 'ges'
        element. 'otio_timeline' should be the otio.schema.Timeline that
        'otio_stack' belongs to, or None if 'otio_stack' is a sub-stack.
        """
        metadatas = self._get_element_metadatas(otio_stack, "project")
        if not metadatas.get_typed("name", "string"):
            if otio_timeline is not None and otio_timeline.name:
                self._set_structure_value(
                    metadatas, "name", "string", otio_timeline.name)
            elif otio_stack.name:
                self._set_structure_value(
                    metadatas, "name", "string", otio_stack.name)
        project = self._insert_new_sub_element(ges, "project")
        self._add_properties_and_metadatas_to_element(
            project, otio_stack, "project", metadatas=metadatas)
        return project

    @staticmethod
    def _already_have_marker_at_position(
            position, color, comment, marker_list):
        """
        Test whether we already have a GESMarker in the GESMarkerList
        'marker_list' at the given 'position', approximately of the given
        otio.schema.MarkerColor 'color' and with the given 'comment'.
        """
        comment = comment or None
        for marker in marker_list.markers_at_position(position):
            if marker.get_nearest_otio_color() == color and \
                    marker.metadatas.get("comment") == comment:
                return True
        return False

    def _put_otio_marker_into_marker_list(self, otio_marker, marker_list):
        """
        Translate the otio.schema.Marker 'otio_marker' into a GESMarker
        and place it in the GESMarkerList 'marker_list' if it is not
        suspected to be a duplicate.
        If the duration of 'otio_marker' is not 0, up to two markers can
        be put in 'marker_list': one for the start time and one for the
        end time.
        """
        start, dur = self._range_to_gstclocktimes(otio_marker.marked_range)
        if dur:
            positions = (start, start + dur)
        else:
            positions = (start, )
        for position in positions:
            name = otio_marker.name
            if not self._already_have_marker_at_position(
                    position, otio_marker.color, name, marker_list):
                ges_marker = GESMarker(position)
                ges_marker.set_color_from_otio_color(otio_marker.color)
                if name:
                    ges_marker.metadatas.set(
                        "comment", "string", name)
                marker_list.add(ges_marker)

    def _serialize_stack_to_timeline(self, otio_stack, project):
        """
        Convert 'otio_stack' into an xges <timeline> under the xges
        'project', and return it. The timeline is not filled.
        """
        timeline = self._insert_new_sub_element(project, "timeline")
        metadatas = self._get_element_metadatas(otio_stack, "timeline")
        if otio_stack.markers:
            marker_list = metadatas.get_typed("markers", "GESMarkerList")
            if marker_list is None:
                lists = metadatas.values_of_type("GESMarkerList")
                if lists:
                    marker_list = max(lists, key=lambda lst: len(lst))
            if marker_list is None:
                self._set_structure_value(
                    metadatas, "markers", "GESMarkerList", GESMarkerList())
                marker_list = metadatas.get("markers")
            for otio_marker in otio_stack.markers:
                self._put_otio_marker_into_marker_list(
                    otio_marker, marker_list)
        self._add_properties_and_metadatas_to_element(
            timeline, otio_stack, "timeline", metadatas=metadatas)
        return timeline

    def _serialize_stack_to_ges(self, otio_stack, otio_timeline=None):
        """
        Convert 'otio_stack' into an xges <ges> and return it.
        'otio_timeline' should be the otio.schema.Timeline that
        'otio_stack' belongs to, or None if 'otio_stack' is a sub-stack.
        """
        ges = ElementTree.Element("ges", version="0.6")
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
            if otio_track.effects:
                min_start = None
                max_end = 0
                for clip in layer:
                    start = int(clip.get("start"))
                    end = start + int(clip.get("duration"))
                    if min_start is None or start < min_start:
                        min_start = start
                    if end > max_end:
                        max_end = end
                if min_start is None:
                    min_start = 0
                for otio_effect in otio_track.effects:
                    self._serialize_track_effect_to_effect_clip(
                        otio_effect, layer, layer_priority, min_start,
                        max_end - min_start, track_types, clip_id)
                    clip_id += 1
        return ges

    @staticmethod
    def _remove_non_xges_metadata(otio_obj):
        """Remove non-xges metadata from 'otio_obj.'"""
        keys = [k for k in otio_obj.metadata.keys()]
        for key in keys:
            if key != META_NAMESPACE:
                del otio_obj.metadata[key]

    @staticmethod
    def _add_track_types(otio_track, track_type):
        """
        Append the given 'track_type' to the metadata of 'otio_track'.
        """
        otio_track.metadata["track-types"] |= track_type

    @staticmethod
    def _set_track_types(otio_track, track_type):
        """Set the given 'track_type' on the metadata of 'otio_track."""
        otio_track.metadata["track-types"] = track_type

    @staticmethod
    def _get_track_types(otio_track):
        """
        Get the track types that we set on the metadata of 'otio_track'.
        """
        return otio_track.metadata["track-types"]

    @classmethod
    def _get_stack_track_types(cls, otio_stack):
        """Get the xges track types corresponding to 'otio_stack'."""
        track_types = 0
        for otio_track in otio_stack:
            track_types |= cls._get_track_types(otio_track)
        return track_types

    @classmethod
    def _init_track_types(cls, otio_track):
        """Initialise the track type metadat on 'otio_track'."""
        # May overwrite the metadata, but we have a deepcopy of the
        # original timeline and track-type is not otherwise used.
        cls._set_track_types(
            otio_track, GESTrackType.from_otio_kind(otio_track.kind))

    @classmethod
    def _merge_track_in_place(cls, otio_track, merge):
        """
        Merge the otio.schema.Track 'merge' into 'otio_track'.
        Note that the two tracks should be equal, modulo their track kind.
        """
        cls._add_track_types(otio_track, cls._get_track_types(merge))

    @classmethod
    def _equal_track_modulo_kind(cls, otio_track, compare):
        """
        Test whether 'otio_track' is equivalent to 'compare', ignoring
        any difference in their otio.schema.TrackKind.
        """
        otio_track_types = cls._get_track_types(otio_track)
        compare_track_types = cls._get_track_types(compare)
        if otio_track_types & compare_track_types:
            # do not want to merge two tracks if they overlap in
            # their track types. Otherwise, we may "loose" a track
            # after merging
            return False
        tmp_kind = compare.kind
        compare.kind = otio_track.kind
        cls._set_track_types(compare, otio_track_types)
        same = otio_track.is_equivalent_to(compare)
        compare.kind = tmp_kind
        cls._set_track_types(compare, compare_track_types)
        return same

    @classmethod
    def _merge_tracks_in_stack(cls, otio_stack):
        """
        Merge equivalent tracks found in the stack, modulo their track
        kind.
        """
        index = len(otio_stack) - 1  # start with higher priority
        while index > 0:
            track = otio_stack[index]
            next_track = otio_stack[index - 1]
            if cls._equal_track_modulo_kind(track, next_track):
                # want to merge if two tracks are the same, except their
                # track kind is *different*
                # merge down
                cls._merge_track_in_place(next_track, track)
                del otio_stack[index]
                # next track will be the merged one, which allows
                # us to merge again. Currently this is redundant since
                # there are only two track kinds
            index -= 1

    @classmethod
    def _pad_source_range_track(cls, otio_stack):
        """
        Go through the children of 'otio_stack'. If we find an
        otio.schema.Track with a set source_range, we replace it with an
        otio.schema.Track with no source_range. This track will have only
        one child, which will be an otio.schema.Stack with the same
        source_range. This stack will have only one child, which will be
        the original track.
        This is done because the source_range of a track is ignored when
        converting to xges, but the source_range of a stack is not.
        """
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
                cls._init_track_types(new_track)
                new_stack = otio.schema.Stack(
                    name=child.name,
                    source_range=child.source_range)
                child.source_range = None
                otio_stack[index] = new_track
                new_track.append(new_stack)
                new_stack.append(child)
            index += 1

    @staticmethod
    def _pad_double_track(otio_track):
        """
        If we find another otio.schema.Track under 'otio_track', we
        replace it with an otio.schema.Stack that contains the previous
        track as a single child.
        This is done because the conversion to xges expects to only find
        non-tracks under a track.
        """
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

    @classmethod
    def _pad_non_track_children_of_stack(cls, otio_stack):
        """
        If we find a child of 'otio_stack' that is not an
        otio.schema.Track, we replace it with a new otio.schema.Track
        that contains the previous child as its own single child.
        This is done because the conversion to xges expects to only find
        tracks under a stack.
        """
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
                    cls._set_track_types(
                        insert, cls._get_stack_track_types(child))
                else:
                    warnings.warn(
                        "Found an otio {} object directly under a "
                        "Stack.\nTreating as a Video and Audio source."
                        "".format(child.schema_name()))
                    cls._set_track_types(
                        insert, GESTrackType.VIDEO | GESTrackType.AUDIO)
                otio_stack[index] = insert
                insert.append(child)
            index += 1

    @staticmethod
    def _move_markers_into(from_otio, into_otio):
        """Move the markers found in 'from_otio' into 'into_otio'."""
        for otio_marker in from_otio.markers:
            otio_marker.marked_range = from_otio.transformed_time_range(
                otio_marker.marked_range, into_otio)
            into_otio.markers.append(otio_marker)
        if hasattr(from_otio.markers, "clear"):
            from_otio.markers.clear()
        else:
            # TODO: remove below when python2 has ended
            # markers has no clear method
            while from_otio.markers:
                from_otio.markers.pop()

    @classmethod
    def _move_markers_to_stack(cls, otio_stack):
        """
        Move all the otio.schema.Markers found in the children of
        'otio_stack' into itself.
        """
        for otio_track in otio_stack:
            cls._move_markers_into(otio_track, otio_stack)
            for otio_composable in otio_track:
                if isinstance(otio_composable, otio.core.Item) and \
                        not isinstance(otio_composable, otio.schema.Stack):
                    cls._move_markers_into(otio_composable, otio_stack)

    @classmethod
    def _perform_bottom_up(cls, func, otio_composable, filter_type):
        """
        Perform the given 'func' on all otio composables of the given
        'filter_type' that are found below the given 'otio_composable'.

        This works from the lowest child upwards.

        The given function 'func' should accept a single argument, and
        should not change the number or order of siblings within the
        arguments's parent, but it is OK to change the children of the
        argument.
        """
        if isinstance(otio_composable, otio.core.Composition):
            for child in otio_composable:
                cls._perform_bottom_up(func, child, filter_type)
        if isinstance(otio_composable, filter_type):
            func(otio_composable)

    def _prepare_timeline(self):
        """
        Prepare the timeline given to 'self' for conversion to xges, by
        placing it in a desired format.
        """
        if self.timeline.tracks.source_range is not None or \
                self.timeline.tracks.effects:
            # only xges clips can correctly handle a trimmed
            # source_range, so place this stack one layer down. Note
            # that a dummy track will soon be inserted between these
            # two stacks
            #
            # if the top stack contains effects, we do the same so that
            # we can simply apply the effects to the clip
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
        self._perform_bottom_up(
            self._move_markers_to_stack,
            self.timeline.tracks, otio.schema.Stack)

    def to_xges(self):
        """
        Convert the otio.schema.Timeline given to 'self' into an xges
        string.
        """
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
    GstStructure  GstStructure  structure
                  schema
    GstCaps       GstCaps
                  schema
    GESMarkerList GESMarkerList
                  schema

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

    INT_TYPES = ("int", "glong", "gint64")
    UINT_TYPES = ("uint", "gulong", "guint64")
    FLOAT_TYPES = ("float", "double")
    BOOLEAN_TYPE = "boolean"
    FRACTION_TYPE = "fraction"
    STRING_TYPE = "string"
    STRUCTURE_TYPE = "structure"
    CAPS_TYPE = "GstCaps"
    MARKER_LIST_TYPE = "GESMarkerList"
    KNOWN_TYPES = INT_TYPES + UINT_TYPES + FLOAT_TYPES + (
        BOOLEAN_TYPE, FRACTION_TYPE, STRING_TYPE, STRUCTURE_TYPE,
        CAPS_TYPE, MARKER_LIST_TYPE)

    TYPE_ALIAS = {
        "i": "int",
        "gint": "int",
        "u": "uint",
        "guint": "uint",
        "f": "float",
        "gfloat": "float",
        "d": "double",
        "gdouble": "double",
        "b": BOOLEAN_TYPE,
        "bool": BOOLEAN_TYPE,
        "gboolean": BOOLEAN_TYPE,
        "GstFraction": FRACTION_TYPE,
        "str": STRING_TYPE,
        "s": STRING_TYPE,
        "GstStructure": STRUCTURE_TYPE
    }

    def __init__(self, name=None, fields=None):
        otio.core.SerializableObject.__init__(self)
        if name is None:
            name = "Unnamed"
        if fields is None:
            fields = {}
        name = unicode_to_str(name)
        if type(name) is not str:
            _wrong_type_for_arg(name, "str", "name")
        self._check_name(name)
        self.name = name
        try:
            fields = dict(fields)
        except (TypeError, ValueError):
            _wrong_type_for_arg(fields, "dict", "fields")
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

    def __repr__(self):
        return f"GstStructure({self.name!r}, {self.fields!r})"

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

    def _field_to_str(self, key):
        """Return field in a serialized form"""
        _type, value = self.fields[key]
        _type = unicode_to_str(_type)
        key = unicode_to_str(key)
        value = unicode_to_str(value)
        if type(key) is not str:
            raise TypeError("Found a key that is not a str type")
        if type(_type) is not str:
            raise TypeError(
                "Found a type name that is not a str type")
        self._check_key(key)
        _type = self.TYPE_ALIAS.get(_type, _type)
        if self._is_unknown_type(_type):
            _type = self._get_unknown_type(_type)
            self._check_type(_type)
            self._check_unknown_typed_value(value)
            # already in serialized form
        else:
            self._check_type(_type)
            value = self.serialize_value(_type, value)
        return f"{key}=({_type}){value}"

    def _fields_to_str(self):
        write = []
        for key in self.fields:
            write.append(f", {self._field_to_str(key)}")
        return "".join(write)

    def _name_to_str(self):
        """Return the name in a serialized form"""
        name = unicode_to_str(self.name)
        self._check_name(name)
        return name

    def __str__(self):
        """Emulates gst_structure_to_string"""
        return f"{self._name_to_str()}{self._fields_to_str()};"

    def get_type_name(self, key):
        """Return the field type"""
        _type = self.fields[key][0]
        _type = unicode_to_str(_type)
        return _type

    def get_value(self, key):
        """Return the field value"""
        value = self.fields[key][1]
        value = unicode_to_str(value)
        return value

    def __getitem__(self, key):
        return self.get_value(key)

    def __len__(self):
        return len(self.fields)

    @staticmethod
    def _val_type_err(typ, val, expect):
        raise TypeError(
            "Received value ({!s}) is a {} rather than a {}, even "
            "though the {} type was given".format(
                val, type(val).__name__, expect, typ))

    def set(self, key, _type, value):
        """Set a field to the given typed value"""
        key = unicode_to_str(key)
        _type = unicode_to_str(_type)
        value = unicode_to_str(value)
        if type(key) is not str:
            _wrong_type_for_arg(key, "str", "key")
        if type(_type) is not str:
            _wrong_type_for_arg(_type, "str", "_type")
        _type = self.TYPE_ALIAS.get(_type, _type)
        if self.fields.get(key) == (_type, value):
            return
        self._check_key(key)
        type_is_unknown = True
        if self._is_unknown_type(_type):
            # this can happen if the user is setting a GstStructure
            # using a preexisting GstStructure, the type will then
            # be passed and marked as unknown
            _type = self._get_unknown_type(_type)
            self._check_type(_type)
        else:
            self._check_type(_type)
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
                    raise InvalidValueError(
                        "value", value, "a positive integer for {} "
                        "types".format(_type))
            elif _type in self.FLOAT_TYPES:
                type_is_unknown = False
                if type(value) is not float:
                    self._val_type_err(_type, value, "float")
            elif _type == self.BOOLEAN_TYPE:
                type_is_unknown = False
                if type(value) is not bool:
                    self._val_type_err(_type, value, "bool")
            elif _type == self.FRACTION_TYPE:
                type_is_unknown = False
                if type(value) is Fraction:
                    value = str(value)  # store internally as a str
                elif type(value) is str:
                    try:
                        Fraction(value)
                    except ValueError:
                        raise InvalidValueError(
                            "value", value, "a fraction for the {} "
                            "types".format(_type))
                else:
                    self._val_type_err(_type, value, "Fraction or str")
            elif _type == self.STRING_TYPE:
                type_is_unknown = False
                if value is not None and type(value) is not str:
                    self._val_type_err(_type, value, "str or None")
            elif _type == self.STRUCTURE_TYPE:
                type_is_unknown = False
                if not isinstance(value, GstStructure):
                    self._val_type_err(_type, value, "GstStructure")
            elif _type == self.CAPS_TYPE:
                type_is_unknown = False
                if not isinstance(value, GstCaps):
                    self._val_type_err(_type, value, "GstCaps")
            elif _type == self.MARKER_LIST_TYPE:
                type_is_unknown = False
                if not isinstance(value, GESMarkerList):
                    self._val_type_err(_type, value, "GESMarkerList")
        if type_is_unknown:
            self._check_unknown_typed_value(value)
            warnings.warn(
                "The GstStructure type {} with the value ({}) is "
                "unknown. The value will be stored and serialized as "
                "given.".format(_type, value))
            _type = self._make_type_unknown(_type)
        self.fields[key] = (_type, value)
        # NOTE: in python2, otio will convert a str value to a unicode

    def get(self, key, default=None):
        """Return the raw value associated with key"""
        if key in self.fields:
            value = self.get_value(key)
            value = unicode_to_str(value)
            return value
        return default

    def get_typed(self, key, expect_type, default=None):
        """
        Return the raw value associated with key if its type matches.
        Raises a warning if a value exists under key but is of the
        wrong type.
        """
        expect_type = unicode_to_str(expect_type)
        if type(expect_type) is not str:
            _wrong_type_for_arg(expect_type, "str", "expect_type")
        expect_type = self.TYPE_ALIAS.get(expect_type, expect_type)
        if key in self.fields:
            type_name = self.get_type_name(key)
            if expect_type == type_name:
                value = self.get_value(key)
                value = unicode_to_str(value)
                return value
            warnings.warn(
                "The structure {} contains a value under {}, but is "
                "a {}, rather than the expected {} type".format(
                    self.name, key, type_name, expect_type))
        return default

    def values(self):
        """Return a list of all values contained in the structure"""
        return [self.get_value(key) for key in self.fields]

    def values_of_type(self, _type):
        """
        Return a list of all values contained of the given type in the
        structure
        """
        _type = unicode_to_str(_type)
        if type(_type) is not str:
            _wrong_type_for_arg(_type, "str", "_type")
        _type = self.TYPE_ALIAS.get(_type, _type)
        return [self.get_value(key) for key in self.fields
                if self.get_type_name(key) == _type]

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
        # TODO: once python2 has ended, use 'fullmatch'
        if not regex.match(check):
            raise InvalidValueError(
                name, check, "to match the regular expression {}"
                "".format(regex.pattern))

    # TODO: once python2 has ended, we can drop the trailing $ and use
    # re.fullmatch in _check_against_regex
    NAME_REGEX = re.compile(NAME_FORMAT + "$")
    KEY_REGEX = re.compile(KEY_FORMAT + "$")
    TYPE_REGEX = re.compile(TYPE_FORMAT + "$")

    @classmethod
    def _check_name(cls, name):
        cls._check_against_regex(name, cls.NAME_REGEX, "name")

    @classmethod
    def _check_key(cls, key):
        cls._check_against_regex(key, cls.KEY_REGEX, "key")

    @classmethod
    def _check_type(cls, _type):
        cls._check_against_regex(_type, cls.TYPE_REGEX, "type")

    @classmethod
    def _check_unknown_typed_value(cls, value):
        if type(value) is not str:
            cls._val_type_err("unknown", value, "string")
        try:
            # see if the value could be successfully parsed in again
            ret_type, ret_val, _ = cls._parse_value(value, False)
        except DeserializeError as err:
            raise InvalidValueError(
                "value", value, "unknown-typed values to be in a "
                "serialized format ({!s})".format(err))
        else:
            if ret_type is not None:
                raise InvalidValueError(
                    "value", value, "unknown-typed values to *not* "
                    "start with a type specification, only the "
                    "serialized value should be given")
            if ret_val != value:
                raise InvalidValueError(
                    "value", value, "unknown-typed values to be the "
                    "same as its parsed value {}".format(ret_val))

    PARSE_NAME_REGEX = re.compile(
        ASCII_SPACES + NAME_FORMAT + END_FORMAT)

    @classmethod
    def _parse_name(cls, read):
        match = cls.PARSE_NAME_REGEX.match(read)
        if match is None:
            raise DeserializeError(
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
        while read and read[0] != end:
            if first:
                first = False
            else:
                if read and read[0] != ',':
                    DeserializeError(
                        read, "does not contain a comma between listed "
                        "items")
                values.append(", ")
                read = read[1:]
            _type, value, read = cls._parse_value(read, False)
            if _type is not None:
                if cls._is_unknown_type(_type):
                    # remove unknown marker for serialization
                    _type = cls._get_unknown_type(_type)
                values.extend(('(', _type, ')'))
            values.append(value)
        if not read:
            raise DeserializeError(
                read, f"ended before {end} could be found")
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
            raise DeserializeError(
                read, "does not contain a valid '(type)' format")
        _type = cls.TYPE_ALIAS.get(_type, _type)
        type_is_unknown = True
        read = read[match.end("end"):]
        if read and read[0] in ('[', '{', '<'):
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
                raise DeserializeError(
                    read, "does not have a valid value format")
            read = read[match.end("end"):]
            value = match.group("value")
            if deserialize:
                if _type in cls.KNOWN_TYPES:
                    type_is_unknown = False
                    try:
                        value = cls.deserialize_value(_type, value)
                    except DeserializeError as err:
                        raise DeserializeError(
                            read, "contains an invalid typed value "
                            "({!s})".format(err))
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
            raise DeserializeError(
                read, "does not have a valid 'key=...' format")
        key = match.group("key")
        read = read[match.end("end"):]
        _type, value, read = cls._parse_value(read)
        return key, _type, value, read

    @classmethod
    def _parse_fields(cls, read):
        read = unicode_to_str(read)
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        fields = {}
        while read and read[0] != ';':
            if read and read[0] != ',':
                DeserializeError(
                    read, "does not separate fields with commas")
            read = read[1:]
            key, _type, value, read = cls._parse_field(read)
            fields[key] = (_type, value)
        if read:
            # read[0] == ';'
            read = read[1:]
        return fields, read

    @classmethod
    def new_from_str(cls, read):
        """
        Returns a new instance of GstStructure, based on the Gst library
        function gst_structure_from_string.
        Strings obtained from the GstStructure str() method can be
        parsed in to recreate the original GstStructure.
        """
        read = unicode_to_str(read)
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        name, read = cls._parse_name(read)
        fields = cls._parse_fields(read)[0]
        return GstStructure(name=name, fields=fields)

    @staticmethod
    def _val_read_err(typ, val):
        raise DeserializeError(
            val, f"does not translated to the {typ} type")

    @classmethod
    def deserialize_value(cls, _type, value):
        """Return the value as the corresponding type"""
        _type = unicode_to_str(_type)
        if type(_type) is not str:
            _wrong_type_for_arg(_type, "str", "_type")
        value = unicode_to_str(value)
        if type(value) is not str:
            _wrong_type_for_arg(value, "str", "value")
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
        elif _type == cls.BOOLEAN_TYPE:
            try:
                value = cls.deserialize_boolean(value)
            except DeserializeError:
                cls._val_read_err(_type, value)
        elif _type == cls.FRACTION_TYPE:
            try:
                value = str(Fraction(value))  # store internally as a str
            except ValueError:
                cls._val_read_err(_type, value)
        elif _type == cls.STRING_TYPE:
            try:
                value = cls.deserialize_string(value)
            except DeserializeError as err:
                raise DeserializeError(
                    value, "does not translate to a string ({!s})"
                    "".format(err))
        elif _type == cls.STRUCTURE_TYPE:
            try:
                value = cls.deserialize_structure(value)
            except DeserializeError as err:
                raise DeserializeError(
                    value, "does not translate to a GstStructure ({!s})"
                    "".format(err))
        elif _type == cls.CAPS_TYPE:
            try:
                value = cls.deserialize_caps(value)
            except DeserializeError as err:
                raise DeserializeError(
                    value, "does not translate to a GstCaps ({!s})"
                    "".format(err))
        elif _type == cls.MARKER_LIST_TYPE:
            try:
                value = cls.deserialize_marker_list(value)
            except DeserializeError as err:
                raise DeserializeError(
                    value, "does not translate to a GESMarkerList "
                    "({!s})".format(err))
        else:
            raise ValueError(
                "The type {} is unknown, so the value ({}) can not "
                "be deserialized.".format(_type, value))
        return value

    @classmethod
    def serialize_value(cls, _type, value):
        """Serialize the typed value as a string"""
        _type = unicode_to_str(_type)
        if type(_type) is not str:
            _wrong_type_for_arg(_type, "str", "_type")
        value = unicode_to_str(value)
        _type = cls.TYPE_ALIAS.get(_type, _type)
        if _type in cls.INT_TYPES + cls.UINT_TYPES + cls.FLOAT_TYPES \
                + (cls.FRACTION_TYPE, ):
            return str(value)
        if _type == cls.BOOLEAN_TYPE:
            return cls.serialize_boolean(value)
        if _type == cls.STRING_TYPE:
            return cls.serialize_string(value)
        if _type == cls.STRUCTURE_TYPE:
            return cls.serialize_structure(value)
        if _type == cls.CAPS_TYPE:
            return cls.serialize_caps(value)
        if _type == cls.MARKER_LIST_TYPE:
            return cls.serialize_marker_list(value)
        raise ValueError(
            "The type {} is unknown, so the value ({}) can not be "
            "serialized.".format(_type, str(value)))

    # see GST_ASCII_IS_STRING in gst_private.h
    GST_ASCII_CHARS = [
        ord(letter) for letter in
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "_-+/:."
    ]
    LEADING_OCTAL_CHARS = [ord(letter) for letter in "0123"]
    OCTAL_CHARS = [ord(letter) for letter in "01234567"]

    @classmethod
    def serialize_string(cls, value):
        """
        Emulates gst_value_serialize_string.
        Accepts a bytes, str or None type.
        Returns a str type.
        """
        if value is not None and type(value) is not str:
            _wrong_type_for_arg(value, "None or str", "value")
        return cls._wrap_string(value)

    @classmethod
    def _wrap_string(cls, read):
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
            _wrong_type_for_arg(read, "None, str, or bytes", "read")
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
                ser_string_list.append(f"\\{byte:03o}")
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
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        if read == "NULL":
            return None
        if not read:
            return ""
        if read[0] != '"' or read[-1] != '"':
            return read
        return cls._unwrap_string(read)

    @classmethod
    def _unwrap_string(cls, read):
        """Emulates gst_string_unwrap"""
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
                raise DeserializeError(read, "end unexpectedly")

        byte = next_byte()
        if byte != ord('"'):
            raise DeserializeError(
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
                raise DeserializeError(
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
                        raise DeserializeError(
                            read, "contains the start of an octal "
                            "sequence but not the end")
                else:
                    if byte == 0:
                        raise DeserializeError(
                            read, "contains a null byte after an escape")
                    byte_list.append(byte)
            else:
                raise DeserializeError(
                    read, "contains an unexpected un-escaped character")
        out_str = bytes(bytearray(byte_list))
        if type(out_str) is str:
            # TODO: remove once python2 has ended
            # and simplify above to only call bytes(byte_list)
            return out_str
        try:
            return out_str.decode()
        except (UnicodeError, ValueError):
            raise DeserializeError(
                read, "contains invalid utf-8 byte sequences")

    @staticmethod
    def serialize_boolean(value):
        """
        Emulates gst_value_serialize_boolean.
        Accepts bool type.
        Returns a str type.
        """
        if type(value) is not bool:
            _wrong_type_for_arg(value, "bool", "value")
        if value:
            return "true"
        return "false"

    @staticmethod
    def deserialize_boolean(read):
        """
        Emulates gst_value_deserialize_boolean.
        Accepts str type.
        Returns a bool type.
        """
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        if read.lower() in ("true", "t", "yes", "1"):
            return True
        if read.lower() in ("false", "f", "no", "0"):
            return False
        raise DeserializeError(read, "is an unknown boolean value")

    @classmethod
    def serialize_structure(cls, value):
        """
        Emulates gst_value_serialize_structure.
        Accepts a GstStructure.
        Returns a str type.
        """
        if not isinstance(value, GstStructure):
            _wrong_type_for_arg(value, "GstStructure", "value")
        return cls._wrap_string(str(value))

    @classmethod
    def deserialize_structure(cls, read):
        """
        Emulates gst_value_serialize_structure.
        Accepts a str type.
        Returns a GstStructure.
        """
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        if read[0] == '"':
            # NOTE: since all GstStructure strings end with ';', we
            # don't ever expect the above to *not* be true, but the
            # GStreamer library allows for this case
            try:
                read = cls._unwrap_string(read)
                # NOTE: in the GStreamer library, serialized
                # GstStructure and GstCaps strings are sent to
                # _priv_gst_value_parse_string with unescape set to
                # TRUE. What this essentially does is replace "\x" with
                # just "x". Since caps and structure strings should only
                # contain printable ascii characters before they are
                # passed to _wrap_string, this should be equivalent to
                # calling _unwrap_string. Our method is more clearly a
                # reverse of the serialization method.
            except DeserializeError as err:
                raise DeserializeError(
                    read, "could not be unwrapped as a string ({!s})"
                    "".format(err))
        return GstStructure.new_from_str(read)

    @classmethod
    def serialize_caps(cls, value):
        """
        Emulates gst_value_serialize_caps.
        Accepts a GstCaps.
        Returns a str type.
        """
        if not isinstance(value, GstCaps):
            _wrong_type_for_arg(value, "GstCaps", "value")
        return cls._wrap_string(str(value))

    @classmethod
    def deserialize_caps(cls, read):
        """
        Emulates gst_value_serialize_caps.
        Accepts a str type.
        Returns a GstCaps.
        """
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        if read[0] == '"':
            # can be not true if a caps only contains a single empty
            # structure, or is ALL or NONE
            try:
                read = cls._unwrap_string(read)
            except DeserializeError as err:
                raise DeserializeError(
                    read, "could not be unwrapped as a string ({!s})"
                    "".format(err))
        return GstCaps.new_from_str(read)

    @classmethod
    def serialize_marker_list(cls, value):
        """
        Emulates ges_marker_list_serialize.
        Accepts a GESMarkerList.
        Returns a str type.
        """
        if not isinstance(value, GESMarkerList):
            _wrong_type_for_arg(value, "GESMarkerList", "value")
        caps = GstCaps()
        for marker in value.markers:
            caps.append(GstStructure(
                "marker-times",
                {"position": ("guint64", marker.position)}))
            caps.append(marker.metadatas)
            # NOTE: safe to give the metadatas to the caps since we
            # will not be using caps after this function
            # i.e. the caller will still have essential ownership of
            # the matadatas
        return cls._escape_string(str(caps))

    @staticmethod
    def _escape_string(read):
        """
        Emulates some of g_strescape's behaviour in
        ges_marker_list_serialize
        """
        # NOTE: in the original g_strescape, all the special characters
        # '\b', '\f', '\n', '\r', '\t', '\v', '\' and '"' are escaped,
        # and all characters in the range 0x01-0x1F and non-ascii
        # characters are replaced by an octal sequence
        # (similar to _wrap_string).
        # However, a caps string should only contain printable ascii
        # characters, so it should be sufficient to simply escape '\'
        # and '"'.
        escaped = ['"']
        for character in read:
            if character in ('"', '\\'):
                escaped.append('\\')
            escaped.append(character)
        escaped.append('"')
        return "".join(escaped)

    @classmethod
    def deserialize_marker_list(cls, read):
        """
        Emulates ges_marker_list_deserialize.
        Accepts a str type.
        Returns a GESMarkerList.
        """
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        read = cls._unescape_string(read)
        # Above is actually performed by _priv_gst_value_parse_value,
        # but it is called immediately before gst_value_deserialize
        caps = GstCaps.new_from_str(read)
        if len(caps) % 2:
            raise DeserializeError(
                read, "does not contain an even-sized caps")
        position = None
        marker_list = GESMarkerList()
        for index, (struct, _) in enumerate(caps.structs):
            if index % 2 == 0:
                if struct.name != "marker-times":
                    raise DeserializeError(
                        read, "contains a structure named {} rather "
                        "than the expected \"marker-times\"".format(
                            struct.name))
                if "position" not in struct.fields:
                    raise DeserializeError(
                        read, "is missing a position value")
                if struct.get_type_name("position") != "guint64":
                    raise DeserializeError(
                        read, "does not have a guint64 typed position")
                position = struct["position"]
            else:
                marker_list.add(GESMarker(position, struct))
        return marker_list

    @staticmethod
    def _unescape_string(read):
        """
        Emulates behaviour of _priv_gst_value_parse_string with
        unescape set to TRUE. This should undo _escape_string
        """
        if read[0] != '"':
            return read
        character_iter = iter(read)

        def next_char():
            try:
                return next(character_iter)
            except StopIteration:
                raise DeserializeError(read, "ends unexpectedly")

        next_char()  # skip '"'
        unescaped = []
        while True:
            character = next_char()
            if character == '"':
                break
            if character == '\\':
                unescaped.append(next_char())
            else:
                unescaped.append(character)
        return "".join(unescaped)


@otio.core.register_type
class GstCapsFeatures(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema that contains a collection of features,
    mimicking a GstCapsFeatures of the Gstreamer C libarary.
    """
    _serializable_label = "GstCapsFeatures.1"
    is_any = otio.core.serializable_field(
        "is_any", bool, "Whether a GstCapsFeatures matches any. If "
        "True, then features must be empty.")
    features = otio.core.serializable_field(
        "features", list, "A list of features, as strings")

    def __init__(self, *features):
        """
        Initialize the GstCapsFeatures.

        'features' should be a series of feature names as strings.
        """
        otio.core.SerializableObject.__init__(self)
        self.is_any = False
        self.features = []
        for feature in features:
            feature = unicode_to_str(feature)
            if type(feature) is not str:
                _wrong_type_for_arg(feature, "strs", "features")
            self._check_feature(feature)
            self.features.append(feature)
            # NOTE: if 'features' is a str, rather than a list of strs
            # then this will iterate through all of its characters! But,
            # a single character can not match the feature regular
            # expression.

    def __getitem__(self, index):
        return self.features[index]

    def __len__(self):
        return len(self.features)

    @classmethod
    def new_any(cls):
        features = cls()
        features.is_any = True
        return features

    # Based on gst_caps_feature_name_is_valid
    FEATURE_FORMAT = r"(?P<feature>[a-zA-Z]*:[a-zA-Z][a-zA-Z0-9]*)"
    # TODO: once python2 has ended, we can drop the trailing $ and use
    # re.fullmatch in _check_feature
    FEATURE_REGEX = re.compile(FEATURE_FORMAT + "$")

    @classmethod
    def _check_feature(cls, feature):
        # TODO: once python2 has ended, use 'fullmatch'
        if not cls.FEATURE_REGEX.match(feature):
            raise InvalidValueError(
                "feature", feature, "to match the regular expression "
                "{}".format(cls.FEATURE_REGEX.pattern))

    PARSE_FEATURE_REGEX = re.compile(
        r" *" + FEATURE_FORMAT + "(?P<end>)")

    @classmethod
    def new_from_str(cls, read):
        """
        Returns a new instance of GstCapsFeatures, based on the Gst
        library function gst_caps_features_from_string.
        Strings obtained from the GstCapsFeatures str() method can be
        parsed in to recreate the original GstCapsFeatures.
        """
        read = unicode_to_str(read)
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        if read == "ANY":
            return cls.new_any()
        first = True
        features = []
        while read:
            if first:
                first = False
            else:
                if read[0] != ',':
                    DeserializeError(
                        read, "does not separate features with commas")
                read = read[1:]
            match = cls.PARSE_FEATURE_REGEX.match(read)
            if match is None:
                raise DeserializeError(
                    read, "does not match the regular expression {}"
                    "".format(cls.PARSE_FEATURE_REGEX.pattern))
            features.append(match.group("feature"))
            read = read[match.end("end"):]
        return cls(*features)

    def __repr__(self):
        if self.is_any:
            return "GstCapsFeatures.new_any()"
        write = ["GstCapsFeatures("]
        first = True
        for feature in self.features:
            if first:
                first = False
            else:
                write.append(", ")
            write.append(repr(feature))
        write.append(")")
        return "".join(write)

    def __str__(self):
        """Emulate gst_caps_features_to_string"""
        if not self.features and self.is_any:
            return "ANY"
        write = []
        first = True
        for feature in self.features:
            feature = unicode_to_str(feature)
            if type(feature) is not str:
                raise TypeError(
                    "Found a feature that is not a str type")
            if first:
                first = False
            else:
                write.append(", ")
            write.append(feature)
        return "".join(write)


@otio.core.register_type
class GstCaps(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema that acts as an ordered collection of
    GstStructures, essentially mimicking the GstCaps of the Gstreamer C
    libarary. Each GstStructure is linked to a GstCapsFeatures, which is
    a list of features.

    In particular, this schema mimics the gst_caps_to_string and
    gst_caps_from_string C methods.
    """
    _serializable_label = "GstCaps.1"

    structs = otio.core.serializable_field(
        "structs", list, "A list of GstStructures and GstCapsFeatures, "
        "of the form:\n"
        "    (struct, features)\n"
        "where 'struct' is a GstStructure, and 'features' is a "
        "GstCapsFeatures")
    flags = otio.core.serializable_field(
        "flags", int, "Additional GstCapsFlags on the GstCaps")

    GST_CAPS_FLAG_ANY = 1 << 4
    # from GST_MINI_OBJECT_FLAG_LAST

    def __init__(self, *structs):
        """
        Initialize the GstCaps.

        'structs' should be a series of GstStructures, and
        GstCapsFeatures pairs:
            struct0, features0, struct1, features1, ...
        None may be given in place of a GstCapsFeatures, in which case
        an empty features is assigned to the structure.

        Note, this instance will need to take ownership of any given
        GstStructure or GstCapsFeatures.
        """
        otio.core.SerializableObject.__init__(self)
        if len(structs) % 2:
            raise InvalidValueError(
                "*structs", structs, "an even number of arguments")
        self.flags = 0
        self.structs = []
        struct = None
        for index, arg in enumerate(structs):
            if index % 2 == 0:
                struct = arg
            else:
                self.append(struct, arg)

    def get_structure(self, index):
        """Return the GstStructure at the given index"""
        return self.structs[index][0]

    def get_features(self, index):
        """Return the GstStructure at the given index"""
        return self.structs[index][1]

    def __getitem__(self, index):
        return self.get_structure(index)

    def __len__(self):
        return len(self.structs)

    @classmethod
    def new_any(cls):
        caps = cls()
        caps.flags = cls.GST_CAPS_FLAG_ANY
        return caps

    def is_any(self):
        return self.flags & self.GST_CAPS_FLAG_ANY != 0

    FEATURES_FORMAT = r"\((?P<features>[^)]*)\)"
    NAME_FEATURES_REGEX = re.compile(
        GstStructure.ASCII_SPACES + GstStructure.NAME_FORMAT
        + r"(" + FEATURES_FORMAT + r")?" + GstStructure.END_FORMAT)

    @classmethod
    def new_from_str(cls, read):
        """
        Returns a new instance of GstCaps, based on the Gst library
        function gst_caps_from_string.
        Strings obtained from the GstCaps str() method can be parsed in
        to recreate the original GstCaps.
        """
        read = unicode_to_str(read)
        if type(read) is not str:
            _wrong_type_for_arg(read, "str", "read")
        if read == "ANY":
            return cls.new_any()
        if read in ("EMPTY", "NONE"):
            return cls()
        structs = []
        # restriction-caps is otherwise serialized in the format:
        #   "struct-name-nums(feature), "
        #   "field1=(type1)val1, field2=(type2)val2; "
        #   "struct-name-alphas(feature), "
        #   "fieldA=(typeA)valA, fieldB=(typeB)valB"
        # Note the lack of ';' for the last structure, and the
        # '(feature)' is optional.
        #
        # NOTE: gst_caps_from_string also accepts:
        #   "struct-name(feature"
        # without the final ')', but this must be the end of the string,
        # but we will require that this final ')' is still given
        while read:
            match = cls.NAME_FEATURES_REGEX.match(read)
            if match is None:
                raise DeserializeError(
                    read, "does not match the regular expression {}"
                    "".format(cls.NAME_FEATURE_REGEX.pattern))
            read = read[match.end("end"):]
            name = match.group("name")
            features = match.group("features")
            # NOTE: features may be None since the features part of the
            # regular expression is optional
            if features is None:
                features = GstCapsFeatures()
            else:
                features = GstCapsFeatures.new_from_str(features)
            fields, read = GstStructure._parse_fields(read)
            structs.append(GstStructure(name, fields))
            structs.append(features)
        return cls(*structs)

    def __repr__(self):
        if self.is_any():
            return "GstCaps.new_any()"
        write = ["GstCaps("]
        first = True
        for struct in self.structs:
            if first:
                first = False
            else:
                write.append(", ")
            write.append(repr(struct[0]))
            write.append(", ")
            write.append(repr(struct[1]))
        write.append(")")
        return "".join(write)

    def __str__(self):
        """Emulate gst_caps_to_string"""
        if self.is_any():
            return "ANY"
        if not self.structs:
            return "EMPTY"
        first = True
        write = []
        for struct, features in self.structs:
            if first:
                first = False
            else:
                write.append("; ")
            write.append(struct._name_to_str())
            if features.is_any or features.features:
                # NOTE: is gst_caps_to_string, the feature will not
                # be written if it only contains the
                # GST_FEATURE_MEMORY_SYSTEM_MEMORY feature, since this
                # considered equal to being an empty features.
                # We do not seem to require this behaviour
                write.append(f"({features!s})")
            write.append(struct._fields_to_str())
        return "".join(write)

    def append(self, structure, features=None):
        """Append a structure with the given features"""
        if not isinstance(structure, GstStructure):
            _wrong_type_for_arg(structure, "GstStructure", "structure")
        if features is None:
            features = GstCapsFeatures()
        if not isinstance(features, GstCapsFeatures):
            _wrong_type_for_arg(
                features, "GstCapsFeatures or None", "features")
        self.structs.append((structure, features))


@otio.core.register_type
class GESMarker(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema that is a timestamp with metadata,
    essentially mimicking the GstMarker of the GES C libarary.
    """
    _serializable_label = "GESMarker.1"

    position = otio.core.serializable_field(
        "position", int, "The timestamp of the marker as a "
        "GstClockTime (unsigned integer time in nanoseconds)")

    metadatas = otio.core.serializable_field(
        "metadatas", GstStructure, "The metadatas associated with the "
        "position")

    def __init__(self, position=0, metadatas=None):
        """
        Note, this instance will need to take ownership of any given
        GstSructure.
        """
        otio.core.SerializableObject.__init__(self)
        if metadatas is None:
            metadatas = GstStructure("metadatas")
        if type(position) is not int:
            # TODO: remove below once python2 has ended
            # currently in python2, can receive either an int or
            # a long
            if isinstance(position, numbers.Integral):
                position = int(position)
                # may still be an int if the position is too big
            if type(position) is not int:
                _wrong_type_for_arg(position, "int", "position")
        if position < 0:
            raise InvalidValueError(
                "position", position, "a positive integer")

        if not isinstance(metadatas, GstStructure):
            _wrong_type_for_arg(metadatas, "GstStructure", "metadatas")
        _force_gst_structure_name(metadatas, "metadatas", "GESMarker")
        self.position = position
        self.metadatas = metadatas

    GES_META_MARKER_COLOR = "marker-color"

    def set_color_from_argb(self, argb):
        """Set the color of the marker using the AARRGGBB hex value"""
        if not isinstance(argb, int):
            _wrong_type_for_arg(argb, "int", "argb")
        if argb < 0 or argb > 0xffffffff:
            raise InvalidValueError(
                "argb", argb, "an unsigned 8 digit AARRGGBB hexadecimal")
        self.metadatas.set(self.GES_META_MARKER_COLOR, "uint", argb)

    def is_colored(self):
        """Return whether a marker is colored"""
        return self.GES_META_MARKER_COLOR in self.metadatas.fields

    def get_argb_color(self):
        """Return the markers color, or None if it has not been set"""
        if self.is_colored:
            return self.metadatas[self.GES_META_MARKER_COLOR]
        return None

    OTIO_COLOR_TO_ARGB = {
        otio.schema.MarkerColor.RED: 0xffff0000,
        otio.schema.MarkerColor.PINK: 0xffff7070,
        otio.schema.MarkerColor.ORANGE: 0xffffa000,
        otio.schema.MarkerColor.YELLOW: 0xffffff00,
        otio.schema.MarkerColor.GREEN: 0xff00ff00,
        otio.schema.MarkerColor.CYAN: 0xff00ffff,
        otio.schema.MarkerColor.BLUE: 0xff0000ff,
        otio.schema.MarkerColor.PURPLE: 0xffa000d0,
        otio.schema.MarkerColor.MAGENTA: 0xffff00ff,
        otio.schema.MarkerColor.WHITE: 0xffffffff,
        otio.schema.MarkerColor.BLACK: 0xff000000
    }

    def set_color_from_otio_color(self, otio_color):
        """
        Set the color of the marker using to an otio color, by mapping it
        to a corresponding argb color.
        """
        if otio_color not in self.OTIO_COLOR_TO_ARGB:
            raise InvalidValueError(
                "otio_color", otio_color, "an otio.schema.MarkerColor")
        self.set_color_from_argb(self.OTIO_COLOR_TO_ARGB[otio_color])

    @staticmethod
    def _otio_color_from_hue(hue):
        """Return an otio color, based on hue in [0.0, 1.0]"""
        if hue <= 0.04 or hue > 0.93:
            return otio.schema.MarkerColor.RED
        if hue <= 0.13:
            return otio.schema.MarkerColor.ORANGE
        if hue <= 0.2:
            return otio.schema.MarkerColor.YELLOW
        if hue <= 0.43:
            return otio.schema.MarkerColor.GREEN
        if hue <= 0.52:
            return otio.schema.MarkerColor.CYAN
        if hue <= 0.74:
            return otio.schema.MarkerColor.BLUE
        if hue <= 0.82:
            return otio.schema.MarkerColor.PURPLE
        return otio.schema.MarkerColor.MAGENTA

    def get_nearest_otio_color(self):
        """
        Return an otio.schema.MarkerColor based on the markers argb color,
        or None if it has not been set.
        For colors close to the otio color set, this should return the
        expected color name.
        For edge cases, the 'correct' color is more apparently subjective.
        This method does not work well for colors that are fairly gray
        (low saturation values in HLS). For really gray colours, WHITE or
        BLACK will be returned depending on the lightness.
        The transparency of a color is ignored.
        """
        argb = self.get_argb_color()
        if argb is None:
            return None
        nearest = None
        red = float((argb & 0xff0000) >> 16) / 255.0
        green = float((argb & 0x00ff00) >> 8) / 255.0
        blue = float(argb & 0x0000ff) / 255.0
        hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
        if saturation < 0.2:
            if lightness > 0.65:
                nearest = otio.schema.MarkerColor.WHITE
            else:
                nearest = otio.schema.MarkerColor.BLACK
        if nearest is None:
            if lightness < 0.13:
                nearest = otio.schema.MarkerColor.BLACK
            if lightness > 0.9:
                nearest = otio.schema.MarkerColor.WHITE
        if nearest is None:
            nearest = self._otio_color_from_hue(hue)
            if nearest == otio.schema.MarkerColor.RED \
                    and lightness > 0.53:
                nearest = otio.schema.MarkerColor.PINK
            if nearest == otio.schema.MarkerColor.MAGENTA \
                    and hue < 0.89 and lightness < 0.42:
                # some darker magentas look more like purple
                nearest = otio.schema.MarkerColor.PURPLE
        return nearest

    def __repr__(self):
        return "GESMarker({!r}, {!r})".format(
            self.position, self.metadatas)


@otio.core.register_type
class GESMarkerList(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema that is a list of GESMarkers, ordered by
    their positions, essentially mimicking the GstMarkerList of the GES
    C libarary.
    """
    _serializable_label = "GESMarkerList.1"

    markers = otio.core.serializable_field(
        "markers", list, "A list of GESMarkers")

    def __init__(self, *markers):
        """
        Note, this instance will need to take ownership of any given
        GESMarker.
        """
        otio.core.SerializableObject.__init__(self)
        self.markers = []
        for marker in markers:
            self.add(marker)

    def add(self, marker):
        """
        Add the GESMarker to the GESMarkerList such that the markers
        list remains ordered by marker position (smallest first).
        """
        if not isinstance(marker, GESMarker):
            _wrong_type_for_arg(marker, "GESMarker", "marker")
        for index, existing_marker in enumerate(self.markers):
            if existing_marker.position > marker.position:
                self.markers.insert(index, marker)
                return
        self.markers.append(marker)

    def markers_at_position(self, position):
        """Return a list of markers with the given position"""
        if not isinstance(position, int):
            _wrong_type_for_arg(position, "int", "position")
        return [mrk for mrk in self.markers if mrk.position == position]

    def __getitem__(self, index):
        return self.markers[index]

    def __len__(self):
        return len(self.markers)

    def __repr__(self):
        write = ["GESMarkerList("]
        first = True
        for marker in self.markers:
            if first:
                first = False
            else:
                write.append(", ")
            write.append(repr(marker))
        write.append(")")
        return "".join(write)


@otio.core.register_type
class XgesTrack(otio.core.SerializableObject):
    """
    An OpenTimelineIO Schema for storing a GESTrack.

    Not to be confused with OpenTimelineIO's schema.Track.
    """
    _serializable_label = "XgesTrack.1"

    caps = otio.core.serializable_field(
        "caps", GstCaps, "The GstCaps of the track")
    track_type = otio.core.serializable_field(
        "track-type", int, "The GESTrackType of the track")
    properties = otio.core.serializable_field(
        "properties", GstStructure, "The GObject properties of the track")
    metadatas = otio.core.serializable_field(
        "metadatas", GstStructure, "Metadata for the track")

    def __init__(
            self, caps=None, track_type=GESTrackType.UNKNOWN,
            properties=None, metadatas=None):
        """
        Initialize the XgesTrack.

        properties and metadatas are passed as the second argument to
        GstStructure.
        """
        otio.core.SerializableObject.__init__(self)
        if caps is None:
            caps = GstCaps()
        if not isinstance(caps, GstCaps):
            _wrong_type_for_arg(caps, "GstCaps", "caps")
        if not isinstance(track_type, int):
            _wrong_type_for_arg(track_type, "int", "track_type")
        if track_type not in GESTrackType.ALL_TYPES:
            raise InvalidValueError(
                "track_type", track_type, "a GESTrackType")
        if properties is None:
            properties = GstStructure("properties")
        if metadatas is None:
            metadatas = GstStructure("metadatas")
        if not isinstance(properties, GstStructure):
            _wrong_type_for_arg(properties, "GstStructure", "properties")
        if not isinstance(metadatas, GstStructure):
            _wrong_type_for_arg(metadatas, "GstStructure", "metadatas")
        _force_gst_structure_name(properties, "properties", "XGESTrack")
        _force_gst_structure_name(metadatas, "metadatas", "XGESTrack")
        self.caps = caps
        self.track_type = track_type
        self.properties = properties
        self.metadatas = metadatas

    def __repr__(self):
        return \
            "XgesTrack(caps={!r}, track_type={!r}, "\
            "properties={!r}, metadatas={!r})".format(
                self.caps, self.track_type,
                self.properties, self.metadatas)

    @classmethod
    def new_from_otio_track_kind(cls, kind):
        """Return a new default XgesTrack for the given track kind"""
        return cls.new_from_track_type(GESTrackType.from_otio_kind(kind))

    @classmethod
    def new_from_track_type(cls, track_type):
        """Return a new default XgesTrack for the given track type"""
        props = {}
        if track_type == GESTrackType.VIDEO:
            caps = GstCaps.new_from_str("video/x-raw(ANY)")
            # TODO: remove restriction-caps property once the GES
            # library supports default, non-NULL restriction-caps for
            # GESVideoTrack (like GESAudioTrack).
            # For time being, framerate is needed for stability.
            props["restriction-caps"] = \
                ("string", "video/x-raw, framerate=(fraction)30/1")
        elif track_type == GESTrackType.AUDIO:
            caps = GstCaps.new_from_str("audio/x-raw(ANY)")
        else:
            raise UnhandledValueError("track_type", track_type)
        props["mixing"] = ("boolean", True)
        return cls(caps, track_type, GstStructure("properties", props))
