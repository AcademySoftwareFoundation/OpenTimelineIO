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
import unittest
import os

import opentimelineio as otio
from tests import baseline_reader

"""Unit tests for the schemadef plugin system."""


SCHEMADEF_NAME = "schemadef_example"
EXAMPLE_ARG = "exampleArg"
EXCLASS = "<class 'opentimelineio.schemadef.example_schemadef.exampleSchemaDef'>"
TEST_STRING = """
{
    "OTIO_SCHEMA": "exampleSchemaDef.1",
    "exampleArg": "foobar"
}
"""


def _clean_plugin_module():
    """Remove the example_schemadef if its already been loaded to test
    autoload/explicit load behavior.
    """
    try:
        del otio.schemadef.example_schemadef
    except AttributeError:
        pass

    try:
        plugin = otio.schema.schemadef.from_name("example_schemadef")
        plugin._module = None
    except otio.exceptions.NotSupportedError:
        pass


class TestPluginSchemadefs(unittest.TestCase):
    def setUp(self):
        self.save_manifest = otio.plugins.manifest._MANIFEST
        self.save_manifest_path = os.environ.get('OTIO_PLUGIN_MANIFEST_PATH')
        # find the path to the baselines/schemadef_example.json
        self.manifest_path = baseline_reader.path_to_baseline(SCHEMADEF_NAME)
        os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = self.manifest_path
        otio.plugins.manifest.ActiveManifest(force_reload=True)
        _clean_plugin_module()

    def tearDown(self):
        # restore original state
        if self.save_manifest_path:
            os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = self.save_manifest_path
        else:
            del os.environ['OTIO_PLUGIN_MANIFEST_PATH']
        otio.plugins.manifest._MANIFEST = self.save_manifest

        _clean_plugin_module()

    def test_autoloaded_plugin(self):
        with self.assertRaises(AttributeError):
            otio.schemadef.example_schemadef
        # should force an autoload
        thing = otio.adapters.read_from_string(TEST_STRING, "otio_json")
        self.assertEqual(thing.exampleArg, "foobar")

    def test_plugin_schemadef(self):
        with self.assertRaises(AttributeError):
            otio.schemadef.example_schemadef
        # force loading the module
        otio.schema.schemadef.module_from_name("example_schemadef")

        # Our test manifest should have been loaded, including
        # the example_schemadef.
        # Try creating a schema object using the instance_from_schema method.
        peculiar_value = "something One-derful"
        example = otio.core.instance_from_schema("exampleSchemaDef", 1, {
            EXAMPLE_ARG: peculiar_value
        })

        self.assertEqual(str(type(example)), EXCLASS)
        self.assertEqual(example.exampleArg, peculiar_value)

    def test_plugin_schemadef_namespace(self):
        with self.assertRaises(AttributeError):
            otio.schemadef.example_schemadef

        # force loading the module
        plugin_module = otio.schema.schemadef.module_from_name(
            "example_schemadef"
        )

        # Try creating schema object with the direct class definition method:
        peculiar_value = "something Two-derful"
        example = otio.schemadef.example_schemadef.exampleSchemaDef(peculiar_value)
        self.assertEqual(plugin_module, otio.schemadef.example_schemadef)
        self.assertEqual(str(type(example)), EXCLASS)
        self.assertEqual(example.exampleArg, peculiar_value)


if __name__ == '__main__':
    unittest.main()
