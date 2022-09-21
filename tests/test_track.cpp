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
        "test_children_if", [] {
        using namespace otio;
        {
            // Find a clip in a track.
            otio::SerializableObject::Retainer<otio::Clip> cl =
                new otio::Clip();
            otio::SerializableObject::Retainer<otio::Track> tr =
                new otio::Track();
            tr->append_child(cl);
            opentimelineio::v1_0::ErrorStatus err;
            auto result = tr->children_if<otio::Clip>(&err);
            assertEqual(result.size(), 1);
        }
        {
            // Test the search range parameter.
            TimeRange range(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0));
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
            auto result = tr->children_if<otio::Clip>(
                &err,
                TimeRange(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0)));
            assertEqual(result.size(), 1);
            assertTrue(result[0] = cl0);
            result = tr->children_if<otio::Clip>(
                &err,
                TimeRange(RationalTime(24.0, 24.0), RationalTime(24.0, 24.0)));
            assertEqual(result.size(), 1);
            assertTrue(result[0] = cl1);
            result = tr->children_if<otio::Clip>(
                &err,
                TimeRange(RationalTime(48.0, 24.0), RationalTime(24.0, 24.0)));
            assertEqual(result.size(), 1);
            assertTrue(result[0] = cl1);
            result = tr->children_if<otio::Clip>(
                &err,
                TimeRange(RationalTime(0.0, 24.0), RationalTime(48.0, 24.0)));
            assertEqual(result.size(), 2);
            assertTrue(result[0] = cl0);
            assertTrue(result[1] = cl1);
            result = tr->children_if<otio::Clip>(
                &err,
                TimeRange(RationalTime(24.0, 24.0), RationalTime(48.0, 24.0)));
            assertEqual(result.size(), 2);
            assertTrue(result[0] = cl1);
            assertTrue(result[1] = cl2);
            result = tr->children_if<otio::Clip>(
                &err,
                TimeRange(RationalTime(0.0, 24.0), RationalTime(72.0, 24.0)));
            assertEqual(result.size(), 3);
            assertTrue(result[0] = cl0);
            assertTrue(result[1] = cl1);
            assertTrue(result[2] = cl2);
        }
        {
            // Test the shallow search parameter.
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
            auto result = tr->children_if<otio::Clip>(&err, nullopt, true);
            assertEqual(result.size(), 1);
            assertTrue(result[0] = cl0);
            result = tr->children_if<otio::Clip>(&err, nullopt, false);
            assertEqual(result.size(), 2);
            assertTrue(result[0] = cl0);
            assertTrue(result[1] = cl1);
        }
    });

    tests.run(argc, argv);
    return 0;
}
