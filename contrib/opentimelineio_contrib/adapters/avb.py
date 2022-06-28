# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OpenTimelineIO Avid Bin (AVB) Adapter

Depending on if/where pyavb is installed, you may need to set this env var:
    OTIO_AVB_PYTHON_LIB - should point at the pyavb module.
"""
import colorsys
import copy
import numbers
import os
import sys
from uuid import UUID

try:
    # Python 2
    text_type = unicode
except NameError:
    # Python 3
    text_type = str

try:
    # Python 3.3+
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc
import fractions
import opentimelineio as otio

lib_path = os.environ.get("OTIO_AVB_PYTHON_LIB")
if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

import avb  # noqa: E402
from avb.core import AVBPropertyData  # noqa: E402
try:
    # this module is optional
    from avb._ext import AVBPropertyData as AVBPropertyDataExt  # noqa: E402
except ImportError:
    AVBPropertyDataExt = AVBPropertyData

debug = False

# If enabled, output recursive traversal info of _transcribe() method.
_TRANSCRIBE_DEBUG = False

_INTERPOLATION_MAP = {
    2: 'ConstantInterp',
    3: 'LinearInterp',
    5: 'AvidBezierInterpolator',
    6: 'AvidCubicInterpolator',
}

_PER_POINT_MAP = {
    5: 'PP_IN_TANGENT_POS_U',
    6: 'PP_IN_TANGENT_VAL_U',
    7: 'PP_OUT_TANGENT_POS_U',
    8: 'PP_OUT_TANGENT_VAL_U',
    9: 'PP_TANGENT_MODE_U',
    14: 'PP_BASE_FRAME_U',
}

_PARAM_SPEED_OFFSET_MAP_U_ID = UUID("8d56827d-847e-11d5-935a-50f857c10000")


def _avb_pretty_value(value):
    if isinstance(value, bytearray):
        return "bytearray(%d)" % len(value)
        #  return ''.join(format(x, '02x') for x in value)
    return value


def _avb_dump(obj, space=""):
    if obj is None:
        return

    property_keys = []
    property_data = None
    if isinstance(obj, avb.core.AVBObject):
        print(space, text_type(obj))
        space += "  "
        property_data = obj.property_data
        for pdef in obj.propertydefs:
            key = pdef.name
            if key not in obj.property_data:
                continue
            property_keys.append(key)

    elif isinstance(obj, dict):
        property_keys = list(obj.keys())
        property_keys.sort()
        property_data = obj
    else:
        print(space, obj)
        return

    for key in property_keys:
        value = property_data[key]
        if isinstance(value, (avb.core.AVBObject, dict)):
            print("%s%s:" % (space, key))
            _avb_dump(value, space + " ")
        elif isinstance(value, list):
            print("%s%s:" % (space, key))
            for item in value:
                _avb_dump(item, space + " ")
        else:
            if value is not None:
                print("%s%s:" % (space, key), _avb_pretty_value(value))


def _transcribe_log(s, indent=0, always_print=False):
    if always_print or _TRANSCRIBE_DEBUG:
        print("{}{}".format(" " * indent, s))


class AVBAdapterError(otio.exceptions.OTIOError):
    """ Raised for AVB adapter-specific errors. """


def _get_class_name(item):
    return item.__class__.__name__


def _encoded_name(item):

    name = _get_name(item)
    # TODO: ask why is this being done?
    return name.encode("utf-8", "replace")


def _get_name(item):
    if isinstance(item, avb.components.SourceClip):
        try:
            return item.mob.name or "Untitled SourceClip"
        except AttributeError:
            # Some AVB produce this error:
            # RuntimeError: failed with [-2146303738]: mob not found
            return "SourceClip Missing Mob"
    if hasattr(item, 'name'):
        name = item.name
        if name:
            return name
    return _get_class_name(item)


def _transcribe_property(prop, owner=None):
    # XXX: The unicode type doesn't exist in Python 3 (all strings are unicode)
    # so we have to use type(u"") which works in both Python 2 and 3.

    if prop is None:
        return None

    if isinstance(prop, (AVBPropertyData, AVBPropertyDataExt)):
        result = {}
        for key, value in prop.items():
            # skip None values to save space
            if value is None:
                continue
            result[key] = _transcribe_property(value, prop)
        return result
    elif isinstance(prop, (avb.core.AVBRefList, list, tuple)):
        result = []
        for value in prop:
            result.append(_transcribe_property(value, prop))
        return result
    elif isinstance(prop, avb.core.AVBObject):
        result = _transcribe_property(prop.property_data, prop)
        return result
    elif isinstance(prop, UUID):
        return str(prop)
    elif isinstance(prop, bytearray):
        # skip any binary data for now
        return None
    elif isinstance(prop, (str, type(u""), numbers.Integral, float, dict)):
        return prop
    elif isinstance(prop, set):
        return list(prop)
    else:
        return str(prop)


def _otio_color_from_hue(hue):
    """Return an OTIO marker color, based on hue in range of [0.0, 1.0].

    Args:
        hue (float): marker color hue value

    Returns:
        otio.schema.MarkerColor: converted / estimated marker color

    """
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


def _marker_color_from_string(color):
    """Tries to derive a valid marker color from a string.

    Args:
        color (str): color name (e.g. "Yellow")

    Returns:
        otio.schema.MarkerColor: matching color or `None`
    """
    if not color:
        return

    return getattr(otio.schema.MarkerColor, color.upper(), None)


def _convert_rgb_to_marker_color(rgb_dict):
    """Returns a matching OTIO marker color for a given AAF color string.

    Adapted from `get_nearest_otio_color()` in the `xges.py` adapter.

    Args:
        rgb_dict (dict): marker color as dict,
                         e.g. `"{'red': 41471, 'green': 12134, 'blue': 6564}"`

    Returns:
        otio.schema.MarkerColor: converted / estimated marker color

    """

    float_colors = {
        (1.0, 0.0, 0.0): otio.schema.MarkerColor.RED,
        (0.0, 1.0, 0.0): otio.schema.MarkerColor.GREEN,
        (0.0, 0.0, 1.0): otio.schema.MarkerColor.BLUE,
        (0.0, 0.0, 0.0): otio.schema.MarkerColor.BLACK,
        (1.0, 1.0, 1.0): otio.schema.MarkerColor.WHITE,
    }

    # convert from UInt to float
    red = float(rgb_dict["red"]) / 65535.0
    green = float(rgb_dict["green"]) / 65535.0
    blue = float(rgb_dict["blue"]) / 65535.0
    rgb_float = (red, green, blue)

    # check for exact match
    marker_color = float_colors.get(rgb_float)
    if marker_color:
        return marker_color

    # try to get an approxiate match based on hue
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    nearest = None
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
        nearest = _otio_color_from_hue(hue)
        if nearest == otio.schema.MarkerColor.RED and lightness > 0.53:
            nearest = otio.schema.MarkerColor.PINK
        if (
            nearest == otio.schema.MarkerColor.MAGENTA
            and hue < 0.89
            and lightness < 0.42
        ):
            # some darker magentas look more like purple
            nearest = otio.schema.MarkerColor.PURPLE

    # default to red color
    return nearest or otio.schema.MarkerColor.RED


def iter_source_clips(component):
    if isinstance(component, avb.components.SourceClip):
        yield component

    elif isinstance(component, avb.components.Sequence):
        for c in component.components:
            if isinstance(c, avb.components.SourceClip):
                yield c
    elif isinstance(component, avb.trackgroups.EssenceGroup):
        source_clip = None

        for track in component.tracks:
            for clip in iter_source_clips(track.component):
                source_clip = clip
                break
            if source_clip:
                break

        if source_clip:
            yield source_clip


def _walk_reference_chain(item, time, results):

    if item is None:
        return results

    results.append([time, item])

    if isinstance(item, avb.components.SourceClip):

        mob = item.mob
        track = item.track

        if track:
            results.append([item.start_time + time, mob])
            results.append([item.start_time + time, track])
            # TODO: check for this affects anything
            if hasattr(track, 'start_pos'):
                raise AVBAdapterError("start_pos not handles, sample please")

            # TODO: check if we need to scale time
            if item.edit_rate != track.component.edit_rate:
                pass

            return _walk_reference_chain(track.component,
                                         item.start_time + time, results)

        return results

    elif isinstance(item, avb.components.Sequence):
        comp, start = item.nearest_component_at_time(time)
        end = start + comp.length
        if start <= time < end:
            return _walk_reference_chain(comp, time - start, results)

        msg = "component time out of range: {} <= {} < {}".format(start, time, end)
        _transcribe_log(msg, always_print=True)

    elif isinstance(item, (avb.components.Filler, avb.components.ControlClip)):
        return results

    elif isinstance(item, avb.trackgroups.Selector):
        selected = item.selected

        for i, track in enumerate(item.tracks):
            if i == selected:
                results.append([time, track])
                return _walk_reference_chain(track.component, time, results)

    elif isinstance(item, (avb.trackgroups.EssenceGroup,
                           avb.trackgroups.MotionEffect,
                           avb.trackgroups.TrackEffect,
                           avb.trackgroups.TrackGroup)):

        # TODO: further test this
        # first search for first track that chain terminates with sourceclip
        for track in item.tracks:
            if hasattr(track, 'start_pos'):
                raise AVBAdapterError("start_pos not handles, sample please")

            r = _walk_reference_chain(track.component, time, [])
            if r and isinstance(r[-1][1], avb.components.SourceClip):
                results.append([time, track])
                results.extend(r)
                return results

        # give up and return first track
        for track in item.tracks:
            r = _walk_reference_chain(track.component, time, [])
            if r:
                results.append([time, track])
                results.extend(r)
                return r

        assert False
    else:
        _avb_dump(item)
        assert False

    for v in results:
        print(v)
    assert False


def timecode_values_are_same(timecodes):
    """
    A SourceClip can have multiple timecode objects (for example an auxTC24
    value that got added via the Avid Bin column). As long as they have the
    same start and length values, they can be treated as being the same.
    """
    if len(timecodes) == 1:
        return True

    start_set = set()
    length_set = set()

    for timecode in timecodes:
        start_set.add(timecode.start)
        length_set.add(timecode.length)

    # If all timecode objects are having same start and length we can consider
    # them equivalent.
    if len(start_set) == 1 and len(length_set) == 1:
        return True

    return False


def _extract_timecode_info(source_mob, start_time):

    # TODO: need to find sample with multiple timecode samples
    for track in source_mob.tracks:
        if track.component.media_kind == 'timecode':

            # TODO: check if this is Physical track?
            if track.index != 1:
                continue

            if isinstance(track.component, avb.components.Sequence):
                component = track.component

                # start timecode is the first timecode sample
                timecode, _ = component.nearest_component_at_time(0)
                track_tc = timecode.start

                # source timecode is nearest timecode sample
                tc, tc_offset = component.nearest_component_at_time(start_time)
                source_tc = tc.start + start_time - tc_offset

                return track_tc, source_tc, timecode.fps

            elif isinstance(track.component, avb.components.Timecode):
                timecode = track.component
                track_tc = timecode.start
                source_tc = track_tc + start_time

                return track_tc, source_tc, timecode.fps

    return None, None, None


def _add_child(parent, child, source):
    if child is None:
        if debug:
            print("Adding null child? {}".format(source))
    elif isinstance(child, otio.schema.Marker):
        parent.markers.append(child)
    else:
        parent.append(child)


def _transcribe(item, parents, edit_rate, indent=0):
    result = None
    metadata = {}
    markers = []

    metadata["Name"] = _get_name(item)
    metadata["ClassName"] = _get_class_name(item)

    if hasattr(item, "edit_rate"):
        edit_rate = float(item.edit_rate)

    if isinstance(item, avb.core.AVBObject):
        for key in item.property_data.keys():

            # skip transcribing of main children like properties
            if isinstance(item, avb.trackgroups.TrackGroup):
                if key in ('tracks', ):
                    continue

            if isinstance(item, avb.trackgroups.Track):
                if key in ('component',):
                    continue

            if isinstance(item, avb.components.Sequence):
                if key in ('components', ):
                    continue

            v = _transcribe_property(item.property_data[key], owner=item)

            # skip None values to save space
            if v is None or v == "":
                continue

            metadata[key] = v

    # Markers
    if isinstance(item, avb.components.Component):
        attributes = item.get('attributes', None) or {}
        for marker_item in attributes.get("_TMP_CRM", []):
            marker = _transcribe(marker_item, parents + [item], edit_rate, indent + 2)
            markers.append(marker)

    if isinstance(item, avb.trackgroups.Composition):
        _transcribe_log("Creating Timeline for {}".format(_encoded_name(item)), indent)
        result = otio.schema.Timeline()

        for item_track in item.tracks:
            track = _transcribe(item_track, parents + [item], edit_rate, indent + 2)
            _add_child(result.tracks, track, item_track)

            # Use a heuristic to find the starting timecode from
            # this track and use it for the Timeline's global_start_time
            start_time = _find_timecode_track_start(item_track)
            if start_time:
                result.global_start_time = start_time

    elif isinstance(item, avb.trackgroups.EssenceGroup):
        _transcribe_log("Creating Stack for {}".format(_encoded_name(item)), indent)
        result = otio.schema.Stack()

        # just use the first track
        for item_track in item.tracks:
            track = _transcribe(item_track, parents + [item], edit_rate, indent + 2)
            _add_child(result, track, item_track)
            break

    elif isinstance(item, avb.trackgroups.Track):
        msg = "Creating Track for Track for {}".format(_encoded_name(item))
        _transcribe_log(msg, indent)
        result = otio.schema.Track()

        metadata['media_kind'] = item.component.media_kind

        child = _transcribe(item.component, parents + [item], edit_rate, indent + 2)
        _add_child(result, child, item.component)

    elif isinstance(item, avb.components.Sequence):
        msg = "Creating Track for Sequence for {}".format(_encoded_name(item))
        _transcribe_log(msg, indent)
        result = otio.schema.Track()

        for component in item.components:
            child = _transcribe(component, parents + [item], edit_rate, indent + 2)
            _add_child(result, child, component)

    elif isinstance(item, avb.components.SourceClip):
        clip_usage = None

        if item.mob is not None:
            clip_usage = item.mob.usage

        if clip_usage:
            itemMsg = "Creating SourceClip for {} ({})".format(
                _encoded_name(item), clip_usage
            )
        else:
            itemMsg = "Creating SourceClip for {}".format(_encoded_name(item))

        _transcribe_log(itemMsg, indent)
        result = otio.schema.Clip()

        # store source mob usage to allow OTIO pipelines to adapt downstream
        # example: pipeline code adjusting source_range and name for subclips only
        metadata["SourceMobUsage"] = clip_usage or ""

        # Evidently the last mob is the one with the timecode
        ref_chain = _walk_reference_chain(item, 0, [])
        mobs = [mob for start, mob in ref_chain
                if isinstance(mob, avb.trackgroups.Composition)]

        source_start = item.start_time
        source_length = item.length

        media_start = 0
        media_length = item.length
        media_edit_rate = edit_rate

        source_mob = None
        for start_time, comp in ref_chain:
            if isinstance(comp, avb.trackgroups.Composition) \
               and comp.mob_type == "SourceMob":
                source_mob = comp

            if isinstance(comp, avb.components.SourceClip):
                source_start = start_time
                media_start = comp.start_time
                media_length = comp.length
                media_edit_rate = comp.edit_rate

                if source_mob:
                    track_tc, source_tc, tc_rate = _extract_timecode_info(source_mob,
                                                                          start_time)
                    if track_tc is not None:
                        source_start = source_tc
                        media_start = track_tc
                        media_edit_rate = tc_rate

        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(source_start, media_edit_rate),
            otio.opentime.RationalTime(source_length, media_edit_rate)
        )

        mastermobs = []
        name = None
        for mob in mobs:
            # use the name of the first mob seen with name
            if not name:
                name = mob.name

            if mob.mob_type == "MasterMob":
                mastermobs.append(mob)

        if name:
            metadata["Name"] = name
            result.name = metadata["Name"]

        mastermob = mastermobs[0] if mastermobs else None

        if mastermob:
            _transcribe_log("[found mastermob]", indent)
        else:
            _transcribe_log("[found no mastermob]", indent)

        if mastermob:
            mastermob_child = _transcribe(mastermob, list(), edit_rate, indent)

            target_paths = []
            for mob in mobs:
                path = mob.attributes.get("_USER", {}).get("UNC Path", None)
                if path:
                    target_paths.append(path)

                descriptor = mob.get("descriptor", None)
                if not descriptor:
                    continue

                physical_media = descriptor.get("physical_media", None)
                if not physical_media:
                    continue

                locator = physical_media.get("locator", None)
                if not locator:
                    continue

                for path_type in ['path_utf8', 'path_posix', 'path']:
                    path = locator.get(path_type, None)
                    if path:
                        target_paths.append(path)

            if target_paths:
                metadata['alternative_paths'] = target_paths

            # if we have target path, create an ExternalReference, otherwise
            # create an MissingReference.
            if target_paths:
                target_path = target_paths[0]
                if not target_path.startswith("file://"):
                    target_path = "file://" + target_path
                target_path = target_path.replace("\\", "/")
                media = otio.schema.ExternalReference(target_url=target_path)
            else:
                media = otio.schema.MissingReference()

            media.available_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(media_start, edit_rate),
                otio.opentime.RationalTime(media_length, edit_rate)
            )

            # Copy the metadata from the master into the media_reference
            clip_metadata = copy.deepcopy(mastermob_child.metadata.get("AVB", {}))
            media.metadata["AVB"] = clip_metadata

            result.media_reference = media

    elif isinstance(item, avb.trackgroups.Selector):
        msg = "Transcribe selector for  {}".format(_encoded_name(item))
        _transcribe_log(msg, indent)

        selected = item.selected
        selected_track = None
        alternates = []

        for i, track in enumerate(item.tracks):
            if i == selected:
                selected_track = track
            else:
                alternates.append(track)

        if not selected_track or isinstance(selected_track.component,
                                            avb.components.Filler):
            for track in alternates:
                if not isinstance(track.component, avb.components.Filler):
                    selected_track = track
                    break

            if not selected_track:
                err = "AVB Selector parsing error: object has unexpected number of " \
                      "alternates - {}".format(len(alternates))
                raise AVBAdapterError(err)
            component = track.component
            result = _transcribe(component, parents + [item], edit_rate, indent + 2)

            # Filler/ScopeReference means the clip is muted/not enabled
            result.enabled = False

        else:
            # This is most likely a multi-cam clip
            component = track.component
            result = _transcribe(component, parents + [item], edit_rate, indent + 2)

            # A Selector can have a set of alternates to handle multiple options for an
            # editorial decision - we do a full parse on those objects too
            if alternates:
                alternates = [
                    _transcribe(alt.component, parents + [item], edit_rate, indent + 2)
                    for alt in alternates
                ]

            metadata['alternates'] = alternates

    elif isinstance(item, avb.trackgroups.TransitionEffect):
        msg = "Creating Transition for {}".format(_encoded_name(item))
        _transcribe_log(msg, indent)
        result = otio.schema.Transition()
        result.name = "Transition"
        result.transition_type = otio.schema.TransitionTypes.SMPTE_Dissolve

        in_offset = int(metadata.get("cutpoint", "0"))
        out_offset = item.length - in_offset
        result.in_offset = otio.opentime.RationalTime(in_offset, edit_rate)
        result.out_offset = otio.opentime.RationalTime(out_offset, edit_rate)

    elif isinstance(item, avb.trackgroups.TrackEffect):
        msg = "Creating Effect for {}".format(_encoded_name(item))
        _transcribe_log(msg, indent)
        result = _transcribe_track_effect(item, parents, metadata,
                                          edit_rate, indent + 2)

    elif isinstance(item, avb.trackgroups.MotionEffect):
        msg = "Creating Retime for {}".format(_encoded_name(item))
        _transcribe_log(msg, indent)
        result = _transcribe_motion_effect(item, parents, metadata,
                                           edit_rate, indent + 2)

    elif isinstance(item, (avb.components.Filler, avb.components.Component)):
        # AVB puts zero length Filler at the head of tail of Sequences skip them
        if item.length > 0:
            _transcribe_log("Creating Gap for {}".format(_encoded_name(item)), indent)
            result = otio.schema.Gap()

            length = item.length
            result.source_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, edit_rate),
                otio.opentime.RationalTime(length, edit_rate)
            )

    elif isinstance(item, avb.misc.Marker):
        attributes = item.attributes
        name = attributes.get("_ATN_CRM_COM", "")
        _transcribe_log(
            "Create Marker for '{}'".format(_encoded_name(item)), indent
        )
        result = otio.schema.Marker()
        result.name = name

        # determine marker color
        color = _marker_color_from_string(
            attributes.get("_ATN_CRM_COLOR", None)
        )
        if color is None:
            color = _convert_rgb_to_marker_color(
                item.color
            )

        result.color = color
        length = 1
        position = item.comp_offset

        result.marked_range = otio.opentime.TimeRange(
            start_time=otio.opentime.from_frames(position, edit_rate),
            duration=otio.opentime.from_frames(length, edit_rate),
        )

    elif isinstance(item, collections_abc.Iterable):
        msg = "Creating SerializableCollection for Iterable for {}".format(
            _encoded_name(item))
        _transcribe_log(msg, indent)

        result = otio.schema.SerializableCollection()
        for child in item:
            result.append(_transcribe(child, parents + [item], edit_rate, indent + 2))

    else:
        # For everything else, we just ignore it.
        # To see what is being ignored, turn on the debug flag
        if debug:
            print("SKIPPING: {}: {} -- {}".format(type(item), item, result))

    # Did we get anything? If not, we're done
    if result is None:
        return None

    # Okay, now we've turned the AVB thing into an OTIO result
    # There's a bit more we can do before we're ready to return the result.

    # If we didn't get a name yet, use the one we have in metadata
    if not result.name:
        result.name = metadata["Name"]

    # AVB stores markers with component relative offsets
    # this converts them to media reference relative offsets
    for marker in markers:
        if isinstance(result, otio.core.Item):
            duration = marker.marked_range.duration
            current_start = marker.marked_range.start_time
            source_range = result.source_range
            if source_range:
                offset = source_range.start_time
                marker.marked_range = otio.opentime.TimeRange(
                    start_time=current_start + offset,
                    duration=duration
                )

        result.markers.append(marker)

    # Attach the AVB metadata
    if not result.metadata:
        result.metadata.clear()
    result.metadata["AVB"] = metadata

    # Double check that we got the length we expected
    if isinstance(result, otio.core.Item):
        length = metadata.get("length")
        if (
                length
                and result.source_range is not None
                and result.source_range.duration.value != length
        ):
            raise AVBAdapterError(
                "Wrong duration? {} should be {} in {}".format(
                    result.source_range.duration.value,
                    length,
                    result
                )
            )

    # Did we find a Track?
    if isinstance(result, otio.schema.Track):
        # Try to figure out the kind of Track it is
        if hasattr(item, 'media_kind'):
            media_kind = str(item.media_kind)
            result.metadata["AVB"]["media_kind"] = media_kind
            if media_kind == "picture":
                result.kind = otio.schema.TrackKind.Video
            elif media_kind == 'sound':
                result.kind = otio.schema.TrackKind.Audio
            else:
                # Timecode, Edgecode, others?
                result.kind = ""

    # Done!
    return result


def _find_timecode_track_start(track):
    # Is this a Timecode track?
    if track.component.media_kind != "timecode":
        return

    # Edit Protocol section 3.6 specifies PhysicalTrackNumber of 1 as the
    # Primary timecode
    if track.index != 1:
        return

    if not isinstance(track.component, avb.components.Timecode):
        return

    edit_rate = fractions.Fraction(track.component.fps)
    start = track.component.start

    if edit_rate.denominator == 1:
        rate = edit_rate.numerator
    else:
        rate = float(edit_rate)

    return otio.opentime.RationalTime(
        value=int(start),
        rate=rate,
    )


def _get_composition_user_comments(compositionMob):
    compositionMetadata = {}

    if compositionMob.mob_type != "CompositionMob":
        return compositionMetadata

    compositionMobUserComments = compositionMob.attributes.get("_USER", {})
    for key, value in compositionMobUserComments.items():
        compositionMetadata[key] = _transcribe_property(value)

    return compositionMetadata


def _get_effect_name(item):
    for start, component in _walk_reference_chain(item, 0, []):
        if isinstance(component, avb.trackgroups.Composition):
            name = component.get("name", None)
            if name:
                return name


def _transcribe_motion_effect(item, parents, metadata, edit_rate, indent):
    result = otio.schema.Stack()

    effect_id = item.effect_id
    result.name = _get_effect_name(item) or effect_id
    # Trust the length that is specified in the AVB
    length = item.length
    result.source_range = otio.opentime.TimeRange(
        otio.opentime.RationalTime(0, edit_rate),
        otio.opentime.RationalTime(length, edit_rate)
    )

    effect = None
    offset_map = None
    interpolation = None

    # input_format = item.attributes.get('_MFX_INPUT_FORMAT', None)
    # output_format = item.attributes.get('_MFX_OUTPUT_FORMAT', None)
    ratio = item.get('speed_ratio', None)

    for param in item.param_list:
        if param.uuid == _PARAM_SPEED_OFFSET_MAP_U_ID:
            offset_map = param
            interpolation = _INTERPOLATION_MAP[param.control_track.interp_kind]

    if interpolation == 'LinearInterp':
        points = []
        for p in offset_map.control_track.control_points:
            t = float(p.offset[0]) / float(p.offset[1])
            points.append([t, p.value])

        if len(points) > 2:
            # fancy retime
            effect = otio.schema.TimeEffect()
            effect.effect_name = ""
            effect.name = item.get("Name", "")
        elif (
            len(points) == 2
            and float(points[0][0]) == 0
            and float(points[0][1]) == 0
        ):
            effect = otio.schema.LinearTimeWarp()
            # With just two points, we can compute the slope
            effect.time_scalar = float(points[1][1]) / float(points[1][0])

    if effect is None and ratio and ratio[1] != 0:
        effect = otio.schema.LinearTimeWarp()
        ratio = float(ratio[0]) / float(ratio[1])
        if ratio == item.length:
            # If the SpeedRatio == the length, this is a freeze frame
            effect.time_scalar = 0
        else:
            effect.time_scalar = 1.0 / ratio

    # Is this is a freeze frame?
    if effect and \
       isinstance(effect, otio.schema.LinearTimeWarp) and \
       effect.time_scalar == 0:
        # Note: we might end up here if any of the code paths above
        # produced a 0 time_scalar.
        # Use the FreezeFrame class instead of LinearTimeWarp
        effect = otio.schema.FreezeFrame()

    if effect is None:
        # Unsupported effect
        effect = otio.schema.Effect()
        effect.effect_name = ""
        effect.name = effect_id

    if effect is not None:
        result.effects.append(effect)
        # effect.metadata.update(metadata
        # effect.metadata.clear()
        effect.metadata.update({
            "AVB": metadata
        })

    for track in item.tracks:
        child = _transcribe(track, parents + [item], edit_rate, indent)
        if child:
            _add_child(result, child, track)

    return result


def _transcribe_track_effect(item, parents, metadata, edit_rate, indent):
    result = otio.schema.Stack()
    effect_id = item.effect_id
    result.name = _get_effect_name(item) or effect_id

    # Trust the length that is specified in the AVB
    length = item.length
    result.source_range = otio.opentime.TimeRange(
        otio.opentime.RationalTime(0, edit_rate),
        otio.opentime.RationalTime(length, edit_rate)
    )

    # Unsupported effect
    effect = otio.schema.Effect()
    effect.effect_name = effect_id

    if effect is not None:
        result.effects.append(effect)

        effect.metadata.clear()
        effect.metadata.update({"AVB": metadata})

    for track in item.tracks:
        child = _transcribe(track, parents + [item], edit_rate, indent)
        if child:
            _add_child(result, child, track)

    return result


def _fix_transitions(thing):
    if isinstance(thing, otio.schema.Timeline):
        _fix_transitions(thing.tracks)
    elif (
        isinstance(thing, otio.core.Composition)
        or isinstance(thing, otio.schema.SerializableCollection)
    ):
        if isinstance(thing, otio.schema.Track):
            for c, child in enumerate(thing):

                # Don't touch the Transitions themselves,
                # only the Clips & Gaps next to them.
                if not isinstance(child, otio.core.Item):
                    continue

                # Was the item before us a Transition?
                if c > 0 and isinstance(
                    thing[c - 1],
                    otio.schema.Transition
                ):
                    pre_trans = thing[c - 1]

                    if child.source_range is None:
                        child.source_range = child.trimmed_range()
                    csr = child.source_range
                    child.source_range = otio.opentime.TimeRange(
                        start_time=csr.start_time + pre_trans.in_offset,
                        duration=csr.duration - pre_trans.in_offset
                    )

                    # offset markers
                    for marker in child.markers:
                        msr = marker.marked_range
                        marker.marked_range = otio.opentime.TimeRange(
                            start_time=msr.start_time + pre_trans.in_offset,
                            duration=msr.duration
                        )

                # Is the item after us a Transition?
                if c < len(thing) - 1 and isinstance(
                    thing[c + 1],
                    otio.schema.Transition
                ):
                    post_trans = thing[c + 1]

                    if child.source_range is None:
                        child.source_range = child.trimmed_range()
                    csr = child.source_range
                    child.source_range = otio.opentime.TimeRange(
                        start_time=csr.start_time,
                        duration=csr.duration - post_trans.out_offset
                    )

        for child in thing:
            _fix_transitions(child)


def _simplify(thing):
    # If the passed in is an empty dictionary or None, nothing to do.
    # Without this check it would still return thing, but this way we avoid
    # unnecessary if-chain compares.
    if not thing:
        return thing

    if isinstance(thing, otio.schema.SerializableCollection):
        if len(thing) == 1:
            return _simplify(thing[0])
        else:
            for c, child in enumerate(thing):
                thing[c] = _simplify(child)
            return thing

    elif isinstance(thing, otio.schema.Timeline):
        result = _simplify(thing.tracks)

        # Only replace the Timeline's stack if the simplified result
        # was also a Stack. Otherwise leave it (the contents will have
        # been simplified in place).
        if isinstance(result, otio.schema.Stack):
            thing.tracks = result

        return thing

    elif isinstance(thing, otio.core.Composition):
        # simplify our children
        for c, child in enumerate(thing):
            thing[c] = _simplify(child)

        # remove empty children of Stacks
        if isinstance(thing, otio.schema.Stack):
            for c in reversed(range(len(thing))):
                child = thing[c]
                if not _contains_something_valuable(child):
                    # TODO: We're discarding metadata... should we retain it?
                    del thing[c]

            # Look for Stacks within Stacks
            c = len(thing) - 1
            while c >= 0:
                child = thing[c]
                # Is my child a Stack also? (with no effects)
                if (
                    not _has_effects(child)
                    and
                    (
                        isinstance(child, otio.schema.Stack)
                        or (
                            isinstance(child, otio.schema.Track)
                            and len(child) == 1
                            and isinstance(child[0], otio.schema.Stack)
                            and child[0]
                            and isinstance(child[0][0], otio.schema.Track)
                        )
                    )
                ):
                    if isinstance(child, otio.schema.Track):
                        child = child[0]

                    # Pull the child's children into the parent
                    num = len(child)
                    children_of_child = child[:]
                    # clear out the ownership of 'child'
                    del child[:]
                    thing[c:c + 1] = children_of_child

                    # TODO: We may be discarding metadata, should we merge it?
                    # TODO: Do we need to offset the markers in time?
                    thing.markers.extend(child.markers)
                    # Note: we don't merge effects, because we already made
                    # sure the child had no effects in the if statement above.

                    # Preserve the enabled/disabled state as we merge these two.
                    thing.enabled = thing.enabled and child.enabled

                    c = c + num
                c = c - 1

        # skip redundant containers
        if _is_redundant_container(thing):
            # TODO: We may be discarding metadata here, should we merge it?
            result = thing[0].deepcopy()

            # As we are reducing the complexity of the object structure through
            # this process, we need to make sure that any/all enabled statuses
            # are being respected and applied in an appropriate way
            if not thing.enabled:
                result.enabled = False

            # TODO: Do we need to offset the markers in time?
            result.markers.extend(thing.markers)

            # TODO: The order of the effects is probably important...
            # should they be added to the end or the front?
            # Intuitively it seems like the child's effects should come before
            # the parent's effects. This will need to be solidified when we
            # add more effects support.
            result.effects.extend(thing.effects)
            # Keep the parent's length, if it has one
            if thing.source_range:
                # make sure it has a source_range first
                if not result.source_range:
                    try:
                        result.source_range = result.trimmed_range()
                    except otio.exceptions.CannotComputeAvailableRangeError:
                        result.source_range = copy.copy(thing.source_range)
                # modify the duration, but leave the start_time as is
                result.source_range = otio.opentime.TimeRange(
                    result.source_range.start_time,
                    thing.source_range.duration
                )
            return result

    # if thing is the top level stack, all of its children must be in tracks
    if isinstance(thing, otio.schema.Stack) and thing.parent() is None:
        children_needing_tracks = []
        for child in thing:
            if isinstance(child, otio.schema.Track):
                continue
            children_needing_tracks.append(child)

        for child in children_needing_tracks:
            orig_index = thing.index(child)
            del thing[orig_index]
            new_track = otio.schema.Track()
            new_track.append(child)
            thing.insert(orig_index, new_track)

    return thing


def _has_effects(thing):
    if isinstance(thing, otio.core.Item):
        if len(thing.effects) > 0:
            return True


def _is_redundant_container(thing):

    is_composition = isinstance(thing, otio.core.Composition)
    if not is_composition:
        return False

    has_one_child = len(thing) == 1
    if not has_one_child:
        return False

    am_top_level_track = (
        type(thing) is otio.schema.Track
        and type(thing.parent()) is otio.schema.Stack
        and thing.parent().parent() is None
    )

    return (
        not am_top_level_track
        # am a top level track but my only child is a track
        or (
            type(thing) is otio.schema.Track
            and type(thing[0]) is otio.schema.Track
        )
    )


def _contains_something_valuable(thing):
    if isinstance(thing, otio.core.Item):
        if len(thing.effects) > 0 or len(thing.markers) > 0:
            return True

    if isinstance(thing, otio.core.Composition):

        if len(thing) == 0:
            # NOT valuable because it is empty
            return False

        for child in thing:
            if _contains_something_valuable(child):
                # valuable because this child is valuable
                return True

        # none of the children were valuable, so thing is NOT valuable
        return False

    if isinstance(thing, otio.schema.Gap):
        # TODO: Are there other valuable things we should look for on a Gap?
        return False

    # anything else is presumed to be valuable
    return True


def _get_mobs_for_transcription(content):
    """
    When we describe our AVB into OTIO space, we apply the following heuristic:

    1) First look for top level mobs and if found use that to transcribe.

    2) If we don't have top level mobs, look for composition mobs and use them to
    transcribe.

    3) Lastly if we don't have either, try to use master mobs to transcribe.

    If we don't find any Mobs, just tell the user and do transcription on an empty
    list (to generate some 'empty-level' OTIO structure)

    This heuristic is based on 'real-world' examples. There may still be some
    corner cases / open questions (like could there be metadata on both
    a composition mob and master mob? And if so, who would 'win'?)

    In any way, this heuristic satisfies the current set of AVBs we are using
    in our test-environment.

    """

    top_level_mobs = list(content.toplevel())
    if len(top_level_mobs) > 0:
        _transcribe_log("---\nTranscribing top level mobs\n---")
        return top_level_mobs

    composition_mobs = list(content.compositionmobs())
    if len(composition_mobs) > 0:
        _transcribe_log("---\nTranscribing composition mobs\n---")
        return composition_mobs

    master_mobs = list(content.mastermobs())
    if len(master_mobs) > 0:
        _transcribe_log("---\nTranscribing master mobs\n---")
        return master_mobs

    _transcribe_log("---\nNo mobs found to transcribe\n---")

    return []


def read_from_file(
    filepath,
    simplify=True,
    transcribe_log=False,
    attach_markers=True,
    bake_keyframed_properties=False
):
    """Reads AVB content from `filepath` and outputs an OTIO timeline object.

    Args:
        filepath (str): AVB filepath
        simplify (bool, optional): simplify timeline structure by stripping empty items
        transcribe_log (bool, optional): log activity as items are getting transcribed
        attach_markers (bool, optional): attaches markers to their appropriate items
                                         like clip, gap. etc on the track
        bake_keyframed_properties (bool, optional): bakes animated property values
                                                    for each frame in a source clip
    Returns:
        otio.schema.Timeline

    """
    # 'activate' transcribe logging if adapter argument is provided.
    # Note that a global 'switch' is used in order to avoid
    # passing another argument around in the _transcribe() method.
    #
    global _TRANSCRIBE_DEBUG
    _TRANSCRIBE_DEBUG = transcribe_log

    with avb.open(filepath) as avb_file:
        # TODO: there is additional Bin data that might be useful

        avb_file.content.build_mob_dict()
        mobs_to_transcribe = _get_mobs_for_transcription(avb_file.content)

        result = _transcribe(mobs_to_transcribe, parents=list(), edit_rate=None)

    # AVB is typically more deeply nested than OTIO.
    # Let's try to simplify the structure by collapsing or removing
    # unnecessary stuff.
    if simplify:
        result = _simplify(result)

    # OTIO represents transitions a bit different than AVB, so
    # we need to iterate over them and modify the items on either side.
    # Note that we do this *after* simplifying, since the structure
    # may change during simplification.
    _fix_transitions(result)

    # Reset transcribe_log debugging
    _TRANSCRIBE_DEBUG = False

    return result
