// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

// Example for converting an .otio file into a bundle.

#include "util.h"

#include <opentimelineio/bundle.h>

#include <filesystem>

using namespace OTIO_NS;

int
main(int argc, char** argv)
{
    if (argc != 3) {
        std::cout << "Usage: bundle (input.otio) (output.otioz|output.otiod)" << std::endl;
        return 1;
    }
    const std::string input  = examples::normalize_path(argv[1]);
    const std::string output = examples::normalize_path(argv[2]);

    // Read the timeline
    ErrorStatus                            error_status;
    SerializableObject::Retainer<Timeline> timeline(dynamic_cast<Timeline*>(
        Timeline::from_json_file(input, &error_status)));
    if (!timeline || is_error(error_status)) {
        examples::print_error(error_status);
        return 1;
    }

    // Write the bundle
    bundle::WriteOptions options;
    options.relative_media_base_dir =
        std::filesystem::u8path(input).parent_path().u8string();
    auto const ext = std::filesystem::u8path(output).extension().u8string();
    if (".otiod" == ext)
    {
        if (!bundle::write_otiod(
            timeline,
            output,
            options,
            &error_status)) {
            examples::print_error(error_status);
            return 1;
        }
    }
    else
    {
        if (!bundle::write_otioz(
            timeline,
            output,
            options,
            &error_status)) {
            examples::print_error(error_status);
            return 1;
        }
    }

    return 0;
}
