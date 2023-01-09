#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Utility assertions for OTIO Unit tests."""

import re

from . import (
    adapters
)


class OTIOAssertions:
    def assertJsonEqual(self, known, test_result):
        """Convert to json and compare that (more readable)."""
        self.maxDiff = None

        known_str = adapters.write_to_string(known, 'otio_json')
        test_str = adapters.write_to_string(test_result, 'otio_json')

        def strip_trailing_decimal_zero(s):
            return re.sub(r'"(value|rate)": (\d+)\.0', r'"\1": \2', s)

        self.assertMultiLineEqual(
            strip_trailing_decimal_zero(known_str),
            strip_trailing_decimal_zero(test_str)
        )

    def assertIsOTIOEquivalentTo(self, known, test_result):
        """Test using the 'is equivalent to' method on SerializableObject"""

        self.assertTrue(known.is_equivalent_to(test_result))
