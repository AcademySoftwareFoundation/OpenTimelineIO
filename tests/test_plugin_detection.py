#
# Copyright 2018 Pixar Animation Studios
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
import logging
import os
import pkg_resources

try:
    # Python 3.3 forward includes the mock module
    from unittest import mock
except ImportError:
    # Fallback for older python
    import mock

import opentimelineio as otio
import baseline_reader


class TestSetuptoolsPlugin(unittest.TestCase):
    def setUp(self):
        # Get the location of the mock plugin module metadata
        mock_module_path = os.path.join(
            baseline_reader.path_to_baseline_directory(),
            'plugin_module',
        )

        # Create a WorkingSet as if the module were installed
        entries = [mock_module_path] + pkg_resources.working_set.entries
        working_set = pkg_resources.WorkingSet(entries)

        # Make a mock of the loaded plugin module
        self.mock_adapter = mock.Mock()
        self.mock_linker = mock.Mock()
        mock_manifest = otio.plugins.manifest.Manifest()
        mock_manifest.adapters = [self.mock_adapter]
        mock_manifest.media_linkers = [self.mock_linker]
        self.mock_plugin_module = mock.Mock(
            plugin_manifest=mock.Mock(return_value=mock_manifest)
        )

        # Patch the plugin module as if it was loaded as otio_mockplugin
        self.module_patcher = mock.patch.dict(
            'sys.modules',
            otio_mockplugin=self.mock_plugin_module
        )
        self.module_patcher.start()

        # linker from the entry point
        self.entry_patcher = mock.patch(
            'pkg_resources.iter_entry_points',
            working_set.iter_entry_points
        )
        self.entry_patcher.start()

    def tearDown(self):
        self.module_patcher.stop()
        self.entry_patcher.stop()

    def test_detect_pugin(self):
        # Create a manifest and ensure it detected the mock adapter and linker
        man = otio.plugins.manifest.load_manifest()
        self.assertIn(self.mock_adapter, man.adapters)
        self.assertIn(self.mock_linker, man.media_linkers)
        self.assertNotIn(self.mock_linker, man.adapters)
        self.assertNotIn(self.mock_adapter, man.media_linkers)

    def test_failed_plugin_load(self):
        # Disable the error logging to keep the test from being scary
        logging.disable(logging.CRITICAL)

        self.mock_plugin_module.plugin_manifest = mock.Mock(
            side_effect=Exception
        )

        # Ensure we can load the manifest, safely
        man = otio.plugins.manifest.load_manifest()
        self.assertNotIn(self.mock_adapter, man.adapters)
        self.assertNotIn(self.mock_linker, man.media_linkers)

        # Reset the logging
        logging.disable(logging.NOTSET)
