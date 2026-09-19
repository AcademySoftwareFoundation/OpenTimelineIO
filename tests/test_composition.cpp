// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/composition.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/item.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
#include <opentimelineio/transition.h>

#include <iostream>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    // test a basic case of find_children
    tests.add_test("test_find_children", [] {
        SerializableObject::Retainer<Composition> comp = new Composition;
        SerializableObject::Retainer<Item>        item = new Item;

        comp->append_child(item);
        OTIO_NS::ErrorStatus err;
        auto                 result = comp->find_children<>(&err);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, item.value);
    });

    // test stack and track correctly calls find_clips from composition parent class
    tests.add_test("test_find_clips", [] {
        SerializableObject::Retainer<Stack>      stack      = new Stack();
        SerializableObject::Retainer<Track>      track      = new Track;
        SerializableObject::Retainer<Clip>       clip       = new Clip;
        SerializableObject::Retainer<Transition> transition = new Transition;

        stack->append_child(track);
        track->append_child(transition);
        track->append_child(clip);

        OTIO_NS::ErrorStatus err;
        auto                 items = stack->find_clips(&err);
        assertFalse(is_error(err));
        assertEqual(items.size(), 1);
        assertEqual(items[0].value, clip.value);

        items = track->find_clips(&err);
        assertFalse(is_error(err));
        assertEqual(items.size(), 1);
        assertEqual(items[0].value, clip.value);
    });

    tests.add_test("test_trimmed_range_of_nested_child", [] {
        SerializableObject::Retainer<Stack> root  = new Stack;
        SerializableObject::Retainer<Track> track = new Track;
        SerializableObject::Retainer<Stack> stack = new Stack;
        SerializableObject::Retainer<Clip>  clip  = new Clip;

        clip->set_source_range(
            TimeRange(RationalTime(100, 24), RationalTime(50, 24)));
        root->append_child(track);
        track->append_child(new Gap(RationalTime(10, 24)));
        track->append_child(stack);
        stack->append_child(clip);

        OTIO_NS::ErrorStatus err;
        auto                 range = root->trimmed_range_of_child(clip, &err);
        assertFalse(is_error(err));
        assertTrue(range.has_value());
        assertEqual(
            *range,
            TimeRange(RationalTime(10, 24), RationalTime(50, 24)));
    });

    tests.add_test("test_composable_available_image_bounds", [] {
        SerializableObject::Retainer<Gap> gap = new Gap();
        // Calling available_image_bounds with default nullptr should not crash
        auto bounds = gap->available_image_bounds();
        assertFalse(bounds.has_value());

        // Calling with explicit nullptr should not crash
        bounds = gap->available_image_bounds(nullptr);
        assertFalse(bounds.has_value());

        // Calling with valid error_status pointer sets NOT_IMPLEMENTED
        OTIO_NS::ErrorStatus err;
        bounds = gap->available_image_bounds(&err);
        assertFalse(bounds.has_value());
        assertTrue(is_error(err));
        assertEqual(err.outcome, OTIO_NS::ErrorStatus::NOT_IMPLEMENTED);

        // Also test Composable directly
        SerializableObject::Retainer<Composable> composable = new Composable();
        bounds = composable->available_image_bounds();
        assertFalse(bounds.has_value());

        bounds = composable->available_image_bounds(nullptr);
        assertFalse(bounds.has_value());

        OTIO_NS::ErrorStatus comp_err;
        bounds = composable->available_image_bounds(&comp_err);
        assertFalse(bounds.has_value());
        assertTrue(is_error(comp_err));
        assertEqual(comp_err.outcome, OTIO_NS::ErrorStatus::NOT_IMPLEMENTED);
    });

    tests.run(argc, argv);
    return 0;
}
