// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/serializableCollection.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>

#include <iostream>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test(
        "test_find_children", [] {
        SerializableObject::Retainer<Clip> cl = new Clip();
        SerializableObject::Retainer<Track> tr = new Track();
        tr->append_child(cl);
        SerializableObject::Retainer<Timeline> tl = new Timeline();
        tl->tracks()->append_child(tr);
        SerializableObject::Retainer<SerializableCollection>
            sc = new SerializableCollection();
        sc->insert_child(0, tl);
        OTIO_NS::ErrorStatus err;
        auto result = sc->find_children<Clip>(&err, {}, false);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl.value);
    });
    tests.add_test(
        "test_find_children_search_range", [] {
        const TimeRange range(RationalTime(0.0, 24.0), RationalTime(24.0, 24.0));
        SerializableObject::Retainer<Clip> cl0 = new Clip();
        cl0->set_source_range(range);
        SerializableObject::Retainer<Clip> cl1 = new Clip();
        cl1->set_source_range(range);
        SerializableObject::Retainer<Clip> cl2 = new Clip();
        cl2->set_source_range(range);
        SerializableObject::Retainer<Track> tr = new Track();
        tr->append_child(cl0);
        tr->append_child(cl1);
        tr->append_child(cl2);
        SerializableObject::Retainer<Timeline> tl = new Timeline();
        tl->tracks()->append_child(tr);
        SerializableObject::Retainer<SerializableCollection>
            sc = new SerializableCollection();
        sc->insert_child(0, tl);
        OTIO_NS::ErrorStatus err;
        auto result = sc->find_children<Clip>(&err, range);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl0.value);
    });
    tests.add_test(
        "test_find_children_shallow_search", [] {
        SerializableObject::Retainer<Clip> cl = new Clip();
        SerializableObject::Retainer<Track> tr = new Track();
        tr->append_child(cl);
        SerializableObject::Retainer<Timeline> tl = new Timeline();
        tl->tracks()->append_child(tr);
        SerializableObject::Retainer<SerializableCollection>
            sc = new SerializableCollection();
        sc->insert_child(0, tl);
        OTIO_NS::ErrorStatus err;
        auto result = sc->find_children<Clip>(&err, std::nullopt, true);
        assertEqual(result.size(), 0);
        result = sc->find_children<Clip>(&err, std::nullopt, false);
        assertEqual(result.size(), 1);
        assertEqual(result[0].value, cl.value);
    });

    tests.run(argc, argv);
    return 0;
}
