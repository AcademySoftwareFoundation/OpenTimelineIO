#
# Copyright Contributors to the OpenTimelineIO project
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

"""This file is here to support the test_schemadef_plugin unittest.
If you want to learn how to write your own SchemaDef plugin, please read:
https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-schemadef.html
"""

import opentimelineio as otio


@otio.core.register_type
class exampleSchemaDef(otio.core.SerializableObject):
    """Example of a SchemaDef plugin class for testing."""

    _serializable_label = "exampleSchemaDef.1"
    _name = "exampleSchemaDef"

    def __init__(
        self,
        exampleArg=None,
    ):
        otio.core.SerializableObject.__init__(self)
        self.exampleArg = exampleArg

    exampleArg = otio.core.serializable_field(
        "exampleArg",
        doc=(
            "example of an arg passed to the exampleSchemaDef"
        )
    )

    def __str__(self):
        return 'exampleSchemaDef({})'.format(
            repr(self.exampleArg)
        )

    def __repr__(self):
        return \
            'otio.schemadef.example_schemadef.exampleSchemaDef(exampleArg={})'.format(
                repr(self.exampleArg)
            )
