# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""AAF Adapter Transcriber

Specifies how to transcribe an OpenTimelineIO file into an AAF file.
"""

import aaf2
import abc
import uuid
import opentimelineio as otio
import os
import copy
import re


AAF_PARAMETERDEF_PAN = aaf2.auid.AUID("e4962322-2267-11d3-8a4c-0050040ef7d2")
AAF_OPERATIONDEF_MONOAUDIOPAN = aaf2.auid.AUID("9d2ea893-0968-11d3-8a38-0050040ef7d2")
AAF_PARAMETERDEF_AVIDPARAMETERBYTEORDER = uuid.UUID(
    "c0038672-a8cf-11d3-a05b-006094eb75cb")
AAF_PARAMETERDEF_AVIDEFFECTID = uuid.UUID(
    "93994bd6-a81d-11d3-a05b-006094eb75cb")
AAF_PARAMETERDEF_AFX_FG_KEY_OPACITY_U = uuid.UUID(
    "8d56813d-847e-11d5-935a-50f857c10000")
AAF_PARAMETERDEF_LEVEL = uuid.UUID("e4962320-2267-11d3-8a4c-0050040ef7d2")
AAF_VVAL_EXTRAPOLATION_ID = uuid.UUID("0e24dd54-66cd-4f1a-b0a0-670ac3a7a0b3")
AAF_OPERATIONDEF_SUBMASTER = uuid.UUID("f1db0f3d-8d64-11d3-80df-006008143e6f")


def _is_considered_gap(thing):
    """Returns whether or not thiing can be considered gap.

    TODO: turns generators w/ kind "Slug" inito gap.  Should probably generate
          opaque black instead.
    """
    if isinstance(thing, otio.schema.Gap):
        return True

    if (
            isinstance(thing, otio.schema.Clip)
            and isinstance(
                thing.media_reference,
                otio.schema.GeneratorReference)
    ):
        if thing.media_reference.generator_kind in ("Slug",):
            return True
        else:
            raise otio.exceptions.NotSupportedError(
                "AAF adapter does not support generator references of kind"
                " '{}'".format(thing.media_reference.generator_kind)
            )

    return False


class AAFAdapterError(otio.exceptions.OTIOError):
    pass


class AAFValidationError(AAFAdapterError):
    pass


class AAFFileTranscriber:
    """
    AAFFileTranscriber

    AAFFileTranscriber manages the file-level knowledge during a conversion from
    otio to aaf. This includes keeping track of unique tapemobs and mastermobs.
    """

    def __init__(self, input_otio, aaf_file, **kwargs):
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
        self._clip_mob_ids_map = _gather_clip_mob_ids(input_otio, **kwargs)

    def _unique_mastermob(self, otio_clip):
        """Get a unique mastermob, identified by clip metadata mob id."""
        mob_id = self._clip_mob_ids_map.get(otio_clip)
        mastermob = self._unique_mastermobs.get(mob_id)
        if not mastermob:
            mastermob = self.aaf_file.create.MasterMob()
            mastermob.name = otio_clip.name
            mastermob.mob_id = aaf2.mobid.MobID(mob_id)
            self.aaf_file.content.mobs.append(mastermob)
            self._unique_mastermobs[mob_id] = mastermob
        return mastermob

    def _unique_tapemob(self, otio_clip):
        """Get a unique tapemob, identified by clip metadata mob id."""
        mob_id = self._clip_mob_ids_map.get(otio_clip)
        tapemob = self._unique_tapemobs.get(mob_id)
        if not tapemob:
            tapemob = self.aaf_file.create.SourceMob()
            tapemob.name = otio_clip.name
            tapemob.descriptor = self.aaf_file.create.ImportDescriptor()
            # If the edit_rate is not an integer, we need
            # to use drop frame with a nominal integer fps.
            edit_rate = otio_clip.visible_range().duration.rate
            timecode_fps = round(edit_rate)
            tape_timecode_slot = tapemob.create_timecode_slot(
                edit_rate=edit_rate,
                timecode_fps=timecode_fps,
                drop_frame=(edit_rate != timecode_fps)
            )
            timecode_start = int(
                otio_clip.media_reference.available_range.start_time.value
            )
            timecode_length = int(
                otio_clip.media_reference.available_range.duration.value
            )

            tape_timecode_slot.segment.start = int(timecode_start)
            tape_timecode_slot.segment.length = int(timecode_length)
            self.aaf_file.content.mobs.append(tapemob)
            self._unique_tapemobs[mob_id] = tapemob
        return tapemob

    def track_transcriber(self, otio_track):
        """Return an appropriate _TrackTranscriber given an otio track."""
        if otio_track.kind == otio.schema.TrackKind.Video:
            transcriber = VideoTrackTranscriber(self, otio_track)
        elif otio_track.kind == otio.schema.TrackKind.Audio:
            transcriber = AudioTrackTranscriber(self, otio_track)
        else:
            raise otio.exceptions.NotSupportedError(
                f"Unsupported track kind: {otio_track.kind}")
        return transcriber


def validate_metadata(timeline):
    """Print a check of necessary metadata requirements for an otio timeline."""

    all_checks = [__check(timeline, "duration().rate")]
    edit_rate = __check(timeline, "duration().rate").value

    for child in timeline.each_child():
        checks = []
        if _is_considered_gap(child):
            checks = [
                __check(child, "duration().rate").equals(edit_rate)
            ]
        if isinstance(child, otio.schema.Clip):
            checks = [
                __check(child, "duration().rate").equals(edit_rate),
                __check(child, "media_reference.available_range.duration.rate"
                        ).equals(edit_rate),
                __check(child, "media_reference.available_range.start_time.rate"
                        ).equals(edit_rate)
            ]
        if isinstance(child, otio.schema.Transition):
            checks = [
                __check(child, "duration().rate").equals(edit_rate),
                __check(child, "metadata['AAF']['PointList']"),
                __check(child, "metadata['AAF']['OperationGroup']['Operation']"
                        "['DataDefinition']['Name']"),
                __check(child, "metadata['AAF']['OperationGroup']['Operation']"
                        "['Description']"),
                __check(child, "metadata['AAF']['OperationGroup']['Operation']"
                        "['Name']"),
                __check(child, "metadata['AAF']['CutPoint']")
            ]
        all_checks.extend(checks)

    if any(check.errors for check in all_checks):
        raise AAFValidationError("\n" + "\n".join(
            sum([check.errors for check in all_checks], [])))


def _gather_clip_mob_ids(input_otio,
                         prefer_file_mob_id=False,
                         use_empty_mob_ids=False,
                         **kwargs):
    """
    Create dictionary of otio clips with their corresponding mob ids.
    """

    def _from_clip_metadata(clip):
        """Get the MobID from the clip.metadata."""
        return clip.metadata.get("AAF", {}).get("SourceID")

    def _from_media_reference_metadata(clip):
        """Get the MobID from the media_reference.metadata."""
        return (clip.media_reference.metadata.get("AAF", {}).get("MobID") or
                clip.media_reference.metadata.get("AAF", {}).get("SourceID"))

    def _from_aaf_file(clip):
        """ Get the MobID from the AAF file itself."""
        mob_id = None
        target_url = clip.media_reference.target_url
        if os.path.isfile(target_url) and target_url.endswith("aaf"):
            with aaf2.open(clip.media_reference.target_url) as aaf_file:
                mastermobs = list(aaf_file.content.mastermobs())
                if len(mastermobs) == 1:
                    mob_id = mastermobs[0].mob_id
        return mob_id

    def _generate_empty_mobid(clip):
        """Generate a meaningless MobID."""
        return aaf2.mobid.MobID.new()

    strategies = [
        _from_clip_metadata,
        _from_media_reference_metadata,
        _from_aaf_file
    ]

    if prefer_file_mob_id:
        strategies.remove(_from_aaf_file)
        strategies.insert(0, _from_aaf_file)

    if use_empty_mob_ids:
        strategies.append(_generate_empty_mobid)

    clip_mob_ids = {}

    for otio_clip in input_otio.each_clip():
        if _is_considered_gap(otio_clip):
            continue
        for strategy in strategies:
            mob_id = strategy(otio_clip)
            if mob_id:
                clip_mob_ids[otio_clip] = mob_id
                break
        else:
            raise AAFAdapterError(f"Cannot find mob ID for clip {otio_clip}")

    return clip_mob_ids


def _stackify_nested_groups(timeline):
    """
    Ensure that all nesting in a given timeline is in a stack container.
    This conforms with how AAF thinks about nesting, there needs
    to be an outer container, even if it's just one object.
    """
    copied = copy.deepcopy(timeline)
    for track in copied.tracks:
        for i, child in enumerate(track.each_child()):
            is_nested = isinstance(child, otio.schema.Track)
            is_parent_in_stack = isinstance(child.parent(), otio.schema.Stack)
            if is_nested and not is_parent_in_stack:
                stack = otio.schema.Stack()
                track.remove(child)
                stack.append(child)
                track.insert(i, stack)
    return copied


class _TrackTranscriber:
    """
    _TrackTranscriber is the base class for the conversion of a given otio track.

    _TrackTranscriber is not meant to be used by itself. It provides the common
    functionality to inherit from. We need an abstract base class because Audio and
    Video are handled differently.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, root_file_transcriber, otio_track):
        """
        _TrackTranscriber

        Args:
            root_file_transcriber: the corresponding 'parent' AAFFileTranscriber object
            otio_track: the given otio_track to convert
        """
        self.root_file_transcriber = root_file_transcriber
        self.compositionmob = root_file_transcriber.compositionmob
        self.aaf_file = root_file_transcriber.aaf_file
        self.otio_track = otio_track
        self.edit_rate = next(self.otio_track.each_child()).duration().rate
        self.timeline_mobslot, self.sequence = self._create_timeline_mobslot()
        self.timeline_mobslot.name = self.otio_track.name

    def transcribe(self, otio_child):
        """Transcribe otio child to corresponding AAF object"""
        if _is_considered_gap(otio_child):
            filler = self.aaf_filler(otio_child)
            return filler
        elif isinstance(otio_child, otio.schema.Transition):
            transition = self.aaf_transition(otio_child)
            return transition
        elif isinstance(otio_child, otio.schema.Clip):
            source_clip = self.aaf_sourceclip(otio_child)
            return source_clip
        elif isinstance(otio_child, otio.schema.Track):
            sequence = self.aaf_sequence(otio_child)
            return sequence
        elif isinstance(otio_child, otio.schema.Stack):
            operation_group = self.aaf_operation_group(otio_child)
            return operation_group
        else:
            raise otio.exceptions.NotSupportedError(
                f"Unsupported otio child type: {type(otio_child)}")

    @property
    @abc.abstractmethod
    def media_kind(self):
        """Return the string for what kind of track this is."""
        pass

    @property
    @abc.abstractmethod
    def _master_mob_slot_id(self):
        """
        Return the MasterMob Slot ID for the corresponding track media kind
        """
        # MasterMob's and MasterMob slots have to be unique. We handle unique
        # MasterMob's with _unique_mastermob(). We also need to protect against
        # duplicate MasterMob slots. As of now, we mandate all picture clips to
        # be created in MasterMob slot 1 and all sound clips to be created in
        # MasterMob slot 2. While this is a little inadequate, it works for now
        pass

    @abc.abstractmethod
    def _create_timeline_mobslot(self):
        """
        Return a timeline_mobslot and sequence for this track.

        In AAF, a TimelineMobSlot is a container for the Sequence. A Sequence is
        analogous to an otio track.

        Returns:
            Returns a tuple of (TimelineMobSlot, Sequence)
        """
        pass

    @abc.abstractmethod
    def default_descriptor(self, otio_clip):
        pass

    @abc.abstractmethod
    def _transition_parameters(self):
        pass

    def aaf_filler(self, otio_gap):
        """Convert an otio Gap into an aaf Filler"""
        length = int(otio_gap.visible_range().duration.value)
        filler = self.aaf_file.create.Filler(self.media_kind, length)
        return filler

    def aaf_sourceclip(self, otio_clip):
        """Convert an otio Clip into an aaf SourceClip"""
        tapemob, tapemob_slot = self._create_tapemob(otio_clip)
        filemob, filemob_slot = self._create_filemob(otio_clip, tapemob, tapemob_slot)
        mastermob, mastermob_slot = self._create_mastermob(otio_clip,
                                                           filemob,
                                                           filemob_slot)

        # We need both `start_time` and `duration`
        # Here `start` is the offset between `first` and `in` values.

        offset = (otio_clip.visible_range().start_time -
                  otio_clip.available_range().start_time)
        start = offset.value
        length = otio_clip.visible_range().duration.value

        compmob_clip = self.compositionmob.create_source_clip(
            slot_id=self.timeline_mobslot.slot_id,
            # XXX: Python3 requires these to be passed as explicit ints
            start=int(start),
            length=int(length),
            media_kind=self.media_kind
        )
        compmob_clip.mob = mastermob
        compmob_clip.slot = mastermob_slot
        compmob_clip.slot_id = mastermob_slot.slot_id
        return compmob_clip

    def aaf_transition(self, otio_transition):
        """Convert an otio Transition into an aaf Transition"""
        if (otio_transition.transition_type !=
                otio.schema.TransitionTypes.SMPTE_Dissolve):
            print(
                "Unsupported transition type: {}".format(
                    otio_transition.transition_type))
            return None

        transition_params, varying_value = self._transition_parameters()

        interpolation_def = self.aaf_file.create.InterpolationDef(
            aaf2.misc.LinearInterp, "LinearInterp", "Linear keyframe interpolation")
        self.aaf_file.dictionary.register_def(interpolation_def)
        varying_value["Interpolation"].value = (
            self.aaf_file.dictionary.lookup_interperlationdef("LinearInterp"))

        pointlist = otio_transition.metadata["AAF"]["PointList"]

        c1 = self.aaf_file.create.ControlPoint()
        c1["EditHint"].value = "Proportional"
        c1.value = pointlist[0]["Value"]
        c1.time = pointlist[0]["Time"]

        c2 = self.aaf_file.create.ControlPoint()
        c2["EditHint"].value = "Proportional"
        c2.value = pointlist[1]["Value"]
        c2.time = pointlist[1]["Time"]

        varying_value["PointList"].extend([c1, c2])

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

        # Create OperationDefinition
        op_def = self.aaf_file.create.OperationDef(uuid.UUID(effect_id), op_def_name)
        self.aaf_file.dictionary.register_def(op_def)
        op_def.media_kind = self.media_kind
        datadef = self.aaf_file.dictionary.lookup_datadef(self.media_kind)
        op_def["IsTimeWarp"].value = is_time_warp
        op_def["Bypass"].value = by_pass
        op_def["NumberInputs"].value = number_inputs
        op_def["OperationCategory"].value = str(operation_category)
        op_def["ParametersDefined"].extend(transition_params)
        op_def["DataDefinition"].value = data_def
        op_def["Description"].value = str(description)

        # Create OperationGroup
        length = int(otio_transition.duration().value)
        operation_group = self.aaf_file.create.OperationGroup(op_def, length)
        operation_group["DataDefinition"].value = datadef
        operation_group["Parameters"].append(varying_value)

        # Create Transition
        transition = self.aaf_file.create.Transition(self.media_kind, length)
        transition["OperationGroup"].value = operation_group
        transition["CutPoint"].value = otio_transition.metadata["AAF"]["CutPoint"]
        transition["DataDefinition"].value = datadef
        return transition

    def aaf_sequence(self, otio_track):
        """Convert an otio Track into an aaf Sequence"""
        sequence = self.aaf_file.create.Sequence(media_kind=self.media_kind)
        length = 0
        for nested_otio_child in otio_track:
            result = self.transcribe(nested_otio_child)
            length += result.length
            sequence.components.append(result)
        sequence.length = length
        return sequence

    def aaf_operation_group(self, otio_stack):
        """
        Create and return an OperationGroup which will contain other AAF objects
        to support OTIO nesting
        """
        # Create OperationDefinition
        op_def = self.aaf_file.create.OperationDef(AAF_OPERATIONDEF_SUBMASTER,
                                                   "Submaster")
        self.aaf_file.dictionary.register_def(op_def)
        op_def.media_kind = self.media_kind
        datadef = self.aaf_file.dictionary.lookup_datadef(self.media_kind)

        # These values are necessary for pyaaf2 OperationDefinitions
        op_def["IsTimeWarp"].value = False
        op_def["Bypass"].value = 0
        op_def["NumberInputs"].value = -1
        op_def["OperationCategory"].value = "OperationCategory_Effect"
        op_def["DataDefinition"].value = datadef

        # Create OperationGroup
        operation_group = self.aaf_file.create.OperationGroup(op_def)
        operation_group.media_kind = self.media_kind
        operation_group["DataDefinition"].value = datadef

        length = 0
        for nested_otio_child in otio_stack:
            result = self.transcribe(nested_otio_child)
            length += result.length
            operation_group.segments.append(result)
        operation_group.length = length
        return operation_group

    def _create_tapemob(self, otio_clip):
        """
        Return a physical sourcemob for an otio Clip based on the MobID.

        Returns:
            Returns a tuple of (TapeMob, TapeMobSlot)
        """
        tapemob = self.root_file_transcriber._unique_tapemob(otio_clip)
        tapemob_slot = tapemob.create_empty_slot(self.edit_rate, self.media_kind)
        tapemob_slot.segment.length = int(
            otio_clip.media_reference.available_range.duration.value)
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
        timecode_length = int(otio_clip.media_reference.available_range.duration.value)

        try:
            mastermob_slot = mastermob.slot_at(self._master_mob_slot_id)
        except IndexError:
            mastermob_slot = (
                mastermob.create_timeline_slot(edit_rate=self.edit_rate,
                                               slot_id=self._master_mob_slot_id))
        mastermob_clip = mastermob.create_source_clip(
            slot_id=mastermob_slot.slot_id,
            length=timecode_length,
            media_kind=self.media_kind)
        mastermob_clip.mob = filemob
        mastermob_clip.slot = filemob_slot
        mastermob_clip.slot_id = filemob_slot.slot_id
        mastermob_slot.segment = mastermob_clip
        return mastermob, mastermob_slot


class VideoTrackTranscriber(_TrackTranscriber):
    """Video track kind specialization of TrackTranscriber."""

    @property
    def media_kind(self):
        return "picture"

    @property
    def _master_mob_slot_id(self):
        return 1

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

    def _transition_parameters(self):
        """
        Return video transition parameters
        """
        # Create ParameterDef for AvidParameterByteOrder
        byteorder_typedef = self.aaf_file.dictionary.lookup_typedef("aafUInt16")
        param_byteorder = self.aaf_file.create.ParameterDef(
            AAF_PARAMETERDEF_AVIDPARAMETERBYTEORDER,
            "AvidParameterByteOrder",
            "",
            byteorder_typedef)
        self.aaf_file.dictionary.register_def(param_byteorder)

        # Create ParameterDef for AvidEffectID
        avid_effect_typdef = self.aaf_file.dictionary.lookup_typedef("AvidBagOfBits")
        param_effect_id = self.aaf_file.create.ParameterDef(
            AAF_PARAMETERDEF_AVIDEFFECTID,
            "AvidEffectID",
            "",
            avid_effect_typdef)
        self.aaf_file.dictionary.register_def(param_effect_id)

        # Create ParameterDef for AFX_FG_KEY_OPACITY_U
        opacity_param_def = self.aaf_file.dictionary.lookup_typedef("Rational")
        opacity_param = self.aaf_file.create.ParameterDef(
            AAF_PARAMETERDEF_AFX_FG_KEY_OPACITY_U,
            "AFX_FG_KEY_OPACITY_U",
            "",
            opacity_param_def)
        self.aaf_file.dictionary.register_def(opacity_param)

        # Create VaryingValue
        opacity_u = self.aaf_file.create.VaryingValue()
        opacity_u.parameterdef = self.aaf_file.dictionary.lookup_parameterdef(
            "AFX_FG_KEY_OPACITY_U")
        opacity_u["VVal_Extrapolation"].value = AAF_VVAL_EXTRAPOLATION_ID
        opacity_u["VVal_FieldCount"].value = 1

        return [param_byteorder, param_effect_id], opacity_u


class AudioTrackTranscriber(_TrackTranscriber):
    """Audio track kind specialization of TrackTranscriber."""

    @property
    def media_kind(self):
        return "sound"

    @property
    def _master_mob_slot_id(self):
        return 2

    def aaf_sourceclip(self, otio_clip):
        # Parameter Definition
        typedef = self.aaf_file.dictionary.lookup_typedef("Rational")
        param_def = self.aaf_file.create.ParameterDef(AAF_PARAMETERDEF_PAN,
                                                      "Pan",
                                                      "Pan",
                                                      typedef)
        self.aaf_file.dictionary.register_def(param_def)
        interp_def = self.aaf_file.create.InterpolationDef(aaf2.misc.LinearInterp,
                                                           "LinearInterp",
                                                           "LinearInterp")
        self.aaf_file.dictionary.register_def(interp_def)
        # PointList
        length = int(otio_clip.duration().value)
        c1 = self.aaf_file.create.ControlPoint()
        c1["ControlPointSource"].value = 2
        c1["Time"].value = aaf2.rational.AAFRational(f"0/{length}")
        c1["Value"].value = 0
        c2 = self.aaf_file.create.ControlPoint()
        c2["ControlPointSource"].value = 2
        c2["Time"].value = aaf2.rational.AAFRational(f"{length - 1}/{length}")
        c2["Value"].value = 0
        varying_value = self.aaf_file.create.VaryingValue()
        varying_value.parameterdef = param_def
        varying_value["Interpolation"].value = interp_def
        varying_value["PointList"].extend([c1, c2])
        opgroup = self.timeline_mobslot.segment
        opgroup.parameters.append(varying_value)

        return super().aaf_sourceclip(otio_clip)

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
        opdef = self.aaf_file.create.OperationDef(AAF_OPERATIONDEF_MONOAUDIOPAN,
                                                  "Audio Pan")
        opdef.media_kind = self.media_kind
        opdef["NumberInputs"].value = 1
        self.aaf_file.dictionary.register_def(opdef)
        # OperationGroup
        total_length = int(sum([t.duration().value for t in self.otio_track]))
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
        descriptor["Length"].value = int(
            otio_clip.media_reference.available_range.duration.value
        )
        return descriptor

    def _transition_parameters(self):
        """
        Return audio transition parameters
        """
        # Create ParameterDef for ParameterDef_Level
        def_level_typedef = self.aaf_file.dictionary.lookup_typedef("Rational")
        param_def_level = self.aaf_file.create.ParameterDef(AAF_PARAMETERDEF_LEVEL,
                                                            "ParameterDef_Level",
                                                            "",
                                                            def_level_typedef)
        self.aaf_file.dictionary.register_def(param_def_level)

        # Create VaryingValue
        level = self.aaf_file.create.VaryingValue()
        level.parameterdef = (
            self.aaf_file.dictionary.lookup_parameterdef("ParameterDef_Level"))

        return [param_def_level], level


class __check:
    """
    __check is a private helper class that safely gets values given to check
    for existence and equality
    """

    def __init__(self, obj, tokenpath):
        self.orig = obj
        self.value = obj
        self.errors = []
        self.tokenpath = tokenpath
        try:
            for token in re.split(r"[\.\[]", tokenpath):
                if token.endswith("()"):
                    self.value = getattr(self.value, token.replace("()", ""))()
                elif "]" in token:
                    self.value = self.value[token.strip("[]'\"")]
                else:
                    self.value = getattr(self.value, token)
        except Exception as e:
            self.value = None
            self.errors.append("{}{} {}.{} does not exist, {}".format(
                self.orig.name if hasattr(self.orig, "name") else "",
                type(self.orig),
                type(self.orig).__name__,
                self.tokenpath, e))

    def equals(self, val):
        """Check if the retrieved value is equal to a given value."""
        if self.value is not None and self.value != val:
            self.errors.append(
                "{}{} {}.{} not equal to {} (expected) != {} (actual)".format(
                    self.orig.name if hasattr(self.orig, "name") else "",
                    type(self.orig),
                    type(self.orig).__name__, self.tokenpath, val, self.value))
        return self
