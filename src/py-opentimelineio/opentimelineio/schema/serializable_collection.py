# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.SerializableCollection)
def __str__(self):
    return "SerializableCollection({}, {}, {})".format(
        str(self.name),
        str(list(self)),
        str(self.metadata)
    )


@add_method(_otio.SerializableCollection)
def __repr__(self):
    return (
        "otio.{}("
        "name={}, "
        "children={}, "
        "metadata={}"
        ")".format(
            "schema.SerializableCollection",
            repr(self.name),
            repr(list(self)),
            repr(self.metadata)
        )
    )
