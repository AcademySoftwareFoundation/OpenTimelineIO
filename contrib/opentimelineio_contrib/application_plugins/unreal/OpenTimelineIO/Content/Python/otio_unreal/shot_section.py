# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import re

import unreal
import opentimelineio as otio
from opentimelineio.opentime import RationalTime, TimeRange

from .util import METADATA_KEY_UE, METADATA_KEY_SUB_SEQ


class ShotSectionProxy(object):
    """Shot section wrapper."""

    def __init__(self, shot_section, parent):
        """
        Args:
            shot_section (unreal.MovieSceneCinematicShotSection): Shot
                section.
            parent (LevelSequenceProxy): Proxy for section's parent
                level sequence.
        """
        self.section = shot_section
        self.parent = parent

    def get_start_frame_offset(self):
        """Calculate start frame offset for this section's
        sub-sequence.

        Returns:
            int: Offset in frames
        """
        start_ticks_offset = self.section.parameters.start_frame_offset.value
        ticks_per_frame = self.parent.get_ticks_per_frame()

        return round(float(start_ticks_offset) / float(ticks_per_frame))

    def set_start_frame_offset(self, frames):
        """Set start frame offset for this section's sub-sequence.

        Args:
            frames (int): Start frame offset
        """
        ticks_per_frame = self.parent.get_ticks_per_frame()
        self.section.parameters.start_frame_offset.value = frames * ticks_per_frame

    def get_time_scale(self):
        """Return this section's time scale, which scales the playback
        range of its sub-sequence.

        Returns:
            float: Time scalar
        """
        return self.section.parameters.time_scale

    def set_time_scale(self, time_scale):
        """Set this section's time scale, which scales the playback
        range of its sub-sequence.

        Args:
            time_scale (float): Time scale value
        """
        self.section.parameters.time_scale = time_scale

    def get_range_in_parent(self):
        """Calculate OTIO item range within its parent track.

        Returns:
            otio.opentime.TimeRange: Section range
        """
        frame_rate = self.parent.get_frame_rate()

        # NOTE: section.get_*_frame() methods always use floor rounding, so
        #       we round from float-seconds here ourselves.
        parent_start_frame = round(self.section.get_start_frame_seconds() * frame_rate)
        parent_end_frame = round(self.section.get_end_frame_seconds() * frame_rate)
        parent_duration = parent_end_frame - parent_start_frame

        return TimeRange(
            start_time=RationalTime(parent_start_frame, frame_rate),
            duration=RationalTime(parent_duration, frame_rate),
        )

    def update_from_item_range(self, item):
        """Update section range within its parent track from an OTIO
        item.

        Args:
            item (otio.schema.Item): Item to update ranges from
        """
        range_in_parent = item.range_in_parent()

        if self.parent.global_start_time is not None:
            start_frames = (
                range_in_parent.start_time + self.parent.global_start_time
            ).to_frames()
            end_frames = start_frames + range_in_parent.duration.to_frames()
        else:
            start_frames = range_in_parent.start_time.to_frames()
            end_frames = range_in_parent.end_time_exclusive().to_frames()

        self.section.set_range(start_frames, end_frames)

    def update_effects(self, item):
        """Add effects needed to represent this section to an OTIO
        item.

        Args:
            item (otio.schema.Item): Item to add effects to
        """
        time_scale = self.get_time_scale()
        if time_scale != 1.0:
            item.effects.append(otio.schema.LinearTimeWarp(time_scalar=time_scale))

    def update_from_effects(self, item):
        """Update shot section properties from OTIO item effects.

        Args:
            item (otio.schema.Item): item to get effects from
        """
        time_scale = 1.0
        for effect in item.effects:
            if isinstance(effect, otio.schema.LinearTimeWarp):
                time_scale *= effect.time_scalar
        self.set_time_scale(time_scale)

    def update_metadata(self, item):
        """Serialize shot section properties into OTIO item metadata.

        Args:
            item (otio.schema.Item): Item to set metadata on
        """
        timecode_source = self.section.get_editor_property("timecode_source")
        timecode_obj = timecode_source.get_editor_property("timecode")
        timecode_str = "{h:02d}:{m:02d}:{s:02d}{sep}{f:02d}".format(
            sep=":" if not timecode_obj.drop_frame_format else ";",
            h=timecode_obj.hours,
            m=timecode_obj.minutes,
            s=timecode_obj.seconds,
            f=timecode_obj.frames,
        )

        # NOTE: start_frame_offset and time_scale are omitted here since they
        #       will factor into a clip's source range and effects.
        metadata = {
            "timecode": timecode_str,
            "is_active": self.section.is_active(),
            "is_locked": self.section.is_locked(),
            "pre_roll_frames": self.section.get_pre_roll_frames(),
            "post_roll_frames": self.section.get_post_roll_frames(),
            "can_loop": self.section.parameters.can_loop,
            "end_frame_offset": self.section.parameters.end_frame_offset.value,
            "first_loop_start_frame_offset":
            self.section.parameters.first_loop_start_frame_offset.value,
            "hierarchical_bias": self.section.parameters.hierarchical_bias,
            METADATA_KEY_SUB_SEQ: self.section.get_sequence().get_path_name(),
            "network_mask": self.section.get_editor_property("network_mask"),
        }

        item.metadata[METADATA_KEY_UE] = metadata

    def update_from_metadata(self, item):
        """Update shot section properties from deserialized OTIO item
        metadata.

        Args:
            item (otio.schema.Item): item to get metadata from
        """
        metadata = item.metadata.get(METADATA_KEY_UE)
        if not metadata:
            return

        timecode_source = self.section.get_editor_property("timecode_source")

        if "timecode" in metadata:
            timecode_match = re.match(
                r"^"
                r"(?P<h>\d{2}):"
                r"(?P<m>\d{2}):"
                r"(?P<s>\d{2})(?P<sep>[:;])"
                r"(?P<f>\d{2})"
                r"$",
                metadata["timecode"],
            )
            if timecode_match:
                timecode_obj = unreal.Timecode(
                    hours=int(timecode_match.group("h")),
                    minutes=int(timecode_match.group("m")),
                    seconds=int(timecode_match.group("s")),
                    frames=int(timecode_match.group("f")),
                    drop_frame_format=timecode_match.group("sep") == ";",
                )
                timecode_source.set_editor_property("timecode", timecode_obj)

        # NOTE: METADATA_KEY_SUB_SEQ is omitted here since it should have
        #       already been applied by the calling code.
        # NOTE: start_frame_offset and time_scale are omitted here since they
        #       will factor into a clip's source range and effects.
        if "is_active" in metadata:
            self.section.set_is_active(metadata["is_active"])
        if "is_locked" in metadata:
            self.section.set_is_locked(metadata["is_locked"])
        if "pre_roll_frames" in metadata:
            self.section.set_pre_roll_frames(metadata["pre_roll_frames"])
        if "post_roll_frames" in metadata:
            self.section.set_post_roll_frames(metadata["post_roll_frames"])
        if "can_loop" in metadata:
            self.section.parameters.can_loop = metadata["can_loop"]
        if "end_frame_offset" in metadata:
            self.section.parameters.end_frame_offset.value = metadata[
                "end_frame_offset"
            ]
        if "first_loop_start_frame_offset" in metadata:
            self.section.parameters.first_loop_start_frame_offset.value = metadata[
                "first_loop_start_frame_offset"
            ]
        if "hierarchical_bias" in metadata:
            self.section.parameters.hierarchical_bias = metadata["hierarchical_bias"]
        if "network_mask" in metadata:
            self.section.set_editor_property("network_mask", metadata["network_mask"])
