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
        opentimelineio::v1_0::ErrorStatus err;
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
        opentimelineio::v1_0::ErrorStatus err;
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
        opentimelineio::v1_0::ErrorStatus err;
        auto result = tr->find_children<otio::Clip>(&err, std::nullopt, true);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
        result = tr->find_children<otio::Clip>(&err, std::nullopt, false);
        assertEqual(result.size(), 2);
        assertEqual(result[0].value, cl0.value);
        assertEqual(result[1].value, cl1.value);
    });

    tests.run(argc, argv);
    return 0;
}
