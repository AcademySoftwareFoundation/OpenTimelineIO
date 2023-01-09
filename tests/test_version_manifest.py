# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""unit tests for the version manifest plugin system"""

import unittest
import os
import json

import opentimelineio as otio
from tests import utils


FIRST_MANIFEST = """{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "version_manifests": {
        "UNIQUE_FAMILY": {
            "TEST_LABEL": {
                "second_thing": 3
            }
        },
        "LAYERED_FAMILY": {
            "June2022": {
                "SimpleClass": 2
            },
            "May2022": {
                "SimpleClass": 1
            }
        }
    }
}
"""

SECOND_MANIFEST = """{
    "OTIO_SCHEMA" : "PluginManifest.1",
    "version_manifests": {
        "LAYERED_FAMILY": {
            "May2022": {
                "SimpleClass": 2
            },
            "April2022": {
                "SimpleClass": 1
            }
        }
    }
}
"""


class TestPlugin_VersionManifest(unittest.TestCase):
    def setUp(self):
        self.bak = otio.plugins.ActiveManifest()
        self.man = utils.create_manifest()
        otio.plugins.manifest._MANIFEST = self.man

        if "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL" in os.environ:
            del os.environ["OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"]

    def tearDown(self):
        otio.plugins.manifest._MANIFEST = self.bak
        utils.remove_manifest(self.man)
        if "OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL" in os.environ:
            del os.environ["OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"]

    def test_read_in_manifest(self):
        self.assertIn("TEST_FAMILY_NAME", self.man.version_manifests)
        self.assertIn(
            "TEST_LABEL",
            self.man.version_manifests["TEST_FAMILY_NAME"]
        )

    def test_full_map(self):
        d = otio.versioning.full_map()
        self.assertIn("TEST_FAMILY_NAME", d)
        self.assertIn(
            "TEST_LABEL",
            d["TEST_FAMILY_NAME"]
        )

    def test_fetch_map(self):
        self.assertEqual(
            otio.versioning.fetch_map("TEST_FAMILY_NAME", "TEST_LABEL"),
            {"ExampleSchema": 2, "EnvVarTestSchema": 1, "Clip": 1}
        )

    def test_env_variable_downgrade(self):
        @otio.core.register_type
        class EnvVarTestSchema(otio.core.SerializableObject):
            _serializable_label = "EnvVarTestSchema.2"
            foo_two = otio.core.serializable_field("foo_2")

        @otio.core.downgrade_function_from(EnvVarTestSchema, 2)
        def downgrade_2_to_1(_data_dict):
            return {"foo": _data_dict["foo_2"]}

        evt = EnvVarTestSchema()
        evt.foo_two = "asdf"

        result = json.loads(otio.adapters.otio_json.write_to_string(evt))
        self.assertEqual(result["OTIO_SCHEMA"], "EnvVarTestSchema.2")

        # env variable should make a downgrade by default...
        os.environ["OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"] = (
            "TEST_FAMILY_NAME:TEST_LABEL"
        )
        result = json.loads(otio.adapters.otio_json.write_to_string(evt))
        self.assertEqual(result["OTIO_SCHEMA"], "EnvVarTestSchema.1")

        # ...but can still be overridden by passing in an argument
        result = json.loads(otio.adapters.otio_json.write_to_string(evt, {}))
        self.assertEqual(result["OTIO_SCHEMA"], "EnvVarTestSchema.2")

    def test_garbage_env_variables(self):
        cl = otio.schema.Clip()
        invalid_env_error = otio.exceptions.InvalidEnvironmentVariableError

        # missing ":"
        os.environ["OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"] = (
            "invalid_formatting"
        )
        with self.assertRaises(invalid_env_error):
            otio.adapters.otio_json.write_to_string(cl)

        # asking for family/label that doesn't exist in the plugins
        os.environ["OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL"] = (
            "nosuch:labelorfamily"
        )
        with self.assertRaises(invalid_env_error):
            otio.adapters.otio_json.write_to_string(cl)

    def test_two_version_manifests(self):
        """test that two manifests layer correctly"""

        fst = otio.plugins.manifest.manifest_from_string(FIRST_MANIFEST)
        snd = otio.plugins.manifest.manifest_from_string(SECOND_MANIFEST)
        fst.extend(snd)

        self.assertIn("UNIQUE_FAMILY", fst.version_manifests)

        lay_fam = fst.version_manifests["LAYERED_FAMILY"]

        self.assertIn("June2022", lay_fam)
        self.assertIn("April2022", lay_fam)
        self.assertEqual(lay_fam["May2022"]["SimpleClass"], 2)


if __name__ == '__main__':
    unittest.main()
