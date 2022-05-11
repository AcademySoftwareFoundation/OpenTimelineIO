# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import os

# Public import/export interface access
from .adapter import import_otio, export_otio
from .hooks import (
    HOOK_PRE_IMPORT,
    HOOK_PRE_IMPORT_ITEM,
    HOOK_POST_EXPORT,
    HOOK_POST_EXPORT_ITEM,
)
from .level_sequence import LevelSequenceProxy
from .shot_section import ShotSectionProxy
from .util import (
    METADATA_KEY_UE,
    METADATA_KEY_SUB_SEQ,
    MARKER_COLOR_MAP,
    get_level_seq_references,
    get_item_frame_ranges,
    get_sub_sequence_path,
    set_sub_sequence_path,
    get_root_level_seq_path,
    load_or_create_level_seq,
)

if os.getenv("OTIO_UE_REGISTER_UCLASSES", "1") == "1":
    # Register import/export uclasses
    from . import uclasses
