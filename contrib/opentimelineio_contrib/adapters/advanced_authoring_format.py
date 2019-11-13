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
import copy
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
from opentimelineio_contrib.adapters.aaf_adapter import aaf_writer  # noqa: E402


debug = False
__names = set()


class AAFAdapterError(otio.exceptions.OTIOError):
    """ Raised for AAF adatper-specific errors. """


def _get_parameter(item, parameter_name):
    values = dict((value.name, value) for value in item.parameters.value)
    return values.get(parameter_name)


def _get_name(item):
    if isinstance(item, aaf2.components.SourceClip):
        try:
            return item.mob.name or "Untitled SourceClip"
        except AttributeError:
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
    """Given a SourceClip, find all the relevant mobs down the chain to
       extract the needed values and calculate the correct starting
       frame/timecode value
    """
    def _traverse_item_for_mobs(i, edit_unit=None):
        for c in i.walk(edit_unit):
            if isinstance(c, aaf2.components.SourceClip):
                yield c.mob
            elif isinstance(c, aaf2.components.Sequence):
                for d in _traverse_item_for_mobs(c, 0):
                    yield d
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

    mobs = []
    if item.mob is not None:
        mobs.append(item.mob)

    for m in _traverse_item_for_mobs(item):
        if m and m not in mobs:
            mobs.append(m)

    return mobs


def _extract_timecode_info(mob):
    """Given a mob with a single timecode slot, return the timecode and length
    in that slot as a tuple
    """
    def is_timecode_kind(slot):
        return any(
            isinstance(slot.segment, tc_type) for tc_type in
            (aaf2.components.Timecode, aaf2.components.EdgeCode,
             aaf2.components.SourceClip, aaf2.components.Sequence)
        )

    if isinstance(mob, aaf2.mobs.SourceMob) and isinstance(mob.descriptor, aaf2.essence.TapeDescriptor):
        return None

    timecodes = [slot.segment for slot in mob.slots if is_timecode_kind(slot)]

    if len(timecodes) >= 1:
        timecode = timecodes[-1]
        if isinstance(timecode, aaf2.components.SourceClip):
            timecode_start = timecode.getvalue('StartTime')
        elif isinstance(timecode, aaf2.components.Sequence):
            timecode_start = timecode.components[0].getvalue('StartTime')
        else:
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


def _new_extract_timecode_info(mobs, edit_rate):
    """"""

    def _traverse_mob_for_source_clip(mob, mob_id=None):
        """"""

        def _walk_for_source_clip(item, edit_unit=None):
            for thing in item.walk(edit_unit):
                if isinstance(thing, aaf2.components.SourceClip):
                    yield thing
                elif isinstance(thing, aaf2.components.Sequence):
                    for next_thing in _walk_for_source_clip(thing, 0):
                        yield next_thing
                else:
                    continue

        # def _str_rate_to_float(rate):
        #     num, denom = map(float, rate.split('/'))
        #     return num / denom

        def _find_timecode_frame_value(source_mob):
            for slot in source_mob.slots:
                if slot['PhysicalTrackNumber'].value == 1:
                    tc = slot.segment
                    if isinstance(tc, aaf2.components.Sequence):
                        for comp in tc.components:
                            if isinstance(comp, aaf2.components.Timecode):
                                tc = comp
                    if isinstance(tc, aaf2.components.Timecode):
                        return tc.start, slot.edit_rate
            return 0, None

        mob_id_to_return = None
        source_clip_to_return = None
        frame_value = 0
        length_value = 0
        edit_rate_rational = None

        if isinstance(mob, aaf2.mobs.SourceMob):
            if isinstance(mob.descriptor, aaf2.essence.TapeDescriptor) \
                    or isinstance(mob.descriptor, aaf2.essence.ImportDescriptor):
                frame_value, edit_rate_rational = _find_timecode_frame_value(mob)
                mob_id_to_return = mob.mob_id
            elif isinstance(mob.descriptor, aaf2.essence.CDCIDescriptor) \
                    or isinstance(mob.descriptor, aaf2.essence.PCMDescriptor):
                for slot in mob.slots:
                    if isinstance(slot.segment, aaf2.components.SourceClip):
                        if slot.segment.mob_id == mob_id:
                            source_clip_to_return = slot.segment
                            edit_rate_rational = slot.edit_rate
                            mob_id_to_return = mob.mob_id
                    else:
                        for component in slot.segment.components:
                            if isinstance(component, aaf2.components.SourceClip) \
                                    and component.mob_id == mob_id:
                                source_clip_to_return = component
                                edit_rate_rational = slot.edit_rate
                                mob_id_to_return = mob.mob_id
        elif isinstance(mob, aaf2.mobs.MasterMob):
            for slot in mob.slots:
                if isinstance(slot.segment, aaf2.components.SourceClip):
                    if slot.segment.mob_id == mob_id:
                        source_clip_to_return = slot.segment
                        length_value += source_clip_to_return.length
                        edit_rate_rational = slot.edit_rate
                        mob_id_to_return = mob.mob_id
                elif isinstance(slot.segment, aaf2.components.Sequence):
                    for component in slot.segment.components:
                        if isinstance(component, aaf2.components.SourceClip) \
                                and component.mob_id == mob_id:
                            source_clip_to_return = component
                            length_value += source_clip_to_return.length
                            edit_rate_rational = slot.edit_rate
                            mob_id_to_return = mob.mob_id
        elif isinstance(mob, aaf2.mobs.CompositionMob):
            for slot in mob.slots:
                if isinstance(slot.segment, aaf2.components.SourceClip) \
                        and slot.segment.mob_id == mob_id:
                    source_clip_to_return = slot.segment
                    edit_rate_rational = slot.edit_rate
                    mob_id_to_return = mob.mob_id
                elif isinstance(slot.segment, aaf2.components.Sequence):
                    for sc in _walk_for_source_clip(slot.segment, 0):
                        if sc.mob and sc.mob.mob_id == mob_id:
                            source_clip_to_return = sc
                            edit_rate_rational = slot.edit_rate
                            mob_id_to_return = mob.mob_id
                            break

        if source_clip_to_return:
            frame_value = source_clip_to_return.start

        if frame_value == 0:
            pass
        elif edit_rate_rational and edit_rate != edit_rate_rational.__float__():
                frame_value = int(round(frame_value / (edit_rate_rational.__float__() / edit_rate)))
        elif not edit_rate_rational:
            raise AAFAdapterError(
                "Error: a frame value of '{}' has been found for {} "
                "but no edit_rate - this should not happen.".format(frame_value, mob.name)
            )

        return frame_value, length_value, mob_id_to_return

    frame_count = 0
    length = 0
    mob_id = None
    for mob in mobs:
        frame_value, length_value, mob_id = _traverse_mob_for_source_clip(mob, mob_id)
        frame_count += frame_value
        length += length_value

    return frame_count, length


def _add_child(parent, child, source):
    if child is None:
        if debug:
            print("Adding null child? {}".format(source))
    elif isinstance(child, otio.schema.Marker):
        parent.markers.append(child)
    else:
        parent.append(child)


def _transcribe(item, parents, editRate, masterMobs):
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
        editRate = float(item.edit_rate)

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
        # for mob in item.mastermobs():
        #     child = _transcribe(mob, parents + [item], editRate, masterMobs)
        #     if child is not None:
        #         mobID = child.metadata.get("AAF", {}).get("MobID")
        #         masterMobs[mobID] = child

        for mob in item.compositionmobs():
            child = _transcribe(mob, parents + [item], editRate, masterMobs)
            _add_child(result, child, mob)

    elif isinstance(item, aaf2.mobs.Mob):
        result = otio.schema.Timeline()

        for slot in item.slots:
            track = _transcribe(slot, parents + [item], editRate, masterMobs)
            _add_child(result.tracks, track, slot)

            # Use a heuristic to find the starting timecode from
            # this track and use it for the Timeline's global_start_time
            start_time = _find_timecode_track_start(track)
            if start_time:
                result.global_start_time = start_time

    elif isinstance(item, aaf2.components.SourceClip):
        result = otio.schema.Clip()

        def _find_source_clip(item, slot_id=None):
            if isinstance(item, aaf2.components.SourceClip):
                return item
            elif isinstance(item, aaf2.components.OperationGroup):
                # segments = [s for s in item.segments]
                # if len(segments) > 1:
                #     print("More than one segment in OperationGroup: ", segments)
                return _find_source_clip(item.segments[0])
            elif isinstance(item, aaf2.components.Sequence):
                # components = [c for c in item.components]
                # if len(components) > 1:
                #     print("More than one component in Sequence: ", components)
                return _find_source_clip(item.components[0])
            elif isinstance(item, aaf2.mobs.MasterMob) \
                    or isinstance(item, aaf2.mobs.SourceMob) \
                    or isinstance(item, aaf2.mobs.CompositionMob):
                assert slot_id
                slot = [s.segment for s in item.slots if s.slot_id == slot_id]
                return _find_source_clip(slot[0])
            elif isinstance(item, aaf2.components.EssenceGroup):
                pass
            elif isinstance(item, aaf2.components.Filler):
                pass
            else:
                assert False

        def _find_mob_chain(source_clip):
            assert isinstance(source_clip, aaf2.components.SourceClip)
            mob_chain = [source_clip.mob]
            slot_id = source_clip.slot_id
            for mob in mob_chain:
                if hasattr(mob, 'descriptor') \
                        and mob.descriptor.name in ['TapeDescriptor', 'ImportDescriptor']:
                    break
                else:
                    mob_source_clip = _find_source_clip(mob, slot_id)
                    if mob_source_clip and mob_source_clip.mob:
                        slot_id = mob_source_clip.slot_id
                        mob_chain.append(mob_source_clip.mob)
            return mob_chain

        # Get the MasterMob and the SourceMobs down the tree
        # This may also contain CompositionMobs, which will need
        # to be taken in to account when calculating correct start values
        # mobs = _find_timecode_mobs(item)
        mobs = _find_mob_chain(item)

        # Iterate the mobs in reverse to walk from the bottom up the tree and
        # try to find the Timecode start and length values
        mobs.reverse()
        # timecode_info = None
        # for tc_mob in mobs:
        #     timecode_info = _extract_timecode_info(tc_mob)
        #     if timecode_info is not None:
        #         break

        new_timecode_info = None
        new_timecode_info = _new_extract_timecode_info(mobs, editRate)

        source_start = int(metadata.get("StartTime", "0"))
        source_length = item.length
        media_start = source_start
        media_length = item.length

        if new_timecode_info:
            media_start, media_length = new_timecode_info
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
                otio.opentime.RationalTime(source_start, editRate),
                otio.opentime.RationalTime(source_length, editRate)
            )

        # The goal here is to find an available range. Media ranges are stored
        # in the related MasterMob, and there should only be one - hence the name
        # "Master" mob. Somewhere down our chain (either a child or our parents)
        # is a MasterMob. For SourceClips in the CompositionMob, it is our child.
        # For everything else, it is a previously encountered parent. Find the
        # MasterMob in our chain, and then extract the information from that.
        child_mastermob = (
            item.mob if isinstance(item.mob, aaf2.mobs.MasterMob) else None
        )
        parent_mastermobs = [
            parent for parent in parents
            if isinstance(parent, aaf2.mobs.MasterMob)
        ]
        parent_mastermob = parent_mastermobs[0] if len(parent_mastermobs) > 1 else None
        mastermob = child_mastermob or parent_mastermob or None

        # if mastermob:
        #     # get target path
        #     mastermob_child = masterMobs.get(str(mastermob.mob_id))
        #     target_path = (mastermob_child.metadata.get("AAF", {})
        #                                            .get("UserComments", {})
        #                                            .get("UNC Path"))
        #     if not target_path:
        #         # retrieve locator form the MasterMob's Essence
        #         for mobslot in mastermob.slots:
        #             if isinstance(mobslot.segment, aaf2.components.SourceClip):
        #                 sourcemob = mobslot.segment.mob
        #                 locator = None
        #                 # different essences store locators in different places
        #                 if (isinstance(sourcemob.descriptor,
        #                                aaf2.essence.DigitalImageDescriptor)
        #                         and sourcemob.descriptor.locator):
        #                     locator = sourcemob.descriptor.locator[0]
        #                 elif "Locator" in sourcemob.descriptor.keys():
        #                     locator = sourcemob.descriptor["Locator"].value[0]
        #
        #                 if locator:
        #                     target_path = locator["URLString"].value
        #
        #     # if we have target path, create an ExternalReference, otherwise
        #     # create an MissingReference.
        #     if target_path:
        #         if not target_path.startswith("file://"):
        #             target_path = "file://" + target_path
        #         target_path = target_path.replace("\\", "/")
        #         media = otio.schema.ExternalReference(target_url=target_path)
        #     else:
        #         media = otio.schema.MissingReference()
        #
        #     media.available_range = otio.opentime.TimeRange(
        #         otio.opentime.RationalTime(media_start, editRate),
        #         otio.opentime.RationalTime(media_length, editRate)
        #     )
        #     # copy the metadata from the master into the media_reference
        #     media.metadata["AAF"] = mastermob_child.metadata.get("AAF", {})
        #     result.media_reference = media

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
            child = _transcribe(slot, parents + [item], editRate, masterMobs)
            _add_child(result, child, slot)

    elif isinstance(item, aaf2.components.Sequence):
        result = otio.schema.Track()

        for component in item.components:
            child = _transcribe(component, parents + [item], editRate, masterMobs)
            _add_child(result, child, component)

    elif isinstance(item, aaf2.components.OperationGroup):
        result = _transcribe_operation_group(
            item, parents, metadata, editRate, masterMobs
        )

    elif isinstance(item, aaf2.mobslots.TimelineMobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parents + [item], editRate, masterMobs)
        _add_child(result, child, item.segment)

    elif isinstance(item, aaf2.mobslots.MobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parents + [item], editRate, masterMobs)
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
            parents + [item],
            editRate,
            masterMobs
        )

        alternates = [
            _transcribe(alt, parents + [item], editRate, masterMobs)
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

    elif isinstance(item, collections.Iterable):
        result = otio.schema.SerializableCollection()
        for child in item:
            result.append(
                _transcribe(
                    child,
                    parents + [item],
                    editRate,
                    masterMobs
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
            "Timecode missing '{}'".format(e)
        )

    if edit_rate.denominator == 1:
        rate = edit_rate.numerator
    else:
        rate = float(edit_rate)

    return otio.opentime.RationalTime(
        value=int(start),
        rate=rate,
    )


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


def _transcribe_operation_group(item, parents, metadata, editRate, masterMobs):
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
        child = _transcribe(segment, parents + [item], editRate, masterMobs)
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


def read_from_file(filepath, simplify=True):

    with aaf2.open(filepath) as aaf_file:

        storage = aaf_file.content

        # Note: We're skipping: f.header
        # Is there something valuable in there?

        __names.clear()
        masterMobs = {}

        # result = _transcribe(
        #     storage,
        #     parents=list(),
        #     editRate=None,
        #     masterMobs=masterMobs
        # )

        top = storage.toplevel()
        if top:
            # re-transcribe just the top-level mobs
            # but use all the master mobs we found in the 1st pass
            __names.clear()  # reset the names back to 0
        result = _transcribe(top, parents=list(), editRate=None, masterMobs=masterMobs)

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
