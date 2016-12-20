#!/usr/bin/env python

import unittest
import os

import baseline_reader

import opentimelineio as otio

__doc__ = """ Unit tests for the adapter plugin system. """


MANIFEST_PATH = "adapter_plugin_manifest.plugin_manifest"
ADAPTER_PATH = "adapter_example"


class TestPluginAdapters(unittest.TestCase):

    def test_plugin_adapter(self):
        jsn = baseline_reader.json_baseline_as_string(ADAPTER_PATH)
        adp = otio.adapters.otio_json.read_from_string(jsn)
        self.assertEqual(adp.name, "example")
        self.assertEqual(adp.execution_scope, "in process")
        self.assertEqual(adp.filepath, "example.py")
        self.assertEqual(adp.suffixes, ["EXAMPLE"])

    def test_load_adapter_module(self):
        jsn = baseline_reader.json_baseline_as_string(ADAPTER_PATH)
        adp = otio.adapters.otio_json.read_from_string(jsn)
        adp._json_path = os.path.join(
            baseline_reader.MODPATH, "baseline", ADAPTER_PATH)
        # self.assertTrue(hasattr(adp.module(), "read_from_file"))

        target = os.path.join(baseline_reader.MODPATH,
                              "baseline", "example.py")

        self.assertEqual(adp.module_abs_path(), target)
        self.assertTrue(hasattr(adp.module(), "read_from_file"))
        self.assertEqual(adp.module().read_from_file("foo").name, "foo")


MAN_PATH = '/var/tmp/test_otio_manifest'


def test_manifest():
    full_baseline = baseline_reader.json_baseline_as_string(MANIFEST_PATH)

    with open(MAN_PATH, 'w') as fo:
        fo.write(full_baseline)
    man = otio.adapters.manifest_from_file(MAN_PATH)
    man._update_adapter_source(baseline_reader.path_to_baseline(MANIFEST_PATH))
    return man


class TestPluginManifest(unittest.TestCase):

    def test_plugin_manifest(self):
        man = test_manifest()

        self.assertEqual(man.source_files, [MAN_PATH])

        self.assertNotEqual(man.adapters, [])

    def test_find_adapter_by_suffix(self):
        man = test_manifest()
        self.assertEqual(man.from_filepath("EXAMPLE").name, "example")
        with self.assertRaises(Exception):
            man.from_filepath("BLARG")
        adp = man.from_filepath("EXAMPLE")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(man.adapter_module_from_suffix(
            "EXAMPLE").read_from_file("path").name, "path")

    def test_find_adapter_by_name(self):
        man = test_manifest()
        self.assertEqual(man.from_name("example").name, "example")
        with self.assertRaises(Exception):
            man.from_name("BLARG")
        adp = man.from_name("example")
        self.assertEqual(adp.module().read_from_file("path").name, "path")
        self.assertEqual(man.adapter_module_from_name(
            "example").read_from_file("path").name, "path")


if __name__ == '__main__':
    unittest.main()
