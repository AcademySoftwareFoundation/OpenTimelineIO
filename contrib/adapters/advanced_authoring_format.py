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

Requires that you set the environment variables:
    OTIO_AAF_PYTHON_LIB - should point at the PyAAF module.
"""

import os
import sys
import opentimelineio as otio

if os.environ["OTIO_AAF_PYTHON_LIB"] not in sys.path:
    sys.path += [os.environ["OTIO_AAF_PYTHON_LIB"]]

import aaf  # noqa (E402 module level import not at top of file)
import aaf.storage  # noqa
import aaf.mob  # noqa
import aaf.define  # noqa
import aaf.component  # noqa
import aaf.base  # noqa

debug = False


def _get_name(item):
    if hasattr(item, 'name'):
        name = item.name
        if name:
            return name
    if isinstance(item, aaf.component.SourceClip):
        return item.resolve_ref().name or "Untitled SourceClip"
    return _get_class_name(item)


def _get_class_name(item):
    if hasattr(item, "class_name"):
        return item.class_name
    else:
        return item.__class__.__name__


def _transcribe_property(prop):
    if isinstance(prop, list):
        return [_transcribe_property(child) for child in prop]

    elif type(prop) in (str, unicode, int, float, bool):
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
            # elif hasattr(child, "name"):
            #     result[child.name] = _transcribe(child)
            else:
                if debug:
                    print "???", child
        return result

    else:
        return str(prop)


def _transcribe(item, parent=None, editRate=24):
    result = None
    metadata = {}

    metadata["Name"] = _get_name(item)
    metadata["ClassName"] = _get_class_name(item)

    if isinstance(item, aaf.component.Component):
        metadata["Length"] = item.length

    if isinstance(item, aaf.base.AAFObject):
        for prop in item.properties():
            if hasattr(prop, 'name') and hasattr(prop, 'value'):
                key = str(prop.name)
                value = prop.value
                # if isinstance(value, aaf.dictionary.Dictionary):
                # ???
                metadata[key] = _transcribe_property(value)

    if False:
        pass

    # elif isinstance(item, aaf.storage.File):
    #     self.extendChildItems([item.header])

    # elif isinstance(item, aaf.storage.Header):
    #     self.extendChildItems([item.storage()])
    #     self.extendChildItems([item.dictionary()])

    # elif isinstance(item, DummyItem):
    #     self.extendChildItems(item.item)

    elif isinstance(item, aaf.storage.ContentStorage):
        result = otio.schema.SerializableCollection()

        for mob in item.composition_mobs():
            child = _transcribe(mob, item)
            if child is not None:
                result.append(child)

        # TODO: Do we want these mixed in with the composition?
        # for mob in item.master_mobs():
        #     child = _transcribe(mob, item)
        #     if child is not None:
        #         result.append(child)

        # for mob in item.GetSourceMobs():
        #     result.append(_transcribe(mob, item))

    elif isinstance(item, aaf.mob.Mob):
        result = otio.schema.Timeline()

        for slot in item.slots():
            child = _transcribe(slot, item)
            if child is not None:
                result.tracks.append(child)
            else:
                if debug:
                    print "NO CHILD?", slot

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

#         elif isinstance(item, pyaaf.AxSelector):
#             self.extendChildItems(list(item.EnumAlternateSegments()))
#
#         elif isinstance(item, pyaaf.AxScopeReference):
#             #print item, item.GetRelativeScope(),item.GetRelativeSlot()
#             pass
#
#         elif isinstance(item, pyaaf.AxEssenceGroup):
#             segments = []
#
#             for i in xrange(item.CountChoices()):
#                 choice = item.GetChoiceAt(i)
#                 segments.append(choice)
#             self.extendChildItems(segments)
#
#         elif isinstance(item, pyaaf.AxProperty):
#             self.properties['Value'] = str(item.GetValue())
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
        result = otio.schema.Track()

        for segment in item.segments():
            child = _transcribe(segment, item)
            if child is not None:
                result.append(child)
            else:
                if debug:
                    print "NO CHILD?", segment

    elif isinstance(item, aaf.component.Sequence):
        result = otio.schema.Track()

        for component in item.components():
            child = _transcribe(component, item)
            if child is not None:
                result.append(child)
            else:
                if debug:
                    print "NO CHILD?", component

    elif isinstance(item, aaf.mob.TimelineMobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, item)
        if child is not None:
            child.metadata["AAF"]["MediaKind"] = str(item.segment.media_kind)
            result.append(child)
        else:
            if debug:
                print "NO CHILD?", item.segment

    elif isinstance(item, aaf.mob.MobSlot):
        result = otio.schema.Track()

        child = _transcribe(item.segment, item)
        if child is not None:
            result.append(child)
        else:
            if debug:
                print "NO CHILD?", item.segment

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

    else:
        # result = otio.core.Composition()
        if debug:
            print("SKIPPING: {}: {} -- {}".format(type(item), item, result))

    if result is not None:
        result.name = str(metadata["Name"])
        if not result.metadata:
            result.metadata = {}
        result.metadata["AAF"] = metadata

    return result


def _simplify(thing):
    
    if isinstance(thing, otio.schema.SerializableCollection):
        if len(thing)==1:
            return _simplify(thing[0])
        else:
            for c, child in enumerate(thing):
                thing[c] = _simplify(child)
            return thing

    elif isinstance(thing, otio.schema.Timeline):
        # note that we ignore the return value of _simplify here
        # so that we don't ever get rid of the Timeline's Stack.
        _simplify(thing.tracks)
        return thing

    elif isinstance(thing, otio.core.Composition):
        # simplify our children
        for c, child in enumerate(thing):
            thing[c] = _simplify(child)
        
        # remove empty children
        for c in reversed(range(len(thing))):
            child = thing[c]
            if not _contains_something_valuable(child):
                # TODO: We're discarding metadata here, should we retain it?
                del thing[c]
        
        # skip redundant containers
        if len(thing) == 1:
            # TODO: We may be discarding metadata here, should we merge it?
            return thing[0]

    return thing


def _contains_something_valuable(thing):
    if isinstance(thing, otio.core.Composition):

        if len(thing)==0:
            # NOT valuable because it is empty
            return False

        for child in thing:
            if _contains_something_valuable(child):
                # valuable because this child is valuable
                return True

        # none of the children were valuable, so thing is NOT valuable
        return False

    if isinstance(thing, otio.schema.Gap):
        if len(thing.effects)>0 or len(thing.markers)>0:
            return True
        # TODO: Are there other valuable things we should look for on a Gap?
        return False

    # anything else is presumed to be valuable
    return True


def read_from_file(filepath, simplify=True):

    f = aaf.open(filepath)

    # header = f.header
    storage = f.storage
    # topLevelMobs = list(storage.toplevel_mobs())

    result = _transcribe(storage)

    if simplify:
        result = _simplify(result)

    return result
