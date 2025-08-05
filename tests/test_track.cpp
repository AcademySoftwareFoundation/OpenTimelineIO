// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>

#include <iostream>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test(
        "test_find_children", [] {
        using namespace otio;
        otio::SerializableObject::Retainer<otio::Clip> cl =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl);
        OTIO_NS::ErrorStatus err;
        auto result = tr->find_children<otio::Clip>(&err);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl.value);
    });
    tests.add_test(
        "test_find_children_search_range", [] {
        using namespace otio;
        const TimeRange range(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0));
        otio::SerializableObject::Retainer<otio::Clip> cl0 =
            new otio::Clip();
        cl0->set_source_range(range);
        otio::SerializableObject::Retainer<otio::Clip> cl1 =
            new otio::Clip();
        cl1->set_source_range(range);
        otio::SerializableObject::Retainer<otio::Clip> cl2 =
            new otio::Clip();
        cl2->set_source_range(range);
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl0);
        tr->append_child(cl1);
        tr->append_child(cl2);
        OTIO_NS::ErrorStatus err;
        auto result = tr->find_children<otio::Clip>(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
        result = tr->find_children<otio::Clip>(
            &err,
            TimeRange(RationalTime(24.0, 24.0), RationalTime(24.0, 24.0)));
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl1.value);
        result = tr->find_children<otio::Clip>(
            &err,
            TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)));
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl2.value);
        result = tr->find_children<otio::Clip>(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(48.0, 24.0)));
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
        result = tr->find_children<otio::Clip>(
            &err,
            TimeRange(RationalTime(24.0, 24.0), RationalTime(48.0, 24.0)));
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl1.value);
        assertEqual(result[1].value, cl2.value);
        result = tr->find_children<otio::Clip>(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(72.0, 24.0)));
        assertEqual(result.size(), 3);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
        assertEqual(result[2].value, cl2.value);
    });
    tests.add_test(
        "test_find_children_shallow_search", [] {
        using namespace otio;
        otio::SerializableObject::Retainer<otio::Clip> cl0 =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Clip> cl1 =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Stack> st =
            new otio::Stack();
        st->append_child(cl1);
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl0);
        tr->append_child(st);
        OTIO_NS::ErrorStatus err;
        auto result = tr->find_children<otio::Clip>(&err, std::nullopt, true);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
        result = tr->find_children<otio::Clip>(&err, std::nullopt, false);
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
    });

    tests.add_test(
        "test_find_children_stack", [] {
        using namespace otio;

        SerializableObject::Retainer<Stack> stack = new Stack();
        SerializableObject::Retainer<Track> track = new Track;
        SerializableObject::Retainer<Clip>  clip  = new Clip;
        stack->append_child(track);
        track->append_child(clip);

        // Simple find.
        clip->set_source_range(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(3.0, 24.0)));
        otio::ErrorStatus err;
        auto items = stack->find_children(
            &err,
            TimeRange(RationalTime(0.0, 24.0), RationalTime(1.0, 24.0)));
        assertFalse(is_error(err));
        assertEqual(items.size(), 2);
        assertTrue(
            std::find(items.begin(), items.end(), track.value) != items.end());
        assertTrue(
            std::find(items.begin(), items.end(), clip.value) != items.end());

        // Set a short source range on the track.
        track->set_source_range(
            TimeRange(RationalTime(0.0, 24.0), RationalTime(2.0, 24.0)));
        items = stack->find_children(
            &err,
            TimeRange(RationalTime(2.0, 24.0), RationalTime(1.0, 24.0)));
        assertFalse(is_error(err));
        assertEqual(items.size(), 0);

        // Set a source range with a positive offset on the track.
        track->set_source_range(
            TimeRange(RationalTime(3.0, 24.0), RationalTime(3.0, 24.0)));
        items = stack->find_children(
            &err,
            TimeRange(RationalTime(2.0, 24.0), RationalTime(1.0, 24.0)));
        assertFalse(is_error(err));
        assertEqual(items.size(), 1);
        assertTrue(
            std::find(items.begin(), items.end(), track.value) != items.end());

        // Set a source range with a negative offset on the track.
        track->set_source_range(
            TimeRange(RationalTime(-1.0, 24.0), RationalTime(3.0, 24.0)));
        items = stack->find_children(
            &err,
            TimeRange(RationalTime(1.0, 24.0), RationalTime(1.0, 24.0)));
        assertFalse(is_error(err));
        assertEqual(items.size(), 2);
        assertTrue(
            std::find(items.begin(), items.end(), track.value) != items.end());
        assertTrue(
            std::find(items.begin(), items.end(), clip.value) != items.end());
    });

    tests.run(argc, argv);
    return 0;
}
