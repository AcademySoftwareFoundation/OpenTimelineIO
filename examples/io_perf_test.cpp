#include <iostream>

#include "opentimelineio/clip.h"
#include "opentimelineio/typeRegistry.h"
#include "util.h"
#include <opentimelineio/any.h>
#include <opentimelineio/serialization.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/timeline.h>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

using chrono_time_point = std::chrono::steady_clock::time_point;

constexpr struct {
    bool TO_JSON_STRING = true;
    bool TO_JSON_STRING_NO_DOWNGRADE = true;
    bool TO_JSON_FILE = true;
    bool TO_JSON_FILE_NO_DOWNGRADE = true;
    bool CLONE_TEST = true;
    bool SINGLE_CLIP_DOWNGRADE_TEST = true;
} RUN_STRUCT ;

/// utility function for printing std::chrono elapsed time
const void
print_elapsed_time(
        const std::string& message,
        const chrono_time_point& begin,
        const chrono_time_point& end
)
{
    const auto dur = (
            std::chrono::duration_cast<std::chrono::microseconds>(
                end - begin
            ).count()
    );
    std::cout << message << ": " << dur/1000000.0 << " [s]" << std::endl;
}

void
print_version_map()
{
    std::cerr << "current version map: "  << std::endl;
    for (auto kv_lbl: opentimelineio::v1_0::core_release_to_schema_version_map())
    {
        std::cerr << "  " << kv_lbl.first << std::endl;
        for (auto kv_schema_version : kv_lbl.second)
        {
            std::cerr << "    \"" << kv_schema_version.first << "\": ";
            std::cerr << kv_schema_version.second << std::endl;
        }
    }

}

int
main(
        int argc,
        char *argv[]
)
{
    print_version_map();

    if (argc < 2) {
        std::cerr << "usage: otio_io_perf_test path/to/timeline.otio";
        std::cerr << std::endl;
        return 1;
    }

    otio::ErrorStatus err;

    otio::schema_version_map downgrade_manifest = {
        {"FakeSchema", 3},
        {"Clip", 1},
        {"OtherThing", 12000}
    };

    print_version_map();

    if (RUN_STRUCT.CLONE_TEST)
    {
        otio::SerializableObject::Retainer<otio::Clip> cl = new otio::Clip("test");
        cl->metadata()["example thing"] = "banana";
        const auto intermediate = cl->clone(&err);
        assert(intermediate != nullptr);
        const auto cl_clone = dynamic_cast<otio::Clip*>(intermediate);
        assert(cl_clone != nullptr);
        assert(!otio::is_error(err));
        assert(cl->name() == cl_clone->name());
    }

    if (RUN_STRUCT.SINGLE_CLIP_DOWNGRADE_TEST)
    {
        otio::SerializableObject::Retainer<otio::Clip> cl = new otio::Clip("test");
        cl->metadata()["example thing"] = "banana";
        chrono_time_point begin = std::chrono::steady_clock::now();
        cl->to_json_file("/var/tmp/clip.otio", &err, &downgrade_manifest);
        chrono_time_point end = std::chrono::steady_clock::now();
        print_elapsed_time("downgrade clip", begin, end);
    }

    otio::any tl;
    std::string fname = std::string(argv[1]);

    chrono_time_point begin = std::chrono::steady_clock::now();
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
            dynamic_cast<otio::Timeline*>(
                otio::Timeline::from_json_file(argv[1], &err)
            )
    );
    chrono_time_point end = std::chrono::steady_clock::now();
    if (!timeline)
    {
        examples::print_error(err);
        return 1;
    }

    print_elapsed_time("deserialize_json_from_file", begin, end);


    if (RUN_STRUCT.TO_JSON_STRING)
    {
        begin = std::chrono::steady_clock::now();
        const std::string result = timeline.value->to_json_string(
                &err,
                &downgrade_manifest
        );
        end = std::chrono::steady_clock::now();

        if (otio::is_error(err))
        {
            examples::print_error(err);
            return 1;
        }
        print_elapsed_time("serialize_json_to_string", begin, end);
    }

    if (RUN_STRUCT.TO_JSON_STRING_NO_DOWNGRADE)
    {
        begin = std::chrono::steady_clock::now();
        const std::string result = timeline.value->to_json_string(&err, {});
        end = std::chrono::steady_clock::now();

        if (otio::is_error(err))
        {
            examples::print_error(err);
            return 1;
        }
        print_elapsed_time("serialize_json_to_string [no downgrade]", begin, end);
    }

    if (RUN_STRUCT.TO_JSON_FILE)
    {
        begin = std::chrono::steady_clock::now();
        timeline.value->to_json_file(
                "/var/tmp/io_perf_test.otio",
                &err,
                &downgrade_manifest
        );
        end = std::chrono::steady_clock::now();
        print_elapsed_time("serialize_json_to_file", begin, end);
    }

    if (RUN_STRUCT.TO_JSON_FILE_NO_DOWNGRADE)
    {
        begin = std::chrono::steady_clock::now();
        timeline.value->to_json_file("/var/tmp/io_perf_test.nodowngrade.otio", &err, {});
        end = std::chrono::steady_clock::now();
        print_elapsed_time("serialize_json_to_file [no downgrade]", begin, end);
    }

    return 0;
}
