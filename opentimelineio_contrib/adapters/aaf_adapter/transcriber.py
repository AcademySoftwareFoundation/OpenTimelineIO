#
# AAF writer section
#
import aaf2
from aaf2.rational import AAFRational
from aaf2.auid import AUID
import uuid


def _timecode_length(clip):
    timecode_length = clip.duration().value
    try:
        timecode_length = clip.media_reference.available_range.duration.value
        timecode_length = clip.metadata["AAF"]["Length"]
    except BaseException:
        pass
    return timecode_length


class AAFFileTranscriber(object):
    def __init__(self, input_otio, aaf_file):
        self.f = aaf_file
        self.compositionmob = self.f.create.CompositionMob()
        self.compositionmob.name = input_otio.name
        self.compositionmob.usage = "Usage_TopLevel"
        self.f.content.mobs.append(self.compositionmob)
        self._unique_mastermobs = {}
        self._unique_tapemobs = {}

    def _unique_mastermob(self, otio_clip):
        mob_id = otio_clip.metadata["AAF"]["SourceID"]
        master_mob = self._unique_mastermobs.get(mob_id)
        if not master_mob:
            master_mob = self.f.create.MasterMob()
            master_mob.name = "MasterMob_" + str(otio_clip.name)
            master_mob.mob_id = aaf2.mobid.MobID(mob_id)
            self.f.content.mobs.append(master_mob)
            self._unique_mastermobs[mob_id] = master_mob
        return master_mob

    def _unique_tapemob(self, otio_clip):
        mob_id = otio_clip.metadata["AAF"]["SourceID"]
        tape_mob = self._unique_tapemobs.get(mob_id)
        if not tape_mob:
            tape_mob = self.f.create.SourceMob()
            tape_mob.name = "TapeMob_" + str(otio_clip.name)
            tape_mob.descriptor = self.f.create.ImportDescriptor()
            edit_rate = otio_clip.duration().rate
            tape_timecode_slot = tape_mob.create_timecode_slot(edit_rate,
                                                               edit_rate)
            try:
                timecode_start = \
                    otio_clip.media_reference.available_range.start_time.value
                timecode_start = otio_clip.metadata["AAF"]["StartTime"]
            except BaseException:
                timecode_start = 86400
            timecode_length = _timecode_length(otio_clip)
            tape_timecode_slot.segment.start = timecode_start
            tape_timecode_slot.segment.length = timecode_length
            self.f.content.mobs.append(tape_mob)
            self._unique_tapemobs[mob_id] = tape_mob
        return tape_mob

    def track_transcriber(self, otio_track):
        if otio_track.kind == "Video":
            transcriber = VideoTrackTranscriber(self, otio_track)
        elif otio_track.kind == "Audio":
            transcriber = AudioTrackTranscriber(self, otio_track)
        assert transcriber
        return transcriber


class TrackTranscriber(object):
    """
    TrackTranscriber
    """

    def __init__(self, aaf_file_transcriber, otio_track):
        self.aaf_file_transcriber = aaf_file_transcriber
        self.compositionmob = aaf_file_transcriber.compositionmob
        self.f = aaf_file_transcriber.f
        self.otio_track = otio_track
        self.timeline_mobslot, self.sequence = self._create_timeline_mobslot()

    @property
    def media_kind(self):
        raise NotImplementedError()

    def aaf_filler(self, otio_gap):
        length = otio_gap.duration().value
        filler = self.f.create.Filler(self.media_kind, length)
        return filler

    def aaf_sourceclip(self, otio_clip):
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
        # Create ParameterDef for AvidParameterByteOrder
        avid_param_byteorder_id = uuid.UUID("c0038672-a8cf-11d3-a05b-006094eb75cb")
        byteorder_typedef = self.f.dictionary.lookup_typedef("aafUInt16")
        param_byteorder = self.f.create.ParameterDef(avid_param_byteorder_id,
                                                     "AvidParameterByteOrder",
                                                     "",
                                                     byteorder_typedef)
        self.f.dictionary.register_def(param_byteorder)

        # Create ParameterDef for AvidEffectID
        avid_effect_id = uuid.UUID("93994bd6-a81d-11d3-a05b-006094eb75cb")
        avid_effect_typdef = self.f.dictionary.lookup_typedef("AvidBagOfBits")
        param_effect_id = self.f.create.ParameterDef(avid_effect_id,
                                                     "AvidEffectID",
                                                     "",
                                                     avid_effect_typdef)
        self.f.dictionary.register_def(param_effect_id)

        # Create ParameterDef for AFX_FG_KEY_OPACITY_U
        opacity_param_id = uuid.UUID("8d56813d-847e-11d5-935a-50f857c10000")
        opacity_param_def = self.f.dictionary.lookup_typedef("Rational")
        opacity_param = self.f.create.ParameterDef(opacity_param_id,
                                                   "AFX_FG_KEY_OPACITY_U",
                                                   "",
                                                   opacity_param_def)
        self.f.dictionary.register_def(opacity_param)

        # Create VaryingValue
        opacity_u = self.f.create.VaryingValue()
        opacity_u.parameterdef = self.f.dictionary.lookup_parameterdef(
            "AFX_FG_KEY_OPACITY_U")
        vval_extrapolation_id = uuid.UUID("0e24dd54-66cd-4f1a-b0a0-670ac3a7a0b3")
        opacity_u["VVal_Extrapolation"].value = vval_extrapolation_id
        opacity_u["VVal_FieldCount"].value = 1

        interpolation_id = uuid.UUID("5b6c85a4-0ede-11d3-80a9-006008143e6f")
        interpolation_def = self.f.create.InterpolationDef(
            interpolation_id, "LinearInterp", "Linear keyframe interpolation")
        self.f.dictionary.register_def(interpolation_def)
        opacity_u["Interpolation"].value = self.f.dictionary.lookup_interperlationdef(
            "LinearInterp")

        pointlist = otio_transition.metadata["AAF"]["PointList"]

        if not pointlist:
            return None

        c1 = self.f.create.ControlPoint()
        c1["EditHint"].value = "Proportional"
        c1.value = pointlist[0]["Value"]
        c1.time = pointlist[0]["Time"]

        c2 = self.f.create.ControlPoint()
        c2["EditHint"].value = "Proportional"
        c2.value = pointlist[1]["Value"]
        c2.time = pointlist[1]["Time"]

        opacity_u["PointList"].extend([c1, c2])

        # Create OperationDefinition
        op_group_metadata = otio_transition.metadata["AAF"]["OperationGroup"]
        effect_id = op_group_metadata["Operation"]["Identification"]
        is_time_warp = op_group_metadata["Operation"]["IsTimeWarp"]
        by_pass = op_group_metadata["Operation"]["Bypass"]
        number_inputs = op_group_metadata["Operation"]["NumberInputs"]
        operation_category = op_group_metadata["Operation"]["OperationCategory"]
        data_def_name = op_group_metadata["Operation"]["DataDefinition"]["Name"]
        data_def = self.f.dictionary.lookup_datadef(str(data_def_name))
        description = op_group_metadata["Operation"]["Description"]
        op_def_name = otio_transition.metadata["AAF"][
            "OperationGroup"
        ]["Operation"]["Name"]

        op_def = self.f.create.OperationDef(uuid.UUID(effect_id), op_def_name)
        self.f.dictionary.register_def(op_def)
        op_def.media_kind = self.media_kind
        datadef = self.f.dictionary.lookup_datadef("Picture")
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
        operation_group = self.f.create.OperationGroup(op_def, length)
        operation_group["DataDefinition"].value = datadef
        operation_group["Parameters"].append(opacity_u)

        # Create Transition
        transition = self.f.create.Transition(self.media_kind, length)
        transition["OperationGroup"].value = operation_group
        transition["CutPoint"].value = otio_transition.metadata["AAF"]["CutPoint"]
        transition["DataDefinition"].value = datadef
        return transition

    def _create_timeline_mobslot(self):
        raise NotImplementedError()

    def _create_tapemob(self, otio_clip):
        edit_rate = otio_clip.duration().rate
        tapemob = self.aaf_file_transcriber._unique_tapemob(otio_clip)
        tapemob_slot = tapemob.create_empty_slot(edit_rate, self.media_kind)
        tapemob_slot.segment.length = _timecode_length(otio_clip)
        return tapemob, tapemob_slot

    def _create_filemob(self, otio_clip, tapemob, tapemob_slot):
        raise NotImplementedError()

    def _create_mastermob(self, otio_clip, filemob, filemob_slot):
        mastermob = self.aaf_file_transcriber._unique_mastermob(otio_clip)
        edit_rate = otio_clip.duration().rate
        timecode_length = _timecode_length(otio_clip)
        slot_id = otio_clip.metadata["AAF"]["SourceMobSlotID"]
        try:
            mastermob_slot = mastermob.slot_at(slot_id)
        except BaseException:
            mastermob_slot = mastermob.create_timeline_slot(
                edit_rate=edit_rate, slot_id=slot_id)
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

    def _create_filemob(self, otio_clip, tapemob, tapemob_slot):
        edit_rate = otio_clip.duration().rate
        # Create file SourceMob
        filemob = self.f.create.SourceMob()
        self.f.content.mobs.append(filemob)
        # TODO: Determine if these values are the correct, and if so,
        # maybe they should be in the AAF metadata
        filemob.descriptor = self.f.create.CDCIDescriptor()
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
            length=tapemob_slot.segment.length,
            media_kind=tapemob_slot.segment.media_kind)
        filemob_clip.mob = tapemob
        filemob_clip.slot = tapemob_slot
        filemob_clip.slot_id = tapemob_slot.slot_id
        filemob_slot.segment = filemob_clip
        return filemob, filemob_slot

    def _create_timeline_mobslot(self):
        media_kind = "picture"
        sequence = self.f.create.Sequence(media_kind=media_kind)
        edit_rate = next(self.otio_track.each_clip()).duration().rate
        timeline_mobslot = self.compositionmob.create_timeline_slot(edit_rate=edit_rate)
        timeline_mobslot.segment = sequence
        return timeline_mobslot, sequence


class AudioTrackTranscriber(TrackTranscriber):

    @property
    def media_kind(self):
        return "sound"

    def aaf_sourceclip(self, otio_clip):
        # Parameter Definition
        param_id = AUID("e4962322-2267-11d3-8a4c-0050040ef7d2")
        typedef = self.f.dictionary.lookup_typedef("Rational")
        param_def = self.f.create.ParameterDef(param_id,
                                               "Pan",
                                               "Pan",
                                               typedef)
        self.f.dictionary.register_def(param_def)
        interp_def = self.f.create.InterpolationDef(aaf2.misc.LinearInterp,
                                                    "LinearInterp",
                                                    "LinearInterp")
        self.f.dictionary.register_def(interp_def)
        # PointList
        length = otio_clip.duration().value
        c1 = self.f.create.ControlPoint()
        c1["ControlPointSource"].value = 2
        c1["Time"].value = AAFRational("0/{}".format(length))
        c1["Value"].value = 0
        c2 = self.f.create.ControlPoint()
        c2["ControlPointSource"].value = 2
        c2["Time"].value = AAFRational("{}/{}".format(length - 1, length))
        c2["Value"].value = 0
        varying_value = self.f.create.VaryingValue()
        varying_value.parameterdef = param_def
        varying_value["Interpolation"].value = interp_def
        varying_value["PointList"].extend([c1, c2])
        opgroup = self.timeline_mobslot.segment
        opgroup.parameters.append(varying_value)

        return super(AudioTrackTranscriber, self).aaf_sourceclip(otio_clip)

    def _create_filemob(self, otio_clip, tapemob, tapemob_slot):
        # Create the file source mob
        edit_rate = otio_clip.duration().rate
        filemob = self.f.create.SourceMob()
        self.f.content.mobs.append(filemob)
        descriptor = self.f.create.PCMDescriptor()
        descriptor["AverageBPS"].value = 96000
        descriptor["BlockAlign"].value = 2
        descriptor["QuantizationBits"].value = 16
        descriptor["AudioSamplingRate"].value = 48000
        descriptor["Channels"].value = 1
        descriptor["SampleRate"].value = 48000
        descriptor["Length"].value = _timecode_length(otio_clip)
        filemob.descriptor = descriptor
        filemob_slot = filemob.create_timeline_slot(edit_rate)
        filemob_clip = filemob.create_source_clip(
            slot_id=filemob_slot.slot_id,
            length=tapemob_slot.segment.length,
            media_kind=tapemob_slot.segment.media_kind)
        filemob_clip.mob = tapemob
        filemob_clip.slot = tapemob_slot
        filemob_clip.slot_id = tapemob_slot.slot_id
        filemob_slot.segment = filemob_clip
        return filemob, filemob_slot

    def _create_timeline_mobslot(self):
        edit_rate = next(self.otio_track.each_clip()).duration().rate
        total_length = sum([t.duration().value for t in self.otio_track])
        # TimelineMobSlot
        timeline_mobslot = self.compositionmob.create_sound_slot(edit_rate=edit_rate)
        # OperationDefinition
        opdef_auid = AUID("9d2ea893-0968-11d3-8a38-0050040ef7d2")
        opdef = self.f.create.OperationDef(opdef_auid, "Audio Pan")
        opdef.media_kind = self.media_kind
        opdef["NumberInputs"].value = 1
        self.f.dictionary.register_def(opdef)
        # OperationGroup
        opgroup = self.f.create.OperationGroup(opdef)
        opgroup.media_kind = self.media_kind
        opgroup.length = total_length
        timeline_mobslot.segment = opgroup
        # Sequence
        sequence = self.f.create.Sequence(media_kind=self.media_kind)
        sequence.length = total_length
        opgroup.segments.append(sequence)
        return timeline_mobslot, sequence