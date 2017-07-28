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

import baseline_reader

import opentimelineio as otio

"""Unit tests for the adapter plugin system."""


MANIFEST_PATH = "adapter_plugin_manifest.plugin_manifest"
ADAPTER_PATH = "adapter_example"
MEDIA_LINKER_EXAMPLE = "media_linker_example"


class TestAdapterSuffixes(unittest.TestCase):
    def test_supported_suffixes_is_not_none(self):
        result = otio.adapters.suffixes_with_defined_adapters()
        self.assertIsNotNone(result)
        self.assertNotEqual(result, [])
        self.assertNotEqual(result, set([]))


class TestPluginAdapters(unittest.TestCase):
    def setUp(self):
        self.jsn = baseline_reader.json_baseline_as_string(ADAPTER_PATH)
        self.adp = otio.adapters.otio_json.read_from_string(self.jsn)
        self.adp._json_path = os.path.join(
            baseline_reader.MODPATH,
            "baselines",
            ADAPTER_PATH
        )

    def test_plugin_adapter(self):
        self.assertEqual(self.adp.name, "example")
        self.assertEqual(self.adp.execution_scope, "in process")
        self.assertEqual(self.adp.filepath, "example.py")
        self.assertEqual(self.adp.suffixes, ["example"])

        self.assertMultiLineEqual(
            str(self.adp),
            "Adapter("
            "{}, "
            "{}, "
            "{}, "
            "{}"
            ")".format(
                repr(self.adp.name),
                repr(self.adp.execution_scope),
                repr(self.adp.filepath),
                repr(self.adp.suffixes),
            )
        )
        self.assertMultiLineEqual(
            repr(self.adp),
            "otio.adapter.Adapter("
            "name={}, "
            "execution_scope={}, "
            "filepath={}, "
            "suffixes={}"
            ")".format(
                repr(self.adp.name),
                repr(self.adp.execution_scope),
                repr(self.adp.filepath),
                repr(self.adp.suffixes),
            )
        )

        self.assertNotEqual(self.adp._json_path, None)

    def test_load_adapter_module(self):
        target = os.path.join(
            baseline_reader.MODPATH,
            "baselines",
            "example.py"
        )

        self.assertEqual(self.adp.module_abs_path(), target)
        self.assertTrue(hasattr(self.adp.module(), "read_from_file"))

        # call through the module accessor
        self.assertEqual(self.adp.module().read_from_file("foo").name, "foo")

        # call through the convienence wrapper
        self.assertEqual(self.adp.read_from_file("foo").name, "foo")

    def test_has_feature(self):
        self.assertTrue(self.adp.has_feature("read"))
        self.assertTrue(self.adp.has_feature("read_from_file"))
        self.assertFalse(self.adp.has_feature("write"))

    def test_run_media_linker_during_adapter(self):
        mfest = otio.plugins.ActiveManifest()

        # this wires up the media linkers into the active manifest
        mfest.media_linkers.extend(test_manifest().media_linkers)
        fake_tl = self.adp.read_from_file("foo", media_linker_name="example")

        self.assertTrue(
            fake_tl.tracks[0][0].media_reference.metadata.get(
                'from_test_linker'
            )
        )

        fake_tl = self.adp.read_from_string(
            "foo",
            media_linker_name="example"
        )

        self.assertTrue(
            fake_tl.tracks[0][0].media_reference.metadata.get(
                'from_test_linker'
            )
        )

        # explicitly turn the media_linker off
        fake_tl = self.adp.read_from_file("foo", media_linker_name=None)
        self.assertIsNone(
            fake_tl.tracks[0][0].media_reference.metadata.get(
                'from_test_linker'
            )
        )


MAN_PATH = '/var/tmp/test_otio_manifest'


def test_manifest():
    full_baseline = baseline_reader.json_baseline_as_string(MANIFEST_PATH)

    with open(MAN_PATH, 'w') as fo:
        fo.write(full_baseline)
    man = otio.plugins.manifest_from_file(MAN_PATH)
    man._update_plugin_source(baseline_reader.path_to_baseline(MANIFEST_PATH))
    return man


class TestPluginManifest(unittest.TestCase):

    def test_plugin_manifest(self):
        man = test_manifest()

        self.assertEqual(man.source_files, [MAN_PATH])

        self.assertNotEqual(man.adapters, [])

    def test_find_adapter_by_suffix(self):
        man = test_manifest()
        self.assertEqual(man.from_filepath("example").name, "example")
        with self.assertRaises(Exception):
            man.from_filepath("BLARG")
        adp = man.from_filepath("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(
            man.adapter_module_from_suffix(
                "example"
            ).read_from_file("path").name,
            "path"
        )

    def test_find_adapter_by_name(self):
        man = test_manifest()
        self.assertEqual(man.from_name("example").name, "example")
        with self.assertRaises(Exception):
            man.from_name("BLARG")
        adp = man.from_name("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(
            man.adapter_module_from_name("example").read_from_file(
                "path"
            ).name,
            "path"
        )


if __name__ == '__main__':
    unittest.main()
