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

"""OpenTimelineIO Advanced Authoring Format (AAF) Adapter"""

import sys
sys.path.append("/depts/tools/mpg/lib/python/pyaafosx")

import aaf
import aaf.storage
import aaf.mob
import aaf.define
import aaf.component
import aaf.base

import opentimelineio as otio

def _get_name(item):
    if hasattr(item, 'name'):
        name = item.name
        if name:
            return name
    return _get_class_name(item)

def _get_class_name(item):
    if hasattr(item,"class_name"):
        return item.class_name
    else:
        return item.__class__.__name__

def _transcribe(item, parent=None, editRate=24):
    result = None
    metadata = {}
    
    if False:
        pass
    # if isinstance(item, list):
    #     self.extendChildItems(item)
    
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
        for mob in item.master_mobs():
            child = _transcribe(mob, item)
            if child is not None:
                result.append(child)

        # for mob in item.GetSourceMobs():
        #     result.append(_transcribe(mob, item))
    
    elif isinstance(item, aaf.mob.Mob):
        result = otio.schema.Timeline()
        
        for slot in item.slots():
            child = _transcribe(slot, item)
            if child is not None:
                result.tracks.append(child)
            
    
    # elif isinstance(item, aaf.dictionary.Dictionary):
    #     l = []
    #     l.append(DummyItem(list(item.class_defs()), 'ClassDefs'))
    #     l.append(DummyItem(list(item.codec_defs()), 'CodecDefs'))
    #     l.append(DummyItem(list(item.container_defs()), 'ContainerDefs'))
    #     l.append(DummyItem(list(item.data_defs()), 'DataDefs'))
    #     l.append(DummyItem(list(item.interpolation_defs()), 'InterpolationDefs'))
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
        result.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0,editRate),
            otio.opentime.RationalTime(length,editRate)
        )

    elif isinstance(item, aaf.component.Filler):
        result = otio.schema.Gap()

    elif isinstance(item, aaf.component.NestedScope):
        result = otio.schema.Sequence()
        
        for segment in item.segments():
            child = _transcribe(segment, item)
            if child is not None:
                result.append(child)

    elif isinstance(item, aaf.component.Sequence):
        result = otio.schema.Sequence()
        
        for component in item.components():
            child = _transcribe(component, item)
            if child is not None:
                result.append(child)

    elif isinstance(item, aaf.mob.TimelineMobSlot):
        result = otio.schema.Sequence()
        
        child = _transcribe(item.segment, item)
        if child is not None:
            result.append(child)

    elif isinstance(item, aaf.component.Timecode):
        pass
    elif isinstance(item, aaf.component.Pulldown):
        pass
    elif isinstance(item, aaf.component.EdgeCode):
        pass
    elif isinstance(item, aaf.component.ScopeReference):
        pass
        
    else:
        # result = otio.core.Composition()
        print("SKIPPING: {}: {} -- {}".format(type(item), item, result))

    metadata["Name"] = _get_name(item)
    metadata["ClassName"] = _get_class_name(item)

    if isinstance(item, aaf.component.Component):
        metadata["Length"] = item.length

    if result is not None:
        result.name = str(metadata["Name"])
        if not result.metadata:
            result.metadata = {}
        result.metadata["AAF"] = metadata

    return result

def read_from_file(filepath):
    
    f = aaf.open(filepath)
    
    header = f.header
    storage = f.storage
    
    print("F: {}".format(f))
    print("HEADER: {}".format(header))
    print("STORAGE: {}".format(storage))
    
    topLevelMobs = list(storage.toplevel_mobs())

    print("topLevelMobs: {}".format(topLevelMobs))

    collection = _transcribe(storage)
    # otio.schema.SerializableCollection()
    #
    # for mob in topLevelMobs:
    #     timeline = otio.schema.Timeline()
    #     timeline.name = mob.name
    #     collection.append(timeline)
    
    return collection

