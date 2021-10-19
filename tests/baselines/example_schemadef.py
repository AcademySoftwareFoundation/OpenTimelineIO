# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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
