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
        "test_children_if", [] {
        using namespace otio;

        // Find a clip in a serializable collection.
        otio::SerializableObject::Retainer<otio::Clip>  cl = new otio::Clip();
        otio::SerializableObject::Retainer<otio::Track> tr = new otio::Track();
        tr->append_child(cl);
        otio::SerializableObject::Retainer<otio::Timeline> tl = new otio::Timeline();
        tl->tracks()->append_child(tr);
        otio::SerializableObject::Retainer<otio::SerializableCollection> sc =
            new otio::SerializableCollection();
        sc->insert_child(0, tl);
        opentimelineio::v1_0::ErrorStatus err;
        auto result = sc->children_if<otio::Clip>(&err, {}, false);
        assertEqual(result.size(), 1);
    });

    tests.run(argc, argv);
    return 0;
}
