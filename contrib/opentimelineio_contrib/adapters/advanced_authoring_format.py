# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OpenTimelineIO Advanced Authoring Format (AAF) Adapter

Depending on if/where PyAAF is installed, you may need to set this env var:
    OTIO_AAF_PYTHON_LIB - should point at the PyAAF module.
"""
import colorsys
import copy
import numbers
import os
import sys

import collections
import fractions
import opentimelineio as otio

lib_path = os.environ.get("OTIO_AAF_PYTHON_LIB")
if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

import aaf2  # noqa: E402
import aaf2.content  # noqa: E402
import aaf2.mobs  # noqa: E402
import aaf2.components  # noqa: E402
import aaf2.core  # noqa: E402
import aaf2.misc  # noqa: E402
from opentimelineio_contrib.adapters.aaf_adapter import aaf_writer  # noqa: E402


debug = False

# If enabled, output recursive traversal info of _transcribe() method.
_TRANSCRIBE_DEBUG = False

# bake keyframed parameter
_BAKE_KEYFRAMED_PROPERTIES_VALUES = False

_PROPERTY_INTERPOLATION_MAP = {
    aaf2.misc.ConstantInterp: "Constant",
    aaf2.misc.LinearInterp: "Linear",
    aaf2.misc.BezierInterpolator: "Bezier",
    aaf2.misc.CubicInterpolator: "Cubic",
}


def _transcribe_log(s, indent=0, always_print=False):
    if always_print or _TRANSCRIBE_DEBUG:
        print("{}{}".format(" " * indent, s))


class AAFAdapterError(otio.exceptions.OTIOError):
    """ Raised for AAF adatper-specific errors. """


def _get_parameter(item, parameter_name):
    values = {value.name: value for value in item.parameters.value}
    return values.get(parameter_name)


def _encoded_name(item):

    name = _get_name(item)
    return name.encode("utf-8", "replace")


def _get_name(item):
    if isinstance(item, aaf2.components.SourceClip):
        try:
            return item.mob.name or "Untitled SourceClip"
        except AttributeError:
            # Some AAFs produce this error:
            # RuntimeError: failed with [-2146303738]: mob not found
            return "SourceClip Missing Mob"
    if hasattr(item, 'name'):
        name = item.name
        if name:
            return name
    return _get_class_name(item)


def _get_class_name(item):
    if hasattr(item, "class_name"):
        return item.class_name
    else:
        return item.__class__.__name__


def _transcribe_property(prop, owner=None):
    # XXX: The unicode type doesn't exist in Python 3 (all strings are unicode)
    # so we have to use type(u"") which works in both Python 2 and 3.
    if isinstance(prop, (str, numbers.Integral, float, dict)):
        return prop
    elif isinstance(prop, set):
        return list(prop)
    elif isinstance(prop, list):
        result = {}
        for child in prop:
            if hasattr(child, "name"):
                if isinstance(child, aaf2.misc.VaryingValue):
                    # keyframed values
                    control_points = []
                    for control_point in child["PointList"]:
                        try:
                            # Some values cannot be transcribed yet
                            control_points.append(
                                [
                                    control_point.time,
                                    _transcribe_property(control_point.value),
                                ]
                            )
                        except TypeError:
                            _transcribe_log(
                                "Unable to transcribe value for property: "
                                "'{}' (Type: '{}', Parent: '{}')".format(
                                    child.name, type(child), prop
                                )
                            )

                    # bake keyframe values for owner time range
                    baked_values = None
                    if _BAKE_KEYFRAMED_PROPERTIES_VALUES:
                        if isinstance(owner, aaf2.components.Component):
                            baked_values = []
                            for t in range(0, owner.length):
                                baked_values.append([t, child.value_at(t)])
                        else:
                            _transcribe_log(
                                "Unable to bake values for property: "
                                "'{}'. Owner: {}, Control Points: {}".format(
                                    child.name, owner, control_points
                                )
                            )

                    value_dict = {
                        "_aaf_keyframed_property": True,
                        "keyframe_values": control_points,
                        "keyframe_interpolation": _PROPERTY_INTERPOLATION_MAP.get(
                            child.interpolationdef.auid, "Linear"
                        ),
                        "keyframe_baked_values": baked_values
                    }
                    result[child.name] = value_dict

                elif hasattr(child, "value"):
                    # static value
                    result[child.name] = _transcribe_property(child.value, owner=owner)
            else:
                # @TODO: There may be more properties that we might want also.
                # If you want to see what is being skipped, turn on debug.
                if debug:
                    debug_message = "Skipping unrecognized property: '{}', parent '{}'"
                    _transcribe_log(debug_message.format(child, prop))
        return result
    elif hasattr(prop, "properties"):
        result = {}
        for child in prop.properties():
            result[child.name] = _transcribe_property(child.value, owner=owner)
        return result
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


def _find_timecode_mobs(item):
    mobs = [item.mob]

    for c in item.walk():
        if isinstance(c, aaf2.components.SourceClip):
            mob = c.mob
            if mob:
                mobs.append(mob)
            else:
                continue
        else:
            # This could be 'EssenceGroup', 'Pulldown' or other segment
            # subclasses
            # For example:
            # An EssenceGroup is a Segment that has one or more
            # alternate choices, each of which represent different variations
            # of one actual piece of content.
            # According to the AAF Object Specification and Edit Protocol
            # documents:
            # "Typically the different representations vary in essence format,
            # compression, or frame size. The application is responsible for
            # choosing the appropriate implementation of the essence."
            # It also says they should all have the same length, but
            # there might be nested Sequences inside which we're not attempting
            # to handle here (yet). We'll need a concrete example to ensure
            # we're doing the right thing.
            # TODO: Is the Timecode for an EssenceGroup correct?
            # TODO: Try CountChoices() and ChoiceAt(i)
            # For now, lets just skip it.
            continue

    return mobs


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
        start_set.add(timecode.getvalue('Start'))
        length_set.add(timecode.getvalue('Length'))

    # If all timecode objects are having same start and length we can consider
    # them equivalent.
    if len(start_set) == 1 and len(length_set) == 1:
        return True

    return False


def _extract_timecode_info(mob):
    """Given a mob with a single timecode slot, return the timecode and length
    in that slot as a tuple
    """
    timecodes = [slot.segment for slot in mob.slots
                 if isinstance(slot.segment, aaf2.components.Timecode)]

    # Only use timecode if we have just one or multiple ones with same
    # start/length.
    if timecode_values_are_same(timecodes):
        timecode = timecodes[0]
        timecode_start = timecode.getvalue('Start')
        timecode_length = timecode.getvalue('Length')

        if timecode_start is None or timecode_length is None:
            raise otio.exceptions.NotSupportedError(
                "Unexpected timecode value(s) in mob named: `{}`."
                " `Start`: {}, `Length`: {}".format(mob.name,
                                                    timecode_start,
                                                    timecode_length)
            )

        return timecode_start, timecode_length
    elif len(timecodes) > 1:
        raise otio.exceptions.NotSupportedError(
            "Error: mob has more than one timecode slot with different values."
            " This is currently not supported by the AAF adapter. Found:"
            " {} slots,  mob name is: '{}'".format(len(timecodes), mob.name)
        )
    else:
        return None


def _add_child(parent, child, source):
    if child is None:
        if debug:
            print(f"Adding null child? {source}")
    elif isinstance(child, otio.schema.Marker):
        parent.markers.append(child)
    else:
        parent.append(child)


def _transcribe(item, parents, edit_rate, indent=0):
    result = None
    metadata = {}

    # First lets grab some standard properties that are present on
    # many types of AAF objects...
    metadata["Name"] = _get_name(item)
    metadata["ClassName"] = _get_class_name(item)

    # Some AAF objects (like TimelineMobSlot) have an edit rate
    # which should be used for all of the object's children.
    # We will pass it on to any recursive calls to _transcribe()
    if hasattr(item, "edit_rate"):
        edit_rate = float(item.edit_rate)

    if isinstance(item, aaf2.components.Component):
        metadata["Length"] = item.length

    if isinstance(item, aaf2.core.AAFObject):
        for prop in item.properties():
            if hasattr(prop, 'name') and hasattr(prop, 'value'):
                key = str(prop.name)
                value = prop.value
                metadata[key] = _transcribe_property(value, owner=item)

    # Now we will use the item's class to determine which OTIO type
    # to transcribe into. Note that the order of this if/elif/... chain
    # is important, because the class hierarchy of AAF objects is more
    # complex than OTIO.

    if isinstance(item, aaf2.content.ContentStorage):
        msg = f"Creating SerializableCollection for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        result = otio.schema.SerializableCollection()

        for mob in item.compositionmobs():
            _transcribe_log("compositionmob traversal", indent)
            child = _transcribe(mob, parents + [item], edit_rate, indent + 2)
            _add_child(result, child, mob)

    elif isinstance(item, aaf2.mobs.Mob):
        _transcribe_log(f"Creating Timeline for {_encoded_name(item)}", indent)
        result = otio.schema.Timeline()

        for slot in item.slots:
            track = _transcribe(slot, parents + [item], edit_rate, indent + 2)
            _add_child(result.tracks, track, slot)

            # Use a heuristic to find the starting timecode from
            # this track and use it for the Timeline's global_start_time
            start_time = _find_timecode_track_start(track)
            if start_time:
                result.global_start_time = start_time

    elif isinstance(item, aaf2.components.SourceClip):
        clipUsage = None
        if item.mob is not None:
            clipUsage = item.mob.usage

        if clipUsage:
            itemMsg = "Creating SourceClip for {} ({})".format(
                _encoded_name(item), clipUsage
            )
        else:
            itemMsg = f"Creating SourceClip for {_encoded_name(item)}"

        _transcribe_log(itemMsg, indent)
        result = otio.schema.Clip()

        # store source mob usage to allow OTIO pipelines to adapt downstream
        # example: pipeline code adjusting source_range and name for subclips only
        metadata["SourceMobUsage"] = clipUsage or ""

        # Evidently the last mob is the one with the timecode
        mobs = _find_timecode_mobs(item)

        # Get the Timecode start and length values
        last_mob = mobs[-1] if mobs else None
        timecode_info = _extract_timecode_info(last_mob) if last_mob else None

        source_start = int(metadata.get("StartTime", "0"))
        source_length = item.length
        media_start = source_start
        media_length = item.length

        if timecode_info:
            media_start, media_length = timecode_info
            source_start += media_start

        # The goal here is to find a source range. Actual editorial opinions are
        # found on SourceClips in the CompositionMobs. To figure out whether this
        # clip is directly in the CompositionMob, we detect if our parent mobs
        # are only CompositionMobs. If they were anything else - a MasterMob, a
        # SourceMob, we would know that this is in some indirect relationship.
        parent_mobs = filter(lambda parent: isinstance(parent, aaf2.mobs.Mob), parents)
        is_directly_in_composition = all(
            isinstance(mob, aaf2.mobs.CompositionMob)
            for mob in parent_mobs
        )
        if is_directly_in_composition:
            result.source_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(source_start, edit_rate),
                otio.opentime.RationalTime(source_length, edit_rate)
            )

        # The goal here is to find an available range. Media ranges are stored
        # in the related MasterMob, and there should only be one - hence the name
        # "Master" mob. Somewhere down our chain (either a child or our parents)
        # is a MasterMob.
        # There are some special cases where the masterMob could be:
        # 1) For SourceClips in the CompositionMob, the mob the SourceClip is
        #    referencing can be our MasterMob.
        # 2) If the source clip is referencing another CompositionMob,
        #    drill down to see if the composition holds the MasterMob
        # 3) For everything else, it is a previously encountered parent. Find the
        #    MasterMob in our chain, and then extract the information from that.

        child_mastermob, composition_user_metadata = \
            _find_mastermob_for_sourceclip(item)

        if composition_user_metadata:
            metadata['UserComments'] = composition_user_metadata

        parent_mastermobs = [
            parent for parent in parents
            if isinstance(parent, aaf2.mobs.MasterMob)
        ]
        parent_mastermob = parent_mastermobs[0] if len(parent_mastermobs) > 1 else None

        if child_mastermob:
            _transcribe_log("[found child_mastermob]", indent)
        elif parent_mastermob:
            _transcribe_log("[found parent_mastermob]", indent)
        else:
            _transcribe_log("[found no mastermob]", indent)

        mastermob = child_mastermob or parent_mastermob or None

        if mastermob:
            # Get target path
            mastermob_child = _transcribe(mastermob, list(), edit_rate, indent)

            target_path = (mastermob_child.metadata.get("AAF", {})
                                                   .get("UserComments", {})
                                                   .get("UNC Path"))
            if not target_path:
                # retrieve locator form the MasterMob's Essence
                for mobslot in mastermob.slots:
                    if isinstance(mobslot.segment, aaf2.components.SourceClip):
                        sourcemob = mobslot.segment.mob
                        locator = None
                        # different essences store locators in different places
                        if (isinstance(sourcemob.descriptor,
                                       aaf2.essence.DigitalImageDescriptor)
                                and sourcemob.descriptor.locator):
                            locator = sourcemob.descriptor.locator[0]
                        elif "Locator" in sourcemob.descriptor:
                            locator = sourcemob.descriptor["Locator"].value[0]

                        if locator:
                            target_path = locator["URLString"].value

            # if we have target path, create an ExternalReference, otherwise
            # create an MissingReference.
            if target_path:
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
            clip_metadata = copy.deepcopy(mastermob_child.metadata.get("AAF", {}))

            # If the composition was holding UserComments and the current masterMob has
            # no UserComments, use the ones from the CompositionMob. But if the
            # masterMob has any, prefer them over the compositionMob, since the
            # masterMob is the ultimate authority for a source clip.
            if composition_user_metadata:
                if "UserComments" not in clip_metadata:
                    clip_metadata['UserComments'] = composition_user_metadata

            media.metadata["AAF"] = clip_metadata

            result.media_reference = media

    elif isinstance(item, aaf2.components.Transition):
        _transcribe_log("Creating Transition for {}".format(
            _encoded_name(item)), indent)
        result = otio.schema.Transition()

        # Does AAF support anything else?
        result.transition_type = otio.schema.TransitionTypes.SMPTE_Dissolve

        # Extract value and time attributes of both ControlPoints used for
        # creating AAF Transition objects
        varying_value = None
        for param in item.getvalue('OperationGroup').parameters:
            if isinstance(param, aaf2.misc.VaryingValue):
                varying_value = param
                break

        if varying_value is not None:
            for control_point in varying_value.getvalue('PointList'):
                value = control_point.value
                time = control_point.time
                metadata.setdefault('PointList', []).append({'Value': value,
                                                             'Time': time})

        in_offset = int(metadata.get("CutPoint", "0"))
        out_offset = item.length - in_offset
        result.in_offset = otio.opentime.RationalTime(in_offset, edit_rate)
        result.out_offset = otio.opentime.RationalTime(out_offset, edit_rate)

    elif isinstance(item, aaf2.components.Filler):
        _transcribe_log(f"Creating Gap for {_encoded_name(item)}", indent)
        result = otio.schema.Gap()

        length = item.length
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, edit_rate),
            otio.opentime.RationalTime(length, edit_rate)
        )

    elif isinstance(item, aaf2.components.NestedScope):
        msg = f"Creating Stack for NestedScope for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        # TODO: Is this the right class?
        result = otio.schema.Stack()

        for slot in item.slots:
            child = _transcribe(slot, parents + [item], edit_rate, indent + 2)
            _add_child(result, child, slot)

    elif isinstance(item, aaf2.components.Sequence):
        msg = f"Creating Track for Sequence for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        result = otio.schema.Track()

        # if parent is a sequence add SlotID / PhysicalTrackNumber to attach markers
        parent = parents[-1]
        if isinstance(parent, (aaf2.components.Sequence, aaf2.components.NestedScope)):
            timeline_slots = [
                p for p in parents if isinstance(p, aaf2.mobslots.TimelineMobSlot)
            ]
            timeline_slot = timeline_slots[-1]
            if timeline_slot:
                metadata["PhysicalTrackNumber"] = list(parent.slots).index(item) + 1
                metadata["SlotID"] = int(timeline_slot["SlotID"].value)

        for component in item.components:
            child = _transcribe(component, parents + [item], edit_rate, indent + 2)
            _add_child(result, child, component)

    elif isinstance(item, aaf2.components.OperationGroup):
        msg = f"Creating operationGroup for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        result = _transcribe_operation_group(item, parents, metadata,
                                             edit_rate, indent + 2)

    elif isinstance(item, aaf2.mobslots.TimelineMobSlot):
        msg = f"Creating Track for TimelineMobSlot for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        result = otio.schema.Track()

        child = _transcribe(item.segment, parents + [item], edit_rate, indent + 2)

        _add_child(result, child, item.segment)

    elif isinstance(item, aaf2.mobslots.MobSlot):
        msg = f"Creating Track for MobSlot for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        result = otio.schema.Track()

        child = _transcribe(item.segment, parents + [item], edit_rate, indent + 2)
        _add_child(result, child, item.segment)

    elif isinstance(item, aaf2.components.Timecode):
        pass

    elif isinstance(item, aaf2.components.Pulldown):
        pass

    elif isinstance(item, aaf2.components.EdgeCode):
        pass

    elif isinstance(item, aaf2.components.ScopeReference):
        msg = f"Creating Gap for ScopedReference for {_encoded_name(item)}"
        _transcribe_log(msg, indent)
        # TODO: is this like FILLER?

        result = otio.schema.Gap()

        length = item.length
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, edit_rate),
            otio.opentime.RationalTime(length, edit_rate)
        )

    elif isinstance(item, aaf2.components.DescriptiveMarker):
        event_mobs = [p for p in parents if isinstance(p, aaf2.mobslots.EventMobSlot)]
        if event_mobs:
            _transcribe_log(
                f"Create marker for '{_encoded_name(item)}'", indent
            )

            result = otio.schema.Marker()
            result.name = metadata["Comment"]

            event_mob = event_mobs[-1]

            metadata["AttachedSlotID"] = int(metadata["DescribedSlots"][0])
            metadata["AttachedPhysicalTrackNumber"] = int(
                event_mob["PhysicalTrackNumber"].value
            )

            # determine marker color
            color = _marker_color_from_string(
                metadata.get("CommentMarkerAttributeList", {}).get("_ATN_CRM_COLOR")
            )
            if color is None:
                color = _convert_rgb_to_marker_color(
                    metadata["CommentMarkerColor"]
                )
            result.color = color

            position = metadata["Position"]

            # Length can be None, but the property will always exist
            # so get('Length', 1) wouldn't help.
            length = metadata["Length"]
            if length is None:
                length = 1

            result.marked_range = otio.opentime.TimeRange(
                start_time=otio.opentime.from_frames(position, edit_rate),
                duration=otio.opentime.from_frames(length, edit_rate),
            )
        else:
            _transcribe_log(
                "Cannot attach marker item '{}'. "
                "Missing event mob in hierarchy.".format(
                    _encoded_name(item)
                )
            )

    elif isinstance(item, aaf2.components.Selector):
        msg = f"Transcribe selector for  {_encoded_name(item)}"
        _transcribe_log(msg, indent)

        selected = item.getvalue('Selected')
        alternates = item.getvalue('Alternates', None)

        # First we check to see if the Selected component is either a Filler
        # or ScopeReference object, meaning we have to use the alternate instead
        if isinstance(selected, aaf2.components.Filler) or \
                isinstance(selected, aaf2.components.ScopeReference):

            # Safety check of the alternates list, then transcribe first object -
            # there should only ever be one alternate in this situation
            if alternates is None or len(alternates) != 1:
                err = "AAF Selector parsing error: object has unexpected number of " \
                      "alternates - {}".format(len(alternates))
                raise AAFAdapterError(err)
            result = _transcribe(alternates[0], parents + [item], edit_rate, indent + 2)

            # Filler/ScopeReference means the clip is muted/not enabled
            result.enabled = False

            # Muted tracks are handled in a slightly odd way so we need to do a
            # check here and pass the param back up to the track object
            # if isinstance(parents[-1], aaf2.mobslots.TimelineMobSlot):
            #     pass # TODO: Figure out mechanism for passing this up to parent

        else:

            # This is most likely a multi-cam clip
            result = _transcribe(selected, parents + [item], edit_rate, indent + 2)

            # Perform a check here to make sure no potential Gap objects
            # are slipping through the cracks
            if isinstance(result, otio.schema.Gap):
                err = f"AAF Selector parsing error: {type(item)}"
                raise AAFAdapterError(err)

            # A Selector can have a set of alternates to handle multiple options for an
            # editorial decision - we do a full parse on those obects too
            if alternates is not None:
                alternates = [
                    _transcribe(alt, parents + [item], edit_rate, indent + 2)
                    for alt in alternates
                ]

            metadata['alternates'] = alternates

    # @TODO: There are a bunch of other AAF object types that we will
    # likely need to add support for. I'm leaving this code here to help
    # future efforts to extract the useful information out of these.

    # elif isinstance(item, aaf.storage.File):
    #     self.extendChildItems([item.header])

    # elif isinstance(item, aaf.storage.Header):
    #     self.extendChildItems([item.storage()])
    #     self.extendChildItems([item.dictionary()])

    # elif isinstance(item, aaf.dictionary.Dictionary):
    #     l = []
    #     l.append(DummyItem(list(item.class_defs()), 'ClassDefs'))
    #     l.append(DummyItem(list(item.codec_defs()), 'CodecDefs'))
    #     l.append(DummyItem(list(item.container_defs()), 'ContainerDefs'))
    #     l.append(DummyItem(list(item.data_defs()), 'DataDefs'))
    #     l.append(DummyItem(list(item.interpolation_defs()),
    #        'InterpolationDefs'))
    #     l.append(DummyItem(list(item.klvdata_defs()), 'KLVDataDefs'))
    #     l.append(DummyItem(list(item.operation_defs()), 'OperationDefs'))
    #     l.append(DummyItem(list(item.parameter_defs()), 'ParameterDefs'))
    #     l.append(DummyItem(list(item.plugin_defs()), 'PluginDefs'))
    #     l.append(DummyItem(list(item.taggedvalue_defs()), 'TaggedValueDefs'))
    #     l.append(DummyItem(list(item.type_defs()), 'TypeDefs'))
    #     self.extendChildItems(l)
    #
    #     elif isinstance(item, pyaaf.AxSelector):
    #         self.extendChildItems(list(item.EnumAlternateSegments()))
    #
    #     elif isinstance(item, pyaaf.AxScopeReference):
    #         #print item, item.GetRelativeScope(),item.GetRelativeSlot()
    #         pass
    #
    #     elif isinstance(item, pyaaf.AxEssenceGroup):
    #         segments = []
    #
    #         for i in xrange(item.CountChoices()):
    #             choice = item.GetChoiceAt(i)
    #             segments.append(choice)
    #         self.extendChildItems(segments)
    #
    #     elif isinstance(item, pyaaf.AxProperty):
    #         self.properties['Value'] = str(item.GetValue())

    elif isinstance(item, collections.abc.Iterable):
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
            print(f"SKIPPING: {type(item)}: {item} -- {result}")

    # Did we get anything? If not, we're done
    if result is None:
        return None

    # Okay, now we've turned the AAF thing into an OTIO result
    # There's a bit more we can do before we're ready to return the result.

    # If we didn't get a name yet, use the one we have in metadata
    if not result.name:
        result.name = metadata["Name"]

    # Attach the AAF metadata
    if not result.metadata:
        result.metadata.clear()
    result.metadata["AAF"] = metadata

    # Double check that we got the length we expected
    if isinstance(result, otio.core.Item):
        length = metadata.get("Length")
        if (
                length
                and result.source_range is not None
                and result.source_range.duration.value != length
        ):
            raise AAFAdapterError(
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
            result.metadata["AAF"]["MediaKind"] = media_kind
            if media_kind == "Picture":
                result.kind = otio.schema.TrackKind.Video
            elif media_kind in ("SoundMasterTrack", "Sound"):
                result.kind = otio.schema.TrackKind.Audio
            else:
                # Timecode, Edgecode, others?
                result.kind = ""

    # Done!
    return result


def _find_timecode_track_start(track):
    # See if we can find a starting timecode in here...
    aaf_metadata = track.metadata.get("AAF", {})

    # Is this a Timecode track?
    if aaf_metadata.get("MediaKind") not in {"Timecode", "LegacyTimecode"}:
        return

    # Edit Protocol section 3.6 specifies PhysicalTrackNumber of 1 as the
    # Primary timecode
    try:
        physical_track_number = aaf_metadata["PhysicalTrackNumber"]
    except KeyError:
        raise AAFAdapterError("Timecode missing 'PhysicalTrackNumber'")

    if physical_track_number != 1:
        return

    try:
        edit_rate = fractions.Fraction(aaf_metadata["EditRate"])
        start = aaf_metadata["Segment"]["Start"]
    except KeyError as e:
        raise AAFAdapterError(
            f"Timecode missing '{e}'"
        )

    if edit_rate.denominator == 1:
        rate = edit_rate.numerator
    else:
        rate = float(edit_rate)

    return otio.opentime.RationalTime(
        value=int(start),
        rate=rate,
    )


def _find_mastermob_for_sourceclip(aaf_sourceclip):
    """
    For a given soure clip, find the related masterMob.
    Returns a tuple of (MasterMob, compositionMetadata), where
    MasterMob is an AAF MOB object and compositionMetadata a
    dictionary, extracted from the AAF Tagged Values of UserComments
    (i.e. user metadata)
    """

    # If the mobId of the sourceclip is a mastermob, just return that, we are done.
    if isinstance(aaf_sourceclip.mob, aaf2.mobs.MasterMob):
        return aaf_sourceclip.mob, None

    # There are cases where a composition mob is used as an indirection
    # to the mastermob. In that case the SourceClip points to a
    # CompositionMob instead of a MasterMob. Drill down into the CompositionMob
    # to find the MasterMob related to this SourceClip
    return _get_master_mob_from_source_composition(aaf_sourceclip.mob)


def _get_master_mob_from_source_composition(compositionMob):
    """
    This code covers two special cases:
    if the passed in source-clip-mob is a composition, drill down
    and try to find the master mob in that composition.

    Also, there seems to be a workflow where metadata, specifically UserComments
    are shared between SourceClips via a CompositionMob, in which case there are
    no UserComments on the MasterMob (as we expect in the default case)

    So if we find UserComments on the Composition but not on the MasterMob, we
    return that metadata, so it can be added to the clip (instead of the
    master mob UserComments)

    """

    # If not a composition, we can't discover anything
    if not isinstance(compositionMob, aaf2.mobs.CompositionMob):
        return None, None

    compositionMetadata = _get_composition_user_comments(compositionMob)

    # Iterate over the TimelineMobSlots and extract any source_clips we find.
    source_clips = []
    for slot in compositionMob.slots:
        if isinstance(slot, aaf2.mobslots.TimelineMobSlot):
            if isinstance(slot.segment, aaf2.components.SourceClip):
                source_clips.append(slot.segment)

    # No source clips, no master mob. But we still want to return
    # the composition metadata. If there is another mastermob found 'upstream',
    # but it does not have any UserComments metadata, we still want to use
    # the CompositionMob's metadata.
    if not source_clips:
        return None, compositionMetadata

    # Only expect one source clip for this case.
    # Are there cases where we can have more than one?
    if len(source_clips) > 1:
        print("Found more than one Source Clip ({}) for sourceClipComposition case. "
              "This is unexpected".format(len(source_clips)))

    # We only look at the first source clip right now...
    source_clip = source_clips[0]

    # Not referencing a master mob? Nothing to return
    if not isinstance(source_clip.mob, aaf2.mobs.MasterMob):
        return None, compositionMetadata

    # Found a master mob, return this and also compositionMetadata (if we found any)
    return (source_clip.mob, compositionMetadata)


def _get_composition_user_comments(compositionMob):
    compositionMetadata = {}

    if not isinstance(compositionMob, aaf2.mobs.CompositionMob):
        return compositionMetadata

    compositionMobUserComments = list(compositionMob.get("UserComments", []))
    for prop in compositionMobUserComments:
        key = str(prop.name)
        value = prop.value
        compositionMetadata[key] = _transcribe_property(value)

    return compositionMetadata


def _transcribe_linear_timewarp(item, parameters):
    # this is a linear time warp
    effect = otio.schema.LinearTimeWarp()

    offset_map = _get_parameter(item, 'PARAM_SPEED_OFFSET_MAP_U')

    # If we have a LinearInterp with just 2 control points, then
    # we can compute the time_scalar. Note that the SpeedRatio is
    # NOT correct in many AAFs - we aren't sure why, but luckily we
    # can compute the correct value this way.
    points = offset_map.get("PointList")
    if len(points) > 2:
        # This is something complicated... try the fancy version
        return _transcribe_fancy_timewarp(item, parameters)
    elif (
        len(points) == 2
        and float(points[0].time) == 0
        and float(points[0].value) == 0
    ):
        # With just two points, we can compute the slope
        effect.time_scalar = float(points[1].value) / float(points[1].time)
    else:
        # Fall back to the SpeedRatio if we didn't understand the points
        ratio = parameters.get("SpeedRatio")
        if ratio == str(item.length):
            # If the SpeedRatio == the length, this is a freeze frame
            effect.time_scalar = 0
        elif '/' in ratio:
            numerator, denominator = map(float, ratio.split('/'))
            # OTIO time_scalar is 1/x from AAF's SpeedRatio
            effect.time_scalar = denominator / numerator
        else:
            effect.time_scalar = 1.0 / float(ratio)

    # Is this is a freeze frame?
    if effect.time_scalar == 0:
        # Note: we might end up here if any of the code paths above
        # produced a 0 time_scalar.
        # Use the FreezeFrame class instead of LinearTimeWarp
        effect = otio.schema.FreezeFrame()

    return effect


def _transcribe_fancy_timewarp(item, parameters):

    # For now, this is an unsupported time effect...
    effect = otio.schema.TimeEffect()
    effect.effect_name = ""
    effect.name = item.get("Name", "")

    return effect

    # TODO: Here is some sample code that pulls out the full
    # details of a non-linear speed map.

    # speed_map = item.parameter['PARAM_SPEED_MAP_U']
    # offset_map = item.parameter['PARAM_SPEED_OFFSET_MAP_U']
    # Also? PARAM_OFFSET_MAP_U (without the word "SPEED" in it?)
    # print(speed_map['PointList'].value)
    # print(speed_map.count())
    # print(speed_map.interpolation_def().name)
    #
    # for p in speed_map.points():
    #     print("  ", float(p.time), float(p.value), p.edit_hint)
    #     for prop in p.point_properties():
    #         print("    ", prop.name, prop.value, float(prop.value))
    #
    # print(offset_map.interpolation_def().name)
    # for p in offset_map.points():
    #     edit_hint = p.edit_hint
    #     time = p.time
    #     value = p.value
    #
    #     pass
    #     # print "  ", float(p.time), float(p.value)
    #
    # for i in range(100):
    #     float(offset_map.value_at("%i/100" % i))
    #
    # # Test file PARAM_SPEED_MAP_U is AvidBezierInterpolator
    # # currently no implement for value_at
    # try:
    #     speed_map.value_at(.25)
    # except NotImplementedError:
    #     pass
    # else:
    #     raise


def _transcribe_operation_group(item, parents, metadata, edit_rate, indent):
    result = otio.schema.Stack()

    operation = metadata.get("Operation", {})
    parameters = metadata.get("Parameters", {})
    result.name = operation.get("Name")

    # Trust the length that is specified in the AAF
    length = metadata.get("Length")
    result.source_range = otio.opentime.TimeRange(
        otio.opentime.RationalTime(0, edit_rate),
        otio.opentime.RationalTime(length, edit_rate)
    )

    # Look for speed effects...
    effect = None
    if operation.get("IsTimeWarp"):
        if operation.get("Name") == "Motion Control":

            offset_map = _get_parameter(item, 'PARAM_SPEED_OFFSET_MAP_U')
            # TODO: We should also check the PARAM_OFFSET_MAP_U which has
            # an interpolation_def().name as well.
            if offset_map is not None:
                interpolation = offset_map.interpolation.name
            else:
                interpolation = None

            if interpolation == "LinearInterp":
                effect = _transcribe_linear_timewarp(item, parameters)
            else:
                effect = _transcribe_fancy_timewarp(item, parameters)

        else:
            # Unsupported time effect
            effect = otio.schema.TimeEffect()
            effect.effect_name = ""
            effect.name = operation.get("Name")
    else:
        # Unsupported effect
        effect = otio.schema.Effect()
        effect.effect_name = ""
        effect.name = operation.get("Name")

    if effect is not None:
        result.effects.append(effect)

        effect.metadata.clear()
        effect.metadata.update({
            "AAF": {
                "Operation": operation,
                "Parameters": parameters
            }
        })

    for segment in item.getvalue("InputSegments"):
        child = _transcribe(segment, parents + [item], edit_rate, indent)
        if child:
            _add_child(result, child, segment)

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


def _attach_markers(collection):
    """Search for markers on tracks and attach them to their corresponding item.

    Marked ranges will also be transformed into the new parent space.

    """
    # iterate all timeline objects
    for timeline in collection.each_child(descended_from_type=otio.schema.Timeline):
        tracks_map = {}

        # build track mapping
        for track in timeline.each_child(descended_from_type=otio.schema.Track):
            metadata = track.metadata.get("AAF", {})
            slot_id = metadata.get("SlotID")
            track_number = metadata.get("PhysicalTrackNumber")
            if slot_id is None or track_number is None:
                continue

            tracks_map[(int(slot_id), int(track_number))] = track

        # iterate all tracks for their markers and attach them to the matching item
        for current_track in timeline.each_child(descended_from_type=otio.schema.Track):
            for marker in list(current_track.markers):
                metadata = marker.metadata.get("AAF", {})
                slot_id = metadata.get("AttachedSlotID")
                track_number = metadata.get("AttachedPhysicalTrackNumber")
                target_track = tracks_map.get((slot_id, track_number))
                if target_track is None:
                    raise AAFAdapterError(
                        "Marker '{}' cannot be attached to an item. SlotID: '{}', "
                        "PhysicalTrackNumber: '{}'".format(
                            marker.name, slot_id, track_number
                        )
                    )

                # remove marker from current parent track
                current_track.markers.remove(marker)

                # determine new item to attach the marker to
                try:
                    target_item = target_track.child_at_time(
                        marker.marked_range.start_time
                    )

                    if target_item is None or not hasattr(target_item, 'markers'):
                        # Item found cannot have markers, for example Transition.
                        # See also `marker-over-transition.aaf` in test data.
                        #
                        # Leave markers on the track for now.
                        _transcribe_log(
                            'Skip target_item `{}` cannot have markers'.format(
                                target_item,
                            ),
                        )
                        target_item = target_track

                    # transform marked range into new item range
                    marked_start_local = current_track.transformed_time(
                        marker.marked_range.start_time, target_item
                    )

                    marker.marked_range = otio.opentime.TimeRange(
                        start_time=marked_start_local,
                        duration=marker.marked_range.duration
                    )

                except otio.exceptions.CannotComputeAvailableRangeError as e:
                    # For audio media AAF file (marker-over-audio.aaf),
                    # this exception would be triggered in:
                    # `target_item = target_track.child_at_time()` with error
                    # message:
                    # "No available_range set on media reference on clip".
                    #
                    # Leave markers on the track for now.
                    _transcribe_log(
                        'Cannot compute availableRange from {} to {}: {}'.format(
                            marker,
                            target_track,
                            e,
                        ),
                    )
                    target_item = target_track

                # attach marker to target item
                target_item.markers.append(marker)

                _transcribe_log(
                    "Marker: '{}' (time: {}), attached to item: '{}'".format(
                        marker.name,
                        marker.marked_range.start_time.value,
                        target_item.name,
                    )
                )

    return collection


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


def _get_mobs_for_transcription(storage):
    """
    When we describe our AAF into OTIO space, we apply the following heuristic:

    1) First look for top level mobs and if found use that to transcribe.

    2) If we don't have top level mobs, look for composition mobs and use them to
    transcribe.

    3) Lastly if we don't have either, try to use master mobs to transcribe.

    If we don't find any Mobs, just tell the user and do transcrption on an empty
    list (to generate some 'empty-level' OTIO structure)

    This heuristic is based on 'real-world' examples. There may still be some
    corner cases / open questions (like could there be metadata on both
    a composition mob and master mob? And if so, who would 'win'?)

    In any way, this heuristic satisfies the current set of AAFs we are using
    in our test-environment.

    """

    top_level_mobs = list(storage.toplevel())

    if len(top_level_mobs) > 0:
        _transcribe_log("---\nTranscribing top level mobs\n---")
        return top_level_mobs

    composition_mobs = list(storage.compositionmobs())
    if len(composition_mobs) > 0:
        _transcribe_log("---\nTranscribing composition mobs\n---")
        return composition_mobs

    master_mobs = list(storage.mastermobs())
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
    """Reads AAF content from `filepath` and outputs an OTIO timeline object.

    Args:
        filepath (str): AAF filepath
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
    global _TRANSCRIBE_DEBUG, _BAKE_KEYFRAMED_PROPERTIES_VALUES
    _TRANSCRIBE_DEBUG = transcribe_log
    _BAKE_KEYFRAMED_PROPERTIES_VALUES = bake_keyframed_properties

    with aaf2.open(filepath) as aaf_file:
        # Note: We're skipping: aaf_file.header
        # Is there something valuable in there?

        storage = aaf_file.content
        mobs_to_transcribe = _get_mobs_for_transcription(storage)

        result = _transcribe(mobs_to_transcribe, parents=list(), edit_rate=None)

    # Attach marker to the appropriate clip, gap etc.
    if attach_markers:
        result = _attach_markers(result)

    # AAF is typically more deeply nested than OTIO.
    # Let's try to simplify the structure by collapsing or removing
    # unnecessary stuff.
    if simplify:
        result = _simplify(result)

    # OTIO represents transitions a bit different than AAF, so
    # we need to iterate over them and modify the items on either side.
    # Note that we do this *after* simplifying, since the structure
    # may change during simplification.
    _fix_transitions(result)

    # Reset transcribe_log debugging
    _TRANSCRIBE_DEBUG = False

    return result


def write_to_file(input_otio, filepath, **kwargs):

    with aaf2.open(filepath, "w") as f:

        timeline = aaf_writer._stackify_nested_groups(input_otio)

        aaf_writer.validate_metadata(timeline)

        otio2aaf = aaf_writer.AAFFileTranscriber(timeline, f, **kwargs)

        if not isinstance(timeline, otio.schema.Timeline):
            raise otio.exceptions.NotSupportedError(
                "Currently only supporting top level Timeline")

        for otio_track in timeline.tracks:
            # Ensure track must have clip to get the edit_rate
            if len(otio_track) == 0:
                continue

            transcriber = otio2aaf.track_transcriber(otio_track)

            for otio_child in otio_track:
                result = transcriber.transcribe(otio_child)
                if result:
                    transcriber.sequence.components.append(result)
