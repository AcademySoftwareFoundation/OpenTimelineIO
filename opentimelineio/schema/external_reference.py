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

"""
Implementation of the ExternalReference media reference schema.
"""

from .. import (
    core,
)


@core.register_type
class ExternalReference(core.MediaReference):
    """Reference to media via a url, for example "file:///var/tmp/foo.mov" """

    _serializable_label = "ExternalReference.1"
    _name = "ExternalReference"

    def __init__(
        self,
        target_url=None,
        available_range=None,
        metadata=None,
    ):
        core.MediaReference.__init__(
            self,
            available_range=available_range,
            metadata=metadata
        )

        self.target_url = target_url

    target_url = core.serializable_field(
        "target_url",
        doc=(
            "URL at which this media lives.  For local references, use the "
            "'file://' format."
        )
    )

    def __str__(self):
        return 'ExternalReference("{}")'.format(self.target_url)

    def __repr__(self):
        return 'otio.schema.ExternalReference(target_url={})'.format(
            repr(self.target_url)
        )
