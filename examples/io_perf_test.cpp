// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <iostream>

#include "opentimelineio/clip.h"
#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/serialization.h"
#include "opentimelineio/deserialization.h"
#include "opentimelineio/timeline.h"

#include "util.h"

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

using chrono_time_point = std::chrono::steady_clock::time_point;

const struct {
    bool FIXED_TMP = true;
    bool PRINT_CPP_VERSION_FAMILY    = false;
    bool TO_JSON_STRING              = true;
    bool TO_JSON_STRING_NO_DOWNGRADE = true;
    bool TO_JSON_FILE                = true;
    bool TO_JSON_FILE_NO_DOWNGRADE   = true;
    bool CLONE_TEST                  = true;
    bool SINGLE_CLIP_DOWNGRADE_TEST  = true;
} RUN_STRUCT ;

// typedef std::chrono::duration<float> fsec;
    // auto t0 = Time::now();
    // auto t1 = Time::now();
    // fsec fs = t1 - t0;

/// utility function for printing std::chrono elapsed time
double
print_elapsed_time(
        const std::string& message,
        const chrono_time_point& begin,
        const chrono_time_point& end
)
{
    const std::chrono::duration<float> dur = end - begin;

    std::cout << message << ": " << dur.count() << " [s]" << std::endl;

    return dur.count();
}

void
print_version_map()
{
    std::cerr << "current version map: "  << std::endl;
    for (const auto& kv_lbl: otio::CORE_VERSION_MAP)
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
    if (RUN_STRUCT.PRINT_CPP_VERSION_FAMILY)
    {
        print_version_map();
    }

    if (argc < 2) 
    {
        std::cerr << "usage: otio_io_perf_test path/to/timeline.otio ";
        std::cerr << "[--keep-tmp]" << std::endl;
        return 1;
    }

    bool keep_tmp = false;
    if (argc > 2)
    {
        const std::string arg = argv[2];
        if (arg == "--keep-tmp")
        {
            keep_tmp = true;
        }
    }

    const std::string tmp_dir_path = (
        RUN_STRUCT.FIXED_TMP 
        ? "/var/tmp/ioperftest" 
        : examples::create_temp_dir()
    );

    otio::ErrorStatus err;
    assert(!otio::is_error(err));

    otio::schema_version_map downgrade_manifest = {
        {"FakeSchema", 3},
        {"Clip", 1},
        {"OtherThing", 12000}
    };

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
        cl->to_json_file(
                examples::normalize_path(tmp_dir_path + "/clip.otio"),
                &err,
                &downgrade_manifest
        );
        chrono_time_point end = std::chrono::steady_clock::now();
        assert(!otio::is_error(err));
        print_elapsed_time("downgrade clip", begin, end);
    }

    std::any tl;
    std::string fname = std::string(argv[1]);

    // read file
    chrono_time_point begin = std::chrono::steady_clock::now();
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
            dynamic_cast<otio::Timeline*>(
                otio::Timeline::from_json_file(
                    examples::normalize_path(argv[1]),
                    &err
                )
            )
    );
    chrono_time_point end = std::chrono::steady_clock::now();
    assert(!otio::is_error(err));
    if (!timeline)
    {
        examples::print_error(err);
        return 1;
    }

    print_elapsed_time("deserialize_json_from_file", begin, end);


    double str_dg, str_nodg;
    if (RUN_STRUCT.TO_JSON_STRING)
    {
        begin = std::chrono::steady_clock::now();
        const std::string result = timeline.value->to_json_string(
                &err,
                &downgrade_manifest
        );
        end = std::chrono::steady_clock::now();
        assert(!otio::is_error(err));

        if (otio::is_error(err))
        {
            examples::print_error(err);
            return 1;
        }
        str_dg = print_elapsed_time("serialize_json_to_string", begin, end);
    }

    if (RUN_STRUCT.TO_JSON_STRING_NO_DOWNGRADE)
    {
        begin = std::chrono::steady_clock::now();
        const std::string result = timeline.value->to_json_string(&err, {});
        end = std::chrono::steady_clock::now();
        assert(!otio::is_error(err));

        if (otio::is_error(err))
        {
            examples::print_error(err);
            return 1;
        }
        str_nodg = print_elapsed_time(
                "serialize_json_to_string [no downgrade]",
                begin,
                end
        );
    }

    if (RUN_STRUCT.TO_JSON_STRING && RUN_STRUCT.TO_JSON_STRING_NO_DOWNGRADE)
    {
        std::cout << "  JSON to string no_dg/dg: " << str_dg / str_nodg;
        std::cout << std::endl;
    }

    double file_dg, file_nodg;
    if (RUN_STRUCT.TO_JSON_FILE)
    {
        begin = std::chrono::steady_clock::now();
        timeline.value->to_json_file(
                examples::normalize_path(tmp_dir_path + "/io_perf_test.otio"),
                &err,
                &downgrade_manifest
        );
        end = std::chrono::steady_clock::now();
        assert(!otio::is_error(err));
        file_dg = print_elapsed_time("serialize_json_to_file", begin, end);
    }

    if (RUN_STRUCT.TO_JSON_FILE_NO_DOWNGRADE)
    {
        begin = std::chrono::steady_clock::now();
        timeline.value->to_json_file(
                examples::normalize_path(
                    tmp_dir_path 
                    + "/io_perf_test.nodowngrade.otio"
                ),
                &err,
                {}
        );
        end = std::chrono::steady_clock::now();
        assert(!otio::is_error(err));
        file_nodg = print_elapsed_time(
                "serialize_json_to_file [no downgrade]",
                begin,
                end
        );
    }

    if (RUN_STRUCT.TO_JSON_FILE && RUN_STRUCT.TO_JSON_FILE_NO_DOWNGRADE)
    {
        std::cout << "  JSON to file no_dg/dg: " << file_dg / file_nodg;
        std::cout << std::endl;
    }

    if (keep_tmp || RUN_STRUCT.FIXED_TMP)
    {
        std::cout << "Temp directory preserved.  All files written to: ";
        std::cout << tmp_dir_path << std::endl;
    }
    else
    {
        // clean up
        const auto tmp_files = examples::glob(tmp_dir_path, "*");
        for (const auto& fp : tmp_files)
        {
            remove(fp.c_str());
        }
        remove(tmp_dir_path.c_str());
        std::cout << "cleaned up tmp dir, pass --keep-tmp to preserve";
        std::cout << " output." << std::endl;
    }

    return 0;
}
