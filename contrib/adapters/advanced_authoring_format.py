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
import re
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


# We use this _unique_name function to assign #s at the end of otherwise
# anonymous objects. This aids in debugging when you have loads of objects
# of the same type in a large composition.
def _unique_name(name):
    while name in __names:
        m = re.search(r'(\d+)$', name)
        if m:
            num = int(m.group(1))
            name = re.sub(r'(\d+)$', str(num+1), name)
        else:
            name = name+" 2"
    __names.add(name)
    return name


def _get_name(item):
    if hasattr(item, 'name'):
        name = item.name
        if name:
            return name
    if isinstance(item, aaf.component.SourceClip):
        return item.resolve_ref().name or _unique_name("Untitled SourceClip")
    return _unique_name(_get_class_name(item))


def _get_class_name(item):
    if hasattr(item, "class_name"):
        return item.class_name
    else:
        return item.__class__.__name__


def _transcribe_property(prop):
    if isinstance(prop, list):
        return [_transcribe_property(child) for child in prop]

    # XXX: The unicode type doesn't exist in Python 3 (all strings are unicode)
    # so we have to use type(u"") which works in both Python 2 and 3.
    elif type(prop) in (str, type(u""), int, float, bool):
        return prop

    if isinstance(prop, aaf.iterator.PropValueResolveIter):
        result = {}
        for child in prop:
            if isinstance(child, aaf.property.TaggedValue):
                result[child.name] = _transcribe_property(child.value)
            elif isinstance(child, aaf.mob.MasterMob):
                result[child.name] = str(child.mobID)
            elif isinstance(child, aaf.mob.SourceMob):
                result[child.name] = str(child.mobID)
            else:
                # @TODO: There may be more properties that we might want also.
                # If you want to see what is being skipped, turn on debug.
                if debug:
                    print("Skipping unrecognized property: {}".format(child))
        return result

    else:
        return str(prop)


def _add_child(parent, child, source):
    if child is None:
        if debug:
            print("MISSING CHILD? {}".format(source))
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

    # @TODO: There are a bunch of other AAF object types that we will
    # likely need to add support for. I'm leaving this code here to help
    # future efforts to extract the useful information out of these.

    # elif isinstance(item, aaf.storage.File):
    #     self.extendChildItems([item.header])

    # elif isinstance(item, aaf.storage.Header):
    #     self.extendChildItems([item.storage()])
    #     self.extendChildItems([item.dictionary()])

    # elif isinstance(item, DummyItem):
    #     self.extendChildItems(item.item)

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
    # elif isinstance(item, aaf.mob.Mob):
    #
    #     self.extendChildItems(list(item.slots()))
    #
    # elif isinstance(item, aaf.mob.MobSlot):
    #      self.extendChildItems([item.segment])
    # elif isinstance(item, aaf.component.NestedScope):
    #     self.extendChildItems(list(item.segments()))
    # elif isinstance(item, aaf.component.Sequence):
    #     self.extendChildItems(list(item.components()))
    #
    # elif isinstance(item, aaf.component.SourceClip):
    #     ref = item.resolve_ref()
    #     name = ref.name
    #     if name:
    #         self.extendChildItems([name])
    #
    # elif isinstance(item,aaf.component.OperationGroup):
    #     self.extendChildItems(list(item.input_segments()))
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
    #
    # elif isinstance(item, (aaf.base.AAFObject,aaf.define.MetaDef)):
    #     pass
    #
    # elif isinstance(item, aaf.component.Component):
    #     pass
    #
    # else:
    #     self.properties['Name'] = str(item)
    #     self.properties['ClassName'] = str(type(item))
    #     return

    elif isinstance(item, aaf.component.SourceClip):
        result = otio.schema.Clip()

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

    elif isinstance(item, aaf.mob.TimelineMobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, parent=item, masterMobs=masterMobs)
        _add_child(result, child, item.segment)
        if child is not None:
            child.metadata["AAF"]["MediaKind"] = str(item.segment.media_kind)

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

        # TODO: We can get markers this way, but they come in on
        # a separate Track. We need to consolidate them onto the
        # same track(s) as the Clips.
        # result = otio.schema.Marker()
        pass

    else:
        if debug:
            print("SKIPPING: {}: {} -- {}".format(type(item), item, result))

    if result is not None:
        result.name = str(metadata["Name"])
        if not result.metadata:
            result.metadata = {}
        result.metadata["AAF"] = metadata

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
                    trans = thing[c-1]

                    if child.source_range is None:
                        child.source_range = child.trimmed_range()
                    child.source_range.start_time += trans.in_offset
                    child.source_range.duration -= trans.in_offset

                # Is the item after us a Transition?
                if c < len(thing)-1 and isinstance(
                    thing[c+1],
                    otio.schema.Transition
                ):
                    after = thing[c+1]

                    if child.source_range is None:
                        child.source_range = child.trimmed_range()
                    child.source_range.duration -= after.out_offset

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

        # skip redundant containers
        if len(thing) == 1:
            # TODO: We may be discarding metadata here, should we merge it?
            return thing[0]

    return thing


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
    # Note: We're skipping: f.header and storage.toplevel_mobs()
    # Is there something valuable in those?

    __names.clear()
    result = _transcribe(storage)

    _fix_transitions(result)

    if simplify:
        result = _simplify(result)

    return result
