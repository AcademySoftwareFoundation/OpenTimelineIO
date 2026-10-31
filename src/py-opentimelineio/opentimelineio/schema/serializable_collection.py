# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. import _otio
from ..core._core_utils import add_method


@add_method(_otio.SerializableCollection)
def __str__(self):
    return "SerializableCollection({}, {}, {})".format(
        str(self.name), str(list(self)), str(self.metadata)
    )


@add_method(_otio.SerializableCollection)
def __repr__(self):
    return "otio.{}(name={}, children={}, metadata={})".format(
        "schema.SerializableCollection",
        repr(self.name),
        repr(list(self)),
        repr(self.metadata),
    )
