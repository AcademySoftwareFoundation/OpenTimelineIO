#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest
import os
import pkg_resources
import sys

from unittest import mock

from importlib import reload as import_reload

import opentimelineio as otio
from tests import baseline_reader


class TestSetuptoolsPlugin(unittest.TestCase):
    def setUp(self):
        # Get the location of the mock plugin module metadata
        mock_module_path = os.path.join(
            os.path.normpath(baseline_reader.path_to_baseline_directory()),
            'plugin_module',
        )
        self.mock_module_manifest_path = os.path.join(
            mock_module_path,
            "otio_jsonplugin",
            "plugin_manifest.json"
        )

        self.override_adapter_manifest_path = os.path.join(
            mock_module_path,
            "otio_override_adapter",
            "plugin_manifest.json"
        )

        # Create a WorkingSet as if the module were installed
        entries = [mock_module_path] + pkg_resources.working_set.entries

        self.sys_patch = mock.patch('sys.path', entries)
        self.sys_patch.start()

        working_set = pkg_resources.WorkingSet(entries)

        # linker from the entry point
        self.entry_patcher = mock.patch(
            'pkg_resources.iter_entry_points',
            working_set.iter_entry_points
        )
        self.entry_patcher.start()

    def tearDown(self):
        self.sys_patch.stop()
        self.entry_patcher.stop()
        if 'otio_mockplugin' in sys.modules:
            del sys.modules['otio_mockplugin']

        if 'otio_override_adapter' in sys.modules:
            del sys.modules['otio_override_adapter']

    def test_detect_plugin(self):
        """This manifest uses the plugin_manifest function"""

        # Create a manifest and ensure it detected the mock adapter and linker
        man = otio.plugins.manifest.load_manifest()

        # Make sure the adapter is included in the adapter list
        adapter_names = [adapter.name for adapter in man.adapters]
        self.assertIn('mock_adapter', adapter_names)

        # Make sure the linker is included in the linker list
        linker_names = [linker.name for linker in man.media_linkers]
        self.assertIn('mock_linker', linker_names)

        # Make sure adapters and linkers landed in the proper place
        for adapter in man.adapters:
            self.assertIsInstance(adapter, otio.adapters.Adapter)

        for linker in man.media_linkers:
            self.assertIsInstance(linker, otio.media_linker.MediaLinker)

    def test_override_adapter(self):

        # Test that entrypoint plugins load before builtin and contrib
        man = otio.plugins.manifest.load_manifest()

        # The override_adapter creates another cmx_3600 adapter
        adapters = [adapter for adapter in man.adapters
                    if adapter.name == "cmx_3600"]

        # More then one cmx_3600 adapter should exist.
        self.assertTrue(len(adapters) > 1)

        # Override adapter should be the first adapter found
        manifest = adapters[0].plugin_info_map().get('from manifest', None)
        self.assertEqual(manifest, os.path.abspath(self.override_adapter_manifest_path))

        self.assertTrue(
            any(
                True for p in man.source_files
                if self.override_adapter_manifest_path in p
            )
        )

    def test_pkg_resources_disabled(self):
        os.environ["OTIO_DISABLE_PKG_RESOURCE_PLUGINS"] = "1"
        import_reload(otio.plugins.manifest)

        # detection of the environment variable happens on import, force a
        # reload to ensure that it is triggered
        with self.assertRaises(AssertionError):
            self.test_detect_plugin()

        # override adapter should not be loaded either
        with self.assertRaises(AssertionError):
            self.test_override_adapter()

        # remove the environment variable and reload again for usage in the
        # other tests
        del os.environ["OTIO_DISABLE_PKG_RESOURCE_PLUGINS"]
        import_reload(otio.plugins.manifest)

    def test_detect_plugin_json_manifest(self):
        # Test detecting a plugin that rather than exposing the plugin_manifest
        # function, just simply has a plugin_manifest.json provided at the
        # package top level.
        man = otio.plugins.manifest.load_manifest()

        # Make sure the adapter is included in the adapter list
        adapter_names = [adapter.name for adapter in man.adapters]
        self.assertIn('mock_adapter_json', adapter_names)

        # Make sure the linker is included in the linker list
        linker_names = [linker.name for linker in man.media_linkers]
        self.assertIn('mock_linker_json', linker_names)

        # Make sure adapters and linkers landed in the proper place
        for adapter in man.adapters:
            self.assertIsInstance(adapter, otio.adapters.Adapter)

        for linker in man.media_linkers:
            self.assertIsInstance(linker, otio.media_linker.MediaLinker)

        self.assertTrue(
            any(
                True for p in man.source_files
                if self.mock_module_manifest_path in p
            )
        )

    def test_deduplicate_env_variable_paths(self):
        "Ensure that duplicate entries in the environment variable are ignored"

        # back up existing manifest
        bak_env = os.environ.get('OTIO_PLUGIN_MANIFEST_PATH')

        relative_path = self.mock_module_manifest_path.replace(os.getcwd(), '.')

        # set where to find the new manifest
        os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = os.pathsep.join(
            (
                # absolute
                self.mock_module_manifest_path,

                # relative
                relative_path
            )
        )

        result = otio.plugins.manifest.load_manifest()
        self.assertEqual(
            len(
                [
                    p for p in result.source_files
                    if self.mock_module_manifest_path in p
                ]
            ),
            1
        )
        if relative_path != self.mock_module_manifest_path:
            self.assertNotIn(relative_path, result.source_files)

        if bak_env:
            os.environ['OTIO_PLUGIN_MANIFEST_PATH'] = bak_env
        else:
            del os.environ['OTIO_PLUGIN_MANIFEST_PATH']


if __name__ == '__main__':
    unittest.main()
