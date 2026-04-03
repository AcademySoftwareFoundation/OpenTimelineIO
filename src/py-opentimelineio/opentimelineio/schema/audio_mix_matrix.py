# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.AudioMixMatrix)
def __str__(self):
    return "AudioMixMatrix({})".format(str(self.name))


@add_method(_otio.AudioMixMatrix)
def __repr__(self):
    return "otio.schema.AudioMixMatrix(name={})".format(repr(self.name))
