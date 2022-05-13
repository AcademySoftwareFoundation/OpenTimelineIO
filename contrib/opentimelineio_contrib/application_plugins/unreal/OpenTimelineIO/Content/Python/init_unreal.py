# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import traceback

try:
    import otio_unreal

    __all__ = ["otio_unreal"]

except ImportError:
    traceback.print_exc()
    print("Failed to load otio_unreal! Is opentimelineio on PYTHONPATH?")
