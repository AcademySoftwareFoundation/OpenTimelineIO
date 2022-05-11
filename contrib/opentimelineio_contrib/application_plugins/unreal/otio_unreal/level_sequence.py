# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from collections import defaultdict
from contextlib import contextmanager

import unreal
import opentimelineio as otio
from opentimelineio.opentime import RationalTime, TimeRange

from .shot_section import ShotSectionProxy
from .util import (
    MARKER_COLOR_MAP,
    get_sub_sequence_path,
    load_or_create_level_seq,
    get_nearest_marker_color,
)


class LevelSequenceProxy(object):
    """Level sequence wrapper."""

    def __init__(self, level_seq, parent=None, global_start_time=None):
        """
        Args:
            level_seq (unreal.LevelSequence): Level sequence
            parent (ShotSectionProxy, optional): Proxy for level
                sequence's parent shot section.
            global_start_time (otio.opentime.RationalTime, optional) If
                this level sequence represents an OTIO timeline's root
                "tracks" stack, provide the timeline's global start
                time as a playback and section range offset for
                updating UE from this stack and its immediate children.
        """
        self.level_seq = level_seq
        self.parent = parent
        self.global_start_time = global_start_time

    @contextmanager
    def writable(self):
        """Context manager which makes this level sequence and its shot
        sections temporarily writable. On context exit, the level
        sequence's prior read-only state will be restored, and all shot
        tracks will be locked to preserve the edit.
        """
        # Make level sequence writable
        is_read_only = self.level_seq.is_read_only()
        self.level_seq.set_read_only(False)

        # Unlock shot tracks
        shot_track = self.get_shot_track()
        if shot_track is not None:
            for section in shot_track.get_sections():
                section.set_is_locked(False)

        yield

        # Lock all shot tracks
        shot_track = self.get_shot_track()
        if shot_track is not None:
            for section in shot_track.get_sections():
                section.set_is_locked(True)

        # Restore level sequence read-only state
        self.level_seq.set_read_only(is_read_only)

    def get_shot_track(self):
        """Find and return a singleton MovieSceneCinematicShotTrack. If
        it exists, this level sequence contains sub-sequences and is
        not itself a shot.

        Returns:
            unreal.MovieSceneCinematicShotTrack: Shot track, if found,
                otherwise None.
        """
        shot_tracks = self.level_seq.find_master_tracks_by_exact_type(
            unreal.MovieSceneCinematicShotTrack
        )
        if shot_tracks:
            return shot_tracks[0]
        else:
            return None

    def get_frame_rate(self):
        """Calculate frames rate (frames per second).

        Returns:
            int: Frames per second
        """
        display_rate = self.level_seq.get_display_rate()

        return float(display_rate.numerator) / float(display_rate.denominator)

    def set_frame_rate(self, frame_rate):
        """Set frame rate (frames per second).

        Args:
            frame_rate (float): Frames per second
        """
        self.level_seq.set_display_rate(
            unreal.FrameRate(numerator=frame_rate, denominator=1)
        )

    def get_ticks_per_frame(self):
        """Calculate ticks per frame.

        Returns:
            int: Ticks per frame
        """
        frame_per_second = self.get_frame_rate()
        tick_resolution = self.level_seq.get_tick_resolution()
        ticks_per_second = float(tick_resolution.numerator) / float(
            tick_resolution.denominator
        )

        return ticks_per_second // frame_per_second

    def get_start_time(self):
        """Get start time as a ``Rationaltime`` instance.

        Returns:
            otio.opentime.RationalTime: Start time
        """
        frame_rate = self.get_frame_rate()
        start_frame = round(self.level_seq.get_playback_start_seconds() * frame_rate)

        return RationalTime(start_frame, frame_rate)

    def set_playback_range(self, start_seconds, end_seconds):
        """Set playback range with inclusive start time and exclusive
        end time. This is the sequence's in and out point for
        playback in the parent sequence.

        Args:
            start_seconds (float): Start time in seconds
            end_seconds (float): End time in seconds
        """
        self.level_seq.set_playback_start_seconds(start_seconds)
        self.level_seq.set_playback_end_seconds(end_seconds)

    def expand_work_range(self, start_seconds, end_seconds):
        """Expand work range (scrollable portion of sequence in
        Sequencer) to include provided start and end times.

        Args:
            start_seconds (float): Start time in seconds
            end_seconds (float): End time in seconds
        """
        work_start_sec = self.level_seq.get_work_range_start()
        if work_start_sec > start_seconds:
            self.level_seq.set_work_range_start(start_seconds)

        work_end_sec = self.level_seq.get_work_range_end()
        if work_end_sec < end_seconds:
            self.level_seq.set_work_range_end(end_seconds)

    def expand_view_range(self, start_seconds, end_seconds):
        """Expand view range (currently visible portion of sequence in
        Sequencer) to include provided start and end times.

        Args:
            start_seconds (float): Start time in seconds
            end_seconds (float): End time in seconds
        """
        view_start_sec = self.level_seq.get_view_range_start()
        if view_start_sec > start_seconds:
            self.level_seq.set_view_range_start(start_seconds)

        view_end_sec = self.level_seq.get_view_range_end()
        if view_end_sec < end_seconds:
            self.level_seq.set_view_range_end(end_seconds)

    def get_available_range(self):
        """Calculate OTIO item available range from this level sequence.

        Returns:
            otio.opentime.TimeRange: Available range
        """
        frame_rate = self.get_frame_rate()

        # NOTE: section.get_*_frame() methods always use floor rounding, so
        #       we round from float-seconds here ourselves.
        start_frame = round(self.level_seq.get_playback_start_seconds() * frame_rate)
        end_frame = round(self.level_seq.get_playback_end_seconds() * frame_rate)
        duration = end_frame - start_frame

        return TimeRange(
            start_time=RationalTime(start_frame, frame_rate),
            duration=RationalTime(duration, frame_rate),
        )

    def get_source_range(self):
        """Calculate OTIO item source range from this level sequence.

        Returns:
            otio.opentime.TimeRange: Source range
        """
        available_range = self.get_available_range()
        if self.parent is None:
            return available_range

        frame_rate = self.get_frame_rate()
        range_in_parent = self.parent.get_range_in_parent()

        # Factor in section start frame offset
        start_frame = (
            available_range.start_time.to_frames()
            + self.parent.get_start_frame_offset()
        )

        # Duration should match section
        duration = range_in_parent.duration.to_frames()

        return TimeRange(
            start_time=RationalTime(start_frame, frame_rate),
            duration=RationalTime(duration, frame_rate),
        )

    def update_from_item_ranges(self, item):
        """Update playback, view, and work ranges from an OTIO item.

        Args:
            item (otio.schema.Item): Item to update ranges from
        """
        source_range = item.trimmed_range()
        if (
            hasattr(item, "media_reference")
            and item.media_reference
            and item.media_reference.available_range
        ):
            available_range = item.media_reference.available_range
        else:
            available_range = source_range

        if self.global_start_time is not None:
            start_sec = (
                available_range.start_time + self.global_start_time
            ).to_seconds()
            end_sec = start_sec + available_range.duration.to_seconds()
        else:
            start_sec = available_range.start_time.to_seconds()
            end_sec = available_range.end_time_exclusive().to_seconds()

        # Frame rate
        self.set_frame_rate(available_range.start_time.rate)

        if self.parent is not None and self.global_start_time is None:
            # Calculate start frame offset from source and available range start
            # frame delta.
            self.parent.set_start_frame_offset(
                source_range.start_time.to_frames()
                - available_range.start_time.to_frames()
            )

        # Available range maps to playback range
        self.set_playback_range(start_sec, end_sec)

        # Make sure sequence's range is discoverable in Sequencer GUI
        self.expand_work_range(start_sec, end_sec)
        self.expand_view_range(start_sec, end_sec)

    def update_markers(self, parent_item):
        """Add all markers within this level sequence to a stack.

        Note:
            Markers don't currently roundtrip losslessly since OTIO
            supports them on stacks, tracks, clips, gaps, etc., and UE
            only supports them on level sequences. The result is that a
            roundtrip will push all track markers to their parent
            stack, and gap markers will be lost (since a gap does not
            map to a level sequence). Stack and clip markers are
            preserved.

        Args:
            parent_item (otio.schema.Item): Item to add markers to
        """
        parent_range = parent_item.trimmed_range()
        frame_rate = self.get_frame_rate()

        if parent_item.markers:
            parent_item.markers.clear()

        for frame_marker in self.level_seq.get_marked_frames():
            # Convert from frame number at tick resolution
            frame = frame_marker.frame_number.value // self.get_ticks_per_frame()
            marked_range = TimeRange(
                start_time=RationalTime(frame, frame_rate),
                duration=RationalTime(1, frame_rate),
            )

            # Only add visible markers
            if not (
                parent_range.contains(marked_range.start_time)
                and parent_range.contains(marked_range.end_time_inclusive())
            ):
                continue

            marker = otio.schema.Marker()
            marker.name = frame_marker.label
            marker.marked_range = marked_range
            marker.color = get_nearest_marker_color(
                frame_marker.get_editor_property("color")
            )
            parent_item.markers.append(marker)

    def update_from_markers(self, parent_item):
        """Find all markers within the given parent OTIO item (stack,
        clip, etc.) and add them as frame markers to this level
        sequence.

        Note:
            OTIO markers support a frame range, but UE frame markers
            mark a single frame. Only the first frame of each marker
            range will be marked in UE.

        Args:
            parent_item (otio.schema.Item): Item to add markers from
        """
        # Only clear current markers if the parent_item includes at least one
        if parent_item.markers:
            self.level_seq.delete_marked_frames()

        if isinstance(parent_item, otio.schema.Stack):
            # For Stacks, get markers from the stack and individual tracks
            markers = list(parent_item.markers)
            for track in parent_item:
                markers.extend(track.markers)
        else:
            markers = parent_item.markers

        for marker in markers:
            marker_frame = marker.marked_range.start_time.to_frames()
            if self.global_start_time is not None:
                marker_frame += self.global_start_time.to_frames()

            frame = unreal.FrameNumber(
                # convert to frame number at tick resolution
                marker_frame
                * self.get_ticks_per_frame()
            )
            color = MARKER_COLOR_MAP.get(
                marker.color,
                # UE default marked frame color
                MARKER_COLOR_MAP[otio.schema.MarkerColor.CYAN],
            )

            marked_frame = unreal.MovieSceneMarkedFrame()
            marked_frame.label = marker.name
            marked_frame.frame_number = frame
            marked_frame.set_editor_property("color", color)
            self.level_seq.add_marked_frame(marked_frame)

    def update_stack(self, parent_stack):
        """Recursively update an OTIO stack hierarchy from this level
        sequence. It's assumed this is first called on a root level
        sequence with a timeline's builtin ``tracks`` stack.

        Args:
            parent_stack (otio.schema.Stack): Stack to update from
                level sequence hierarchy.
        """
        parent_shot_track = self.get_shot_track()
        if parent_shot_track is None:
            return

        # Get level sequence start frame and frame rate
        parent_start_time = self.get_start_time()
        parent_start_frame = parent_start_time.to_frames()
        parent_frame_rate = parent_start_time.rate

        # Organize sections into rows
        row_sections = defaultdict(list)
        for section in parent_shot_track.get_sections():
            row_sections[section.get_row_index()].append(section)

        # Build video track for each row
        multi_track = len(row_sections) > 1

        for row_idx, sections in sorted(row_sections.items()):
            video_track = otio.schema.Track(kind=otio.schema.track.TrackKind.Video)

            # Name track if possible
            if not multi_track:
                video_track.name = str(parent_shot_track.get_display_name())
            elif hasattr(parent_shot_track, "get_track_row_display_name"):
                video_track.name = str(
                    parent_shot_track.get_track_row_display_name(row_idx)
                )

            # Video tracks are stacked in reverse in a timeline, with the lowest
            # index at the bottom.
            parent_stack.insert(0, video_track)

            prev_section_end_frame = parent_start_frame

            # Map sections to OTIO items
            for section in sections:
                section_proxy = ShotSectionProxy(section, self)
                section_name = section.get_shot_display_name()
                sub_seq = section.get_sequence()

                # Range in parent
                section_range = section_proxy.get_range_in_parent()
                section_start_frame = section_range.start_time.to_frames()
                section_end_frame = section_range.end_time_exclusive().to_frames()

                # Gap: From previous clip or parent start frame
                if section_start_frame > prev_section_end_frame:
                    gap = otio.schema.Gap(
                        source_range=TimeRange(
                            duration=RationalTime(
                                section_start_frame - prev_section_end_frame,
                                parent_frame_rate,
                            )
                        )
                    )
                    video_track.append(gap)

                # Gap: No sub-sequence reference
                if sub_seq is None:
                    gap = otio.schema.Gap(name=section_name, source_range=section_range)
                    video_track.append(gap)

                    prev_section_end_frame = section_end_frame
                    continue

                sub_seq_proxy = LevelSequenceProxy(sub_seq, section_proxy)

                # Source range
                source_range = sub_seq_proxy.get_source_range()

                # Stack: Nested tracks
                child_shot_track = sub_seq_proxy.get_shot_track()
                if child_shot_track is not None:
                    child_stack = otio.schema.Stack(
                        name=section_name, source_range=source_range
                    )
                    section_proxy.update_effects(child_stack)
                    section_proxy.update_metadata(child_stack)

                    # Recurse into child sequences
                    sub_seq_proxy.update_stack(child_stack)

                    video_track.append(child_stack)

                # Clip
                else:
                    clip = otio.schema.Clip(
                        name=section_name, source_range=source_range
                    )
                    section_proxy.update_effects(clip)
                    section_proxy.update_metadata(clip)

                    # Marked clip frames
                    sub_seq_proxy.update_markers(clip)

                    # Available range
                    media_ref = otio.schema.MissingReference(
                        available_range=sub_seq_proxy.get_available_range()
                    )
                    clip.media_reference = media_ref

                    video_track.append(clip)

                prev_section_end_frame = section_end_frame

        # Marked stack/track frames
        self.update_markers(parent_stack)

    def update_from_stack(self, parent_stack):
        """Recursively update this level sequence's hierarchy from an
        OTIO stack. It's assumed this is first called on a root level
        sequence with a timeline's builtin ``tracks`` stack.

        While a root level sequence must exist before calling this (the
        entry point for the update), sub-sequences will be created if
        they don't exist, and referenced if they exist but aren't in a
        shot track yet. New and existing sub-sequences are updated to
        match the OTIO objects from the stack.

        Args:
            parent_stack (otio.schema.Stack): Stack to update level
                sequence hierarchy from.
        """
        # Make sequence temporarily writable
        with self.writable():

            # Create shot track?
            shot_track = self.get_shot_track()

            if shot_track is None:
                shot_track = self.level_seq.add_master_track(
                    unreal.MovieSceneCinematicShotTrack
                )

            # Map of shots currently referenced in the track
            current_sections = {}
            for section in shot_track.get_sections():
                sub_seq = section.get_sequence()
                if sub_seq is not None:
                    sub_seq_path = sub_seq.get_path_name()
                    if sub_seq_path not in current_sections:
                        current_sections[sub_seq_path] = []
                    current_sections[sub_seq_path].append(section)

            # Create/update shot sections
            multi_track = len(parent_stack) > 1

            # Video tracks are stacked in reverse in a timeline, with the lowest
            # index at the bottom.
            for row_index, track in enumerate(reversed(parent_stack)):
                if track.kind != otio.schema.track.TrackKind.Video:
                    continue

                # Name track if possible
                if not multi_track:
                    shot_track.set_display_name(track.name)
                elif hasattr(shot_track, "set_track_row_display_name"):
                    shot_track.set_track_row_display_name(track.name, row_index)

                # Add or update shots from stack, removing them from the
                # current_shots map in case there are multiple instances.
                for item in track:
                    if not isinstance(item, (otio.schema.Clip, otio.schema.Stack)):
                        continue

                    # Clip or Stack: Update or create section
                    try:
                        sub_seq_path = get_sub_sequence_path(item)
                    except KeyError:
                        continue

                    if (
                        sub_seq_path in current_sections
                        and current_sections[sub_seq_path]
                    ):
                        section = current_sections[sub_seq_path].pop(0)
                        if not current_sections[sub_seq_path]:
                            del current_sections[sub_seq_path]
                        sub_seq = section.get_sequence()
                    else:
                        sub_seq = load_or_create_level_seq(sub_seq_path)

                        section = shot_track.add_section()
                        section.set_sequence(sub_seq)

                    section_proxy = ShotSectionProxy(section, self)
                    sub_seq_proxy = LevelSequenceProxy(sub_seq, section_proxy)

                    # Set track index, supporting multi-track stacks
                    section.set_row_index(row_index)

                    # NOTE: The order of these update methods is important
                    section_proxy.update_from_item_range(item)
                    section_proxy.update_from_effects(item)
                    section_proxy.update_from_metadata(item)
                    sub_seq_proxy.update_from_item_ranges(item)

                    # Stack: Recurse into child sequences
                    if isinstance(item, otio.schema.Stack):
                        sub_seq_proxy.update_from_stack(item)
                    else:
                        # Replace clip markers if present
                        sub_seq_proxy.update_from_markers(item)

            # Remove unreferenced shots (which have not been removed from
            # the current_shots map)
            for sub_seq_path, sections in current_sections.items():
                for section in sections:
                    shot_track.remove_section(section)

            # Replace stack markers if present
            self.update_from_markers(parent_stack)
