# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unreal
import opentimelineio as otio
from opentimelineio.opentime import TimeRange


# Critical metadata keys for this adapter to work with level sequences
METADATA_KEY_UE = "unreal"
METADATA_KEY_SUB_SEQ = "sub_sequence"

# Mapping between OTIO marker colors and UE colors
MARKER_COLOR_MAP = {
    otio.schema.MarkerColor.RED: unreal.LinearColor(1.0, 0.0, 0.0, 1.0),
    otio.schema.MarkerColor.PINK: unreal.LinearColor(1.0, 0.5, 0.5, 1.0),
    otio.schema.MarkerColor.ORANGE: unreal.LinearColor(1.0, 0.5, 0.0, 1.0),
    otio.schema.MarkerColor.YELLOW: unreal.LinearColor(1.0, 1.0, 0.0, 1.0),
    otio.schema.MarkerColor.GREEN: unreal.LinearColor(0.0, 1.0, 0.0, 1.0),
    otio.schema.MarkerColor.CYAN: unreal.LinearColor(0.0, 1.0, 1.0, 1.0),
    otio.schema.MarkerColor.BLUE: unreal.LinearColor(0.0, 0.0, 1.0, 1.0),
    otio.schema.MarkerColor.PURPLE: unreal.LinearColor(0.5, 0.0, 1.0, 1.0),
    otio.schema.MarkerColor.MAGENTA: unreal.LinearColor(1.0, 0.0, 1.0, 1.0),
    otio.schema.MarkerColor.WHITE: unreal.LinearColor(1.0, 1.0, 1.0, 1.0),
    otio.schema.MarkerColor.BLACK: unreal.LinearColor(0.0, 0.0, 0.0, 1.0),
}


def get_level_seq_references(timeline, level_seq=None):
    """Evaluate timeline, returning all referenced level sequence asset
    paths and the OTIO item they reference.

    The intent of this function is to give insight to timeline syncing
    tools being implemented in Unreal Editor which utilize this plugin.

    Args:
        timeline (otio.schema.Timeline): Timeline to evaluate
        level_seq (unreal.LevelSequence, optional): Root level sequence
            to import timeline into. If unspecified, the timeline's
            "tracks" stack metadata will be checked for a sub-sequence
            path, falling back to a sequence named after the timeline
            file and located in "/Game/Sequences".

    Returns:
        list[tuple[str, otio.schema.Item]]: List of asset paths and
            OTIO items.
    """
    if level_seq is not None:
        root_level_seq_path = level_seq.get_path_name()
    else:
        root_level_seq_path = get_sub_sequence_path(timeline.tracks)

    level_seq_refs = [(root_level_seq_path, timeline)]

    for item in timeline.children_if():
        if not isinstance(item, (otio.schema.Stack, otio.schema.Clip)):
            continue

        level_seq_path = get_sub_sequence_path(item)
        if level_seq_path:
            level_seq_refs.append((level_seq_path, item))

    return level_seq_refs


def get_item_frame_ranges(item):
    """Given an OTIO item, return its frame range in parent context and
    its source frame range, as (inclusive start frame, exclusive end
    frame) int tuples.

    Args:
        item (otio.schema.Item): Item to get ranges for

    Returns:
        tuple[tuple[int, int], tuple[int, int]]: Frame range pair
    """
    global_start_time = None

    if isinstance(item, otio.schema.Timeline):
        global_start_time = item.global_start_time
        item = item.tracks

    # Source range
    source_time_range = item.trimmed_range()
    source_frame_range = (
        source_time_range.start_time.to_frames(),
        source_time_range.end_time_exclusive().to_frames(),
    )

    # Range in parent
    time_range_in_parent = None

    if global_start_time is not None:
        # Offset start time with timeline global start time for root "tracks" stack
        time_range_in_parent = TimeRange(
            start_time=source_time_range.start_time + global_start_time,
            duration=source_time_range.duration
        )
    elif item.parent():
        time_range_in_parent = item.range_in_parent()

    if time_range_in_parent is not None:
        frame_range_in_parent = (
            time_range_in_parent.start_time.to_frames(),
            time_range_in_parent.end_time_exclusive().to_frames(),
        )
    else:
        frame_range_in_parent = source_frame_range

    return frame_range_in_parent, source_frame_range


def get_sub_sequence_path(item):
    """Try to get a sub-sequence path reference from OTIO item
    metadata.

    Args:
        item (otio.schema.Item): Item to search metadata

    Returns:
        str|None: Sub-sequence path if found, or None
    """
    try:
        return str(item.metadata[METADATA_KEY_UE][METADATA_KEY_SUB_SEQ])
    except KeyError:
        return None


def set_sub_sequence_path(item, level_seq_path):
    """Set sub-sequence path reference in OTIO item metadata.

    Args:
        item (otio.schema.Item): Item to set metadata
        level_seq_path (str): Level sequence path to reference
    """
    if METADATA_KEY_UE not in item.metadata:
        item.metadata[METADATA_KEY_UE] = {}
    item.metadata[METADATA_KEY_UE][METADATA_KEY_SUB_SEQ] = level_seq_path


def get_root_level_seq_path(
    filepath, timeline, destination_path=None, destination_name=None
):
    """Determine the root level sequence path to sync. This is the
    parent to the level sequence hierarchy and maps to the OTIO
    timeline's root "tracks" stack.

    Args:
        See ``import_otio`` documentation

    Returns:
        str: Level sequence asset path
    """
    level_seq_path = get_sub_sequence_path(timeline.tracks)

    if not level_seq_path or not str(level_seq_path).startswith("/Game/"):
        name = destination_name or unreal.Paths.get_base_filename(filepath)
        if destination_path is not None and destination_path.startswith("/Game/"):
            level_seq_path = destination_path.replace("\\", "/").rstrip(
                "/"
            ) + "/{name}.{name}".format(name=name)
        else:
            # Fallback import location
            level_seq_path = "/Game/Sequences/{name}.{name}".format(name=name)

    return level_seq_path


def load_or_create_level_seq(level_seq_path):
    """Load level sequence, creating it first if it doesn't exist.

    Args:
        level_seq_path (str): Level sequence asset path

    Returns:
        unreal.LevelSequence: Loaded level sequence
    """
    level_seq_data = unreal.EditorAssetLibrary.find_asset_data(level_seq_path)
    if level_seq_data.is_valid():
        level_seq = level_seq_data.get_asset()
    else:
        package_path, asset_name = level_seq_path.rsplit("/", 1)
        asset_name = asset_name.split(".", 1)[0]

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        level_seq = asset_tools.create_asset(
            asset_name,
            package_path,
            unreal.LevelSequence,
            unreal.LevelSequenceFactoryNew(),
        )

    return level_seq


def get_nearest_marker_color(target_color):
    """Given a linear Unreal target color, find the nearest OTIO marker
    color constant.

    Args:
        target_color (unreal.LinearColor): Floating-point linear color

    Returns:
        otio.schema.MarkerColor: Color constant
    """
    target_h, target_s = target_color.rgb_into_hsv_components()[:2]

    # Desaturated colors map to black or white
    if target_s < 0.25:
        if target_color.get_luminance() < 0.18:
            return otio.schema.MarkerColor.BLACK
        else:
            return otio.schema.MarkerColor.WHITE

    # Find saturated constant with the nearest hue
    else:
        # UE default marked frame color
        nearest_h = 180
        nearest_marker_color = otio.schema.MarkerColor.CYAN

        for marker_color, candidate_color in MARKER_COLOR_MAP.items():
            if marker_color in (
                otio.schema.MarkerColor.BLACK,
                otio.schema.MarkerColor.WHITE,
            ):
                continue
            h = candidate_color.rgb_into_hsv_components()[0]
            if h in (0.0, 360.0):
                # Wrap red hue comparison
                hues = [0.0, 360.0]
            else:
                hues = [h]
            for h in hues:
                if abs(h - target_h) < abs(nearest_h - target_h):
                    nearest_h = h
                    nearest_marker_color = marker_color

        # Red and pink have the same hue, so choose the nearest saturation
        if nearest_marker_color == otio.schema.MarkerColor.RED and target_s < 0.75:
            nearest_marker_color = otio.schema.MarkerColor.PINK

        return nearest_marker_color
