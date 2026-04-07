# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.IndexStreamAddress)
def __str__(self):
    return "IndexStreamAddress({})".format(self.index)


@add_method(_otio.IndexStreamAddress)
def __repr__(self):
    return "otio.schema.IndexStreamAddress(index={})".format(repr(self.index))
