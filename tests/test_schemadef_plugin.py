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
import unittest
import os

import opentimelineio as otio
from tests import baseline_reader

"""Unit tests for the schemadef plugin system."""


SCHEMADEF_NAME = "schemadef_example"
EXAMPLE_SCHEMADEF = "exampleSchemaDef"
EXAMPLE_ARG = "exampleArg"


class TestPluginSchemadefs(unittest.TestCase):
    def setUp(self):
        self.save_manifest_path = os.environ.get('OTIO_PLUGIN_MANIFEST_PATH')
        # find the path to the baselines/schemadef_example.json
        self.manifest_path = baseline_reader.path_to_baseline(SCHEMADEF_NAME)
        os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = self.manifest_path
        otio.plugins.manifest.ActiveManifest(force_reload=True)

    def tearDown(self):
        # restore original state
        if self.save_manifest_path:
            os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = self.save_manifest_path
        else:
            del os.environ['OTIO_PLUGIN_MANIFEST_PATH']
        otio.plugins.manifest.ActiveManifest(force_reload=True)

    def test_plugin_schemadef(self):
        # Our test manifest should have been loaded, including
        # the exampleSchemaDef.
        peculiar_value = "something One-derful"
        try:
            example = otio.core.instance_from_schema(EXAMPLE_SCHEMADEF, 1, {
                EXAMPLE_ARG: peculiar_value
            })
        except otio.exceptions.NotSupportedError:
            self.fail("raised NotSupportedError (new schema type was undefined)")

        self.assertEqual(example.exampleArg, peculiar_value)


if __name__ == '__main__':
    unittest.main()
