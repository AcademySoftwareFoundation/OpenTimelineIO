// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>
#include <opentimelineio/serialization.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/serializableObjectWithMetadata.h>
#include <opentimelineio/safely_typed_any.h>

#include <iostream>
#include <string>

namespace otime = opentime::OPENTIME_VERSION_NS;
namespace otio  = opentimelineio::OPENTIMELINEIO_VERSION_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test(
        "success with default indent", [] {
        otio::SerializableObject::Retainer<otio::Clip> cl =
            new otio::Clip();
        otio::SerializableObject::Retainer<otio::Track> tr =
            new otio::Track();
        tr->append_child(cl);
        otio::SerializableObject::Retainer<otio::Timeline> tl =
            new otio::Timeline();
        tl->tracks()->append_child(tr);

        otio::ErrorStatus err;
        auto output = tl.value->to_json_string(&err, {});
        assertFalse(otio::is_error(err));
        assertEqual(output.c_str(), R"CONTENT({
    "OTIO_SCHEMA": "Timeline.1",
    "metadata": {},
    "name": "",
    "global_start_time": null,
    "tracks": {
        "OTIO_SCHEMA": "Stack.1",
        "metadata": {},
        "name": "tracks",
        "source_range": null,
        "effects": [],
        "markers": [],
        "enabled": true,
        "color": null,
        "children": [
            {
                "OTIO_SCHEMA": "Track.1",
                "metadata": {},
                "name": "",
                "source_range": null,
                "effects": [],
                "markers": [],
                "enabled": true,
                "color": null,
                "children": [
                    {
                        "OTIO_SCHEMA": "Clip.2",
                        "metadata": {},
                        "name": "",
                        "source_range": null,
                        "effects": [],
                        "markers": [],
                        "enabled": true,
                        "color": null,
                        "media_references": {
                            "DEFAULT_MEDIA": {
                                "OTIO_SCHEMA": "MissingReference.1",
                                "metadata": {},
                                "name": "",
                                "available_range": null,
                                "available_image_bounds": null
                            }
                        },
                        "active_media_reference_key": "DEFAULT_MEDIA"
                    }
                ],
                "kind": "Video"
            }
        ]
    }
})CONTENT");
    });

    tests.add_test(
        "success with indent set to 0", [] {
        otio::SerializableObject::Retainer<otio::SerializableObjectWithMetadata> so =
            new otio::SerializableObjectWithMetadata();

        otio::ErrorStatus err;
        auto output = so.value->to_json_string(&err, {}, 0);
        assertFalse(otio::is_error(err));
        assertEqual(output.c_str(), R"CONTENT({"OTIO_SCHEMA":"SerializableObjectWithMetadata.1","metadata":{},"name":""})CONTENT");
    });

    tests.add_test(
        "success with indent set to 2", [] {
        otio::SerializableObject::Retainer<otio::SerializableObjectWithMetadata> so =
            new otio::SerializableObjectWithMetadata();

        otio::ErrorStatus err;
        auto output = so.value->to_json_string(&err, {}, 2);
        assertFalse(otio::is_error(err));
        assertEqual(output.c_str(), R"CONTENT({
  "OTIO_SCHEMA": "SerializableObjectWithMetadata.1",
  "metadata": {},
  "name": ""
})CONTENT");
    });

    tests.run(argc, argv);
    return 0;
}
