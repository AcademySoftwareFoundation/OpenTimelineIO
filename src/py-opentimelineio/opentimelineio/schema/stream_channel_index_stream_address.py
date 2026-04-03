# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.StreamChannelIndexStreamAddress)
def __str__(self):
    return "StreamChannelIndexStreamAddress({}, {})".format(
        self.stream_index, self.channel_index
    )


@add_method(_otio.StreamChannelIndexStreamAddress)
def __repr__(self):
    return (
        "otio.schema.StreamChannelIndexStreamAddress("
        "stream_index={}, channel_index={})".format(
            repr(self.stream_index), repr(self.channel_index)
        )
    )
