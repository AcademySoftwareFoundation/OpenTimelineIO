// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/serializableCollection.h>
#include <opentimelineio/timeline.h>
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
        otio::SerializableObject::Retainer<otio::Timeline> tl =
            new otio::Timeline();
        tl->tracks()->append_child(tr);
        otio::SerializableObject::Retainer<otio::SerializableCollection>
            sc = new otio::SerializableCollection();
        sc->insert_child(0, tl);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = sc->find_children<otio::Clip>(&err, {}, false);
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
        otio::SerializableObject::Retainer<otio::Timeline> tl =
            new otio::Timeline();
        tl->tracks()->append_child(tr);
        otio::SerializableObject::Retainer<otio::SerializableCollection>
            sc = new otio::SerializableCollection();
        sc->insert_child(0, tl);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = sc->find_children<otio::Clip>(&err, range);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
    });
    tests.add_test(
        "test_find_children_shallow_search", [] {
        using namespace otio;
        otio::SerializableObject::Retainer<otio::Clip> cl =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl);
        otio::SerializableObject::Retainer<otio::Timeline> tl =
            new otio::Timeline();
        tl->tracks()->append_child(tr);
        otio::SerializableObject::Retainer<otio::SerializableCollection>
            sc = new otio::SerializableCollection();
        sc->insert_child(0, tl);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = sc->find_children<otio::Clip>(&err, std::nullopt, true);
        assertEqual(result.size(), 0);
        result = sc->find_children<otio::Clip>(&err, std::nullopt, false);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl.value);
    });

    tests.run(argc, argv);
    return 0;
}
