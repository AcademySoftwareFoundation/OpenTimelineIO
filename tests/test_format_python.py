# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Verify list cleanup does not change Python tuple or subscript semantics."""

import ast
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "otio_format_python",
    Path(__file__).resolve().parents[1] / "maintainers" / "format_python.py",
)
format_python = importlib.util.module_from_spec(spec)
spec.loader.exec_module(format_python)


class ListCommaTest(unittest.TestCase):
    def check_cleanup(self, source, expected):
        actual = format_python.remove_list_trailing_commas(source)
        self.assertEqual(actual, expected)
        self.assertEqual(ast.dump(ast.parse(actual)), ast.dump(ast.parse(source)))
        self.assertEqual(format_python.remove_list_trailing_commas(actual), actual)

    def test_multiline_and_nested_lists(self):
        self.check_cleanup(
            "x = [\n    [1, 2,],\n    3,\n]\n", "x = [\n    [1, 2],\n    3\n]\n"
        )

    def test_comments_and_unicode(self):
        self.check_cleanup(
            'x = ["café",] # after\ny = [1, # keep comment\n]\n',
            'x = ["café"] # after\ny = [1 # keep comment\n]\n',
        )

    def test_preserves_tuple_and_subscript_commas(self):
        source = "x = [(1,), table[1,], (1, 2),]\n"
        self.check_cleanup(source, "x = [(1,), table[1,], (1, 2)]\n")

    def test_preserves_strings(self):
        self.check_cleanup('x = ["comma,]", ",",]\n', 'x = ["comma,]", ","]\n')

    def test_empty_list_and_comprehension(self):
        source = "x = []\ny = [item for item in values]\n"
        self.check_cleanup(source, source)


if __name__ == "__main__":
    unittest.main()
