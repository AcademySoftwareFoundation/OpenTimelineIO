# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Clip)
def __str__(self):
    return 'Clip("{}", {}, {}, {})'.format(
        self.name,
        self.media_reference,
        self.source_range,
        self.metadata
    )


@add_method(_otio.Clip)
def __repr__(self):
    return (
        'otio.schema.Clip('
        'name={}, '
        'media_reference={}, '
        'source_range={}, '
        'metadata={}'
        ')'.format(
            repr(self.name),
            repr(self.media_reference),
            repr(self.source_range),
            repr(self.metadata),
        )
    )


@add_method(_otio.Clip)
def clip_if(self, search_range=None):
    yield self
