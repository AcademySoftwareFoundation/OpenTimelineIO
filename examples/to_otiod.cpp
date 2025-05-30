// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

// Example OTIO script that converts a timeline to an .otiod file bundle.

#include "util.h"

#include <opentimelineio/bundle.h>
#include <opentimelineio/timeline.h>

#include <filesystem>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;
namespace bundle = opentimelineio::OPENTIMELINEIO_VERSION::bundle;

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "Usage: to_otiod (input.otio) (output.otiod)" << std::endl;
        return 1;
    }
    const std::string input = examples::normalize_path(argv[1]);
    const std::string output = examples::normalize_path(argv[2]);
    
    otio::ErrorStatus error_status;
    otio::SerializableObject::Retainer<otio::Timeline> timeline(
        dynamic_cast<otio::Timeline*>(otio::Timeline::from_json_file(input, &error_status)));
    if (!timeline || otio::is_error(error_status))
    {
        examples::print_error(error_status);
        exit(1);
    }

    if (!bundle::to_otiod(
        timeline,
        std::filesystem::path(input).parent_path().u8string(),
        output,
        bundle::MediaReferencePolicy::ErrorIfNotFile,
        &error_status))
    {
        examples::print_error(error_status);
        exit(1);
    }
    
    return 0;
}
