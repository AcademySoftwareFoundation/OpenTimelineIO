# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.ExternalReference)
def __str__(self):
    return f'ExternalReference("{str(self.target_url)}")'


@add_method(_otio.ExternalReference)
def __repr__(self):
    return 'otio.schema.ExternalReference(target_url={})'.format(
        repr(str(self.target_url))
    )
