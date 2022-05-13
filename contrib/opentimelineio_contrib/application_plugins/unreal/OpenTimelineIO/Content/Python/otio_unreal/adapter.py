# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unreal
import opentimelineio as otio

from .hooks import (
    run_pre_import_otio_hook,
    run_pre_import_otio_item_hook,
    run_post_export_otio_hook,
    run_post_export_otio_clip_hook,
)
from .level_sequence import LevelSequenceProxy
from .util import (
    set_sub_sequence_path,
    get_root_level_seq_path,
    load_or_create_level_seq,
)


def import_otio(
    filepath,
    level_seq=None,
    destination_path=None,
    destination_name=None,
    dry_run=False,
    undo_action_text="Import OTIO Timeline",
):
    """Import OTIO-supported timeline file into sequencer, creating or
    updating a level sequence hierarchy.

    Args:
        filepath (str): Path to an OTIO-supported timeline file
        level_seq (unreal.LevelSequence, optional): Root level sequence
            to import timeline into. If unspecified, the timeline's
            "tracks" stack metadata will be checked for a sub-sequence
            path, falling back to a sequence named after the timeline
            file and located in "/Game/Sequences".
        destination_path (str, optional): Asset directory path in which
            to save the imported level sequence. This parameter has no
            effect if the imported timeline's "tracks" stack metadata
            defines a sub-sequence path.
        destination_name (str, optional): Rename the imported level
            sequence. If undefined, the sequence name will match the
            imported timeline filename. This parameter has no effect if
            the imported timeline's "tracks" stack metadata defines a
            sub-sequence path.
        dry_run (bool, optional): Set to True to process the timeline
            to be imported without making changes in Unreal Editor.
        undo_action_text (str): Text to describe import action for UE
            undo menu.

    Returns:
        tuple[unreal.LevelSequence, otio.schema.Timeline]: Root level
            sequence and processed timeline.
    """
    timeline = otio.adapters.read_from_file(filepath)

    # Implementation-defined timeline update to inject unreal metadata for
    # mapping stacks and clips to sub-sequences.
    timeline = run_pre_import_otio_hook(timeline)

    # Implementation-defined item update to inject unreal metadata that maps
    # items (stacks and clips) to sub-sequences.
    run_pre_import_otio_item_hook(timeline.tracks)

    for item in timeline.children_if():
        if isinstance(item, (otio.schema.Stack, otio.schema.Clip)):
            run_pre_import_otio_item_hook(item)

    # Use transaction to allow single undo action to revert update
    if not dry_run:
        with unreal.ScopedEditorTransaction(undo_action_text):

            # Load or create level sequence to update
            if level_seq is None:
                level_seq_path = get_root_level_seq_path(
                    filepath,
                    timeline,
                    destination_path=destination_path,
                    destination_name=destination_name,
                )
                level_seq = load_or_create_level_seq(level_seq_path)

            # Account for global start time when updating the root level sequence
            level_seq_proxy = LevelSequenceProxy(
                level_seq, global_start_time=timeline.global_start_time
            )

            # Ensure added sections are visible when opened in Sequencer
            level_seq_proxy.update_from_item_ranges(timeline.tracks)

            # Update sequence from timeline
            level_seq_proxy.update_from_stack(timeline.tracks)

        # Update Sequencer UI
        level_seq_lib = unreal.LevelSequenceEditorBlueprintLibrary
        level_seq_lib.refresh_current_level_sequence()

    return level_seq, timeline


def export_otio(filepath, level_seq, dry_run=False):
    """Export OTIO-supported timeline file from a level sequence
    hierarchy.

    Args:
        filepath (str): Path to an OTIO-supported timeline file
        level_seq (unreal.LevelSequence): Level sequence to export
            timeline from.
        dry_run (bool, optional): Set to True to process the timeline
            to be exported without writing it to disk.

    Returns:
        otio.schema.Timeline: Processed timeline
    """
    level_seq_proxy = LevelSequenceProxy(level_seq)

    timeline = otio.schema.Timeline()
    timeline.global_start_time = level_seq_proxy.get_start_time()
    set_sub_sequence_path(timeline.tracks, level_seq.get_path_name())

    # Update timeline from sequence
    level_seq_proxy.update_stack(timeline.tracks)

    # Implementation-defined timeline update to inject media references that
    # map unreal metadata to rendered outputs.
    timeline = run_post_export_otio_hook(timeline)

    for clip in timeline.clip_if():
        # Implementation-defined clip update to inject a media reference
        # that maps unreal metadata to a rendered output.
        run_post_export_otio_clip_hook(clip)

    if not dry_run:
        otio.adapters.write_to_file(timeline, filepath)

    return timeline
