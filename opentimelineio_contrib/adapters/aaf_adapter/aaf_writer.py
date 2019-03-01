#
# Copyright 2019 Pixar Animation Studios
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

"""AAF Adapter Transcriber

Specifies how to transcribe an OpenTimelineIO file into an AAF file.
"""

import aaf2
from aaf2.rational import AAFRational
from aaf2.auid import AUID
import uuid
import opentimelineio as otio
from abc import ABCMeta, abstractmethod


def _timecode_length(clip):
    """Return the timecode length (length of essence data) from an otio clip."""
    try:
        timecode_length = clip.media_reference.available_range.duration.value
    except AttributeError:
        timecode_length = clip.metadata["AAF"]["Length"]
        print("WARNING: FIX ME! Relying on backup metadata value ('AAF.Length')"
              "instead of actual media_reference.available_range.duration")
    return timecode_length


class AAFFileTranscriber(object):
    """
    AAFFileTranscriber

    AAFFileTranscriber manages the file-level knowledge during a conversion from
    otio to aaf. This includes keeping track of unique tapemobs and mastermobs.
    """
    def __init__(self, input_otio, aaf_file):
        """
        AAFFileTranscriber requires an input timeline and an output pyaaf2 file handle.

        Args:
            input_otio: an input OpenTimelineIO timeline
            aaf_file: a pyaaf2 file handle to an output file
        """
        self.aaf_file = aaf_file
        self.compositionmob = self.aaf_file.create.CompositionMob()
        self.compositionmob.name = input_otio.name
        self.compositionmob.usage = "Usage_TopLevel"
        self.aaf_file.content.mobs.append(self.compositionmob)
        self._unique_mastermobs = {}
        self._unique_tapemobs = {}

    def _unique_mastermob(self, otio_clip):
        """Get a unique mastermob, identified by clip metadata mob id."""
        # Currently, we only support clips that are already in Avid with a mob ID
        mob_id = otio_clip.metadata["AAF"]["SourceID"]
        master_mob = self._unique_mastermobs.get(mob_id)
        if not master_mob:
            master_mob = self.aaf_file.create.MasterMob()
            master_mob.name = otio_clip.name
            master_mob.mob_id = aaf2.mobid.MobID(mob_id)
            self.aaf_file.content.mobs.append(master_mob)
            self._unique_mastermobs[mob_id] = master_mob
        return master_mob

    def _unique_tapemob(self, otio_clip):
        """Get a unique tapemob, identified by clip metadata mob id."""
        mob_id = otio_clip.metadata["AAF"]["SourceID"]
        tape_mob = self._unique_tapemobs.get(mob_id)
        if not tape_mob:
            tape_mob = self.aaf_file.create.SourceMob()
            tape_mob.name = otio_clip.name
            tape_mob.descriptor = self.aaf_file.create.ImportDescriptor()
            edit_rate = otio_clip.duration().rate
            tape_timecode_slot = tape_mob.create_timecode_slot(edit_rate,
                                                               edit_rate)
            try:
                timecode_start = \
                    otio_clip.media_reference.available_range.start_time.value
                # HACK: This backup here shouldn't be needed.
            except AttributeError:
                print("WARNING: FIX ME! Relying on metadata value ('AAF.StartTime')"
                      "instead of actual media_reference.available_range.start_time")
                try:
                    timecode_start = otio_clip.metadata["AAF"]["StartTime"]
                except KeyError:
                    raise("AAF.StartTime not found even in backup metadata")

            timecode_length = _timecode_length(otio_clip)
            tape_timecode_slot.segment.start = timecode_start
            tape_timecode_slot.segment.length = timecode_length
            self.aaf_file.content.mobs.append(tape_mob)
            self._unique_tapemobs[mob_id] = tape_mob
        return tape_mob

    def track_transcriber(self, otio_track):
        """Return an appropriate TrackTranscriber given an otio track."""
        if otio_track.kind == otio.schema.TrackKind.Video:
            transcriber = VideoTrackTranscriber(self, otio_track)
        elif otio_track.kind == otio.schema.TrackKind.Audio:
            transcriber = AudioTrackTranscriber(self, otio_track)
        else:
            raise otio.exceptions.NotSupportedError("Unsupported track kind: {}".format(otio_track.kind))
        return transcriber


def validate_metadata(timeline):
    """Print a check of necessary metadata requirements for an otio timeline."""

    errors = []

    def _check(otio_child, keys_path):
        keys = keys_path.split(".")
        value = otio_child.metadata
        try:
            for key in keys:
                value = value[key]
        except KeyError:
            print("{}({}) is missing required metadata {}".format(
                  otio_child.name, type(otio_child), keys_path))
            errors.append((otio_child, keys_path))

    for otio_child in timeline.each_child():
        if isinstance(otio_child, otio.schema.Gap):
            _check(otio_child, "AAF.Length")  # Shouldn't need
        elif isinstance(otio_child, otio.schema.Transition):
            _check(otio_child, "AAF.PointList")
            _check(otio_child, "AAF.OperationGroup")
            _check(otio_child, "AAF.OperationGroup.Operation")
            _check(otio_child,
                   "AAF.OperationGroup.Operation.DataDefinition.Name")
            _check(otio_child, "AAF.OperationGroup.Operation.Description")
            _check(otio_child, "AAF.OperationGroup.Operation.Name")
            _check(otio_child, "AAF.Length")
            _check(otio_child, "AAF.CutPoint")
        elif isinstance(otio_child, otio.schema.Clip):
            _check(otio_child, "AAF.SourceID")
            _check(otio_child, "AAF.SourceMobSlotID")

    return errors


class TrackTranscriber(object):
    """
    TrackTranscriber is the base class for the conversion of a given otio track.

    TrackTranscriber is not meant to be used by itself. It provides the common
    functionality to inherit from.
    """
    __metaclass__ = ABCMeta

    def __init__(self, root_file_transcriber, otio_track):
        """
        TrackTranscriber

        Args:
            root_file_transcriber: the corresponding 'parent' AAFFileTranscriber object
            otio_track: the given otio_track to convert
        """
        self.root_file_transcriber = root_file_transcriber
        self.compositionmob = root_file_transcriber.compositionmob
        self.aaf_file = root_file_transcriber.aaf_file
        self.otio_track = otio_track
        self.edit_rate = next(self.otio_track.each_clip()).duration().rate
        self.timeline_mobslot, self.sequence = self._create_timeline_mobslot()

    @property
    @abstractmethod
    def media_kind(self):
        """Return the string for what kind of track this is."""
        pass

    @abstractmethod
    def _create_timeline_mobslot(self):
        """
        Return a timeline_mobslot and sequence for this track.

        In AAF, a TimelineMobSlot is a container for the Sequence. A Sequence is
        analogous to an otio track.

        Returns:
            Returns a tuple of (TimelineMobSlot, Sequence)
        """
        pass

    @abstractmethod
    def default_descriptor(self, otio_clip):
        pass

    def aaf_filler(self, otio_gap):
        """Convert an otio Gap into an aaf Filler"""
        # length = otio_gap.duration().value  # XXX Not working for some reason
        length = otio_gap.metadata["AAF"]["Length"]
        filler = self.aaf_file.create.Filler(self.media_kind, length)
        return filler

    def aaf_sourceclip(self, otio_clip):
        """Convert an otio Clip into an aaf SourceClip"""
        tapemob, tapemob_slot = self._create_tapemob(otio_clip)
        filemob, filemob_slot = self._create_filemob(otio_clip, tapemob, tapemob_slot)
        mastermob, mastermob_slot = self._create_mastermob(otio_clip, filemob,
                                                           filemob_slot)
        length = otio_clip.duration().value
        compmob_clip = self.compositionmob.create_source_clip(
            slot_id=self.timeline_mobslot.slot_id,
            length=length,
            media_kind=self.media_kind)
        compmob_clip.mob = mastermob
        compmob_clip.slot = mastermob_slot
        compmob_clip.slot_id = mastermob_slot.slot_id
        return compmob_clip

    def aaf_transition(self, otio_transition):
        """Convert an otio Transition into an aaf Transition."""
        # Create ParameterDef for AvidParameterByteOrder
        if otio_transition.transition_type != otio.schema.transition.TransitionTypes.SMPTE_Dissolve:
            print("Unsupported transition type: {}".format(otio_transition.transition_type))
            return None
        avid_param_byteorder_id = uuid.UUID("c0038672-a8cf-11d3-a05b-006094eb75cb")
        byteorder_typedef = self.aaf_file.dictionary.lookup_typedef("aafUInt16")
        param_byteorder = self.aaf_file.create.ParameterDef(avid_param_byteorder_id,
                                                     "AvidParameterByteOrder",
                                                     "",
                                                     byteorder_typedef)
        self.aaf_file.dictionary.register_def(param_byteorder)

        # Create ParameterDef for AvidEffectID
        avid_effect_id = uuid.UUID("93994bd6-a81d-11d3-a05b-006094eb75cb")
        avid_effect_typdef = self.aaf_file.dictionary.lookup_typedef("AvidBagOfBits")
        param_effect_id = self.aaf_file.create.ParameterDef(avid_effect_id,
                                                     "AvidEffectID",
                                                     "",
                                                     avid_effect_typdef)
        self.aaf_file.dictionary.register_def(param_effect_id)

        # Create ParameterDef for AFX_FG_KEY_OPACITY_U
        opacity_param_id = uuid.UUID("8d56813d-847e-11d5-935a-50f857c10000")
        opacity_param_def = self.aaf_file.dictionary.lookup_typedef("Rational")
        opacity_param = self.aaf_file.create.ParameterDef(opacity_param_id,
                                                   "AFX_FG_KEY_OPACITY_U",
                                                   "",
                                                   opacity_param_def)
        self.aaf_file.dictionary.register_def(opacity_param)

        # Create VaryingValue
        opacity_u = self.aaf_file.create.VaryingValue()
        opacity_u.parameterdef = self.aaf_file.dictionary.lookup_parameterdef(
            "AFX_FG_KEY_OPACITY_U")
        vval_extrapolation_id = uuid.UUID("0e24dd54-66cd-4f1a-b0a0-670ac3a7a0b3")
        opacity_u["VVal_Extrapolation"].value = vval_extrapolation_id
        opacity_u["VVal_FieldCount"].value = 1

        interpolation_id = uuid.UUID("5b6c85a4-0ede-11d3-80a9-006008143e6f")
        interpolation_def = self.aaf_file.create.InterpolationDef(
            interpolation_id, "LinearInterp", "Linear keyframe interpolation")
        self.aaf_file.dictionary.register_def(interpolation_def)
        opacity_u["Interpolation"].value = self.aaf_file.dictionary.lookup_interperlationdef(
            "LinearInterp")

        pointlist = otio_transition.metadata["AAF"]["PointList"]

        c1 = self.aaf_file.create.ControlPoint()
        c1["EditHint"].value = "Proportional"
        c1.value = pointlist[0]["Value"]
        c1.time = pointlist[0]["Time"]

        c2 = self.aaf_file.create.ControlPoint()
        c2["EditHint"].value = "Proportional"
        c2.value = pointlist[1]["Value"]
        c2.time = pointlist[1]["Time"]

        opacity_u["PointList"].extend([c1, c2])

        op_group_metadata = otio_transition.metadata["AAF"]["OperationGroup"]
        effect_id = op_group_metadata["Operation"].get("Identification")
        is_time_warp = op_group_metadata["Operation"].get("IsTimeWarp")
        by_pass = op_group_metadata["Operation"].get("Bypass")
        number_inputs = op_group_metadata["Operation"].get("NumberInputs")
        operation_category = op_group_metadata["Operation"].get("OperationCategory")
        data_def_name = op_group_metadata["Operation"]["DataDefinition"]["Name"]
        data_def = self.aaf_file.dictionary.lookup_datadef(str(data_def_name))
        description = op_group_metadata["Operation"]["Description"]
        op_def_name = otio_transition.metadata["AAF"][
            "OperationGroup"
        ]["Operation"]["Name"]

        op_def = self.aaf_file.create.OperationDef(uuid.UUID(effect_id), op_def_name)
        self.aaf_file.dictionary.register_def(op_def)
        op_def.media_kind = self.media_kind
        datadef = self.aaf_file.dictionary.lookup_datadef("Picture")
        op_def["IsTimeWarp"].value = is_time_warp
        op_def["Bypass"].value = by_pass
        op_def["NumberInputs"].value = number_inputs
        op_def["OperationCategory"].value = str(operation_category)
        op_def["ParametersDefined"].extend([param_byteorder,
                                            param_effect_id])
        op_def["DataDefinition"].value = data_def
        op_def["Description"].value = str(description)

        # Create OperationGroup
        length = otio_transition.metadata["AAF"]["Length"]
        operation_group = self.aaf_file.create.OperationGroup(op_def, length)
        operation_group["DataDefinition"].value = datadef
        operation_group["Parameters"].append(opacity_u)

        # Create Transition
        transition = self.aaf_file.create.Transition(self.media_kind, length)
        transition["OperationGroup"].value = operation_group
        transition["CutPoint"].value = otio_transition.metadata["AAF"]["CutPoint"]
        transition["DataDefinition"].value = datadef
        return transition

    def _create_tapemob(self, otio_clip):
        """
        Return a physical sourcemob for an otio Clip based on the MobID.

        Returns:
            Returns a tuple of (TapeMob, TapeMobSlot)
        """
        tapemob = self.root_file_transcriber._unique_tapemob(otio_clip)
        tapemob_slot = tapemob.create_empty_slot(self.edit_rate, self.media_kind)
        tapemob_slot.segment.length = _timecode_length(otio_clip)
        return tapemob, tapemob_slot

    def _create_filemob(self, otio_clip, tapemob, tapemob_slot):
        """
        Return a file sourcemob for an otio Clip. Needs a tapemob and tapemob slot.

        Returns:
            Returns a tuple of (FileMob, FileMobSlot)
        """
        filemob = self.aaf_file.create.SourceMob()
        self.aaf_file.content.mobs.append(filemob)

        filemob.descriptor = self.default_descriptor(otio_clip)
        filemob_slot = filemob.create_timeline_slot(self.edit_rate)
        filemob_clip = filemob.create_source_clip(
            slot_id=filemob_slot.slot_id,
            length=tapemob_slot.segment.length,
            media_kind=tapemob_slot.segment.media_kind)
        filemob_clip.mob = tapemob
        filemob_clip.slot = tapemob_slot
        filemob_clip.slot_id = tapemob_slot.slot_id
        filemob_slot.segment = filemob_clip
        return filemob, filemob_slot

    def _create_mastermob(self, otio_clip, filemob, filemob_slot):
        """
        Return a mastermob for an otio Clip. Needs a filemob and filemob slot.

        Returns:
            Returns a tuple of (MasterMob, MasterMobSlot)
        """
        mastermob = self.root_file_transcriber._unique_mastermob(otio_clip)
        timecode_length = _timecode_length(otio_clip)
        # Prevent duplicate slots by relying on the SlotID
        slot_id = otio_clip.metadata["AAF"]["SourceMobSlotID"]
        try:
            mastermob_slot = mastermob.slot_at(slot_id)
        except IndexError:
            mastermob_slot = mastermob.create_timeline_slot(
                edit_rate=self.edit_rate, slot_id=slot_id)
        mastermob_clip = mastermob.create_source_clip(
            slot_id=mastermob_slot.slot_id,
            length=timecode_length,
            media_kind=self.media_kind)
        mastermob_clip.mob = filemob
        mastermob_clip.slot = filemob_slot
        mastermob_clip.slot_id = filemob_slot.slot_id
        mastermob_slot.segment = mastermob_clip
        return mastermob, mastermob_slot


class VideoTrackTranscriber(TrackTranscriber):

    @property
    def media_kind(self):
        return "picture"

    def _create_timeline_mobslot(self):
        """
        Create a Sequence container (TimelineMobSlot) and Sequence.

        TimelineMobSlot --> Sequence
        """
        timeline_mobslot = self.compositionmob.create_timeline_slot(
            edit_rate=self.edit_rate)
        sequence = self.aaf_file.create.Sequence(media_kind=self.media_kind)
        timeline_mobslot.segment = sequence
        return timeline_mobslot, sequence

    def default_descriptor(self, otio_clip):
        # TODO: Determine if these values are the correct, and if so,
        # maybe they should be in the AAF metadata
        descriptor = self.aaf_file.create.CDCIDescriptor()
        descriptor["ComponentWidth"].value = 8
        descriptor["HorizontalSubsampling"].value = 2
        descriptor["ImageAspectRatio"].value = "16/9"
        descriptor["StoredWidth"].value = 1920
        descriptor["StoredHeight"].value = 1080
        descriptor["FrameLayout"].value = "FullFrame"
        descriptor["VideoLineMap"].value = [42, 0]
        descriptor["SampleRate"].value = 24
        descriptor["Length"].value = 1
        return descriptor


class AudioTrackTranscriber(TrackTranscriber):

    @property
    def media_kind(self):
        return "sound"

    def aaf_sourceclip(self, otio_clip):
        # Parameter Definition
        param_id = AUID("e4962322-2267-11d3-8a4c-0050040ef7d2")
        typedef = self.aaf_file.dictionary.lookup_typedef("Rational")
        param_def = self.aaf_file.create.ParameterDef(param_id,
                                               "Pan",
                                               "Pan",
                                               typedef)
        self.aaf_file.dictionary.register_def(param_def)
        interp_def = self.aaf_file.create.InterpolationDef(aaf2.misc.LinearInterp,
                                                    "LinearInterp",
                                                    "LinearInterp")
        self.aaf_file.dictionary.register_def(interp_def)
        # PointList
        # revisit duration()
        length = otio_clip.duration().value
        c1 = self.aaf_file.create.ControlPoint()
        c1["ControlPointSource"].value = 2
        c1["Time"].value = AAFRational("0/{}".format(length))
        c1["Value"].value = 0
        c2 = self.aaf_file.create.ControlPoint()
        c2["ControlPointSource"].value = 2
        c2["Time"].value = AAFRational("{}/{}".format(length - 1, length))
        c2["Value"].value = 0
        varying_value = self.aaf_file.create.VaryingValue()
        varying_value.parameterdef = param_def
        varying_value["Interpolation"].value = interp_def
        varying_value["PointList"].extend([c1, c2])
        opgroup = self.timeline_mobslot.segment
        opgroup.parameters.append(varying_value)

        return super(AudioTrackTranscriber, self).aaf_sourceclip(otio_clip)

    def _create_timeline_mobslot(self):
        """
        Create a Sequence container (TimelineMobSlot) and Sequence.
        Sequence needs to be in an OperationGroup.

        TimelineMobSlot --> OperationGroup --> Sequence
        """
        # TimelineMobSlot
        timeline_mobslot = self.compositionmob.create_sound_slot(
            edit_rate=self.edit_rate)
        # OperationDefinition
        opdef_auid = AUID("9d2ea893-0968-11d3-8a38-0050040ef7d2")
        opdef = self.aaf_file.create.OperationDef(opdef_auid, "Audio Pan")
        opdef.media_kind = self.media_kind
        opdef["NumberInputs"].value = 1
        self.aaf_file.dictionary.register_def(opdef)
        # OperationGroup
        total_length = sum([t.duration().value for t in self.otio_track])
        opgroup = self.aaf_file.create.OperationGroup(opdef)
        opgroup.media_kind = self.media_kind
        opgroup.length = total_length
        timeline_mobslot.segment = opgroup
        # Sequence
        sequence = self.aaf_file.create.Sequence(media_kind=self.media_kind)
        sequence.length = total_length
        opgroup.segments.append(sequence)
        return timeline_mobslot, sequence

    def default_descriptor(self, otio_clip):
        descriptor = self.aaf_file.create.PCMDescriptor()
        descriptor["AverageBPS"].value = 96000
        descriptor["BlockAlign"].value = 2
        descriptor["QuantizationBits"].value = 16
        descriptor["AudioSamplingRate"].value = 48000
        descriptor["Channels"].value = 1
        descriptor["SampleRate"].value = 48000
        descriptor["Length"].value = _timecode_length(otio_clip)
        return descriptor
