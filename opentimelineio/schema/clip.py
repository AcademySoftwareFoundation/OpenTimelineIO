#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Implementation of the Clip class, for pointing at media."""

from .. import (
    core,
    media_reference as mr,
    exceptions,
)


@core.register_type
class Clip(core.Item):
    """The base editable object in OTIO.

    Contains a media reference and a trim on that media reference.
    """

    _serializeable_label = "Clip.1"

    def __init__(
        self,
        name=None,
        media_reference=None,
        source_range=None,
        metadata=None,
    ):
        core.Item.__init__(
            self,
            name=name,
            source_range=source_range,
            metadata=metadata
        )
        # init everything as None first, so that we will catch uninitialized
        # values via exceptions
        self.name = name

        if not media_reference:
            media_reference = mr.MissingReference()
        self._media_reference = media_reference

    name = core.serializeable_field("name", doc="Name of this clip.")
    transform = core.deprecated_field()
    _media_reference = core.serializeable_field(
        "media_reference",
        mr.MediaReference,
        "Media reference to the media this clip represents."
    )

    @property
    def media_reference(self):
        if self._media_reference is None:
            self._media_reference = mr.MissingReference()
        return self._media_reference

    @media_reference.setter
    def media_reference(self, val):
        if val is None:
            val = mr.MissingReference()
        self._media_reference = val

    def available_range(self):
        if not self.media_reference:
            raise exceptions.CannotComputeAvailableRangeError(
                "No media reference set on clip: {}".format(self)
            )

        if not self.media_reference.available_range:
            raise exceptions.CannotComputeAvailableRangeError(
                "No available_range set on media reference on clip: {}".format(
                    self
                )
            )

        return self.media_reference.available_range

    def __str__(self):
        return 'Clip("{}", {}, {}, {})'.format(
            self.name,
            self.media_reference,
            self.source_range,
            self.metadata
        )

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

    def each_clip(self, search_range=None):
        """Yields self."""

        yield self
