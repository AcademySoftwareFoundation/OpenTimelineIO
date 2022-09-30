# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test harness for Item."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

# add Item to the type registry for the purposes of unit testing
# otio.core.register_type(otio.core.Item)


class GapTester(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_str_gap(self):
        gp = otio.schema.Gap()
        self.assertMultiLineEqual(
            str(gp),
            "Gap(" +
            str(gp.name) + ", " +
            str(gp.source_range) + ", " +
            str(gp.effects) + ", " +
            str(gp.markers) + ", " +
            str(gp.enabled) + ", " +
            str(gp.metadata) +
            ")"
        )
        self.assertMultiLineEqual(
            repr(gp),
            "otio.schema.Gap("
            "name={}, "
            "source_range={}, "
            "effects={}, "
            "markers={}, "
            "enabled={}, "
            "metadata={}"
            ")".format(
                repr(gp.name),
                repr(gp.source_range),
                repr(gp.effects),
                repr(gp.markers),
                repr(gp.enabled),
                repr(gp.metadata),
            )
        )

        encoded = otio.adapters.otio_json.write_to_string(gp)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertJsonEqual(gp, decoded)

    def test_convert_from_filler(self):
        gp = otio.schema.Gap()
        gp._serializable_label = "Filler.1"
        encoded = otio.adapters.otio_json.write_to_string(gp)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        isinstance(decoded, otio.schema.Gap)

    def test_not_both_source_range_and_duration(self):
        with self.assertRaises(TypeError):
            otio.schema.Gap(
                duration=otio.opentime.RationalTime(10, 24),
                source_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 24),
                    otio.opentime.RationalTime(10, 24)
                )
            )

        self.assertJsonEqual(
            otio.schema.Gap(
                duration=otio.opentime.RationalTime(10, 24),
            ),
            otio.schema.Gap(
                source_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 24),
                    otio.opentime.RationalTime(10, 24)
                )
            )
        )


class ItemTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_constructor(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(name="foo", source_range=tr)
        self.assertEqual(it.source_range, tr)
        self.assertEqual(it.name, "foo")

        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(it, decoded)

    def test_copy_arguments(self):
        # make sure all the arguments are copied and not referenced
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 24),
            otio.opentime.RationalTime(10, 24),
        )
        name = "foobar"
        effects = []
        markers = []
        metadata = {}
        it = otio.core.Item(
            name=name,
            source_range=tr,
            effects=effects,
            markers=markers,
            metadata=metadata,
        )
        name = 'foobaz'
        self.assertNotEqual(it.name, name)

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(1, tr.start_time.rate),
            duration=tr.duration
        )
        self.assertNotEqual(it.source_range.start_time, tr.start_time)
        markers.append(otio.schema.Marker())
        self.assertNotEqual(it.markers, markers)
        metadata['foo'] = 'bar'
        self.assertNotEqual(it.metadata, metadata)

    def test_duration(self):
        it = otio.core.Item()

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)

        self.assertEqual(it.duration(), tr.duration)

    def test_available_range(self):
        it = otio.core.Item()

        with self.assertRaises(NotImplementedError):
            it.available_range()

    def test_duration_and_source_range(self):
        it = otio.core.Item()

        with self.assertRaises(NotImplementedError):
            it.duration()

        self.assertEqual(None, it.source_range)

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(1, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it2 = otio.core.Item(source_range=tr)

        self.assertEqual(tr, it2.source_range)
        self.assertEqual(tr.duration, it2.duration())
        self.assertIsNot(tr.duration, it2.duration())

    def test_trimmed_range(self):
        it = otio.core.Item()
        with self.assertRaises(NotImplementedError):
            it.trimmed_range()
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(1, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it2 = otio.core.Item(source_range=tr)
        self.assertEqual(it2.trimmed_range(), tr)
        self.assertIsNot(it2.trimmed_range(), tr)

    def test_serialize(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(it, decoded)

    def test_stringify(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr)
        self.assertMultiLineEqual(
            str(it),
            "Item("
            "{}, "
            "{}, "
            "{}, "
            "{}, "
            "{}, "
            "{}"
            ")".format(
                str(it.name),
                str(it.source_range),
                str(it.effects),
                str(it.markers),
                str(it.enabled),
                str(it.metadata),
            )
        )

        self.assertMultiLineEqual(
            repr(it),
            "otio.core.Item("
            "name={}, "
            "source_range={}, "
            "effects={}, "
            "markers={}, "
            "enabled={}, "
            "metadata={}"
            ")".format(
                repr(it.name),
                repr(it.source_range),
                repr(it.effects),
                repr(it.markers),
                repr(it.enabled),
                repr(it.metadata),
            )
        )

    def test_metadata(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)
        it.metadata["foo"] = "bar"
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(it, decoded)
        self.assertEqual(decoded.metadata["foo"], it.metadata["foo"])

        foo = it.metadata.pop("foo")
        self.assertEqual(foo, "bar")
        foo = it.metadata.pop("foo", "default")
        self.assertEqual(foo, "default")
        with self.assertRaises(KeyError):
            it.metadata.pop("foo")

    def test_add_effect(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)
        it.effects.append(
            otio.schema.Effect(
                effect_name="blur",
                metadata={
                    'amount': '100'
                }
            )
        )
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(it, decoded)
        self.assertJsonEqual(it.effects, decoded.effects)

    def test_add_marker(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)
        it.markers.append(
            otio.schema.Marker(
                name="test_marker",
                marked_range=tr,
                metadata={
                    'some stuff to mark': '100'
                }
            )
        )
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(it, decoded)
        self.assertJsonEqual(it.markers, decoded.markers)

    def test_enabled(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)
        self.assertEqual(it.enabled, True)
        it.enabled = False
        self.assertEqual(it.enabled, False)
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(it, decoded)
        self.assertJsonEqual(it.enabled, decoded.enabled)

    def test_copy(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr, metadata={"foo": "bar"})
        it.markers.append(
            otio.schema.Marker(
                name="test_marker",
                marked_range=tr,
                metadata={
                    'some stuff to mark': '100'
                }
            )
        )
        it.effects.append(
            otio.schema.Effect(
                effect_name="blur",
                metadata={
                    'amount': '100'
                }
            )
        )

        it.metadata["foo"] = "bar2"

        # deep copy should have different dictionaries
        it_dcopy = it.deepcopy()
        it_dcopy.metadata["foo"] = "not bar"
        self.assertNotEqual(it.metadata, it_dcopy.metadata)

    def test_copy_library(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr, metadata={"foo": "bar"})
        it.markers.append(
            otio.schema.Marker(
                name="test_marker",
                marked_range=tr,
                metadata={
                    'some stuff to mark': '100'
                }
            )
        )
        it.effects.append(
            otio.schema.Effect(
                effect_name="blur",
                metadata={
                    'amount': '100'
                }
            )
        )

        import copy

        # deep copy should have different dictionaries
        it_dcopy = copy.deepcopy(it)
        it_dcopy.metadata["foo"] = "not bar"
        self.assertNotEqual(it.metadata, it_dcopy.metadata)

    def test_visible_range(self):
        timeline = otio.schema.Timeline(
            tracks=[
                otio.schema.Track(
                    name="V1",
                    children=[
                        otio.schema.Clip(
                            name="A",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=1,
                                    rate=30
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                )
                            )
                        ),
                        otio.schema.Transition(
                            in_offset=otio.opentime.RationalTime(
                                value=7,
                                rate=30
                            ),
                            out_offset=otio.opentime.RationalTime(
                                value=10,
                                rate=30
                            ),
                        ),
                        otio.schema.Clip(
                            name="B",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=100,
                                    rate=30
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                )
                            )
                        ),
                        otio.schema.Transition(
                            in_offset=otio.opentime.RationalTime(
                                value=17,
                                rate=30
                            ),
                            out_offset=otio.opentime.RationalTime(
                                value=15,
                                rate=30
                            ),
                        ),
                        otio.schema.Clip(
                            name="C",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                )
                            )
                        ),
                        otio.schema.Clip(
                            name="D",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=1,
                                    rate=30
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                )
                            )
                        )
                    ]
                )
            ]
        )
        self.maxDiff = None
        self.assertListEqual(
            ["A", "B", "C", "D"],
            [item.name for item in timeline.clip_if()]
        )
        self.assertListEqual(
            [
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=1,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50,
                        rate=30
                    )
                ),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=100,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50,
                        rate=30
                    )
                ),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=50,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50,
                        rate=30
                    )
                ),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=1,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50,
                        rate=30
                    )
                ),
            ],
            [item.trimmed_range() for item in timeline.clip_if()]
        )

        self.assertListEqual(
            [
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=1,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50 + 10,
                        rate=30
                    )
                ),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=100 - 7,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50 + 15 + 7,
                        rate=30
                    )
                ),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=33,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50 + 17,
                        rate=30
                    )
                ),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=1,
                        rate=30
                    ),
                    duration=otio.opentime.RationalTime(
                        value=50,
                        rate=30
                    )
                ),
            ],
            [item.visible_range() for item in timeline.clip_if()]
        )


if __name__ == '__main__':
    unittest.main()
