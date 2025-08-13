# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Clip)
def __str__(self):
    return 'Clip("{}", {}, {}, {}, {}, {})'.format(
        self.name,
        self.media_reference,
        self.source_range,
        self.metadata,
        self.effects,
        self.markers
    )


@add_method(_otio.Clip)
def __repr__(self):
    return (
        'otio.schema.Clip('
        'name={}, '
        'media_reference={}, '
        'source_range={}, '
        'color={}, '
        'metadata={}, '
        'effects={}, '
        'markers={}'
        ')'.format(
            repr(self.name),
            repr(self.media_reference),
            repr(self.source_range),
            repr(self.color),
            repr(self.metadata),
            repr(self.effects),
            repr(self.markers)
        )
    )


@add_method(_otio.Clip)
def find_clips(self, search_range=None):
    yield self
