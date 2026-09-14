// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/composition.h>
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

    tests.add_test("test_orphan_ranges_report_errors", [] {
        SerializableObject::Retainer<Clip> clip = new Clip;
        OTIO_NS::ErrorStatus               error;

        assertEqual(clip->range_in_parent(&error), TimeRange());
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::NOT_A_CHILD);

        error = OTIO_NS::ErrorStatus();
        assertFalse(clip->trimmed_range_in_parent(&error).has_value());
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::NOT_A_CHILD);
        assertEqual(clip->range_in_parent(), TimeRange());
        assertFalse(clip->trimmed_range_in_parent().has_value());

        SerializableObject::Retainer<Transition> transition = new Transition;
        error = OTIO_NS::ErrorStatus();
        assertFalse(transition->range_in_parent(&error).has_value());
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::NOT_A_CHILD);

        error = OTIO_NS::ErrorStatus();
        assertFalse(transition->trimmed_range_in_parent(&error).has_value());
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::NOT_A_CHILD);
        assertFalse(transition->range_in_parent().has_value());
        assertFalse(transition->trimmed_range_in_parent().has_value());

        SerializableObject::Retainer<Stack> stack = new Stack;
        error = OTIO_NS::ErrorStatus();
        assertEqual(stack->range_of_child(clip, &error), TimeRange());
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::NOT_DESCENDED_FROM);
        assertEqual(stack->range_of_child(clip), TimeRange());
        assertEqual(
            stack->trimmed_range_of_child(clip).value(),
            TimeRange());

        error = OTIO_NS::ErrorStatus();
        stack->trimmed_range_of_child(clip, &error);
        assertEqual(
            error.outcome,
            OTIO_NS::ErrorStatus::NOT_DESCENDED_FROM);
    });

    tests.run(argc, argv);
    return 0;
}
