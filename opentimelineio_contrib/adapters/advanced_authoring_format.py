#
# Copyright 2017 Pixar Animation Studios
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

"""OpenTimelineIO Advanced Authoring Format (AAF) Adapter

Depending on if/where PyAAF is installed, you may need to set this env var:
    OTIO_AAF_PYTHON_LIB - should point at the PyAAF module.
"""

import os
import sys
import numbers
from collections import Iterable
import opentimelineio as otio

lib_path = os.environ.get("OTIO_AAF_PYTHON_LIB")
if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

import aaf2  # noqa: E731
import aaf2.content  # noqa: E731
import aaf2.mobs  # noqa: E731
import aaf2.components  # noqa: E731
import aaf2.core  # noqa: E731
from aaf2.rational import AAFRational  # noqa: E731
from aaf2.auid import AUID  # noqa: E731
import uuid  # noqa: E731

debug = False
__names = set()


def _get_parameter(item, parameter_name):
    values = dict((value.name, value) for value in item.parameters.value)
    return values.get(parameter_name)


def _get_name(item):
    if isinstance(item, aaf2.components.SourceClip):
        try:
            return item.mob.name or "Untitled SourceClip"
        except RuntimeError:
            # Some AAFs produce this error:
            # RuntimeError: failed with [-2146303738]: mob not found
            return "SourceClip Missing Mob?"
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


def _transcribe_property(prop):
    # XXX: The unicode type doesn't exist in Python 3 (all strings are unicode)
    # so we have to use type(u"") which works in both Python 2 and 3.
    if isinstance(prop, (str, type(u""), numbers.Integral, float)):
        return prop

    elif isinstance(prop, list):
        result = {}
        for child in prop:
            if hasattr(child, "name") and hasattr(child, "value"):
                result[child.name] = _transcribe_property(child.value)
            else:
                # @TODO: There may be more properties that we might want also.
                # If you want to see what is being skipped, turn on debug.
                if debug:
                    debug_message = \
                        "Skipping unrecognized property: {} of parent {}"
                    print(debug_message.format(child, prop))
        return result
    elif hasattr(prop, "properties"):
        result = {}
        for child in prop.properties():
            result[child.name] = _transcribe_property(child.value)
        return result
    else:
        return str(prop)


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
            # See also: https://jira.pixar.com/browse/SE-3457
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


def _extract_timecode_info(mob):
    """Given a mob with a single timecode slot, return the timecode and length
    in that slot as a tuple
    """
    timecodes = [slot.segment for slot in mob.slots
                 if isinstance(slot.segment, aaf2.components.Timecode)]

    if len(timecodes) == 1:
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
            "Error: mob has more than one timecode slots, this is not"
            " currently supported by the AAF adapter. found: {} slots, "
            " mob name is: '{}'".format(len(timecodes), mob.name)
        )
    else:
        return None


def _add_child(parent, child, source):
    if child is None:
        if debug:
            print("Adding null child? {}".format(source))
    elif isinstance(child, otio.schema.Marker):
        parent.markers.append(child)
    else:
        parent.append(child)


def _transcribe(item, parent=None, editRate=24, masterMobs=None):
    result = None
    metadata = {}

    # First lets grab some standard properties that are present on
    # many types of AAF objects...
    metadata["Name"] = _get_name(item)
    metadata["ClassName"] = _get_class_name(item)

    if isinstance(item, aaf2.components.Component):
        metadata["Length"] = item.length

    if isinstance(item, aaf2.core.AAFObject):
        for prop in item.properties():
            if hasattr(prop, 'name') and hasattr(prop, 'value'):
                key = str(prop.name)
                value = prop.value
                metadata[key] = _transcribe_property(value)

    # Now we will use the item's class to determine which OTIO type
    # to transcribe into. Note that the order of this if/elif/... chain
    # is important, because the class hierarchy of AAF objects is more
    # complex than OTIO.

    if isinstance(item, aaf2.content.ContentStorage):
        result = otio.schema.SerializableCollection()

        # Gather all the Master Mobs, so we can find them later by MobID
        # when we parse the SourceClips in the composition
        if masterMobs is None:
            masterMobs = {}
        for mob in item.mastermobs():
            child = _transcribe(mob, parent=item)
            if child is not None:
                mobID = child.metadata.get("AAF", {}).get("MobID")
                masterMobs[mobID] = child

        for mob in item.compositionmobs():
            child = _transcribe(mob, parent=item, masterMobs=masterMobs)
            _add_child(result, child, mob)

    elif isinstance(item, aaf2.mobs.Mob):
        result = otio.schema.Timeline()

        for slot in item.slots:
            child = _transcribe(slot, parent=item, masterMobs=masterMobs)
            _add_child(result.tracks, child, slot)

    elif isinstance(item, aaf2.components.SourceClip):
        result = otio.schema.Clip()

        # Evidently the last mob is the one with the timecode
        mobs = _find_timecode_mobs(item)
        # Get the Timecode start and length values
        timecode_info = _extract_timecode_info(mobs[-1]) if mobs else None

        length = item.length
        startTime = int(metadata.get("StartTime", "0"))
        if timecode_info:
            timecode_start, timecode_length = timecode_info
            startTime += timecode_start

        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(startTime, editRate),
            otio.opentime.RationalTime(length, editRate)
        )

        mobID = metadata.get("SourceID")
        if masterMobs and mobID:
            masterMob = masterMobs.get(mobID)
            if masterMob:
                media = otio.schema.MissingReference()
                if timecode_info:
                    media.available_range = otio.opentime.TimeRange(
                        otio.opentime.RationalTime(timecode_start, editRate),
                        otio.opentime.RationalTime(timecode_length, editRate)
                    )
                # copy the metadata from the master into the media_reference
                media.metadata["AAF"] = masterMob.metadata.get("AAF", {})
                result.media_reference = media

    elif isinstance(item, aaf2.components.Transition):
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
        result.in_offset = otio.opentime.RationalTime(in_offset, editRate)
        result.out_offset = otio.opentime.RationalTime(out_offset, editRate)

    elif isinstance(item, aaf2.components.Filler):
        result = otio.schema.Gap()

        length = item.length
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, editRate),
            otio.opentime.RationalTime(length, editRate)
        )

    elif isinstance(item, aaf2.components.NestedScope):
        # TODO: Is this the right class?
        result = otio.schema.Stack()

        for slot in item.slots:
            child = _transcribe(slot, parent=item, masterMobs=masterMobs)
            _add_child(result, child, slot)

    elif isinstance(item, aaf2.components.Sequence):
        result = otio.schema.Track()

        for component in item.components:
            child = _transcribe(component, parent=item, masterMobs=masterMobs)
            _add_child(result, child, component)

    elif isinstance(item, aaf2.components.OperationGroup):
        result = _transcribe_operation_group(
            item, metadata, editRate, masterMobs
        )

    elif isinstance(item, aaf2.mobslots.TimelineMobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parent=item, masterMobs=masterMobs)
        _add_child(result, child, item.segment)

    elif isinstance(item, aaf2.mobslots.MobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parent=item, masterMobs=masterMobs)
        _add_child(result, child, item.segment)

    elif isinstance(item, aaf2.components.Timecode):
        pass

    elif isinstance(item, aaf2.components.Pulldown):
        pass

    elif isinstance(item, aaf2.components.EdgeCode):
        pass

    elif isinstance(item, aaf2.components.ScopeReference):
        # TODO: is this like FILLER?

        result = otio.schema.Gap()

        length = item.length
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, editRate),
            otio.opentime.RationalTime(length, editRate)
        )

    elif isinstance(item, aaf2.components.DescriptiveMarker):

        # Markers come in on their own separate Track.
        # TODO: We should consolidate them onto the same track(s) as the clips
        # result = otio.schema.Marker()
        pass

    elif isinstance(item, aaf2.components.Selector):
        # If you mute a clip in media composer, it becomes one of these in the
        # AAF.
        result = _transcribe(
            item.getvalue("Selected"),
            parent=item, masterMobs=masterMobs
        )

        alternates = [
            _transcribe(alt, parent=item, masterMobs=masterMobs)
            for alt in item.getvalue("Alternates")
        ]

        # muted case -- if there is only one item its muted, otherwise its
        # a multi cam thing
        if alternates and len(alternates) == 1:
            metadata['muted_clip'] = True
            result.name = str(alternates[0].name) + "_MUTED"

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

    elif isinstance(item, Iterable):
        result = otio.schema.SerializableCollection()
        for child in item:
            result.append(
                _transcribe(
                    child,
                    parent=item,
                    masterMobs=masterMobs
                )
            )
    else:
        # For everything else, we just ignore it.
        # To see what is being ignored, turn on the debug flag
        if debug:
            print("SKIPPING: {}: {} -- {}".format(type(item), item, result))

    # Did we get anything? If not, we're done
    if result is None:
        return None

    # Okay, now we've turned the AAF thing into an OTIO result
    # There's a bit more we can do before we're ready to return the result.

    # If we didn't get a name yet, use the one we have in metadata
    if result.name is None:
        # TODO: Some AAFs contain non-utf8 names?
        # This works in Python 2.7, but not 3.5:
        # result.name = metadata["Name"].encode('utf8', 'replace')
        result.name = str(metadata["Name"])

    # Attach the AAF metadata
    if not result.metadata:
        result.metadata = {}
    result.metadata["AAF"] = metadata

    # Double check that we got the length we expected
    if isinstance(result, otio.core.Item):
        length = metadata.get("Length")
        if (
                length and
                result.source_range is not None and
                result.source_range.duration.value != length
        ):
            raise otio.exceptions.OTIOError(
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
                result.kind = None

    # Done!
    return result


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
        len(points) == 2 and
        float(points[0].time) == 0 and
        float(points[0].value) == 0
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
    effect.effect_name = None  # Unsupported
    effect.name = item.get("Name")

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


def _transcribe_operation_group(item, metadata, editRate, masterMobs):
    result = otio.schema.Stack()

    operation = metadata.get("Operation", {})
    parameters = metadata.get("Parameters", {})
    result.name = operation.get("Name")

    # Trust the length that is specified in the AAF
    length = metadata.get("Length")
    result.source_range = otio.opentime.TimeRange(
        otio.opentime.RationalTime(0, editRate),
        otio.opentime.RationalTime(length, editRate)
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
            effect.effect_name = None  # Unsupported
            effect.name = operation.get("Name")
    else:
        # Unsupported effect
        effect = otio.schema.Effect()
        effect.effect_name = None  # Unsupported
        effect.name = operation.get("Name")

    if effect is not None:
        result.effects.append(effect)
        effect.metadata = {
            "AAF": {
                "Operation": operation,
                "Parameters": parameters
            }
        }

    for segment in item.getvalue("InputSegments"):
        child = _transcribe(segment, parent=item, masterMobs=masterMobs)
        if child:
            _add_child(result, child, segment)

    return result


def _fix_transitions(thing):
    if isinstance(thing, otio.schema.Timeline):
        _fix_transitions(thing.tracks)
    elif (
        isinstance(thing, otio.core.Composition) or
        isinstance(thing, otio.schema.SerializableCollection)
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


def _simplify(thing):
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

                    c = c + num
                c = c - 1

        # skip redundant containers
        if _is_redundant_container(thing):
            # TODO: We may be discarding metadata here, should we merge it?
            result = thing[0].deepcopy()
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
                    result.source_range = result.trimmed_range()
                # modify the duration, but leave the start_time as is
                result.source_range = otio.opentime.TimeRange(
                    result.source_range.start_time,
                    thing.source_range.duration
                )
            return result

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


def read_from_file(filepath, simplify=True):

    f = aaf2.open(filepath)

    storage = f.content

    # Note: We're skipping: f.header
    # Is there something valuable in there?

    __names.clear()
    masterMobs = {}

    result = _transcribe(storage, masterMobs=masterMobs)
    top = storage.toplevel()
    if top:
        # re-transcribe just the top-level mobs
        # but use all the master mobs we found in the 1st pass
        __names.clear()  # reset the names back to 0
        result = _transcribe(top, masterMobs=masterMobs)

    # AAF is typically more deeply nested than OTIO.
    # Lets try to simplify the structure by collapsing or removing
    # unnecessary stuff.
    if simplify:
        result = _simplify(result)

    # OTIO represents transitions a bit different than AAF, so
    # we need to iterate over them and modify the items on either side.
    # Note that we do this *after* simplifying, since the structure
    # may change during simplification.
    _fix_transitions(result)

    return result


#
# Begin terrible writing code
#


unique_mastermobs = {}


def _unique_mastermob(f, clip):
    clip_mob_id = clip.metadata["AAF"]["SourceID"]
    master_mob = unique_mastermobs.get(clip_mob_id)
    if not master_mob:
        # Create MasterMob
        master_mob = f.create.MasterMob()
        master_mob.name = "MasterMob_" + str(clip.name)
        master_mob.mob_id = aaf2.mobid.MobID(clip_mob_id)
        f.content.mobs.append(master_mob)
        unique_mastermobs[clip_mob_id] = master_mob
    return master_mob


unique_tapemobs = {}


def _unique_tapemob(f, clip):
    clip_mob_id = clip.metadata["AAF"]["SourceID"]
    tape_mob = unique_tapemobs.get(clip_mob_id)
    if not tape_mob:
        tape_mob = f.create.SourceMob()
        tape_mob.name = "TapeMob_" + str(clip.name)
        tape_mob.descriptor = f.create.ImportDescriptor()
        edit_rate = clip.duration().rate
        tape_timecode_slot = tape_mob.create_timecode_slot(edit_rate,
                                                           edit_rate)
        timecode_start = clip.media_reference.available_range.start_time.value
        timecode_length = clip.media_reference.available_range.duration.value
        tape_timecode_slot.segment.start = timecode_start
        tape_timecode_slot.segment.length = timecode_length
        f.content.mobs.append(tape_mob)
        unique_tapemobs[clip_mob_id] = tape_mob
    return tape_mob


def _filler(f, clip, media_kind):
    length = clip.metadata.get('AAF').get('Length')
    filler = f.create.Filler(media_kind, length)
    return filler


def _transition(f, clip, media_kind):
    # Create ParameterDef for AvidParameterByteOrder
    avid_param_byteorder_id = uuid.UUID("c0038672-a8cf-11d3-a05b-006094eb75cb")
    byteorder_typedef = f.dictionary.lookup_typedef("aafUInt16")
    param_byteorder = f.create.ParameterDef(avid_param_byteorder_id,
                                            "AvidParameterByteOrder",
                                            "",
                                            byteorder_typedef)
    f.dictionary.register_def(param_byteorder)

    # Create ParameterDef for AvidEffectID
    avid_effect_id = uuid.UUID("93994bd6-a81d-11d3-a05b-006094eb75cb")
    avid_effect_typdef = f.dictionary.lookup_typedef("AvidBagOfBits")
    param_effect_id = f.create.ParameterDef(avid_effect_id,
                                            "AvidEffectID",
                                            "",
                                            avid_effect_typdef)
    f.dictionary.register_def(param_effect_id)

    # Create ParameterDef for AFX_FG_KEY_OPACITY_U
    opacity_param_id = uuid.UUID('8d56813d-847e-11d5-935a-50f857c10000')
    opacity_param_def = f.dictionary.lookup_typedef("Rational")
    opacity_param = f.create.ParameterDef(opacity_param_id,
                                          'AFX_FG_KEY_OPACITY_U',
                                          '',
                                          opacity_param_def)
    f.dictionary.register_def(opacity_param)

    # Create VaryingValue
    opacity_u = f.create.VaryingValue()
    opacity_u.parameterdef = f.dictionary.lookup_parameterdef("AFX_FG_KEY_OPACITY_U")
    vval_extrapolation_id = uuid.UUID('0e24dd54-66cd-4f1a-b0a0-670ac3a7a0b3')
    opacity_u['VVal_Extrapolation'].value = vval_extrapolation_id
    opacity_u['VVal_FieldCount'].value = 1

    interpolation_id = uuid.UUID('5b6c85a4-0ede-11d3-80a9-006008143e6f')
    interpolation_def = f.create.InterpolationDef(interpolation_id,
                                                  'LinearInterp',
                                                  'Linear keyframe interpolation')
    f.dictionary.register_def(interpolation_def)
    opacity_u['Interpolation'].value = f.dictionary.lookup_interperlationdef("LinearInterp")

    pointlist = clip.metadata.get('AAF').get('PointList')

    assert pointlist

    c1 = f.create.ControlPoint()
    c1['EditHint'].value = 'Proportional'
    c1.value = pointlist[0]['Value']
    c1.time = pointlist[0]['Time']

    c2 = f.create.ControlPoint()
    c2['EditHint'].value = 'Proportional'
    c2.value = pointlist[1]['Value']
    c2.time = pointlist[1]['Time']

    opacity_u['PointList'].extend([c1, c2])

    # Create OperationDefinition
    op_group_metadata = clip.metadata.get('AAF').get('OperationGroup')
    effect_id = op_group_metadata.get('Operation').get('Identification')
    is_time_warp = op_group_metadata.get('Operation').get('IsTimeWarp')
    by_pass = op_group_metadata.get('Operation').get('Bypass')
    number_inputs = op_group_metadata.get('Operation').get('NumberInputs')
    operation_category = op_group_metadata.get('Operation').get('OperationCategory')
    data_def_name = op_group_metadata.get('Operation').get('DataDefinition').get('Name')
    data_def = f.dictionary.lookup_datadef(str(data_def_name))
    description = op_group_metadata.get('Operation').get('Description')
    op_def_name = clip.metadata.get('AAF').get('OperationGroup').get('Operation').get('Name')

    op_def = f.create.OperationDef(uuid.UUID(effect_id), op_def_name)
    f.dictionary.register_def(op_def)
    op_def.media_kind = media_kind
    datadef = f.dictionary.lookup_datadef('Picture')
    op_def['IsTimeWarp'].value = is_time_warp
    op_def['Bypass'].value = by_pass
    op_def['NumberInputs'].value = number_inputs
    op_def['OperationCategory'].value = str(operation_category)
    op_def['ParametersDefined'].extend([param_byteorder,
                                        param_effect_id])
    op_def['DataDefinition'].value = data_def
    op_def['Description'].value = str(description)

    # Create OperationGroup
    length = clip.metadata.get('AAF').get('Length')
    operation_group = f.create.OperationGroup(op_def, length)
    operation_group['DataDefinition'].value = datadef
    operation_group['Parameters'].append(opacity_u)

    # Create Transition
    transition = f.create.Transition(media_kind, length)
    transition['OperationGroup'].value = operation_group
    transition['CutPoint'].value = clip.metadata.get('AAF').get('CutPoint')
    transition['DataDefinition'].value = datadef
    return transition


def _tapemob():
    pass


def _mastermob(f, otio_clip, media_kind, filemob, filemob_slot):
    mastermob = _unique_mastermob(f, otio_clip)
    edit_rate = otio_clip.duration().rate
    timecode_length = otio_clip.media_reference.available_range.duration.value
    slot_id = otio_clip.metadata.get("AAF").get("SourceMobSlotID")
    try:
        mastermob_slot = mastermob.slot_at(slot_id)
    except:
        mastermob_slot = mastermob.create_timeline_slot(edit_rate=edit_rate, slot_id=slot_id)
    mastermob_clip = mastermob.create_source_clip(
        slot_id=mastermob_slot.slot_id,
        length=timecode_length,
        media_kind=media_kind)
    mastermob_clip.mob = filemob
    mastermob_clip.slot = filemob_slot
    mastermob_clip.slot_id = filemob_slot.slot_id
    mastermob_slot.segment = mastermob_clip
    return mastermob, mastermob_slot


def _picture_clip(f, otio_clip, media_kind, composition_mob, sequence_slot):
    edit_rate = otio_clip.duration().rate

    tape_mob = _unique_tapemob(f, otio_clip)
    tape_slot = tape_mob.create_empty_slot(edit_rate, media_kind)
    timecode_length = otio_clip.media_reference.available_range.duration.value
    tape_slot.segment.length = timecode_length

    # Create file SourceMob
    filemob = f.create.SourceMob()
    f.content.mobs.append(filemob)
    # TODO: Determine if these values are the correct, and if so,
    # maybe they should be in the AAF metadata
    filemob.descriptor = f.create.CDCIDescriptor()
    filemob.descriptor["ComponentWidth"].value = 8
    filemob.descriptor["HorizontalSubsampling"].value = 2
    filemob.descriptor["ImageAspectRatio"].value = "16/9"
    filemob.descriptor["StoredWidth"].value = 1920
    filemob.descriptor["StoredHeight"].value = 1080
    filemob.descriptor["FrameLayout"].value = "FullFrame"
    filemob.descriptor["VideoLineMap"].value = [42, 0]
    filemob.descriptor["SampleRate"].value = 24
    filemob.descriptor["Length"].value = 1
    filemob_slot = filemob.create_timeline_slot(edit_rate)
    filemob_clip = filemob.create_source_clip(
        slot_id=filemob_slot.slot_id,
        length=tape_slot.segment.length,
        media_kind=tape_slot.segment.media_kind)
    filemob_clip.mob = tape_mob
    filemob_clip.slot = tape_slot
    filemob_clip.slot_id = tape_slot.slot_id
    filemob_slot.segment = filemob_clip

    # Create MasterMob
    mastermob, mastermob_slot = _mastermob(f, otio_clip, media_kind, filemob, filemob_slot)

    # Create CompositionMob SourceClip
    # NOTE: It appears the correct length of the clip comes from
    # the AAF metadata. It should come from the clip's length
    # attribute i.e. clip.duration().value
    length = otio_clip.metadata.get('AAF').get('Length')

    compmob_clip = composition_mob.create_source_clip(
        slot_id=sequence_slot.slot_id,
        length=length,
        media_kind=mastermob_slot.segment.media_kind)
    compmob_clip.mob = mastermob
    compmob_clip.slot = mastermob_slot
    compmob_clip.slot_id = mastermob_slot.slot_id
    return compmob_clip


def _sound_clip(f, otio_clip, media_kind, composition_mob, timeline_mobslot, opgroup):
    edit_rate = otio_clip.duration().rate
    length = otio_clip.duration().value

    # Parameter Definition
    param_id = AUID("e4962322-2267-11d3-8a4c-0050040ef7d2")
    typedef = f.dictionary.lookup_typedef("Rational")
    param_def = f.create.ParameterDef(param_id,
                                      "Pan",
                                      "Pan",
                                      typedef)
    f.dictionary.register_def(param_def)
    interp_def = f.create.InterpolationDef(aaf2.misc.LinearInterp,
                                           "LinearInterp",
                                           "LinearInterp")
    f.dictionary.register_def(interp_def)
    # PointList
    c1 = f.create.ControlPoint()
    c1["ControlPointSource"].value = 2
    c1["Time"].value = AAFRational("0/{}".format(length))
    c1["Value"].value = 0
    c2 = f.create.ControlPoint()
    c2["ControlPointSource"].value = 2
    c2["Time"].value = AAFRational("{}/{}".format(length - 1, length))
    c2["Value"].value = 0
    varying_value = f.create.VaryingValue()
    varying_value.parameterdef = param_def
    varying_value["Interpolation"].value = interp_def
    varying_value["PointList"].extend([c1, c2])
    opgroup.parameters.append(varying_value)

    # Create the tape mob
    tape_mob = _unique_tapemob(f, otio_clip)
    tape_slot = tape_mob.create_empty_slot(edit_rate=edit_rate,
                                           media_kind=media_kind)
    timecode_length = otio_clip.media_reference.available_range.duration.value
    tape_slot.segment.length = timecode_length

    # Create the file source mob
    filemob = f.create.SourceMob()
    f.content.mobs.append(filemob)
    descriptor = f.create.PCMDescriptor()
    descriptor["AverageBPS"].value = 96000
    descriptor["BlockAlign"].value = 2
    descriptor["QuantizationBits"].value = 16
    descriptor["AudioSamplingRate"].value = 48000
    descriptor["Channels"].value = 1
    descriptor["SampleRate"].value = 48000
    descriptor["Length"].value = timecode_length # XXX
    filemob.descriptor = descriptor
    filemob_slot = filemob.create_timeline_slot(edit_rate)
    filemob_clip = filemob.create_source_clip(
        slot_id=filemob_slot.slot_id,
        length=tape_slot.segment.length,
        media_kind=tape_slot.segment.media_kind)
    filemob_clip.mob = tape_mob
    filemob_clip.slot = tape_slot
    filemob_clip.slot_id = tape_slot.slot_id
    filemob_slot.segment = filemob_clip

    # Create MasterMob
    mastermob, mastermob_slot = _mastermob(f, otio_clip, media_kind, filemob, filemob_slot)

    compmob_clip = composition_mob.create_source_clip(
        slot_id=timeline_mobslot.slot_id,
        length=length,
        media_kind=mastermob_slot.segment.media_kind)
    compmob_clip.mob = mastermob
    compmob_clip.slot = mastermob_slot
    compmob_clip.slot_id = mastermob_slot.slot_id
    return compmob_clip

def write_to_file(input_otio, filepath, **kwargs):
    with aaf2.open(filepath, "w") as f:

        audio_track_num = 1
        composition_mob = f.create.CompositionMob()
        composition_mob.name = input_otio.name
        composition_mob.usage = 'Usage_TopLevel'
        f.content.mobs.append(composition_mob)

        for track in input_otio.tracks:
            if track.kind == "Video":
                media_kind = "picture"
                sequence = f.create.Sequence(media_kind=media_kind)
                edit_rate = next(track.each_clip()).duration().rate
                total_length = sum([t.duration().value for t in track])
                sequence_slot = composition_mob.create_timeline_slot(edit_rate=edit_rate)
                sequence_slot.segment = sequence

                for clip in track:
                    print "[%s] - %s (%s) " % (media_kind, clip.name, type(clip))
                    if isinstance(clip, otio.schema.Gap):
                        filler = _filler(f, clip, media_kind)
                        sequence.components.append(filler)
                        continue
                    elif isinstance(clip, otio.schema.Transition):
                        if media_kind != 'picture':
                            print("Only video transitions are currently supported")
                            continue
                        transition = _transition(f, clip, media_kind)
                        sequence.components.append(transition)
                        continue
                    elif isinstance(clip, otio.schema.Clip):
                        assert media_kind == "picture"
                        compmob_clip = _picture_clip(f, clip, media_kind, composition_mob, sequence_slot)
                        sequence.components.append(compmob_clip)

            elif track.kind == "Audio":

                media_kind = "sound"
                # TimelineMobSlot
                timeline_mobslot = composition_mob.create_sound_slot(edit_rate=edit_rate)
                # OperationDefinition
                opdef_auid = AUID("9d2ea893-0968-11d3-8a38-0050040ef7d2")
                opdef = f.create.OperationDef(opdef_auid, "Audio Pan")
                opdef.media_kind = media_kind
                opdef["NumberInputs"].value = 1
                f.dictionary.register_def(opdef)
                # OperationGroup
                opgroup = f.create.OperationGroup(opdef)
                opgroup.media_kind = media_kind
                opgroup.length = total_length
                timeline_mobslot.segment = opgroup
                # Sequence
                sequence = f.create.Sequence(media_kind=media_kind)
                sequence.length = total_length
                opgroup.segments.append(sequence)

                assert isinstance(timeline_mobslot, aaf2.mobslots.TimelineMobSlot)
                assert isinstance(timeline_mobslot.segment, aaf2.components.OperationGroup)
                assert hasattr(timeline_mobslot.segment.segments, "__iter__")
                assert isinstance(timeline_mobslot.segment.segments[0], aaf2.components.Sequence)

                for child in track:
                    print "[%s] - %s (%s) " % (media_kind, clip.name, type(clip))

                    if isinstance(child, otio.schema.Gap):
                        filler = _filler(f, child, media_kind)
                        sequence.components.append(filler)
                        continue
                    elif not isinstance(child, otio.schema.Clip):
                        # Skip everything else for now
                        print "Skipping in audio...", type(child)
                        continue
                    else:

                        assert isinstance(child, otio.schema.Clip)

                        compmob_clip = _sound_clip(f, child, media_kind, composition_mob, timeline_mobslot, opgroup)   
                        sequence.components.append(compmob_clip)

                audio_track_num = audio_track_num + 1
