# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.GeneratorReference)
def __str__(self):
    return 'GeneratorReference("{}", "{}", {}, {}, {})'.format(
        self.name,
        self.generator_kind,
        self.parameters,
        self.available_image_bounds,
        self.metadata
    )


@add_method(_otio.GeneratorReference)
def __repr__(self):
    return (
        'otio.schema.GeneratorReference('
        'name={}, '
        'generator_kind={}, '
        'parameters={}, '
        'available_image_bounds={}, '
        'metadata={}'
        ')'.format(
            repr(self.name),
            repr(self.generator_kind),
            repr(self.parameters),
            repr(self.available_image_bounds),
            repr(self.metadata),
        )
    )
