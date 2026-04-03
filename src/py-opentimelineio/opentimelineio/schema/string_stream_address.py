# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.StringStreamAddress)
def __str__(self):
    return "StringStreamAddress({})".format(self.address)


@add_method(_otio.StringStreamAddress)
def __repr__(self):
    return "otio.schema.StringStreamAddress(address={})".format(
        repr(self.address)
    )
