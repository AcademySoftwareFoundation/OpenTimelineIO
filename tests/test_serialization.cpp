// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "utils.h"

#include <opentimelineio/clip.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/safely_typed_any.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/serializableObjectWithMetadata.h>
#include <opentimelineio/serialization.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>

#include <fstream>
#include <iostream>
#include <string>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    Tests tests;

    tests.add_test("reject embedded NUL in JSON", [] {
        std::string input = R"({"x":1})";
        input.push_back('\0');
        input += R"({"y":2})";

        std::any destination = 42;
        OTIO_NS::ErrorStatus error;
        assertFalse(deserialize_json_from_string(input, &destination, &error));
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::JSON_PARSE_ERROR);
        assertEqual(std::any_cast<int>(destination), 42);

        TempDir temp;
        auto const file = temp.path() / "embedded_nul.otio";
        {
            std::ofstream output(file, std::ios::binary);
            output.write(input.data(), input.size());
        }
        error = OTIO_NS::ErrorStatus();
        assertFalse(deserialize_json_from_file(
            file.string(), &destination, &error));
        assertEqual(error.outcome, OTIO_NS::ErrorStatus::JSON_PARSE_ERROR);
        assertEqual(std::any_cast<int>(destination), 42);

        // Escaped NUL is valid JSON, as is whitespace after the root value.
        error = OTIO_NS::ErrorStatus();
        assertTrue(deserialize_json_from_string(
            R"({"x":"\u0000"})" " \n", &destination, &error));
        assertFalse(is_error(error));

        {
            std::ofstream output(file, std::ios::binary | std::ios::trunc);
            output << R"({"x":"\u0000"})" " \n";
        }
        error = OTIO_NS::ErrorStatus();
        assertTrue(deserialize_json_from_file(
            file.string(), &destination, &error));
        assertFalse(is_error(error));
    });

    tests.add_test("success with default indent", [] {
        SerializableObject::Retainer<Clip>  cl = new Clip();
        SerializableObject::Retainer<Track> tr = new Track();
        tr->append_child(cl);
        SerializableObject::Retainer<Timeline> tl = new Timeline();
        tl->tracks()->append_child(tr);

        OTIO_NS::ErrorStatus err;
        auto                 output = tl.value->to_json_string(&err, {});
        assertFalse(is_error(err));
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

    tests.add_test("success with indent set to 0", [] {
        SerializableObject::Retainer<SerializableObjectWithMetadata> so =
            new SerializableObjectWithMetadata();

        OTIO_NS::ErrorStatus err;
        auto                 output = so.value->to_json_string(&err, {}, 0);
        assertFalse(is_error(err));
        assertEqual(
            output.c_str(),
            R"CONTENT({"OTIO_SCHEMA":"SerializableObjectWithMetadata.1","metadata":{},"name":""})CONTENT");
    });

    tests.add_test("success with indent set to 2", [] {
        SerializableObject::Retainer<SerializableObjectWithMetadata> so =
            new SerializableObjectWithMetadata();

        OTIO_NS::ErrorStatus err;
        auto                 output = so.value->to_json_string(&err, {}, 2);
        assertFalse(is_error(err));
        assertEqual(output.c_str(), R"CONTENT({
  "OTIO_SCHEMA": "SerializableObjectWithMetadata.1",
  "metadata": {},
  "name": ""
})CONTENT");
    });

    tests.add_test("clone", [] {
        auto json     = R"CONTENT({
  "OTIO_SCHEMA": "SerializableObjectWithMetadata.1",
  "metadata": {
    "a": 1,
    "b": "two",
    "c": [
      3,
      4,
      5
    ],
    "d": {
      "hello": "nested"
    }
  },
  "name": ""
})CONTENT";
        auto original = SerializableObjectWithMetadata::from_json_string(json);
        auto cloned   = original->clone();
        assert(cloned != nullptr);
        OTIO_NS::ErrorStatus err;
        auto                 cloned_json = cloned->to_json_string(&err, {}, 2);
        assertFalse(is_error(err));
        assertEqual(json, cloned_json.c_str());
    });

    tests.add_test("clone with cycle returns nullptr", [] {
        auto original                 = new SerializableObjectWithMetadata();
        original->metadata()["cycle"] = original;
        auto cloned                   = original->clone();
        assert(cloned == nullptr);
    });

    tests.run(argc, argv);
    return 0;
}
