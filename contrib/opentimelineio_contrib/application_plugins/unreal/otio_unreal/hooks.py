# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import opentimelineio as otio


# Plugin custom hook names
HOOK_PRE_IMPORT = "otio_ue_pre_import"
HOOK_PRE_IMPORT_ITEM = "otio_ue_pre_import_item"
HOOK_POST_EXPORT = "otio_ue_post_export"
HOOK_POST_EXPORT_ITEM = "otio_ue_post_export"


def run_pre_import_otio_hook(timeline):
    """This hook is called to modify or replace a timeline prior to
    creating or updating a level sequence hierarchy during an OTIO
    import.

    Args:
        timeline (otio.schema.Timeline): Timeline to process

    Returns:
        otio.schema.Timeline: New or updated timeline
    """
    if HOOK_PRE_IMPORT in otio.hooks.names():
        return otio.hooks.run(HOOK_PRE_IMPORT, timeline)
    else:
        return timeline


def run_pre_import_otio_item_hook(item):
    """This hook is called to modify a stack or clip prior to using it
    to update a shot section during an OTIO import.

    Args:
        item (otio.schema.Item): Stack or clip to update in place
    """
    if HOOK_PRE_IMPORT_ITEM in otio.hooks.names():
        otio.hooks.run(HOOK_PRE_IMPORT_ITEM, item)


def run_post_export_otio_hook(timeline):
    """This hook is called to modify or replace a timeline following an
    OTIO export from a level sequence hierarchy.

    Args:
        timeline (otio.schema.Timeline): Timeline to process

    Returns:
        otio.schema.Timeline: New or updated timeline
    """
    if HOOK_POST_EXPORT in otio.hooks.names():
        return otio.hooks.run(HOOK_POST_EXPORT, timeline)
    else:
        return timeline


def run_post_export_otio_clip_hook(clip):
    """This hook is called to modify a clip following it being created
    from a shot section during an OTIO export.

    Args:
        clip (otio.schema.Clip): Clip to update in place
    """
    if HOOK_POST_EXPORT_ITEM in otio.hooks.names():
        otio.hooks.run(HOOK_POST_EXPORT_ITEM, clip)
