# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.StreamAddress)
def __str__(self):
    return "StreamAddress()"


@add_method(_otio.StreamAddress)
def __repr__(self):
    return "otio.schema.StreamAddress()"
