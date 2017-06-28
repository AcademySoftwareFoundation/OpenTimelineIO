import unittest
import os

import baseline_reader

import opentimelineio as otio

LINKER_PATH = "media_linker_example"
MANIFEST_PATH = "adapter_plugin_manifest.plugin_manifest"
MAN_PATH = '/var/tmp/test_otio_manifest'


def test_manifest():
    full_baseline = baseline_reader.json_baseline_as_string(MANIFEST_PATH)

    with open(MAN_PATH, 'w') as fo:
        fo.write(full_baseline)
    man = otio.plugins.manifest_from_file(MAN_PATH)
    man._update_plugin_source(baseline_reader.path_to_baseline(MANIFEST_PATH))
    return man


class TestPluginMediaLinker(unittest.TestCase):
    def setUp(self):
        self.man = test_manifest()
        self.jsn = baseline_reader.json_baseline_as_string(LINKER_PATH)
        self.mln = otio.adapters.otio_json.read_from_string(self.jsn)
        self.mln._json_path = os.path.join(
            baseline_reader.MODPATH,
            "baseline",
            LINKER_PATH
        )

    def test_plugin_adapter(self):
        self.assertEqual(self.mln.name, "example")
        self.assertEqual(self.mln.execution_scope, "in process")
        self.assertEqual(self.mln.filepath, "example.py")

    def test_load_adapter_module(self):

        target = os.path.join(
            baseline_reader.MODPATH,
            "baseline",
            "example.py"
        )

        self.assertEqual(self.mln.module_abs_path(), target)
        self.assertTrue(hasattr(self.mln.module(), "link_media_reference"))

    def test_run_linker(self):
        cl = otio.schema.Clip(name="foo")

        linked_mr = self.mln.link_media_reference(cl, {"extra_data": True})
        self.assertIsInstance(linked_mr, otio.media_reference.MissingReference)
        self.assertEqual(linked_mr.name, cl.name + "_tweaked")
        self.assertEqual(linked_mr.metadata.get("extra_data"), True)

    def test_serialize(self):

        self.assertEqual(
            str(self.mln),
            "MediaLinker({}, {}, {})".format(
                repr(self.mln.name),
                repr(self.mln.execution_scope),
                repr(self.mln.filepath)
            )
        )
        self.assertEqual(
            repr(self.mln),
            "otio.media_linker.MediaLinker("
            "name={}, "
            "execution_scope={}, "
            "filepath={}"
            ")".format(
                repr(self.mln.name),
                repr(self.mln.execution_scope),
                repr(self.mln.filepath)
            )
        )
