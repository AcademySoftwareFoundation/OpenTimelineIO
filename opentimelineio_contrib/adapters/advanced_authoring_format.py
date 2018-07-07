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
import opentimelineio as otio

lib_path = os.environ.get("OTIO_AAF_PYTHON_LIB")
if lib_path and lib_path not in sys.path:
    sys.path += [lib_path]

import aaf  # noqa (E402 module level import not at top of file)
import aaf.storage  # noqa
import aaf.mob  # noqa
import aaf.define  # noqa
import aaf.component  # noqa
import aaf.base  # noqa

debug = False
__names = set()


def _get_name(item):
    if hasattr(item, 'name'):
        name = item.name
        if name:
            return name
    if isinstance(item, aaf.component.SourceClip):
        try:
            ref = item.resolve_ref()
        except RuntimeError:
            # Some AAFs produce this error:
            # RuntimeError: failed with [-2146303738]: mob not found
            return "SourceClip Missing Mob?"
        return ref.name or "Untitled SourceClip"
    return _get_class_name(item)


def _get_class_name(item):
    if hasattr(item, "class_name"):
        return item.class_name
    else:
        return item.__class__.__name__


def _transcribe_property(prop):
    # XXX: The unicode type doesn't exist in Python 3 (all strings are unicode)
    # so we have to use type(u"") which works in both Python 2 and 3.
    if type(prop) in (str, type(u""), int, float, bool):
        return prop

    elif isinstance(prop, aaf.iterator.PropValueResolveIter):
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
    elif isinstance(prop, aaf.iterator.PropItemIter):
        result = {}
        for child in prop:
            result[child.name] = _transcribe_property(child.value)
        return result
    else:
        return str(prop)


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

    if isinstance(item, aaf.component.Component):
        metadata["Length"] = item.length

    if isinstance(item, aaf.base.AAFObject):
        for prop in item.properties():
            if hasattr(prop, 'name') and hasattr(prop, 'value'):
                key = str(prop.name)
                value = prop.value
                metadata[key] = _transcribe_property(value)

    # Now we will use the item's class to determine which OTIO type
    # to transcribe into. Note that the order of this if/elif/... chain
    # is important, because the class hierarchy of AAF objects is more
    # complex than OTIO.

    if isinstance(item, aaf.storage.ContentStorage):
        result = otio.schema.SerializableCollection()

        # Gather all the Master Mobs, so we can find them later by MobID
        # when we parse the SourceClips in the composition
        if masterMobs is None:
            masterMobs = {}
        for mob in item.master_mobs():
            child = _transcribe(mob, parent=item)
            if child is not None:
                mobID = child.metadata.get("AAF", {}).get("MobID")
                masterMobs[mobID] = child

        for mob in item.composition_mobs():
            child = _transcribe(mob, parent=item, masterMobs=masterMobs)
            _add_child(result, child, mob)

    elif isinstance(item, aaf.mob.Mob):
        result = otio.schema.Timeline()

        for slot in item.slots():
            child = _transcribe(slot, parent=item, masterMobs=masterMobs)
            _add_child(result.tracks, child, slot)

    elif isinstance(item, aaf.component.SourceClip):
        result = otio.schema.Clip()

        # ref = item.resolve_ref()
        # name = ref.name

        length = item.length
        startTime = int(metadata.get("StartTime", "0"))
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(startTime, editRate),
            otio.opentime.RationalTime(length, editRate)
        )

        mobID = metadata.get("SourceID")
        if masterMobs and mobID:
            masterMob = masterMobs.get(mobID)
            if masterMob:
                media = otio.schema.MissingReference()
                # copy the metadata from the master into the media_reference
                media.metadata["AAF"] = masterMob.metadata.get("AAF", {})
                result.media_reference = media

    elif isinstance(item, aaf.component.Transition):
        result = otio.schema.Transition()

        # Does AAF support anything else?
        result.transition_type = otio.schema.TransitionTypes.SMPTE_Dissolve

        in_offset = int(metadata.get("CutPoint", "0"))
        out_offset = item.length - in_offset
        result.in_offset = otio.opentime.RationalTime(in_offset, editRate)
        result.out_offset = otio.opentime.RationalTime(out_offset, editRate)

    elif isinstance(item, aaf.component.Filler):
        result = otio.schema.Gap()

        length = item.length
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, editRate),
            otio.opentime.RationalTime(length, editRate)
        )

    elif isinstance(item, aaf.component.NestedScope):
        # TODO: Is this the right class?
        result = otio.schema.Stack()

        for segment in item.segments():
            child = _transcribe(segment, parent=item, masterMobs=masterMobs)
            _add_child(result, child, segment)

    elif isinstance(item, aaf.component.Sequence):
        result = otio.schema.Track()

        for component in item.components():
            child = _transcribe(component, parent=item, masterMobs=masterMobs)
            _add_child(result, child, component)

    elif isinstance(item, aaf.component.OperationGroup):
        result = _transcribe_operation_group(
            item, metadata, editRate, masterMobs
        )

    elif isinstance(item, aaf.mob.TimelineMobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parent=item, masterMobs=masterMobs)
        _add_child(result, child, item.segment)

    elif isinstance(item, aaf.mob.MobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parent=item, masterMobs=masterMobs)
        _add_child(result, child, item.segment)

    elif isinstance(item, aaf.component.Timecode):
        pass

    elif isinstance(item, aaf.component.Pulldown):
        pass

    elif isinstance(item, aaf.component.EdgeCode):
        pass

    elif isinstance(item, aaf.component.ScopeReference):
        # TODO: is this like FILLER?

        result = otio.schema.Gap()

        length = item.length
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, editRate),
            otio.opentime.RationalTime(length, editRate)
        )

    elif isinstance(item, aaf.component.DescriptiveMarker):

        # Markers come in on their own separate Track.
        # TODO: We should consolidate them onto the same track(s) as the clips
        # result = otio.schema.Marker()
        pass

    elif isinstance(item, aaf.iterator.MobIter):

        result = otio.schema.SerializableCollection()
        for child in item:
            result.append(
                _transcribe(
                    child,
                    parent=item,
                    masterMobs=masterMobs
                )
            )

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

    offset_map = item.parameter.get('PARAM_SPEED_OFFSET_MAP_U')

    # If we have a LinearInterp with just 2 control points, then
    # we can compute the time_scalar. Note that the SpeedRatio is
    # NOT correct in many AAFs - we aren't sure why, but luckily we
    # can compute the correct value this way.
    points = list(offset_map.points())
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

            offset_map = item.parameter.get('PARAM_SPEED_OFFSET_MAP_U')
            # TODO: We should also check the PARAM_OFFSET_MAP_U which has
            # an interpolation_def().name as well.
            if offset_map is not None:
                interpolation = offset_map.interpolation_def().name
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

    for segment in item.input_segments():
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
                    thing[c-1],
                    otio.schema.Transition
                ):
                    pre_trans = thing[c-1]

                    if child.source_range is None:
                        child.source_range = child.trimmed_range()
                    child.source_range.start_time += pre_trans.in_offset
                    child.source_range.duration -= pre_trans.in_offset

                # Is the item after us a Transition?
                if c < len(thing)-1 and isinstance(
                    thing[c+1],
                    otio.schema.Transition
                ):
                    post_trans = thing[c+1]

                    if child.source_range is None:
                        child.source_range = child.trimmed_range()
                    child.source_range.duration -= post_trans.out_offset

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
            c = len(thing)-1
            while c >= 0:
                child = thing[c]
                # Is my child a Stack also?
                if (
                    isinstance(child, otio.schema.Stack) and
                    not _has_effects(child)
                ):
                    # Pull the child's children into the parent
                    num = len(child)
                    thing[c:c+1] = child[:]

                    # TODO: We may be discarding metadata, should we merge it?
                    # TODO: Do we need to offset the markers in time?
                    thing.markers.extend(child.markers)
                    # Note: we don't merge effects, because we already made
                    # sure the child had no effects in the if statement above.

                    c = c+num
                c = c-1

        # skip redundant containers
        if len(thing) == 1:
            # TODO: We may be discarding metadata here, should we merge it?
            result = thing[0].deepcopy()
            # TODO: Do we need to offset the markers in time?
            result.markers.extend(thing.markers)
            # TODO: The order of the effects is probably important...
            # should they be added to the end or the front?
            result.effects.extend(thing.effects)
            # Keep the parent's length, if it has one
            if thing.source_range:
                # make sure it has a source_range first
                if not result.source_range:
                    result.source_range = result.trimmed_range()
                # modify the duration, but leave the start_time as is
                result.source_range.duration = thing.source_range.duration
            return result

    return thing


def _has_effects(thing):
    if isinstance(thing, otio.core.Item):
        if len(thing.effects) > 0:
            return True


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

    f = aaf.open(filepath)

    storage = f.storage

    # Note: We're skipping: f.header
    # Is there something valuable in there?

    __names.clear()
    masterMobs = {}

    result = _transcribe(storage, masterMobs=masterMobs)
    top = storage.toplevel_mobs()
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
